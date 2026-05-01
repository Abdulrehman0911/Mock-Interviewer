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
        try:
            # Import moviepy locally to avoid import-time failures when not installed
            from moviepy.editor import VideoFileClip
        except Exception:
            return {"success": False, "error": "moviepy_unavailable"}

        clip = VideoFileClip(video_path)
        duration = float(clip.duration or 0.0)

        if clip.audio is None:
            clip.close()
            return {"success": False, "error": "no_audio_in_video"}

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as t:
            tmp_audio = t.name
        clip.audio.write_audiofile(tmp_audio, logger=None)
        clip.close()

        transcript = ""
        if WhisperModel is None:
            print("⚠ faster-whisper not available, skipping transcription")
        else:
            print("Transcribing audio with faster-whisper...")
            try:
                model = WhisperModel("base", device="cpu")
                segments, info = model.transcribe(tmp_audio)
                transcript = " ".join([s.text for s in segments])
            except Exception as e:
                print(f"⚠ Transcription failed: {str(e)}")
                transcript = ""

        if not transcript:
            # fallback: empty transcript
            transcript = ""

        print("Extracting text features...")
        text_features = extract_text_features(transcript, duration)

        print("Analyzing behavior in video... (MediaPipe)")
        behavior = analyze_video_behavior(video_path)

        # Build full features dict (model expects 10 features)
        features = {
            "transcript_length": text_features.get("transcript_length", 0),
            "wpm": text_features.get("wpm", 0.0),
            "pause_count": text_features.get("pause_count", 0),
            "pause_avg_duration": text_features.get("pause_avg_duration", 0.0),
            "filler_count": text_features.get("filler_count", 0),
            "eye_contact_pct": behavior.get("eye_contact_pct", 0.0),
            "head_pose_score": behavior.get("head_pose_score", 0),
            "posture_score": behavior.get("posture_score", 0),
            "facial_stability_score": behavior.get("facial_stability_score", 0),
            # question_difficulty should be supplied by caller / endpoint
            "question_difficulty": 2,
        }

        print("✓ Video processed successfully")
        return {"success": True, "features": features, "transcript": transcript}

    except Exception as e:
        tb = traceback.format_exc()
        print(f"✗ Error processing video: {str(e)}\n{tb}")
        return {"success": False, "error": str(e)}

    finally:
        if tmp_audio:
            _safe_remove(tmp_audio)
