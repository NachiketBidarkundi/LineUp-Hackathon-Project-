"""Real swing analysis: video path -> biomech_result.json shape (team contract)."""
import os
import json

from .pose_extract import extract_pose
from .features import compute_features
from .mlb_comp import nearest_comp

HERE = os.path.dirname(os.path.abspath(__file__))
ELITE_PATH = os.path.join(HERE, "data", "elite_profile.json")
RULES_PATH = os.path.join(HERE, "data", "rules.json")


def _load(path):
    with open(path) as f:
        return json.load(f)


def _z(value, mean, std):
    return 0.0 if std == 0 else (value - mean) / std


def analyze_swing_real(video_path: str) -> dict:
    """Run the full MediaPipe biomech pipeline. Returns the biomech_result contract.

    Raises if pose extraction finds no usable swing — caller falls back to mock.
    """
    feats = compute_features(extract_pose(video_path))
    elite = _load(ELITE_PATH)
    rules = _load(RULES_PATH)

    feature_scores, diagnoses, strengths = {}, [], []

    for fname, value in feats.items():
        if fname not in elite:
            continue
        mean, std = elite[fname]["mean"], elite[fname]["std"]
        z = _z(value, mean, std)
        feature_scores[fname] = {
            "value": round(float(value), 2),
            "elite_avg": round(float(mean), 2),
            "z_score": round(float(z), 2),
        }
        rule = rules.get(fname, {})
        direction = rule.get("direction")

        if direction == "binary":
            elite_mean = elite[fname]["mean"]
            if value == 0 and elite_mean >= 0.85:
                # Only fire as critical if elite hitters reliably pass this
                diagnoses.append({
                    "severity": "critical", "feature": fname,
                    "message": rule["binary_fail_diagnosis"],
                    "estimated_cost": rule["binary_fail_cost"],
                    "fix": rule["binary_fail_fix"],
                })
            elif value == 1:
                strengths.append({"feature": fname, "message": rule["binary_pass_strength"]})
            # else: silent — feature too noisy at elite level to diagnose confidently
        elif direction == "high_is_good" and z <= rule.get("low_threshold_z", -1.0):
            diagnoses.append({
                "severity": "critical" if z <= -2.0 else "warning",
                "feature": fname, "message": rule["low_diagnosis"],
                "estimated_cost": rule["low_cost"], "fix": rule["low_fix"],
            })
        elif direction == "low_is_good" and z >= rule.get("high_threshold_z", 1.0):
            diagnoses.append({
                "severity": "critical" if z >= 2.0 else "warning",
                "feature": fname, "message": rule["high_diagnosis"],
                "estimated_cost": rule["high_cost"], "fix": rule["high_fix"],
            })
        elif direction == "neutral":
            if z <= rule.get("low_threshold_z", -1.5):
                diagnoses.append({
                    "severity": "warning", "feature": fname,
                    "message": rule["low_diagnosis"],
                    "estimated_cost": rule["low_cost"], "fix": rule["low_fix"],
                })
            elif z >= rule.get("high_threshold_z", 1.5):
                diagnoses.append({
                    "severity": "warning", "feature": fname,
                    "message": rule["high_diagnosis"],
                    "estimated_cost": rule["high_cost"], "fix": rule["high_fix"],
                })

    # Overall biomech score: 100 minus weighted penalty, clamped to [0, 100]
    penalty = 0.0
    for fname, fs in feature_scores.items():
        z = fs["z_score"]
        d = rules.get(fname, {}).get("direction")
        if d == "high_is_good" and z < 0:
            penalty += min(abs(z) * 8, 20)
        elif d == "low_is_good" and z > 0:
            penalty += min(z * 8, 20)
        elif d == "binary" and fs["value"] == 0:
            penalty += 10
        elif d == "neutral":
            penalty += min(abs(z) * 4, 10)
    score = int(max(0, min(100, 100 - penalty)))

    diagnoses.sort(key=lambda x: {"critical": 0, "warning": 1, "info": 2}.get(x["severity"], 9))

    mlb_comp, similarity = nearest_comp(feats)

    return {
        "score": score,
        "mlb_comp": mlb_comp,
        "similarity": similarity,
        "feature_scores": feature_scores,
        "diagnoses": diagnoses,
        "strengths": strengths,
    }


if __name__ == "__main__":
    import sys
    print(json.dumps(analyze_swing_real(sys.argv[1]), indent=2))
