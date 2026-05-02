"""Orchestrate video -> audio -> transcript -> features -> behavior pipeline.

Provides `process_video(video_path)` which returns features and transcript ready
for model inference.
"""

from __future__ import annotations

import os
import tempfile
import traceback
from typing import Dict

try:
    # Import inside function to avoid import-time dependency errors during quick imports/tests
    from faster_whisper import WhisperModel
except Exception:
    WhisperModel = None

from feature_extractor import extract_text_features
from mediapipe_analyzer import analyze_video_behavior


def _safe_remove(path: str) -> None:
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def process_video(video_path: str) -> Dict[str, object]:
    """Process a single video and return extracted features and transcript.

    Steps:
        - extract audio to temp file
        - transcribe audio (faster-whisper)
        - extract text features
        - analyze behavior with MediaPipe
        - combine and return

    Returns:
        dict with keys: success (bool), features (dict), transcript (str), error (str)
    """
    tmp_audio = None
    try:
        if not os.path.exists(video_path):
            return {"success": False, "error": "video_not_found"}

        print("Extracting audio from video...")
        
        # Try moviepy first, fall back to librosa if needed
        duration = 0.0
        audio_data = None
        sr = None
        
        try:
            from moviepy.video.io.VideoFileClip import VideoFileClip
            clip = VideoFileClip(video_path)
            duration = float(clip.duration or 0.0)
            if clip.audio is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as t:
                    tmp_audio = t.name
                clip.audio.write_audiofile(tmp_audio, logger=None)
            clip.close()
        except Exception as e:
            print(f"[!] Moviepy failed: {str(e)}, trying librosa...")
            try:
                import librosa
                audio_data, sr = librosa.load(video_path, sr=None)
                duration = librosa.get_duration(y=audio_data, sr=sr)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as t:
                    tmp_audio = t.name
                import soundfile as sf
                sf.write(tmp_audio, audio_data, sr)
            except Exception as e2:
                return {"success": False, "error": f"audio_extraction_failed: {str(e2)}"}

        transcript = ""
        if WhisperModel is None:
            print("[!] faster-whisper not available, skipping transcription")
        elif tmp_audio is None:
            print("[!] No audio track found in video, skipping transcription")
        else:
            print("Transcribing audio with faster-whisper...")
            try:
                model = WhisperModel("base", device="cpu")
                segments, info = model.transcribe(tmp_audio)
                transcript = " ".join([s.text for s in segments]).strip()
                print(f"[OK] Transcription complete: {len(transcript.split())} words")
            except Exception as e:
                print(f"[!] Transcription failed: {str(e)}")
                transcript = ""

        print("Extracting text features...")
        text_features = extract_text_features(transcript, duration)

        print("Analyzing behavior in video... (MediaPipe)")
        behavior = analyze_video_behavior(video_path)
        if not behavior.get("success", False):
            error_msg = behavior.get("error", "unknown")
            print(f"[!] Behavior analysis failed ({error_msg}), using default scores")
            # Use neutral defaults so scoring can still proceed
            behavior = {
                "success": True,
                "eye_contact_pct": 50.0,
                "head_pose_score": 5,
                "posture_score": 5,
                "facial_stability_score": 5,
                "dominant_emotion": "neutral",
            }

        # Build full features dict (model expects 10 features)
        features = {
            "transcript_length": text_features.get("transcript_length", 0),
            "wpm": text_features.get("wpm", 0.0),
            "pause_count": text_features.get("pause_count", 0),
            "pause_avg_duration": text_features.get("pause_avg_duration", 0.0),
            "filler_count": text_features.get("filler_count", 0),
            "eye_contact_pct": behavior["eye_contact_pct"],
            "head_pose_score": behavior["head_pose_score"],
            "posture_score": behavior["posture_score"],
            "facial_stability_score": behavior["facial_stability_score"],
            # question_difficulty should be supplied by caller / endpoint
            "question_difficulty": 2,
        }

        print("[OK] Video processed successfully")
        return {"success": True, "features": features, "transcript": transcript, "behavior": behavior}

    except Exception as e:
        tb = traceback.format_exc()
        print(f"[ERROR] Error processing video: {str(e)}\n{tb}")
        return {"success": False, "error": str(e)}

    finally:
        if tmp_audio:
            _safe_remove(tmp_audio)
