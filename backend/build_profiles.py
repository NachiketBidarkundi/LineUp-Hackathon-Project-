"""Offline: build elite_profile.json + mlb_reference_profiles.json from labeled clips.

Run once (needs mediapipe + the source videos), commit the resulting JSON. The
backend ships only the JSON, not the videos.

Usage:
    python build_profiles.py [VIDEOS_DIR]
        VIDEOS_DIR defaults to ~/biomech-swing/data/videos
"""
import os
import sys
import json
import numpy as np

from swing.pose_extract import extract_pose
from swing.features import compute_features

# elite_00N.mp4 -> MLB player label (order given by the user)
LABELS = {
    "elite_001": "Justin Upton",
    "elite_002": "Andrew McCutchen",
    "elite_003": "Miguel Cabrera",
    "elite_004": "Javier Báez",
    "elite_005": "Troy Tulowitzki",
}

# Hand-tuned stds (replace noise-inflated empirical spread; see tuning session).
# kinematic_sequence keeps its empirical std.
STD_OVERRIDE = {
    "hip_shoulder_separation": 8.0,
    "head_stability": 3.0,
    "bat_speed_proxy": 5.0,
    "swing_tempo": 4.0,
}
FEATURES = ["hip_shoulder_separation", "head_stability", "kinematic_sequence",
            "bat_speed_proxy", "swing_tempo"]

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "swing", "data")


def main():
    videos_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/biomech-swing/data/videos")

    per_clip = {}
    for stem, name in LABELS.items():
        path = os.path.join(videos_dir, f"{stem}.mp4")
        if not os.path.exists(path):
            sys.exit(f"Missing clip: {path}")
        feats = compute_features(extract_pose(path))
        per_clip[name] = {k: round(float(feats[k]), 4) for k in FEATURES}
        print(f"  {name:20s} " + "  ".join(f"{k}={feats[k]:.2f}" for k in FEATURES))

    # MLB reference profiles = per-clip labeled feature vectors
    ref_path = os.path.join(DATA_DIR, "mlb_reference_profiles.json")
    with open(ref_path, "w") as f:
        json.dump(per_clip, f, indent=2)
    print(f"\nWrote {ref_path}")

    # Elite profile = mean across clips, with tuned stds
    elite = {}
    for k in FEATURES:
        vals = np.array([per_clip[n][k] for n in per_clip], dtype=float)
        mean = float(vals.mean())
        std = STD_OVERRIDE.get(k)
        if std is None:  # kinematic_sequence: empirical
            std = float(vals.std(ddof=1)) if len(vals) > 1 else 0.3
            std = max(std, 0.3)
        elite[k] = {"mean": round(mean, 3), "std": round(std, 3)}
    elite_path = os.path.join(DATA_DIR, "elite_profile.json")
    with open(elite_path, "w") as f:
        json.dump(elite, f, indent=2)
    print(f"Wrote {elite_path}")
    print(json.dumps(elite, indent=2))


if __name__ == "__main__":
    main()
