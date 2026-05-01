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
    "like",
    "you know",
    "basically",
    "literally",
    "actually",
    "anyway",
]


def _count_fillers(text: str) -> int:
    """Count filler word occurrences in `text` (case-insensitive).

    Uses simple substring matching for multi-word fillers and word-boundary regex
    for single words.
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
        This function uses lightweight heuristics to estimate pauses and may be
        refined later when we have word-level timestamps from the ASR.
    """
    try:
        if not transcript or not isinstance(transcript, str) or audio_duration <= 0:
            return {
                "transcript_length": 0,
                "wpm": 0.0,
                "pause_count": 0,
                "pause_avg_duration": 0.0,
                "filler_count": 0,
            }

        words = re.findall(r"\w+", transcript)
        transcript_length = len(words)

        # Prevent division by zero
        audio_duration = float(audio_duration) if audio_duration is not None else 0.0
        if audio_duration <= 0 or transcript_length == 0:
            return {
                "transcript_length": transcript_length,
                "wpm": 0.0,
                "pause_count": 0,
                "pause_avg_duration": 0.0,
                "filler_count": _count_fillers(transcript),
            }

        wpm = (transcript_length / audio_duration) * 60.0

        # Heuristic pause count: more words -> fewer pauses. Keep integer.
        pause_count = max(0, int(math.ceil(10 - (transcript_length / 20.0))))

        # Estimate speaking time from words and WPM (words / (words/min) * 60 = seconds)
        speaking_time = (transcript_length / max(wpm, 1e-6)) * 60.0
        remaining_silence = max(0.0, audio_duration - speaking_time)
        pause_avg_duration = remaining_silence / max(pause_count, 1)

        filler_count = _count_fillers(transcript)

        return {
            "transcript_length": int(transcript_length),
            "wpm": round(float(wpm), 1),
            "pause_count": int(pause_count),
            "pause_avg_duration": round(float(pause_avg_duration), 2),
            "filler_count": int(filler_count),
        }

    except Exception:
        # On error, return zeros instead of raising to keep pipeline robust
        return {
            "transcript_length": 0,
            "wpm": 0.0,
            "pause_count": 0,
            "pause_avg_duration": 0.0,
            "filler_count": 0,
        }
