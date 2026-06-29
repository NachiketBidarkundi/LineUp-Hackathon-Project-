"""Extract MediaPipe pose landmarks from a video.

Uses the MediaPipe Tasks PoseLandmarker API (mediapipe >= 0.10 ships only
`mediapipe.tasks`, not the legacy `mp.solutions.pose`). Output: a (frames, 33, 3)
array of 3D world landmarks in meters. NaN-filled where no body is detected.
"""
import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(HERE, "models", "pose_landmarker_full.task")


def extract_pose(video_path: str) -> np.ndarray:
    """Returns (frames, 33, 3) world landmarks (meters). NaN where undetected."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Pose model not found at {MODEL_PATH}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    options = vision.PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    frames = []
    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            ts_ms = int(idx * 1000.0 / fps)
            result = landmarker.detect_for_video(mp_image, ts_ms)
            if result.pose_world_landmarks:
                lm = np.array([[p.x, p.y, p.z] for p in result.pose_world_landmarks[0]])
            else:
                lm = np.full((33, 3), np.nan)
            frames.append(lm)
            idx += 1
    cap.release()

    if not frames:
        raise RuntimeError(f"No frames read from {video_path}")
    return np.stack(frames, axis=0)
