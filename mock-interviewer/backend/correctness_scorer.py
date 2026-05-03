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
    """Score answer correctness by tier matching.
    
    Compares transcript keywords against high/medium/low answer tiers.
    
    Args:
        transcript: User's answer transcript.
        question_id: ID of the question being answered.
        role: Job role/interview type (default: Software Engineer).
    
    Returns:
        dict with correctness_score, tier matched, match percentages, and keywords found.
    """
    
    # Handle empty transcript
    if not transcript or not isinstance(transcript, str):
        print("[Correctness] ERROR: No transcript provided")
        return {
            "correctness_score": 0.0,
            "error": "No transcript provided"
        }
    
    # Load questions if not cached
    qa_data = _QA_CACHE
    if not qa_data:
        print("[Correctness] ERROR: Questions data not loaded")
        return {
            "correctness_score": 0.0,
            "error": "Questions data not loaded"
        }
    
    # Find the role's questions
    role_questions = qa_data.get(role, [])
    if not role_questions:
        print(f"[Correctness] ERROR: Role '{role}' not found")
        return {
            "correctness_score": 0.0,
            "error": f"Role '{role}' not found"
        }
    
    # Find the specific question
    question_obj = None
    for q in role_questions:
        if q.get("question_id") == question_id:
            question_obj = q
            break
    
    if not question_obj:
        print(f"[Correctness] WARNING: Question ID {question_id} not found")
        return {
            "correctness_score": 5.0,  # Default neutral score
            "warning": f"Question ID {question_id} not found, using default"
        }
    
    # Extract user keywords
    user_keywords = extract_user_keywords(transcript)
    print(f"[Correctness] Extracted keywords: {user_keywords[:20]}")
    
    if not user_keywords:
        print("[Correctness] ERROR: No meaningful keywords extracted")
        return {
            "correctness_score": 0.0,
            "error": "No meaningful keywords extracted from transcript",
            "keywords_found": []
        }
    
    # Get answer tiers sorted by quality score (descending)
    answers = question_obj.get("answers", [])
    if not answers:
        print("[Correctness] ERROR: No answer tiers defined")
        return {
            "correctness_score": 0.0,
            "error": "No answer tiers defined for question"
        }
    
    # Sort by quality_score descending: high, medium, low
    answers_sorted = sorted(answers, key=lambda a: a.get("quality_score", 0), reverse=True)
    
    # Extract keywords from each tier
    tier_keywords = {
        "HIGH": answers_sorted[0].get("keywords", []) if len(answers_sorted) > 0 else [],
        "MEDIUM": answers_sorted[1].get("keywords", []) if len(answers_sorted) > 1 else [],
        "LOW": answers_sorted[2].get("keywords", []) if len(answers_sorted) > 2 else [],
    }
    
    # ACTION 3.3: Calculate matches for each tier using fuzzy matching
    match_high = calculate_keyword_matches(user_keywords, tier_keywords["HIGH"], threshold=0.8)
    match_medium = calculate_keyword_matches(user_keywords, tier_keywords["MEDIUM"], threshold=0.8)
    match_low = calculate_keyword_matches(user_keywords, tier_keywords["LOW"], threshold=0.8)
    
    print(f"[Correctness] Match Analysis:")
    print(f"  HIGH tier: {match_high:.1f}% match")
    print(f"  MEDIUM tier: {match_medium:.1f}% match")
    print(f"  LOW tier: {match_low:.1f}% match")
    
    # ACTION 3.4: Determine tier and score
    tier_matched = None
    correctness_score = 0.0
    
    if match_high >= 70.0:
        # HIGH tier: 70-100% match -> 8-10 score
        tier_matched = "HIGH"
        correctness_score = 8.0 + (match_high - 70.0) / 30.0 * 2.0
        print(f"  [HIGH] Tier matched with {match_high:.1f}%")
    elif match_medium >= 60.0:
        # MEDIUM tier: 60-100% match -> 5-7 score
        tier_matched = "MEDIUM"
        correctness_score = 5.0 + (match_medium - 60.0) / 40.0 * 2.0
        print(f"  [MEDIUM] Tier matched with {match_medium:.1f}%")
    elif match_low >= 40.0:
        # LOW tier: 40-100% match -> 2-4 score
        tier_matched = "LOW"
        correctness_score = 2.0 + (match_low - 40.0) / 60.0 * 2.0
        print(f"  [LOW] Tier matched with {match_low:.1f}%")
    elif max(match_high, match_medium, match_low) > 0.0:
        # PARTIAL tier: Any match below thresholds -> 1 score
        tier_matched = "PARTIAL"
        best_match = max(match_high, match_medium, match_low)
        correctness_score = 1.0
        print(f"  [PARTIAL] Partial match with {best_match:.1f}%")
    else:
        # NONE: No matches -> 0 score
        tier_matched = "NONE"
        correctness_score = 0.0
        print(f"  [NONE] No keywords matched")
    
    # ACTION 3.5: Add filler word penalty
    filler_count = _count_fillers(transcript) if hasattr(transcript, '__len__') else 0
    filler_penalty = 0.0
    
    if filler_count > 10:
        filler_penalty = 1.0
        print(f"  [PENALTY] Filler count {filler_count} > 10 → -1.0 penalty")
    elif filler_count > 5:
        filler_penalty = 0.5
        print(f"  [PENALTY] Filler count {filler_count} > 5 → -0.5 penalty")
    
    correctness_score = max(0.0, correctness_score - filler_penalty)
    
    # Clamp and round
    correctness_score = round(min(10.0, max(0.0, correctness_score)), 1)
    
    print(f"  FINAL Correctness Score: {correctness_score}/10")
    
    return {
        "correctness_score": correctness_score,
        "match_high": round(match_high, 1),
        "match_medium": round(match_medium, 1),
        "match_low": round(match_low, 1),
        "tier_matched": tier_matched,
        "filler_count": filler_count,
        "filler_penalty": filler_penalty,
        "keywords_found": user_keywords[:25],  # First 25 for brevity
    }
