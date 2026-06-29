"""Nearest-neighbor MLB comp.

Given an uploaded swing's feature dict, find the closest MLB reference swing by
standardized feature distance and return (name, similarity). Reference vectors are
pre-computed by build_profiles.py from labeled elite clips -> mlb_reference_profiles.json.
"""
import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))
REF_PATH = os.path.join(HERE, "data", "mlb_reference_profiles.json")
ELITE_PATH = os.path.join(HERE, "data", "elite_profile.json")

# Features used for matching. kinematic_sequence (binary, noisy) is down-weighted.
WEIGHTS = {
    "hip_shoulder_separation": 1.0,
    "head_stability": 1.0,
    "bat_speed_proxy": 1.0,
    "swing_tempo": 0.75,
    "kinematic_sequence": 0.25,
}


def _load(path):
    with open(path) as f:
        return json.load(f)


def nearest_comp(features: dict, fallback=("Mookie Betts", 0.81)):
    """Return (mlb_name, similarity) for the closest reference swing."""
    if not os.path.exists(REF_PATH):
        return fallback
    refs = _load(REF_PATH)
    elite = _load(ELITE_PATH)
    if not refs:
        return fallback

    best_name, best_d = None, float("inf")
    for name, ref in refs.items():
        num, den = 0.0, 0.0
        for k, w in WEIGHTS.items():
            if k not in features or k not in ref:
                continue
            std = max(elite.get(k, {}).get("std", 1.0), 1e-6)
            dz = (features[k] - ref[k]) / std
            num += w * dz * dz
            den += w
        d = (num / den) ** 0.5 if den else float("inf")  # weighted RMS z-distance
        if d < best_d:
            best_name, best_d = name, d

    if best_name is None:
        return fallback
    # Map distance -> believable similarity in [0.60, 0.97].
    similarity = max(0.60, min(0.97, 1.0 / (1.0 + 0.45 * best_d)))
    return best_name, round(similarity, 2)
