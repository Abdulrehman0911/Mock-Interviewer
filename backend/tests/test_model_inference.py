"""Test model inference with dummy data (without video processing)."""

import json
from model_inference import predict_score, inference
from evaluator import evaluate_answer


# Feature templates based on answer quality
DUMMY_FEATURES = {
    "high_quality": {
        "transcript_length": 250,      # Long, detailed answer
        "wpm": 145,                    # Good speaking pace
        "pause_count": 2,              # Minimal pauses
        "pause_avg_duration": 1.5,     # Brief pauses
        "filler_count": 1,             # Very few fillers
        "eye_contact_pct": 85,         # Strong eye contact
        "head_pose_score": 9,          # Excellent posture/head position
        "posture_score": 9,            # Confident posture
        "facial_stability_score": 8,   # Stable expressions
        "question_difficulty": 2,      # Medium difficulty
    },
    "medium_quality": {
        "transcript_length": 150,      # Moderate length
        "wpm": 120,                    # Average pace
        "pause_count": 4,              # Some pauses
        "pause_avg_duration": 2.5,     # Moderate pause duration
        "filler_count": 3,             # Few fillers
        "eye_contact_pct": 65,         # Decent eye contact
        "head_pose_score": 6,          # Neutral head position
        "posture_score": 7,            # Good posture
        "facial_stability_score": 6,   # Some fluctuation in expressions
        "question_difficulty": 2,      # Medium difficulty
    },
    "low_quality": {
        "transcript_length": 60,       # Very short answer
        "wpm": 85,                     # Slow pace
        "pause_count": 8,              # Many pauses
        "pause_avg_duration": 4.0,     # Long pauses
        "filler_count": 7,             # Lots of fillers
        "eye_contact_pct": 25,         # Poor eye contact
        "head_pose_score": 3,          # Poor head positioning
        "posture_score": 4,            # Slouched posture
        "facial_stability_score": 3,   # Unstable expressions (nervous)
        "question_difficulty": 3,      # Hard difficulty
    },
}

DUMMY_TRANSCRIPTS = {
    "high_quality": """
    I approached this problem by first understanding the requirements and breaking it down 
    into manageable components. I started with a depth-first search solution because it 
    naturally explores all possible paths. The time complexity is O(n) where n is the number 
    of nodes, and space complexity is O(h) for the recursion stack where h is the height. 
    I've tested this with several edge cases including empty trees and single-node trees. 
    The key insight here is recognizing that we can use backtracking to efficiently 
    explore combinations without redundant calculations.
    """,
    "medium_quality": """
    So, um, for this problem I think we could use a search approach. We go through the data 
    and try different options. It should be pretty efficient because we don't repeat work. 
    The time complexity is probably O(n) or something like that. I tested it a bit and it 
    seemed to work. It handles basic cases well.
    """,
    "low_quality": """
    Uh, yeah so like... I think we could just, um, loop through everything and like... 
    try stuff? I'm not really sure about the complexity or anything. It might be slow 
    but it should work maybe? I haven't really tested it much.
    """,
}


def test_model_predictions():
    """Test model with different quality levels of dummy data."""
    print("=" * 70)
    print("MODEL INFERENCE TEST - Dummy Data Validation")
    print("=" * 70)
    print()

    if inference is None:
        print("❌ ERROR: Model failed to load. Check ML artifacts.")
        return

    results = {}

    for quality_level in ["low_quality", "medium_quality", "high_quality"]:
        print(f"\n{'─' * 70}")
        print(f"Testing: {quality_level.upper().replace('_', ' ')}")
        print(f"{'─' * 70}")

        features = DUMMY_FEATURES[quality_level]
        transcript = DUMMY_TRANSCRIPTS[quality_level]

        # Display features
        print("\nFeatures:")
        for key, value in features.items():
            print(f"  • {key}: {value}")

        print(f"\nTranscript snippet: {transcript[:100]}...")

        try:
            # Test predict_score
            score = predict_score(features)
            print(f"\n✓ Model Prediction: {score}/10")
            results[quality_level] = score

            # Test evaluate_answer (includes follow-up generation)
            evaluation = evaluate_answer(features, transcript)
            print(f"\n✓ Full Evaluation:")
            print(f"   - Score: {evaluation['model_score']}")
            print(f"   - Performance Level: {evaluation['performance_level']}")
            print(f"   - Follow-up Question: {evaluation['follow_up_question'][:80]}...")
            print(f"   - Strengths: {', '.join(evaluation['strengths'])}")
            print(f"   - Improvements: {', '.join(evaluation['improvements'])}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results[quality_level] = None

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print("\nPredicted Scores:")
    for quality, score in results.items():
        quality_display = quality.replace('_', ' ').title()
        if score:
            print(f"  {quality_display:20} → {score}/10")
        else:
            print(f"  {quality_display:20} → ERROR")

    # Validation
    print("\n✓ Validation Checks:")
    if results["low_quality"] is not None and results["high_quality"] is not None:
        if results["low_quality"] < results["high_quality"]:
            print("  ✓ Low quality score < High quality score ✅")
        else:
            print("  ⚠ Warning: Low quality score should be < High quality score")

        if results["medium_quality"] is not None:
            low = results["low_quality"]
            med = results["medium_quality"]
            high = results["high_quality"]
            if low < med < high:
                print("  ✓ Score ordering correct (Low < Medium < High) ✅")
            else:
                print(f"  ⚠ Warning: Ordering issue - {low} < {med} < {high}")

    print(f"\n{'=' * 70}\n")


if __name__ == "__main__":
    test_model_predictions()
