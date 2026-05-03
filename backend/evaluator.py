"""Evaluate interview answers using trained model and correctness scoring."""

import random
from model_inference import predict_score
from correctness_scorer import score_answer_correctness
from prompts import (
    FOLLOW_UP_PROMPTS,
    STRENGTH_STATEMENTS,
    IMPROVEMENT_STATEMENTS,
    SUMMARY_TEMPLATE,
    get_follow_up_question,
    get_performance_level
)


def evaluate_answer(features_dict, transcript, question_id=None, role="Software Engineer", question_text=None):
    """
    Evaluate an interview answer using both behavioral and correctness scoring.

    Args:
        features_dict (dict): Dictionary with 10 interview features.
        transcript (str): The user's answer text.
        question_id (int): ID of the question answered (for correctness scoring).
        role (str): Job role/interview type (default: Software Engineer).
        question_text (str): Optional text of the question for logging.

    Returns:
        dict: Evaluation result with complete breakdown showing behavioral_out_of_4,
              correctness_out_of_6, and final score out of 10.

    Raises:
        ValueError: If features or transcript invalid.
        RuntimeError: If prediction fails.
    """
    if not features_dict:
        raise ValueError("Features dictionary cannot be empty")
    # Allow empty transcript — treat as no speech detected
    if not transcript or not isinstance(transcript, str):
        transcript = ""

    try:
        print("\n" + "="*60)
        print("ANSWER EVALUATION")
        print("="*60)
        if question_text:
            print(f"Question: {question_text}")
        print(f"Transcript: {transcript[:100]}...")
        print()

        # ACTION 4.2: Calculate behavioral score from trained model
        print("BEHAVIORAL SIGNALS:")
        print(f"  Eye contact: {features_dict.get('eye_contact_pct', 0):.1f}%")
        print(f"  Head pose: {features_dict.get('head_pose_score', 0)}/10")
        print(f"  Posture: {features_dict.get('posture_score', 0)}/10")
        print(f"  Stability: {features_dict.get('facial_stability_score', 0)}/10")
        
        behavioral_score = predict_score(features_dict)
        assert 1 <= behavioral_score <= 10, f"Behavioral score out of range: {behavioral_score}"
        print(f"Behavioral Score: {behavioral_score:.1f}/10")

        # ACTION 4.3: Calculate correctness score
        print("\nCONTENT CORRECTNESS:")
        correctness_result = {}
        if question_id is not None:
            correctness_result = score_answer_correctness(transcript, question_id, role)
            correctness_score = correctness_result.get("correctness_score", 0.0)
        else:
            # If no question_id, default to neutral
            correctness_score = 5.0
            correctness_result = {"correctness_score": 5.0, "tier_matched": "UNKNOWN"}

        assert 0 <= correctness_score <= 10, f"Correctness score out of range: {correctness_score}"
        tier_matched = correctness_result.get("tier_matched", "UNKNOWN")
        print(f"Matched tier: {tier_matched}")
        print(f"Correctness Score: {correctness_score:.1f}/10")

        # ACTION 4.4: Apply weighting with clear breakdown
        print("\nSCORING BREAKDOWN (0.4 behavioral / 0.6 correctness):")
        
        # Rule 1: If correctness is 0 (completely wrong), behavior still counts
        if correctness_score == 0.0:
            behavioral_out_of_4 = round((behavioral_score / 10.0) * 4.0, 1)
            correctness_out_of_6 = 0.0
            final_score = behavioral_out_of_4  # Only behavioral counts
            print(f"  Behavioral: ({behavioral_score:.1f}/10) * 0.4 * 10 = {behavioral_out_of_4}/4")
            print(f"  Correctness: 0 (completely wrong) = 0/6")
            print(f"  Final Score: {behavioral_out_of_4} + 0 = {final_score}/10")
        else:
            # Rule 2: Both components contribute
            behavioral_out_of_4 = round((behavioral_score / 10.0) * 4.0, 1)
            correctness_out_of_6 = round((correctness_score / 10.0) * 6.0, 1)
            final_score = round(behavioral_out_of_4 + correctness_out_of_6, 1)
            print(f"  Behavioral: ({behavioral_score:.1f}/10) * 0.4 * 10 = {behavioral_out_of_4}/4")
            print(f"  Correctness: ({correctness_score:.1f}/10) * 0.6 * 10 = {correctness_out_of_6}/6")
            print(f"  Final Score: {behavioral_out_of_4} + {correctness_out_of_6} = {final_score}/10")

        print("="*60 + "\n")

        # ACTION 4.5: Build detailed response dict
        return {
            "success": True,
            "breakdown": {
                "behavioral": {
                    "score": round(behavioral_score, 1),
                    "out_of": 4,
                    "percentage": round((behavioral_score / 10.0) * 100.0, 1),
                    "subscale": {
                        "eye_contact": round(features_dict.get("eye_contact_pct", 0) / 100.0 * 4.0, 1),
                        "head_pose": round(features_dict.get("head_pose_score", 0) / 10.0 * 4.0, 1),
                        "posture": round(features_dict.get("posture_score", 0) / 10.0 * 4.0, 1),
                        "stability": round(features_dict.get("facial_stability_score", 0) / 10.0 * 4.0, 1),
                    }
                },
                "correctness": {
                    "score": round(correctness_score, 1),
                    "out_of": 6,
                    "percentage": round((correctness_score / 10.0) * 100.0, 1),
                    "subscale": correctness_out_of_6,
                    "tier_matched": tier_matched,
                    "match_pct": correctness_result.get("match_pct", 0),
                    "match_high": correctness_result.get("match_high", 0),
                    "match_medium": correctness_result.get("match_medium", 0),
                    "match_low": correctness_result.get("match_low", 0),
                    "filler_count": correctness_result.get("filler_count", 0),
                    "filler_penalty": correctness_result.get("filler_penalty", 0),
                },
                "final": {
                    "score": final_score,
                    "out_of": 10,
                    "percentage": round((final_score / 10.0) * 100.0, 1)
                }
            },
            "model_score": final_score,
            "behavioral_score": round(behavioral_score, 1),
            "behavioral_score_out_of_4": behavioral_out_of_4,
            "correctness_score": round(correctness_score, 1),
            "correctness_score_out_of_6": correctness_out_of_6,
            "correctness_details": correctness_result,
            "follow_up_question": random.choice(FOLLOW_UP_PROMPTS.get(get_follow_up_question(final_score), FOLLOW_UP_PROMPTS["medium"])),
            "strengths": random.sample(STRENGTH_STATEMENTS, min(2, len(STRENGTH_STATEMENTS))),
            "improvements": random.sample(IMPROVEMENT_STATEMENTS, min(2, len(IMPROVEMENT_STATEMENTS))),
            "performance_level": get_performance_level(final_score)
        }

    except Exception as e:
        print(f"[Evaluator] ERROR: {str(e)}")
        raise RuntimeError(f"Answer evaluation failed: {str(e)}")


