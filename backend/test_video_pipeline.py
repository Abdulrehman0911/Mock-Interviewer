"""Test video processing pipeline with sample video (Usman1.mp4)."""

import json
import os
from pathlib import Path

from video_processor import process_video
from model_inference import predict_score


def test_video_processing():
    """Test the full video processing pipeline with Usman1.mp4."""
    
    video_path = Path(__file__).parent / "Usman1.mp4"
    
    print("=" * 80)
    print("VIDEO PROCESSING PIPELINE TEST")
    print("=" * 80)
    print(f"\nVideo: {video_path.name}")
    print(f"Exists: {video_path.exists()}")
    print()
    
    if not video_path.exists():
        print(f"❌ ERROR: Video not found at {video_path}")
        return
    
    print("Processing video...")
    print("-" * 80)
    
    result = process_video(str(video_path))
    
    print()
    print("=" * 80)
    print("PROCESSING RESULT")
    print("=" * 80)
    
    if not result.get("success"):
        print(f"❌ Processing failed: {result.get('error')}")
        return
    
    print("✓ Processing successful")
    print()
    
    # Extract data
    features = result.get("features", {})
    transcript = result.get("transcript", "")
    
    # Display transcript
    print("TRANSCRIPT:")
    print("-" * 80)
    if transcript:
        # Print first 500 chars, then truncate
        display_text = transcript[:500] + ("..." if len(transcript) > 500 else "")
        print(display_text)
    else:
        print("⚠ No transcript extracted (Whisper may not be available)")
    print()
    
    # Display extracted features
    print("EXTRACTED FEATURES:")
    print("-" * 80)
    for key, value in features.items():
        if isinstance(value, float):
            print(f"  {key:30} → {value:.2f}")
        else:
            print(f"  {key:30} → {value}")
    print()
    
    # Predict score
    print("MODEL PREDICTION:")
    print("-" * 80)
    try:
        score = predict_score(features)
        print(f"✓ Model Score: {score}/10")
    except Exception as e:
        print(f"❌ Prediction failed: {str(e)}")
        return
    
    print()
    
    # Feature validation
    print("FEATURE VALIDATION:")
    print("-" * 80)
    checks = [
        ("transcript_length > 0", features.get("transcript_length", 0) > 0),
        ("wpm > 0", features.get("wpm", 0) > 0),
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
    
    # Output JSON for reference
    print("JSON OUTPUT (for API):")
    print("-" * 80)
    output = {
        "success": True,
        "score": score,
        "transcript": transcript[:200] + ("..." if len(transcript) > 200 else ""),
        "features": features,
    }
    print(json.dumps(output, indent=2))
    print()


if __name__ == "__main__":
    test_video_processing()
