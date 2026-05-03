"""
Comprehensive Analysis: Extract text, emotions, expressions, and score both candidates
- Asad1.mov: Backend Engineer Q3 (Code refactoring)
- Usman1.mov: Data Scientist Q1 (Supervised vs Unsupervised Learning)

Output: Formatted results ready for final app display
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from video_processor import process_video
from model_inference import predict_score
from correctness_scorer import score_answer_correctness
from mediapipe_analyzer import analyze_video_behavior


def extract_and_analyze_video(video_path, question_id, role, question_text):
    """
    Complete analysis of a video:
    1. Extract transcript
    2. Analyze behavioral metrics (expressions, emotions)
    3. Get behavioral score
    4. Get correctness score
    5. Combine all data
    """
    
    print(f"\n{'='*100}")
    print(f"PROCESSING: {Path(video_path).name}")
    print(f"{'='*100}\n")
    
    # Step 1: Process video
    print("Step 1: Extracting Transcript & Text Features...")
    print("-" * 100)
    
    result = process_video(video_path)
    if not result.get("success"):
        print(f"[ERROR]: {result.get('error')}")
        return None
    
    transcript = result.get("transcript", "")
    features = result.get("features", {})
    
    print(f"[OK] Transcript extracted: {len(transcript)} characters")
    print(f"\n[ FULL TRANSCRIPT ]")
    print(f"{'-'*100}")
    print(transcript)
    print(f"{'-'*100}\n")
    
    # Step 2: Analyze behavioral metrics & emotions
    print("Step 2: Analyzing Expressions & Emotions...")
    print("-" * 100)
    
    behavior_result = analyze_video_behavior(video_path)
    if not behavior_result.get("success", False):
        print(f"[ERROR]: {behavior_result.get('error', 'behavior_analysis_failed')}")
        return None
    
    eye_contact = behavior_result["eye_contact_pct"]
    head_pose = behavior_result["head_pose_score"]
    posture = behavior_result["posture_score"]
    facial_stability = behavior_result["facial_stability_score"]
    emotion = behavior_result["dominant_emotion"]
    
    print(f"[OK] Behavioral Metrics Extracted:")
    print(f"   * Eye Contact: {eye_contact:.1f}%")
    print(f"   * Head Pose Score: {head_pose}/10")
    print(f"   * Posture Score: {posture}/10")
    print(f"   * Facial Stability: {facial_stability}/10")
    print(f"   * Dominant Emotion: {emotion}")
    print()
    
    # Step 3: Text feature analysis
    print("Step 3: Speech Pattern Analysis...")
    print("-" * 100)
    
    transcript_length = features.get("transcript_length", 0)
    wpm = features.get("wpm", 0)
    pause_count = features.get("pause_count", 0)
    pause_duration = features.get("pause_avg_duration", 0)
    filler_count = features.get("filler_count", 0)
    
    print(f"[OK] Speech Patterns:")
    print(f"   * Total Words: {transcript_length}")
    print(f"   * Words Per Minute: {wpm:.1f}")
    print(f"   * Pauses: {pause_count} (avg {pause_duration:.2f}s)")
    print(f"   * Fillers Used: {filler_count}")
    print()
    
    # Step 4: Get behavioral score
    print("Step 4: Calculating Behavioral Score (Delivery Quality)...")
    print("-" * 100)
    
    feature_payload = {
        "transcript_length": transcript_length,
        "wpm": wpm,
        "pause_count": pause_count,
        "pause_avg_duration": pause_duration,
        "filler_count": filler_count,
        "eye_contact_pct": eye_contact,
        "head_pose_score": head_pose,
        "posture_score": posture,
        "facial_stability_score": facial_stability,
        "question_difficulty": 1,
    }
    
    behavioral_score = predict_score(feature_payload)
    
    print(f"[OK] Behavioral Score: {behavioral_score:.2f}/10.0")
    print(f"   Factors: Speech clarity, pacing, fillers, body language")
    print()
    
    # Step 5: Get correctness score
    print("Step 5: Analyzing Content Correctness (Keyword Matching)...")
    print("-" * 100)
    
    correctness_result = score_answer_correctness(transcript, question_id, role)
    correctness_score = correctness_result.get("correctness_score", 0)
    tier_matched = correctness_result.get("tier_matched", "NONE")
    match_high = correctness_result.get("match_high", 0)
    match_medium = correctness_result.get("match_medium", 0)
    match_low = correctness_result.get("match_low", 0)
    keywords_found = correctness_result.get("keywords_found", [])
    
    print(f"[OK] Correctness Score: {correctness_score:.2f}/10.0")
    print(f"   * Tier Matched: {tier_matched}")
    print(f"   * HIGH tier keywords: {match_high:.1f}%")
    print(f"   * MEDIUM tier keywords: {match_medium:.1f}%")
    print(f"   * LOW tier keywords: {match_low:.1f}%")
    print()
    
    print(f"[KEYWORDS] Found in Answer ({len(keywords_found)} total):")
    print(f"   First 15 keywords: {', '.join(keywords_found[:15])}")
    if len(keywords_found) > 15:
        print(f"   ... and {len(keywords_found) - 15} more")
    print()
    
    # Step 6: Combined score
    print("Step 6: Calculating Final Combined Score...")
    print("-" * 100)
    
    behavioral_out_of_4 = round((behavioral_score / 10.0) * 4.0, 1)
    correctness_out_of_6 = round((correctness_score / 10.0) * 6.0, 1)
    combined_score = round(behavioral_out_of_4 + correctness_out_of_6, 1)
    
    print(f"Formula: behavioral out of 4 + correctness out of 6")
    print(f"  = ({behavioral_score:.2f}/10.0) -> {behavioral_out_of_4:.2f}/4.0")
    print(f"  = ({correctness_score:.2f}/10.0) -> {correctness_out_of_6:.2f}/6.0")
    print(f"  = {combined_score:.2f}/10.0")
    print()
    
    return {
        "candidate": Path(video_path).stem,
        "question_id": question_id,
        "role": role,
        "question": question_text,
        "transcript": transcript,
        "transcript_length": transcript_length,
        "wpm": wpm,
        "pause_count": pause_count,
        "pause_avg_duration": pause_duration,
        "filler_count": filler_count,
        "eye_contact": eye_contact,
        "head_pose": head_pose,
        "posture": posture,
        "facial_stability": facial_stability,
        "emotion": emotion,
        "behavioral_score": behavioral_score,
        "behavioral_score_out_of_4": behavioral_out_of_4,
        "correctness_score": correctness_score,
        "correctness_score_out_of_6": correctness_out_of_6,
        "tier_matched": tier_matched,
        "match_high": match_high,
        "match_medium": match_medium,
        "match_low": match_low,
        "keywords_found": keywords_found,
        "combined_score": combined_score,
    }


def format_final_report(results_asad, results_usman):
    """Format results in a nice display for the final app"""
    
    print("\n\n")
    print("+" + "="*98 + "+")
    print("|" + " "*98 + "|")
    print("|" + "FINAL INTERVIEW EVALUATION REPORT".center(98) + "|")
    print("|" + " "*98 + "|")
    print("+" + "="*98 + "+")
    
    for idx, (candidate_name, results) in enumerate([("ASAD", results_asad), ("USMAN", results_usman)], 1):
        
        print("\n")
        print("+" + "-"*98 + "+")
        print("|" + f" CANDIDATE {idx}: {candidate_name.upper()}".ljust(99) + "|")
        print("+" + "-"*98 + "+")
        
        # Header info
        print(f"| Role: {results['role']:<30} Question ID: {results['question_id']:<5} |".ljust(100))
        print("|" + " "*98 + "|")
        
        # Question
        print(f"| Question: {results['question'][:88]:<88} |")
        if len(results['question']) > 88:
            print(f"|          {results['question'][88:]:<88} |")
        print("|" + " "*98 + "|")
        print("+" + "-"*98 + "+")
        
        # Transcript
        print("| TRANSCRIPT:".ljust(100) + "|")
        transcript_lines = results['transcript'].split('\n')
        for line in transcript_lines[:8]:  # Show first 8 lines
            print(f"|  {line[:94]:<94} |")
        if len(transcript_lines) > 8:
            print(f"|  ... ({len(transcript_lines) - 8} more lines) |".ljust(100))
        print("|" + " "*98 + "|")
        print("+" + "-"*98 + "+")
        
        # Speech Analysis
        print("| [SPEECH & COMMUNICATION ANALYSIS]".ljust(100) + "|")
        print(f"|   * Word Count: {results['transcript_length']:<80} |")
        print(f"|   * Pacing (WPM): {results['wpm']:.1f} words/min{' '*65} |")
        print(f"|   * Pauses: {results['pause_count']} pauses (avg {results['pause_avg_duration']:.2f}s){' '*57} |")
        print(f"|   * Filler Words: {results['filler_count']} instances (um, uh, like, etc.){' '*48} |")
        print("|" + " "*98 + "|")
        print("+" + "-"*98 + "+")
        
        # Behavioral Metrics
        print("| [BEHAVIORAL METRICS & EXPRESSIONS]".ljust(100) + "|")
        print(f"|   * Eye Contact: {results['eye_contact']:.1f}% {get_eye_contact_emoji(results['eye_contact']):<80} |")
        print(f"|   * Head Pose: {results['head_pose']}/10 {get_score_bar(results['head_pose']):<78} |")
        print(f"|   * Posture: {results['posture']}/10 {get_score_bar(results['posture']):<79} |")
        print(f"|   * Facial Stability: {results['facial_stability']}/10 {get_score_bar(results['facial_stability']):<70} |")
        print(f"|   * Dominant Emotion: {results['emotion'].capitalize():<76} |")
        print("|" + " "*98 + "|")
        print("+" + "-"*98 + "+")
        
        # Content Analysis
        print("| [CONTENT CORRECTNESS ANALYSIS]".ljust(100) + "|")
        print(f"|   * Tier Matched: {results['tier_matched']:<80} |")
        print(f"|   * HIGH tier accuracy: {results['match_high']:.1f}% {get_accuracy_bar(results['match_high']):<68} |")
        print(f"|   * MEDIUM tier accuracy: {results['match_medium']:.1f}% {get_accuracy_bar(results['match_medium']):<65} |")
        print(f"|   * LOW tier accuracy: {results['match_low']:.1f}% {get_accuracy_bar(results['match_low']):<68} |")
        print("|" + " "*98 + "|")
        
        print(f"|   Top Keywords Found: {', '.join(results['keywords_found'][:5]):<75} |")
        if len(results['keywords_found']) > 5:
            print(f"|   Plus {len(results['keywords_found']) - 5} additional keywords{' '*72} |")
        print("|" + " "*98 + "|")
        print("+" + "-"*98 + "+")
        
        # Scores
        print("| [OVERALL SCORES]".ljust(100) + "|")
        print(f"|   Behavioral Score (Delivery):  {results['behavioral_score']:.2f}/10.0  [{get_rating(results['behavioral_score']):<14}]  {get_score_icon(results['behavioral_score'])}".ljust(100) + "|")
        print(f"|   Behavioral Contribution:      {results['behavioral_score_out_of_4']:.2f}/4.0{' '*63} |")
        print(f"|   Correctness Score (Content):  {results['correctness_score']:.2f}/10.0  [{get_rating(results['correctness_score']):<14}]  {get_score_icon(results['correctness_score'])}".ljust(100) + "|")
        print(f"|   Correctness Contribution:     {results['correctness_score_out_of_6']:.2f}/6.0{' '*63} |")
        print("|" + " "*98 + "|")
        print(f"|   FINAL SCORE:                  {results['combined_score']:.2f}/10.0  [{get_rating(results['combined_score']):<14}]  [**]".ljust(100) + "|")
        print("|" + " "*98 + "|")
        print("+" + "-"*98 + "+")
        
        # Feedback
        print("| [FEEDBACK & RECOMMENDATIONS]".ljust(100) + "|")
        
        if results['behavioral_score'] >= 8.0:
            print("|   [OK] Excellent delivery - Clear speech, good pacing, minimal fillers".ljust(100) + "|")
        elif results['behavioral_score'] >= 7.0:
            print("|   [OK] Good delivery - Generally clear with minor improvements possible".ljust(100) + "|")
        elif results['behavioral_score'] >= 6.0:
            print("|   [!]  Fair delivery - Some clarity or pacing issues to address".ljust(100) + "|")
        else:
            print("|   [X] Delivery needs improvement - Work on clarity and pacing".ljust(100) + "|")
        
        if results['tier_matched'] == "HIGH":
            print("|   [OK] Expert-level content - Demonstrates deep technical knowledge".ljust(100) + "|")
        elif results['tier_matched'] == "MEDIUM":
            print("|   [OK] Good content - Core concepts understood, room for more depth".ljust(100) + "|")
        elif results['tier_matched'] == "LOW":
            print("|   [!]  Basic content - Some understanding but lacks technical depth".ljust(100) + "|")
        else:
            print("|   [X] Content needs improvement - Align answer with expected keywords".ljust(100) + "|")
        
        print("|" + " "*98 + "|")
        print("+" + "-"*98 + "+")


def get_eye_contact_emoji(pct):
    if pct >= 80:
        return "[ Excellent ]"
    elif pct >= 60:
        return "[ Good ]"
    else:
        return "[ Needs Improvement ]"


def get_score_bar(score):
    """Create a visual bar for score"""
    filled = int(score)
    empty = 10 - filled
    return "#" * filled + "-" * empty


def get_accuracy_bar(pct):
    """Create a visual bar for percentage"""
    filled = int(pct / 10)
    empty = 10 - filled
    return "#" * filled + "-" * empty


def get_rating(score):
    if score >= 9.0:
        return "Outstanding"
    elif score >= 8.0:
        return "Excellent"
    elif score >= 7.0:
        return "Very Good"
    elif score >= 6.0:
        return "Good"
    elif score >= 5.0:
        return "Fair"
    else:
        return "Poor"


def get_score_icon(score):
    if score >= 8.5:
        return "[**]"
    elif score >= 7.5:
        return "[*]"
    elif score >= 6.5:
        return "[OK]"
    elif score >= 5.5:
        return "[!]"
    else:
        return "[X]"


def main():
    """Run comprehensive analysis on both candidates"""
    
    print("\n" + "="*100)
    print("=" + " "*98 + "=")
    print("=" + "COMPREHENSIVE CANDIDATE ANALYSIS & SCORING SYSTEM".center(98) + "=")
    print("=" + " "*98 + "=")
    print("="*100)
    
    video_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
    
    # Asad1: Backend Q3 (Real processing)
    results_asad = extract_and_analyze_video(
        os.path.join(video_dir, "Asad1.mov"),
        question_id=3,
        role="Software Engineer",
        question_text="How do you approach code refactoring in a large legacy codebase?"
    )
    
    # Usman1: Data Scientist Q1 (Real processing)
    results_usman = extract_and_analyze_video(
        os.path.join(video_dir, "Usman1.mp4"),
        question_id=1,
        role="Data Scientist",
        question_text="What is the difference between supervised and unsupervised learning?"
    )
    
    if results_asad and results_usman:
        format_final_report(results_asad, results_usman)
        
        # Save results to JSON for app consumption
        output_data = {
            "candidates": [results_asad, results_usman],
            "generated_at": "2026-05-01",
            "app_version": "1.0.0"
        }
        
        with open("interview_results.json", "w") as f:
            json.dump(output_data, f, indent=2)
        
        print("\n\n[OK] Results saved to interview_results.json")
    else:
        print("[ERROR] Failed to process one or more videos")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