def generate_summary_report(all_scores, all_transcripts):
    """
    Generate a comprehensive summary report for an interview session.

    Args:
        all_scores (list): List of scores from all answers.
        all_transcripts (list): List of transcript texts from all answers.

    Returns:
        dict: Summary report with statistics and assessment.

    Raises:
        ValueError: If inputs invalid.
    """
    if not all_scores or not all_transcripts:
        raise ValueError("Scores and transcripts cannot be empty")
    
    if len(all_scores) != len(all_transcripts):
        raise ValueError("Number of scores must match number of transcripts")

    try:
        # Convert to floats
        scores = [float(s) for s in all_scores]

        # Calculate statistics
        overall_score = sum(scores) / len(scores)
        highest_score = max(scores)
        lowest_score = min(scores)
        average_score = overall_score

        # Identify strengths and improvements for summary
        strength1 = random.choice(STRENGTH_STATEMENTS)
        strength2 = random.choice(STRENGTH_STATEMENTS)
        while strength2 == strength1:
            strength2 = random.choice(STRENGTH_STATEMENTS)

        improvement1 = random.choice(IMPROVEMENT_STATEMENTS)
        improvement2 = random.choice(IMPROVEMENT_STATEMENTS)
        while improvement2 == improvement1:
            improvement2 = random.choice(IMPROVEMENT_STATEMENTS)

        # Determine performance level
        performance_level = get_performance_level(overall_score)

        # Generate summary text
        summary_text = SUMMARY_TEMPLATE.format(
            role="Technical",
            overall_score=round(overall_score, 1),
            average_score=round(average_score, 1),
            strength1=strength1,
            strength2=strength2,
            improvement1=improvement1,
            improvement2=improvement2,
            performance_level=performance_level
        )

        return {
            "overall_score": round(overall_score, 1),
            "average_score": round(average_score, 1),
            "highest_score": round(highest_score, 1),
            "lowest_score": round(lowest_score, 1),
            "total_questions": len(scores),
            "performance_level": performance_level,
            "summary": summary_text,
            "statistics": {
                "mean": round(average_score, 2),
                "max": round(highest_score, 1),
                "min": round(lowest_score, 1),
                "range": round(highest_score - lowest_score, 1)
            }
        }

    except Exception as e:
        raise RuntimeError(f"Summary report generation failed: {str(e)}")
