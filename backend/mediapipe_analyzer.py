"""Analyze behavioral video signals using MediaPipe.

This module provides `analyze_video_behavior(video_path)` which extracts frames
(at 2 FPS) and computes approximate metrics: eye contact percentage, head pose
score, posture score, facial stability and dominant emotion.

The implementation uses heuristics to remain lightweight and robust. It falls
back to zeros if MediaPipe is unavailable or no faces are detected.
"""

from __future__ import annotations

import os
import math
import statistics
from typing import Dict

import cv2

try:
    import mediapipe as mp
except Exception:
    mp = None


def _map_angle_to_score(angle_deg: float) -> int:
    """Map a head angle (degrees) to a 0-10 score. Smaller absolute angles -> higher score."""
    a = min(180.0, abs(angle_deg))
    if a < 10:
        return 10
    if a < 20:
        return 8
    if a < 35:
        return 6
    if a < 60:
        return 4
    return 2


def analyze_video_behavior(video_path: str, target_fps: int = 2) -> Dict[str, object]:
    """Analyze a video file and return behavioral metrics.

    Args:
        video_path: Path to video file.
        target_fps: Frames-per-second to sample (default 2).

    Returns:
        dict with keys: eye_contact_pct, head_pose_score, posture_score,
        facial_stability_score, dominant_emotion
    """
    # Basic validations
    if not os.path.exists(video_path):
        return {
            "eye_contact_pct": 0.0,
            "head_pose_score": 0,
            "posture_score": 0,
            "facial_stability_score": 0,
            "dominant_emotion": "neutral",
            "warning": "video_not_found",
        }

    if mp is None:
        return {
            "eye_contact_pct": 0.0,
            "head_pose_score": 0,
            "posture_score": 0,
            "facial_stability_score": 0,
            "dominant_emotion": "neutral",
            "warning": "mediapipe_unavailable",
        }

    cap = cv2.VideoCapture(video_path)
    orig_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = total_frames / orig_fps if orig_fps else 0

    # Determine timestamps to sample at target_fps
    n_samples = max(1, int(math.ceil(duration * target_fps)))
    sample_times = [i / target_fps for i in range(n_samples)]

    mp_face = mp.solutions.face_mesh.FaceMesh(static_image_mode=True,
                                             max_num_faces=1,
                                             refine_landmarks=True,
                                             min_detection_confidence=0.5)
    mp_pose = mp.solutions.pose.Pose(static_image_mode=True,
                                     model_complexity=1,
                                     enable_segmentation=False,
                                     min_detection_confidence=0.5)

    looking_count = 0
    head_angles = []
    posture_scores = []
    nose_positions = []
    mouth_opens = []
    brow_dists = []

    processed_frames = 0

    for t in sample_times:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ret, frame = cap.read()
        if not ret:
            continue
        processed_frames += 1
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Face mesh
        try:
            face_results = mp_face.process(img_rgb)
        except Exception:
            face_results = None

        # Pose
        try:
            pose_results = mp_pose.process(img_rgb)
        except Exception:
            pose_results = None

        h, w = frame.shape[:2]

        if face_results and face_results.multi_face_landmarks:
            lm = face_results.multi_face_landmarks[0]
            # Nose tip landmark index ~1 or use 1
            # Use normalized landmarks
            nose = lm.landmark[1]
            nose_positions.append((nose.x * w, nose.y * h))

            # Eye centers: use landmarks for left/right eye average
            # left eye approx: 33..133 area; use 33 (left) and 263 (right)
            try:
                left_eye = lm.landmark[33]
                right_eye = lm.landmark[263]
                eye_cx = ((left_eye.x + right_eye.x) / 2.0) * w
                eye_cy = ((left_eye.y + right_eye.y) / 2.0) * h
                # Consider eye contact if eye center horizontally near frame center
                if abs(eye_cx - (w / 2.0)) < (w * 0.15):
                    looking_count += 1
            except Exception:
                pass

            # Mouth openness: distance between upper and lower lip landmarks
            try:
                upper_lip = lm.landmark[13]
                lower_lip = lm.landmark[14]
                mouth_open = math.hypot((upper_lip.x - lower_lip.x) * w,
                                        (upper_lip.y - lower_lip.y) * h)
                mouth_opens.append(mouth_open)
            except Exception:
                pass

            # Brow distance: between inner eyebrow points
            try:
                left_brow = lm.landmark[105]  # approximate
                right_brow = lm.landmark[334]
                brow_dist = math.hypot((left_brow.x - right_brow.x) * w,
                                       (left_brow.y - right_brow.y) * h)
                brow_dists.append(brow_dist)
            except Exception:
                pass

            # Head pose approximation: use eye slope for roll
            try:
                dx = (right_eye.x - left_eye.x) * w
                dy = (right_eye.y - left_eye.y) * h
                roll_rad = math.atan2(dy, dx)
                roll_deg = math.degrees(roll_rad)
                head_angles.append(roll_deg)
            except Exception:
                pass

        # Pose-based posture
        if pose_results and pose_results.pose_landmarks:
            plm = pose_results.pose_landmarks.landmark
            try:
                left_shoulder = plm[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
                right_shoulder = plm[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value]
                left_hip = plm[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
                right_hip = plm[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value]

                # Torso vector angle: shoulders midpoint to hips midpoint
                sx = ((left_shoulder.x + right_shoulder.x) / 2.0) * w
                sy = ((left_shoulder.y + right_shoulder.y) / 2.0) * h
                hx = ((left_hip.x + right_hip.x) / 2.0) * w
                hy = ((left_hip.y + right_hip.y) / 2.0) * h

                torso_dx = hx - sx
                torso_dy = hy - sy
                torso_angle = abs(math.degrees(math.atan2(torso_dx, torso_dy)))
                # torso_angle close to 0 -> upright; larger -> tilted
                if torso_angle < 5:
                    posture_scores.append(10)
                elif torso_angle < 12:
                    posture_scores.append(8)
                elif torso_angle < 20:
                    posture_scores.append(6)
                elif torso_angle < 35:
                    posture_scores.append(4)
                else:
                    posture_scores.append(2)
            except Exception:
                pass

    cap.release()
    mp_face.close()
    mp_pose.close()

    if processed_frames == 0:
        return {
            "eye_contact_pct": 0.0,
            "head_pose_score": 0,
            "posture_score": 0,
            "facial_stability_score": 0,
            "dominant_emotion": "neutral",
            "warning": "no_frames_processed",
        }

    # Aggregate eye contact
    eye_contact_pct = (looking_count / processed_frames) * 100.0

    # Head pose score from average absolute roll
    avg_roll = statistics.mean([abs(a) for a in head_angles]) if head_angles else 0.0
    head_pose_score = _map_angle_to_score(avg_roll)

    # Posture score average
    posture_score = int(round(statistics.mean(posture_scores))) if posture_scores else 0

    # Facial stability: variance of nose positions across frames
    facial_stability_score = 0
    try:
        if len(nose_positions) >= 2:
            xs = [p[0] for p in nose_positions]
            ys = [p[1] for p in nose_positions]
            var = (statistics.pvariance(xs) + statistics.pvariance(ys)) / 2.0
            # Normalize var by frame diagonal (roughly)
            norm = var / ((w ** 2 + h ** 2) ** 0.5 + 1e-6)
            facial_stability_score = int(max(2, min(10, round(10 - norm * 50))))
        else:
            facial_stability_score = 8
    except Exception:
        facial_stability_score = 6

    # Emotion heuristics
    emotion_votes = {"confident": 0, "nervous": 0, "confused": 0, "neutral": 0}
    for mo, bd in zip(mouth_opens, brow_dists):
        # mouth open large + brows normal -> nervous
        if mo > 15 and bd < 25:
            emotion_votes["nervous"] += 1
        elif mo < 8 and bd > 30:
            emotion_votes["confident"] += 1
        else:
            emotion_votes["neutral"] += 1

    dominant_emotion = max(emotion_votes.items(), key=lambda x: x[1])[0]

    return {
        "eye_contact_pct": round(float(eye_contact_pct), 1),
        "head_pose_score": int(head_pose_score),
        "posture_score": int(posture_score),
        "facial_stability_score": int(facial_stability_score),
        "dominant_emotion": dominant_emotion,
    }
