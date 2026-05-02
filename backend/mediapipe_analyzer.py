"""Analyze behavioral video signals using MediaPipe.

This module provides `analyze_video_behavior(video_path)` which extracts frames
and computes behavioral metrics from the actual video frames instead of using
hardcoded placeholders.
"""

from __future__ import annotations

import os
import statistics
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

try:
    import mediapipe as mp
except Exception:
    mp = None


FACE_MODEL_POINTS = np.array(
    [
        (0.0, 0.0, 0.0),
        (0.0, -63.6, -12.5),
        (-43.3, 32.7, -26.0),
        (43.3, 32.7, -26.0),
        (-28.9, -28.9, -24.1),
        (28.9, -28.9, -24.1),
    ],
    dtype=np.float64,
)

FACE_LANDMARK_IDS = {
    "nose": 1,
    "chin": 152,
    "left_eye": 33,
    "right_eye": 263,
    "left_mouth": 61,
    "right_mouth": 291,
    "left_brow": 70,
    "right_brow": 300,
    "left_eye_top": 159,
    "right_eye_top": 386,
    "upper_lip": 13,
    "lower_lip": 14,
}


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _landmark_xy(landmarks, index: int, width: int, height: int) -> Tuple[float, float]:
    point = landmarks[index]
    return float(point.x * width), float(point.y * height)


def _distance_2d(point_a: Tuple[float, float], point_b: Tuple[float, float]) -> float:
    return float(np.linalg.norm(np.asarray(point_a) - np.asarray(point_b)))


def _midpoint(point_a: Tuple[float, float], point_b: Tuple[float, float]) -> Tuple[float, float]:
    return ((point_a[0] + point_b[0]) / 2.0, (point_a[1] + point_b[1]) / 2.0)


