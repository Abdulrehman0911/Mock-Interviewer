"""Text feature extraction for interview transcripts.

Provides a single function `extract_text_features(transcript, audio_duration)` that
computes basic text/audio-derived features used by the scoring model.
"""

from __future__ import annotations

import math
import re
from typing import Dict


FILLER_WORDS = [
    "um",
    "uh",
    "ah",
    "aha",
    "like",
    "you know",
    "basically",
    "literally",
    "actually",
    "anyway",
]


FILLER_PATTERNS = [
    # elongated fillers and stutters such as "ahhh", "uhhh", "ummm", "hmm"
    r"\b(?:a+h+|u+h+|m+h+|e+r+|h+m+|h+u+h+|h+u+m+|a+h+a+){1,}\b",
    # repeated-character stutters like "I-I", "b-b-because"
    r"\b(?:\w-){1,}\w+\b",
]


def _count_fillers(text: str) -> int:
    """Count filler word occurrences in `text` (case-insensitive).

    Uses simple substring matching for multi-word fillers and word-boundary regex
    for single words. Also detects elongated fillers ("ahhh") and stutters.
    """
    if not text:
        return 0
    s = text.lower()
    count = 0
    for filler in FILLER_WORDS:
        if " " in filler:
            # phrase
            count += s.count(filler)
        else:
            # word boundary
            count += len(re.findall(r"\b" + re.escape(filler) + r"\b", s))

    for pattern in FILLER_PATTERNS:
        count += len(re.findall(pattern, s))

    # Count pure repetitions of the same short filler token like "ah ah ah"
    count += len(re.findall(r"\b(?:ah|uh|um|hmm)(?:\s+(?:ah|uh|um|hmm))+\b", s))
    return count


def extract_text_features(transcript: str, audio_duration: float) -> Dict[str, float]:
    """Extract simple text/audio features from a transcript.

    Args:
        transcript: Full transcript string (from Whisper or similar).
        audio_duration: Audio length in seconds.

    Returns:
        A dict containing:
            - transcript_length (int): word count
            - wpm (float): words per minute
            - pause_count (int): estimated number of pauses
            - pause_avg_duration (float): avg pause length in seconds
            - filler_count (int): number of filler words detected

    Notes:
        This function uses speech rate-based heuristics to estimate pauses when
        timestamps are not available from the ASR.
    """
    try:
        # Gracefully handle empty/missing transcript — return safe defaults
        if not transcript or not isinstance(transcript, str) or not transcript.strip():
            print("[Feature Extraction] Empty transcript — returning default features")
            return {
                "transcript_length": 0,
                "wpm": 0.0,
                "pause_count": 0,
                "pause_avg_duration": 0.0,
                "filler_count": 0,
            }

        if audio_duration is None or audio_duration <= 0:
            audio_duration = 30.0  # assume 30s if unknown

        # Print debug: first 100 chars of transcript and duration
        print(f"[Feature Extraction] Transcript received: {transcript[:100]}...")
        print(f"[Feature Extraction] Audio duration: {audio_duration:.1f} seconds")

        words = re.findall(r"\w+", transcript)
        transcript_length = len(words)

        if transcript_length == 0:
            print("[Feature Extraction] No words found — returning default features")
            return {
                "transcript_length": 0,
                "wpm": 0.0,
                "pause_count": 0,
                "pause_avg_duration": 0.0,
                "filler_count": 0,
            }

        wpm = (transcript_length / audio_duration) * 60.0

        # ACTION 1.2: Fix pause calculation using speech rate heuristic
        # Normal speech: ~130-160 WPM with ~2-4 pauses per minute
        # Hesitant speech: ~80-120 WPM with ~5-8 pauses per minute
        # Formula: base pauses + adjustment for abnormal WPM
        if wpm < 100:
            # Hesitant speaker: more pauses
            pause_count = max(2, int(5 + (100 - wpm) / 20))
        elif wpm < 130:
            # Slower than normal
            pause_count = max(2, int(3 + (130 - wpm) / 30))
        elif wpm < 160:
            # Normal range
            pause_count = 3
        else:
            # Fast speaker: fewer pauses
            pause_count = max(1, int(2 - (wpm - 160) / 100))

        # Clamp pause count to reasonable range
        pause_count = int(max(1, min(20, pause_count)))

        # Estimate speaking time from words and WPM
        speaking_time = (transcript_length / max(wpm, 1e-6)) * 60.0
        remaining_silence = max(0.0, audio_duration - speaking_time)
        pause_avg_duration = remaining_silence / max(pause_count, 1)

        filler_count = _count_fillers(transcript)

        # ACTION 1.3: Add detailed debug output
        print("[Feature Extraction] Results:")
        print(f"  transcript_length: {transcript_length}")
        print(f"  wpm: {wpm:.1f}")
        print(f"  pause_count: {pause_count}")
        print(f"  pause_avg_duration: {pause_avg_duration:.2f} seconds")
        print(f"  filler_count: {filler_count}")

        # Clamp WPM to reasonable range (very slow/fast speakers won't crash)
        wpm = max(10.0, min(500.0, wpm))
        assert 0 <= pause_count <= 20, f"Pause count out of range: {pause_count}"
        assert 0 <= filler_count <= 50, f"Filler count out of range: {filler_count}"

        return {
            "transcript_length": int(transcript_length),
            "wpm": round(float(wpm), 1),
            "pause_count": int(pause_count),
            "pause_avg_duration": round(float(pause_avg_duration), 2),
            "filler_count": int(filler_count),
        }

    except (ValueError, AssertionError) as e:
        print(f"[Feature Extraction] ERROR: {str(e)}")
        raise
    except Exception as e:
        print(f"[Feature Extraction] UNEXPECTED ERROR: {str(e)}")
        raise
