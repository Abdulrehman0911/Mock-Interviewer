"""Quick test of video processing without Whisper (MediaPipe + dummy transcript)."""

import json
from pathlib import Path

from mediapipe_analyzer import analyze_video_behavior
from feature_extractor import extract_text_features
from model_inference import predict_score


def test_video_quick():
    """Test MediaPipe behavior analysis on Usman1.mp4 (no Whisper)."""
    
    video_path = Path(__file__).parent / "Usman1.mp4"
    
    print("=" * 80)
    print("QUICK VIDEO TEST - MediaPipe Behavior Analysis (No Whisper)")
    print("=" * 80)
    print(f"\nVideo: {video_path.name}")
    print(f"Exists: {video_path.exists()}")
    print()
    
    if not video_path.exists():
        print(f"❌ ERROR: Video not found at {video_path}")
        return
    
    # Step 1: Analyze video behavior (MediaPipe)
    print("Analyzing video behavior with MediaPipe...")
    print("-" * 80)
    behavior = analyze_video_behavior(str(video_path))
    
    print("\n✓ Video behavior analysis complete")
    print()
    print("BEHAVIORAL METRICS:")
    print("-" * 80)
    for key, value in behavior.items():
        if key == "warning":
            continue
        if isinstance(value, float):
            print(f"  {key:30} → {value:.1f}")
        else:
            print(f"  {key:30} → {value}")
    
    if "warning" in behavior:
        print(f"\n  ⚠ Warning: {behavior['warning']}")
    
    print()
    
    # Step 2: Use dummy transcript (since Whisper is slow)
    print("Using dummy transcript (Whisper skipped for speed)...")
    print("-" * 80)
    
    # Simulate a good answer to the supervised/unsupervised learning question
    dummy_transcript = """
    The difference between supervised and unsupervised learning is fundamental to machine learning.
    In supervised learning, we have labeled training data where we know both the input features
    and the target output. The algorithm learns to map inputs to outputs by minimizing the error
    between predicted and actual values. For example, predicting house prices based on features
    like square footage, bedrooms, and location is a supervised regression problem where we have
    historical houses with known prices.
    
    Unsupervised learning, on the other hand, works with unlabeled data where we don't have
    predetermined outputs. The goal is to discover hidden patterns or structure in the data.
    Clustering algorithms like K-means group similar customers together based on purchasing behavior
    without being told what the groups should be. This is useful for customer segmentation where
    we want to identify natural groupings to target with different marketing strategies.
    
    I would use supervised learning when I have clear business objectives and labeled examples.
    For instance, predicting customer churn when I have historical data of who left and who stayed.
    I would use unsupervised learning for exploratory analysis, like discovering new market segments
    or detecting anomalies in system logs without knowing what anomalies look like beforehand.
    """
    
    dummy_duration = 60.0  # Assume 60 second video (more realistic for this length response)
    
    text_features = extract_text_features(dummy_transcript, dummy_duration)
    
    print("TEXT FEATURES (from dummy transcript):")
    print("-" * 80)
    for key, value in text_features.items():
        if isinstance(value, float):
            print(f"  {key:30} → {value:.2f}")
        else:
            print(f"  {key:30} → {value}")
    
    print()
    
    # Step 3: Combine features
    print("COMBINED FEATURES (for model):")
    print("-" * 80)
    
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
        "question_difficulty": 2,
    }
    
    for key, value in features.items():
        if isinstance(value, float):
            print(f"  {key:30} → {value:.2f}")
        else:
            print(f"  {key:30} → {value}")
    
    print()
    
    # Step 4: Predict score
    print("MODEL PREDICTION:")
    print("-" * 80)
    try:
        score = predict_score(features)
        print(f"✓ Model Score: {score}/10")
    except Exception as e:
        print(f"❌ Prediction failed: {str(e)}")
        return
    
    print()
    
    # Step 5: Feature validation
    print("FEATURE VALIDATION:")
    print("-" * 80)
    checks = [
        ("transcript_length > 0", features.get("transcript_length", 0) > 0),
        ("wpm in [0, 300]", 0 <= features.get("wpm", 0) <= 300),
        ("eye_contact_pct in [0, 100]", 0 <= features.get("eye_contact_pct", 0) <= 100),
        ("head_pose_score in [0, 10]", 0 <= features.get("head_pose_score", 0) <= 10),
        ("posture_score in [0, 10]", 0 <= features.get("posture_score", 0) <= 10),
        ("facial_stability_score in [0, 10]", 0 <= features.get("facial_stability_score", 0) <= 10),
        ("question_difficulty in [1, 3]", 1 <= features.get("question_difficulty", 2) <= 3),
        ("score in [1, 10]", 1 <= score <= 10),
    ]
    
    for check_name, result_bool in checks:
        status = "✓" if result_bool else "❌"
        print(f"  {status} {check_name}")
    
    all_passed = all(r for _, r in checks)
    print()
    print("=" * 80)
    if all_passed:
        print("✓✓✓ ALL VALIDATIONS PASSED ✓✓✓")
    else:
        print("⚠ Some validations failed - review features above")
    print("=" * 80)
    print()
    
    # Output summary
    print("SUMMARY:")
    print("-" * 80)
    print(f"Video processed: {video_path.name}")
    print(f"Extracted {len(features)} features")
    print(f"Predicted score: {score}/10")
    print(f"Performance level: ", end="")
    if score >= 8:
        print("Excellent")
    elif score >= 6:
        print("Good")
    elif score >= 4:
        print("Fair")
    else:
        print("Needs Improvement")
    print()


if __name__ == "__main__":
    test_video_quick()
