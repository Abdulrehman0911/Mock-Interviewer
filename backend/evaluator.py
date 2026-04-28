"""Evaluate interview answers using trained model."""

import random
from model_inference import predict_score
from prompts import (
    FOLLOW_UP_PROMPTS,
    STRENGTH_STATEMENTS,
    IMPROVEMENT_STATEMENTS,
    SUMMARY_TEMPLATE,
    get_follow_up_question,
    get_performance_level
)


def evaluate_answer(features_dict, transcript):
    """
    Evaluate an interview answer using the trained model.

    Args:
        features_dict (dict): Dictionary with 10 interview features.
        transcript (str): The user's answer text.

    Returns:
        dict: Evaluation result with score, follow-up, strengths, improvements.

    Raises:
        ValueError: If features or transcript invalid.
        RuntimeError: If prediction fails.
    """
    if not features_dict:
        raise ValueError("Features dictionary cannot be empty")
    if not transcript or not isinstance(transcript, str):
        raise ValueError("Transcript must be a non-empty string")

    try:
        # Get model score
        model_score = predict_score(features_dict)

        # Determine follow-up question category and select random one
        category = get_follow_up_question(model_score)
        follow_up = random.choice(FOLLOW_UP_PROMPTS[category])

        # Select 2 random strengths
        strengths = random.sample(STRENGTH_STATEMENTS, min(2, len(STRENGTH_STATEMENTS)))

        # Select 2 random improvements
        improvements = random.sample(
            IMPROVEMENT_STATEMENTS, min(2, len(IMPROVEMENT_STATEMENTS))
        )

        return {
            "model_score": model_score,
            "follow_up_question": follow_up,
            "strengths": strengths,
            "improvements": improvements,
            "performance_level": get_performance_level(model_score)
        }

    except Exception as e:
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
