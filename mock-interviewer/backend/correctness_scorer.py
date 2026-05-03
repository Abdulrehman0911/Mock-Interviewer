"""Score answer correctness by matching keywords against expected answers.

Compares user's transcript against high/medium/low quality keyword arrays
from questionsAnswers.json to determine answer quality tier.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List
from difflib import SequenceMatcher

# Fillers to remove from transcript before keyword extraction
FILLERS = [
    "um", "uh", "like", "basically", "you know", "i mean", "actually",
    "kinda", "sorta", "ahh", "ummm", "well", "so", "uh huh", "right"
]


def _load_questions_answers() -> dict:
    """Load and cache questionsAnswers.json."""
    try:
        json_path = Path(__file__).parent / "data" / "questionsAnswers.json"
        with open(json_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to load questionsAnswers.json: {str(e)}")
        return {}


# Cache loaded questions on startup
_QA_CACHE = _load_questions_answers()


def _fuzzy_match(s1: str, s2: str, threshold: float = 0.8) -> bool:
    """Check if two strings are similar enough (fuzzy match)."""
    ratio = SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
    return ratio >= threshold


def _count_fillers(transcript: str) -> int:
    """Count filler words in transcript.
    
    Args:
        transcript: The user's transcript.
    
    Returns:
        Count of filler words found.
    """
    if not transcript:
        return 0
    
    count = 0
    transcript_lower = transcript.lower()
    
    for filler in FILLERS:
        count += transcript_lower.count(filler)
    
    return count


def extract_user_keywords(transcript: str) -> List[str]:
    """Extract meaningful keywords from user's transcript.
    
    Removes filler words and returns cleaned tokens/phrases.
    
    Args:
        transcript: Full transcript from user.
    
    Returns:
        List of meaningful keyword tokens.
    """
    if not transcript:
        return []
    
    # Remove fillers
    cleaned = transcript.lower()
    for filler in FILLERS:
        cleaned = cleaned.replace(filler, " ")
    
    # Split into words, remove empty
    words = [w.strip() for w in cleaned.split() if w.strip()]
    
    # Remove pure punctuation
    import re
    words = [w for w in words if re.search(r"\w", w)]
    
    return words


def calculate_keyword_matches(
    user_keywords: List[str],
    expected_keywords: List[str],
    threshold: float = 0.8
) -> float:
    """Calculate % match between user keywords and expected keywords.
    
    Args:
        user_keywords: Keywords extracted from user transcript.
        expected_keywords: Expected keywords from high/medium/low answer tier.
        threshold: Fuzzy match threshold (0-1).
    
    Returns:
        Match percentage (0-100).
    """
    if not expected_keywords:
        return 0.0
    
    if not user_keywords:
        return 0.0
    
    matched_count = 0
    
    for expected_kw in expected_keywords:
        # Try exact match first
        if expected_kw.lower() in user_keywords:
            matched_count += 1
            continue
        
        # Try fuzzy match
        for user_kw in user_keywords:
            if _fuzzy_match(user_kw, expected_kw, threshold):
                matched_count += 1
                break
    
    return (matched_count / len(expected_keywords)) * 100.0


def score_answer_correctness(
    transcript: str,
    question_id: int,
    role: str = "Software Engineer"
) -> Dict[str, object]:
    """Score answer correctness supporting both 1-tier and 3-tier JSON.
    
    Args:
        transcript: User's answer transcript.
        question_id: ID of the question being answered.
        role: Job role/interview type.
    
    Returns:
        dict with correctness_score and all match percentage keys.
    """
    
    # Handle empty transcript
    if not transcript or not isinstance(transcript, str):
        return {"correctness_score": 0.0, "error": "No transcript provided"}
    
    global _QA_CACHE
    if not _QA_CACHE:
        _QA_CACHE = _load_questions_answers()
    
    qa_data = _QA_CACHE
    if not qa_data:
        return {"correctness_score": 0.0, "error": "Questions data not loaded"}
    
    # Find the role and question
    role_questions = qa_data.get(role, [])
    question_obj = next((q for q in role_questions if q.get("question_id") == question_id), None)
    
    if not question_obj:
        return {"correctness_score": 5.0, "warning": "Question not found"}
    
    user_keywords = extract_user_keywords(transcript)
    if not user_keywords:
        return {"correctness_score": 0.0, "keywords_found": []}

    # --- UNIVERSAL LOGIC ---
    # 1. Try NEW 1-Tier Structure
    master_keywords = question_obj.get("keywords")
    
    # 2. Try OLD 3-Tier Structure
    answers = question_obj.get("answers", [])
    
    match_high = 0.0
    match_medium = 0.0
    match_low = 0.0
    match_pct = 0.0
    tier_matched = "NONE"
    correctness_score = 0.0

    if master_keywords:
        # NEW LOGIC (80/40 rule)
        match_pct = calculate_keyword_matches(user_keywords, master_keywords, threshold=0.8)
        if match_pct >= 80.0:
            tier_matched, correctness_score = "HIGH", 9.0 + (match_pct - 80.0) / 20.0 * 1.0
        elif match_pct >= 40.0:
            tier_matched, correctness_score = "MEDIUM", 6.0 + (match_pct - 40.0) / 40.0 * 2.5
        elif match_pct > 0.0:
            tier_matched, correctness_score = "LOW", 2.0 + (match_pct - 0.0) / 40.0 * 3.5
        
        # Populate old keys for compatibility
        match_high = match_pct if tier_matched == "HIGH" else 0.0
        match_medium = match_pct if tier_matched == "MEDIUM" else 0.0
        match_low = match_pct if tier_matched == "LOW" else 0.0

    elif answers:
        # OLD LOGIC (Tier-based matching)
        answers_sorted = sorted(answers, key=lambda a: a.get("quality_score", 0), reverse=True)
        kw_high = answers_sorted[0].get("keywords", []) if len(answers_sorted) > 0 else []
        kw_medium = answers_sorted[1].get("keywords", []) if len(answers_sorted) > 1 else []
        kw_low = answers_sorted[2].get("keywords", []) if len(answers_sorted) > 2 else []
        
        match_high = calculate_keyword_matches(user_keywords, kw_high, threshold=0.8)
        match_medium = calculate_keyword_matches(user_keywords, kw_medium, threshold=0.8)
        match_low = calculate_keyword_matches(user_keywords, kw_low, threshold=0.8)
        
        if match_high >= 70.0:
            tier_matched, correctness_score = "HIGH", 8.0 + (match_high - 70.0) / 30.0 * 2.0
        elif match_medium >= 60.0:
            tier_matched, correctness_score = "MEDIUM", 5.0 + (match_medium - 60.0) / 40.0 * 2.0
        elif match_low >= 40.0:
            tier_matched, correctness_score = "LOW", 2.0 + (match_low - 40.0) / 60.0 * 2.0
        
        match_pct = max(match_high, match_medium, match_low)

    # Filler word penalty
    filler_count = _count_fillers(transcript)
    filler_penalty = 0.0
    if tier_matched == "HIGH" and filler_count > 2:
        filler_penalty = 0.5 if filler_count <= 6 else 1.5
    elif tier_matched == "MEDIUM" and filler_count > 6:
        filler_penalty = 1.0
    elif filler_count > 10:
        filler_penalty = 1.0

    final_score = round(max(0.0, correctness_score - filler_penalty), 1)
    
    return {
        "correctness_score": final_score,
        "match_pct": round(match_pct, 1),
        "match_high": round(match_high, 1),
        "match_medium": round(match_medium, 1),
        "match_low": round(match_low, 1),
        "tier_matched": tier_matched,
        "filler_count": filler_count,
        "filler_penalty": filler_penalty,
        "keywords_found": user_keywords[:25],
    }
