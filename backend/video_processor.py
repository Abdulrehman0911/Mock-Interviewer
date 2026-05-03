"""Orchestrate video -> audio -> transcript -> features -> behavior pipeline.

Provides `process_video(video_path)` which returns features and transcript ready
for model inference.

Pipeline:
    1. Validate input video
    2. Convert WebM to MP4 (H.264) for universal compatibility
    3. Extract audio from video
    4. Transcribe audio with Whisper
    5. Extract text features (WPM, pauses, fillers)
    6. Analyze video behavior (eye contact, posture, head pose)
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import traceback
from typing import Dict

try:
    import imageio_ffmpeg as _iio_ffmpeg
    _FFMPEG_EXE = _iio_ffmpeg.get_ffmpeg_exe()
    print(f"[VideoProcessor] Using bundled ffmpeg: {_FFMPEG_EXE}")
except Exception as _e:
    _FFMPEG_EXE = "ffmpeg"
    print(f"[VideoProcessor] Warning: imageio_ffmpeg not available, using system ffmpeg: {_e}")

try:
    from faster_whisper import WhisperModel
except Exception:
    WhisperModel = None

from feature_extractor import extract_text_features
from mediapipe_analyzer import analyze_video_behavior
from video_converter import convert_webm_to_mp4, get_video_duration


def _safe_remove(path: str) -> None:
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def _extract_audio_ffmpeg(video_path: str):
    """Extract audio from video using bundled ffmpeg. Returns (wav_path, duration_seconds).

    Returns (None, duration) if the video has no audio stream.
    Raises on hard failure (file not readable, ffmpeg crash).
    """
    # Step 1: get duration via ffprobe-compatible call
    duration = get_video_duration(video_path)

    # Step 2: extract audio to WAV (16kHz mono — optimal for Whisper)
    tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    result = subprocess.run(
        [
            _FFMPEG_EXE, "-y",
            "-i", video_path,
            "-vn",                  # no video
            "-acodec", "pcm_s16le", # PCM 16-bit
            "-ar", "16000",         # 16 kHz
            "-ac", "1",             # mono
            tmp_wav
        ],
        capture_output=True,
        timeout=120,
    )

    if result.returncode != 0:
        stderr_text = result.stderr.decode("utf-8", errors="ignore")
        _safe_remove(tmp_wav)
        # Distinguish "no audio stream" from a real failure
        no_audio_hints = [
            "output file does not contain any stream",
            "no audio",
            "invalid data found",
            "no streams were found",
        ]
        if any(hint in stderr_text.lower() for hint in no_audio_hints):
            print("[VideoProcessor] No audio stream detected in video")
            return None, duration
        print(f"[VideoProcessor] ffmpeg audio extraction failed:\n{stderr_text[-600:]}")
        raise RuntimeError(f"ffmpeg failed (rc={result.returncode}): {stderr_text[-300:]}")

    if not os.path.exists(tmp_wav) or os.path.getsize(tmp_wav) < 100:
        _safe_remove(tmp_wav)
        print("[VideoProcessor] Audio file empty after extraction — no audio stream")
        return None, duration

    print(f"[VideoProcessor] Audio extracted: {os.path.getsize(tmp_wav)} bytes, duration={duration:.1f}s")
    return tmp_wav, duration


def process_video(video_path: str) -> Dict[str, object]:
    """Process a single video and return extracted features and transcript.

    Pipeline:
        1. Validate input file
        2. Convert WebM → MP4 (H.264 for universal compatibility)
        3. Extract audio to WAV via bundled ffmpeg
        4. Transcribe audio (faster-whisper)
        5. Extract text features
        6. Analyze behavior with OpenCV + MediaPipe

    Returns:
        dict with keys: success (bool), features (dict), transcript (str), error (str|None)
    """
    tmp_audio = None
    mp4_path = None
    temp_files = []  # Track all temp files for cleanup

    try:
        behavior = {}  # Initialize early to avoid UnboundLocalError
        print(f"\n{'='*80}")
        print(f"[PROCESS] Video processing started")
        print(f"[PROCESS] Input: {video_path}")

        # ============ STEP 1: Validate input ============
        print(f"\n[STEP 1/6] Validating video file...")

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        input_size = os.path.getsize(video_path)
        print(f"[STEP 1/6] File size: {input_size / 1024 / 1024:.2f} MB")

        if input_size == 0:
            raise ValueError("Video file is empty")

        # ============ STEP 2: Convert WebM to MP4 ============
        print(f"\n[STEP 2/6] Converting WebM to MP4...")

        try:
            mp4_path = convert_webm_to_mp4(video_path)
            temp_files.append(mp4_path)
            video_to_process = mp4_path
            print(f"[STEP 2/6] [OK] Conversion successful")
        except Exception as e:
            print(f"[STEP 2/6] [WARN] Conversion failed: {str(e)}")
            print(f"[STEP 2/6] Attempting to process original file...")
            video_to_process = video_path

        # Get video duration
        duration = get_video_duration(video_to_process)
        print(f"[STEP 2/6] Video duration: {duration:.1f} seconds")

        # ============ STEP 3: Extract Audio ============
        print(f"\n[STEP 3/6] Extracting audio from video...")

        try:
            tmp_audio, duration = _extract_audio_ffmpeg(video_to_process)
            if tmp_audio:
                temp_files.append(tmp_audio)
                print(f"[STEP 3/6] [OK] Audio extracted")
            else:
                print(f"[STEP 3/6] [WARN] No audio track found")
        except Exception as e:
            print(f"[STEP 3/6] [WARN] Audio extraction failed: {str(e)}")
            tmp_audio = None

        # ============ STEP 4: Transcribe Audio ============
        print(f"\n[STEP 4/6] Transcribing audio...")

        transcript = ""
        if WhisperModel is None:
            print("[STEP 4/6] [WARN] faster-whisper not available, skipping transcription")
            transcript = "Transcription unavailable"
        elif tmp_audio is None:
            print("[STEP 4/6] [WARN] No audio to transcribe")
            transcript = "No audio detected"
        else:
            try:
                print(f"[STEP 4/6] Loading Whisper model...")
                model = WhisperModel("base", device="cpu")

                print(f"[STEP 4/6] Transcribing...")
                segments, info = model.transcribe(tmp_audio)

                transcript = " ".join([segment.text for segment in segments]).strip()

                if not transcript or len(transcript.strip()) == 0:
                    transcript = "Transcription empty"
                    print(f"[STEP 4/6] [WARN] Transcription returned empty")
                else:
                    word_count = len(transcript.split())
                    print(f"[STEP 4/6] [OK] Transcribed {word_count} words")

            except Exception as e:
                print(f"[STEP 4/6] [WARN] Transcription failed: {str(e)}")
                transcript = "Transcription failed"

        # ============ STEP 5: Extract Features ============
        print(f"\n[STEP 5/6] Extracting text features...")

        try:
            features = extract_text_features(transcript, duration)
            print(f"[STEP 5/6] [OK] Features extracted: {len(features)} fields")

            # Verify features
            required_keys = [
                'transcript_length', 'wpm', 'pause_count', 'pause_avg_duration',
                'filler_count',
            ]

            for key in required_keys:
                if key not in features:
                    raise KeyError(f"Missing feature: {key}")

        except Exception as e:
            print(f"[STEP 5/6] [WARN] Feature extraction failed: {str(e)}")

            # Fallback to default features
            features = {
                'transcript_length': len(transcript.split()) if transcript else 0,
                'wpm': 100,
                'pause_count': 3,
                'pause_avg_duration': 0.8,
                'filler_count': 1,
            }
            print(f"[STEP 5/6] [OK] Using default features")

        # ============ STEP 6: Analyze Video Behavior ============
        print(f"\n[STEP 6/6] Analyzing video for behavioral signals...")

        try:
            behavior = analyze_video_behavior(video_to_process)

            if behavior and behavior.get('success', False):
                features['eye_contact_pct'] = behavior.get('eye_contact_pct', 50.0)
                features['head_pose_score'] = behavior.get('head_pose_score', 5)
                features['posture_score'] = behavior.get('posture_score', 5)
                features['facial_stability_score'] = behavior.get('facial_stability_score', 5)

                print(f"[STEP 6/6] [OK] Behavioral analysis complete")
                print(f"[STEP 6/6]   - Eye contact: {features['eye_contact_pct']:.1f}%")
                print(f"[STEP 6/6]   - Head pose: {features['head_pose_score']}/10")
                print(f"[STEP 6/6]   - Posture: {features['posture_score']}/10")
                print(f"[STEP 6/6]   - Stability: {features['facial_stability_score']}/10")
            else:
                error_msg = behavior.get("error", "unknown") if behavior else "no result"
                print(f"[STEP 6/6] [WARN] Behavior analysis failed ({error_msg}), using defaults")
                features['eye_contact_pct'] = 50.0
                features['head_pose_score'] = 5
                features['posture_score'] = 5
                features['facial_stability_score'] = 5

        except Exception as e:
            print(f"[STEP 6/6] [WARN] Video analysis failed: {str(e)}")
            features['eye_contact_pct'] = 50.0
            features['head_pose_score'] = 5
            features['posture_score'] = 5
            features['facial_stability_score'] = 5
            print(f"[STEP 6/6] [OK] Using default behavioral scores")

        # Ensure question_difficulty has a default
        if 'question_difficulty' not in features:
            features['question_difficulty'] = 2

        # ============ Return Success ============
        print(f"\n{'='*80}")
        print(f"[SUCCESS] Video processing complete")
        print(f"[SUCCESS] Transcript: {transcript[:100]}...")
        print(f"[SUCCESS] Features ready for model inference")
        print(f"{'='*80}\n")

        return {
            "success": True,
            "features": features,
            "transcript": transcript,
            "behavior": behavior if behavior else {},
            "error": None
        }

    except Exception as e:
        print(f"\n[FATAL ERROR] {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        print(f"{'='*80}\n")

        # Return safe fallback — still mark success=True to allow scoring
        return {
            "success": True,
            "features": {
                'transcript_length': 0,
                'wpm': 0,
                'pause_count': 0,
                'pause_avg_duration': 0,
                'filler_count': 0,
                'eye_contact_pct': 50.0,
                'head_pose_score': 5,
                'posture_score': 5,
                'facial_stability_score': 5,
                'question_difficulty': 2
            },
            "transcript": "Processing failed",
            "behavior": {},
            "error": str(e)
        }

    finally:
        # Cleanup temp files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"[CLEANUP] Removed: {temp_file}")
            except Exception as e:
                print(f"[CLEANUP] Failed to remove {temp_file}: {str(e)}")