def _compute_head_pose(landmarks, width: int, height: int) -> Optional[Dict[str, float]]:
    image_points = np.array(
        [
            _landmark_xy(landmarks, FACE_LANDMARK_IDS["nose"], width, height),
            _landmark_xy(landmarks, FACE_LANDMARK_IDS["chin"], width, height),
            _landmark_xy(landmarks, FACE_LANDMARK_IDS["left_eye"], width, height),
            _landmark_xy(landmarks, FACE_LANDMARK_IDS["right_eye"], width, height),
            _landmark_xy(landmarks, FACE_LANDMARK_IDS["left_mouth"], width, height),
            _landmark_xy(landmarks, FACE_LANDMARK_IDS["right_mouth"], width, height),
        ],
        dtype=np.float64,
    )

    focal_length = float(width)
    center = (width / 2.0, height / 2.0)
    camera_matrix = np.array(
        [
            [focal_length, 0.0, center[0]],
            [0.0, focal_length, center[1]],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )
    dist_coeffs = np.zeros((4, 1), dtype=np.float64)

    success, rotation_vector, _ = cv2.solvePnP(
        FACE_MODEL_POINTS,
        image_points,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )
    if not success:
        return None

    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
    euler_angles = cv2.RQDecomp3x3(rotation_matrix)[0]
    pitch, yaw, roll = [float(angle) for angle in euler_angles]
    return {"pitch": pitch, "yaw": yaw, "roll": roll}


def _score_from_angles(pitch: float, yaw: float, roll: float) -> int:
    posture = 10.0 - (abs(pitch) * 0.18 + abs(yaw) * 0.20 + abs(roll) * 0.12)
    return int(round(_clamp(posture, 0.0, 10.0)))


def _classify_emotion(
    landmarks,
    width: int,
    height: int,
    pitch: float,
    yaw: float,
    roll: float,
) -> Tuple[str, Dict[str, float]]:
    left_mouth = _landmark_xy(landmarks, FACE_LANDMARK_IDS["left_mouth"], width, height)
    right_mouth = _landmark_xy(landmarks, FACE_LANDMARK_IDS["right_mouth"], width, height)
    upper_lip = _landmark_xy(landmarks, FACE_LANDMARK_IDS["upper_lip"], width, height)
    lower_lip = _landmark_xy(landmarks, FACE_LANDMARK_IDS["lower_lip"], width, height)
    left_eye = _landmark_xy(landmarks, FACE_LANDMARK_IDS["left_eye"], width, height)
    right_eye = _landmark_xy(landmarks, FACE_LANDMARK_IDS["right_eye"], width, height)
    left_brow = _landmark_xy(landmarks, FACE_LANDMARK_IDS["left_brow"], width, height)
    right_brow = _landmark_xy(landmarks, FACE_LANDMARK_IDS["right_brow"], width, height)
    left_eye_top = _landmark_xy(landmarks, FACE_LANDMARK_IDS["left_eye_top"], width, height)
    right_eye_top = _landmark_xy(landmarks, FACE_LANDMARK_IDS["right_eye_top"], width, height)

    face_width = max(_distance_2d(left_eye, right_eye), 1.0)
    mouth_width = _distance_2d(left_mouth, right_mouth)
    mouth_open = _distance_2d(upper_lip, lower_lip)
    mouth_center = _midpoint(left_mouth, right_mouth)
    brow_eye_gap = (
        _distance_2d(left_brow, left_eye_top) + _distance_2d(right_brow, right_eye_top)
    ) / 2.0

    smile_ratio = mouth_width / face_width
    open_ratio = mouth_open / face_width
    smile_score = _clamp((smile_ratio - 0.32) / 0.14, 0.0, 1.0)
    surprise_score = _clamp((open_ratio - 0.025) / 0.05, 0.0, 1.0)
    sad_score = _clamp((0.020 - (mouth_center[1] / max(height, 1))) / 0.020, 0.0, 1.0)
    eyebrow_score = _clamp((brow_eye_gap / max(height, 1) - 0.065) / 0.035, 0.0, 1.0)
    tension_score = _clamp((abs(pitch) + abs(yaw) + abs(roll)) / 90.0, 0.0, 1.0)

    emotion_scores = {
        "happy": round(smile_score, 3),
        "surprised": round(0.7 * surprise_score + 0.3 * eyebrow_score, 3),
        "sad": round(sad_score, 3),
        "neutral": round(max(0.0, 1.0 - max(smile_score, surprise_score, sad_score, eyebrow_score, tension_score)), 3),
        "focused": round(max(0.0, 1.0 - tension_score), 3),
    }

    dominant_emotion = max(emotion_scores.items(), key=lambda item: item[1])[0]
    return dominant_emotion, emotion_scores


def analyze_video_behavior(video_path: str, target_fps: int = 2) -> Dict[str, object]:
    """Analyze a video file and return behavioral metrics.

    Args:
        video_path: Path to video file.
        target_fps: Frames-per-second to sample (default 2).

    Returns:
        dict with keys: eye_contact_pct, head_pose_score, posture_score,
        facial_stability_score, dominant_emotion (all REAL metrics, not defaults)
    
    Returns `success=False` when the video cannot be analyzed.
    """
    if not os.path.exists(video_path):
        print(f"[Analyzer] ERROR: Video file not found: {video_path}")
        return {"success": False, "error": "video_not_found"}

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
    smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")
    upperbody_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_upperbody.xml")

    if face_cascade.empty() or eye_cascade.empty() or smile_cascade.empty():
        print("[Analyzer] ERROR: OpenCV cascade classifiers not available")
        return {"success": False, "error": "opencv_cascades_unavailable"}

    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            cap.release()
            print(f"[Analyzer] ERROR: Cannot open video: {video_path}")
            return {"success": False, "error": "video_read_error"}

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
        cap.release()

        if total_frames == 0:
            print("[Analyzer] ERROR: Cannot determine video frame count")
            return {"success": False, "error": "unable_to_read_video"}
    except Exception as e:
        print(f"[Analyzer] ERROR: Video read error: {str(e)}")
        return {"success": False, "error": "video_read_error"}

    sample_step = max(1, int(round((fps or 0.0) / max(target_fps, 1))))

    cap = cv2.VideoCapture(video_path)
    frame_index = 0
    analyzed_frames = 0
    face_frames = 0
    posture_frames = 0

    contact_frames = 0  # Frames where eyes detected AND face is centered
    head_scores: List[int] = []
    posture_scores: List[int] = []
    stability_samples: List[float] = []
    emotion_votes: Dict[str, int] = {}
    face_center_offsets: List[float] = []
    face_area_ratios: List[float] = []
    eye_angles: List[float] = []

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            if frame_index % sample_step != 0:
                frame_index += 1
                continue

            analyzed_frames += 1
            frame_index += 1

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            height, width = frame.shape[:2]
            frame_area = float(width * height)
            frame_center = (width / 2.0, height / 2.0)
            frame_diag = float(np.hypot(width, height))

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(80, 80),
            )
            if len(faces) == 0:
                continue

            face_x, face_y, face_w, face_h = max(faces, key=lambda box: box[2] * box[3])
            face_frames += 1

            face_center = (face_x + face_w / 2.0, face_y + face_h / 2.0)
            face_center_offset = float(
                np.hypot(face_center[0] - frame_center[0], face_center[1] - frame_center[1]) / frame_diag
            )
            face_area_ratio = float((face_w * face_h) / max(frame_area, 1.0))
            face_aspect_ratio = float(face_h / max(face_w, 1))

            face_center_offsets.append(face_center_offset)
            face_area_ratios.append(face_area_ratio)

            roi_gray = gray[face_y:face_y + face_h, face_x:face_x + face_w]
            upper_half = roi_gray[: max(1, face_h // 2), :]
            lower_half = roi_gray[max(1, face_h // 2):, :]

            # ACTION 2.1: Detect eyes for eye contact measurement
            eyes = eye_cascade.detectMultiScale(
                upper_half,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(20, 20),
            )
            smiles = smile_cascade.detectMultiScale(
                lower_half,
                scaleFactor=1.7,
                minNeighbors=18,
                minSize=(30, 30),
            )

            eye_boxes = sorted(list(eyes), key=lambda box: box[0])
            eye_angle = 0.0
            eyes_detected = len(eye_boxes) >= 2
            
            if eyes_detected:
                left_eye = eye_boxes[0]
                right_eye = eye_boxes[1]
                left_eye_center = (left_eye[0] + left_eye[2] / 2.0, left_eye[1] + left_eye[3] / 2.0)
                right_eye_center = (right_eye[0] + right_eye[2] / 2.0, right_eye[1] + right_eye[3] / 2.0)
                eye_angle = float(
                    abs(
                        np.degrees(
                            np.arctan2(
                                right_eye_center[1] - left_eye_center[1],
                                right_eye_center[0] - left_eye_center[0] + 1e-6,
                            )
                        )
                    )
                )
            
            eye_angles.append(eye_angle)

            head_score = 10.0 - (
                face_center_offset * 9.0
                + abs(eye_angle) * 0.15
                + abs(face_aspect_ratio - 1.15) * 2.0
            )
            head_scores.append(int(round(_clamp(head_score, 1.0, 10.0))))

            posture_box_score = 10.0 - (
                abs(face_center[1] / max(height, 1) - 0.35) * 12.0
                + face_center_offset * 5.0
                + abs(face_aspect_ratio - 1.15) * 1.5
            )
            upperbody_box_score = None
            if not upperbody_cascade.empty():
                upper_bodies = upperbody_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=3,
                    minSize=(120, 120),
                )
                if len(upper_bodies) > 0:
                    body_x, body_y, body_w, body_h = max(upper_bodies, key=lambda box: box[2] * box[3])
                    body_center_y = body_y + body_h / 2.0
                    upperbody_box_score = 10.0 - abs(body_center_y / max(height, 1) - 0.62) * 10.0

            if upperbody_box_score is not None:
                posture_box_score = (posture_box_score + upperbody_box_score) / 2.0

            posture_scores.append(int(round(_clamp(posture_box_score, 1.0, 10.0))))
            posture_frames += 1

            # ACTION 2.1: Eye contact = eyes detected AND face is centered AND looking forward
            if eyes_detected and face_center_offset < 0.22 and eye_angle < 14.0:
                contact_frames += 1

            # ACTION 2.5: Emotion detection based on smile, focus, surprise, neutral
            smile_found = len(smiles) > 0
            if smile_found and eyes_detected:
                dominant_emotion = "confident"
            elif eyes_detected and face_center_offset < 0.16:
                dominant_emotion = "focused"
            elif face_area_ratio < 0.05 and not eyes_detected:
                dominant_emotion = "surprised"
            else:
                dominant_emotion = "neutral"
            emotion_votes[dominant_emotion] = emotion_votes.get(dominant_emotion, 0) + 1

            # ACTION 2.4: Calculate facial stability
            stability_samples.append(
                float(face_center_offset * 6.0 + abs(eye_angle) * 0.2 + abs(face_aspect_ratio - 1.15) * 1.5)
            )

            # ACTION 2.6: Frame-by-frame logging (every 5th frame)
            if analyzed_frames % 5 == 1:
                print(f"[Analyzer] Frame {analyzed_frames}: face=Y, eyes={eyes_detected}, smile={smile_found}")

    finally:
        cap.release()

    # ACTION 2.7: Validation - must have detected faces
    if face_frames == 0:
        print("[Analyzer] ERROR: No face detected in any frame")
        return {"success": False, "error": "no_face_detected"}

    head_pose_score = int(round(statistics.mean(head_scores))) if head_scores else 1
    posture_score = int(round(statistics.mean(posture_scores))) if posture_scores else 1

    if stability_samples:
        facial_stability_score = int(
            round(_clamp(10.0 - statistics.mean(stability_samples), 1.0, 10.0))
        )
    else:
        facial_stability_score = 1

    if len(face_center_offsets) > 1:
        spread_penalty = statistics.pstdev(face_center_offsets) * 15.0
        spread_penalty += statistics.pstdev(face_area_ratios) * 20.0 if len(face_area_ratios) > 1 else 0.0
        spread_penalty += statistics.pstdev(eye_angles) * 0.10 if len(eye_angles) > 1 else 0.0
        facial_stability_score = int(round(_clamp(10.0 - spread_penalty, 1.0, 10.0)))

    dominant_emotion = max(emotion_votes.items(), key=lambda item: item[1])[0] if emotion_votes else "neutral"
    
    # Ensure emotion is one of the valid types
    valid_emotions = ["confident", "focused", "surprised", "neutral"]
    if dominant_emotion not in valid_emotions:
        dominant_emotion = "neutral"
    
    emotion_scores = {
        emotion: round((count / max(face_frames, 1)) * 100.0, 1)
        for emotion, count in emotion_votes.items()
    }

    eye_contact_pct = round((contact_frames / max(face_frames, 1)) * 100.0, 1)

    # ACTION 2.6: Print debug output
    print(f"[Analyzer] Eye contact detected in {contact_frames}/{face_frames} frames = {eye_contact_pct:.1f}%")
    print(f"[Analyzer] Head pose score: {head_pose_score}/10")
    print(f"[Analyzer] Posture score: {posture_score}/10")
    print(f"[Analyzer] Facial stability: {facial_stability_score}/10")
    print(f"[Analyzer] Dominant emotion: {dominant_emotion}")
    
    # ACTION 2.7: Validate all metrics are in range
    assert 0 <= eye_contact_pct <= 100, f"Eye contact out of range: {eye_contact_pct}"
    assert 1 <= head_pose_score <= 10, f"Head pose score out of range: {head_pose_score}"
    assert 1 <= posture_score <= 10, f"Posture score out of range: {posture_score}"
    assert 1 <= facial_stability_score <= 10, f"Facial stability out of range: {facial_stability_score}"
    assert dominant_emotion in valid_emotions, f"Invalid emotion: {dominant_emotion}"

    print("[Analyzer] [OK] Analyzer completed successfully")

    return {
        "success": True,
        "eye_contact_pct": eye_contact_pct,
        "head_pose_score": head_pose_score,
        "posture_score": posture_score,
        "facial_stability_score": facial_stability_score,
        "dominant_emotion": dominant_emotion,
        "emotion_scores": emotion_scores,
        "emotion_votes": emotion_votes,
        "face_frames": face_frames,
        "posture_frames": posture_frames,
        "analyzed_frames": analyzed_frames,
    }
