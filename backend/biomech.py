"""Biomechanical swing analysis.

Public entry point `analyze_swing(video_path, seed_key)` runs the real MediaPipe
pipeline (swing/) when a video is supplied and the CV stack is available, and
falls back to the deterministic mock below on any failure — so the demo never
crashes even if MediaPipe can't load (e.g. serverless deploy).
"""
import random
import hashlib
import logging
from typing import Dict, Any, Optional

log = logging.getLogger("lineup")

MLB_COMPS = [
    ("Mookie Betts", 0.81),
    ("Juan Soto", 0.78),
    ("Aaron Judge", 0.74),
    ("Ronald Acuña Jr.", 0.79),
    ("Corey Seager", 0.76),
    ("Freddie Freeman", 0.77),
    ("Mike Trout", 0.72),
]

ELITE_AVG = {
    "hip_shoulder_separation": 52,
    "head_stability": 6,        # cm of nose movement (lower = better)
    "kinematic_sequence": 1,    # binary: 1 = correct order
    "bat_speed_proxy": 75,      # mph
    "swing_tempo": 14,          # frames load -> contact
}

RULES = {
    "hip_shoulder_separation": {
        "low_diagnosis": "Hip-shoulder separation is {value}° (elite avg: 52°). Upper body rotates with hips, breaking the kinetic chain.",
        "low_cost": "−6 mph exit velocity",
        "low_fix": "Hold-the-wall drill — keep front shoulder closed until hips reach 80% rotation.",
    },
    "head_stability": {
        "high_diagnosis": "Excessive head movement: {value}cm (elite avg: 6cm). You're pulling off the ball.",
        "high_cost": "−0.04 AVG vs fastballs",
        "high_fix": "Chin-to-shoulder cue. Keep eyes level through contact.",
    },
    "bat_speed_proxy": {
        "low_diagnosis": "Bat speed proxy at {value} mph (elite avg: 75 mph). Late hand acceleration.",
        "low_cost": "−4 mph exit velocity",
        "low_fix": "Overload/underload bat training, 3x/week.",
    },
    "swing_tempo": {
        "high_diagnosis": "Swing tempo at {value} frames (elite: 14). Too slow from load to contact.",
        "high_cost": "Late on inside fastballs",
        "high_fix": "High-tee work to shorten the path to the ball.",
    },
}


def _seeded_random(seed_str: str) -> random.Random:
    h = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    return random.Random(h)


def _mock_analyze(seed_key: str = "default") -> Dict[str, Any]:
    """Return a deterministic-yet-realistic biomech result keyed by a string seed
    (filename or player_id). Same input -> same output for stable demos."""
    rng = _seeded_random(seed_key)

    hip_shoulder = rng.randint(28, 58)        # below 45 is a problem
    head_stab = rng.randint(3, 18)            # above 9 is a problem
    kin_seq = 1 if rng.random() > 0.25 else 0
    bat_speed = round(rng.uniform(64, 76), 1)
    tempo = rng.randint(11, 19)

    # z-scores (positive = above elite avg; sign meaning varies per feature)
    def z(value, elite, sd):
        return round((value - elite) / sd, 2)

    feature_scores = {
        "hip_shoulder_separation": {"value": hip_shoulder, "elite_avg": 52, "z_score": z(hip_shoulder, 52, 10)},
        "head_stability":          {"value": head_stab,    "elite_avg": 6,  "z_score": z(head_stab, 6, 4)},
        "kinematic_sequence":      {"value": kin_seq,      "elite_avg": 1,  "z_score": 0 if kin_seq == 1 else -2.0},
        "bat_speed_proxy":         {"value": bat_speed,    "elite_avg": 75, "z_score": z(bat_speed, 75, 4)},
        "swing_tempo":             {"value": tempo,        "elite_avg": 14, "z_score": z(tempo, 14, 2)},
    }

    diagnoses = []
    strengths = []

    if feature_scores["hip_shoulder_separation"]["z_score"] <= -1.0:
        r = RULES["hip_shoulder_separation"]
        diagnoses.append({
            "severity": "critical",
            "feature": "hip_shoulder_separation",
            "message": r["low_diagnosis"].format(value=hip_shoulder),
            "estimated_cost": r["low_cost"],
            "fix": r["low_fix"],
        })
    else:
        strengths.append({"feature": "hip_shoulder_separation", "message": f"Strong hip-shoulder separation: {hip_shoulder}°."})

    if feature_scores["head_stability"]["z_score"] >= 1.0:
        r = RULES["head_stability"]
        diagnoses.append({
            "severity": "moderate",
            "feature": "head_stability",
            "message": r["high_diagnosis"].format(value=head_stab),
            "estimated_cost": r["high_cost"],
            "fix": r["high_fix"],
        })
    else:
        strengths.append({"feature": "head_stability", "message": f"Quiet head: only {head_stab}cm of movement."})

    if kin_seq == 1:
        strengths.append({"feature": "kinematic_sequence", "message": "Correct firing order: hips → torso → hands."})
    else:
        diagnoses.append({
            "severity": "critical",
            "feature": "kinematic_sequence",
            "message": "Kinematic sequence broken: hands fire before hips. Power leak.",
            "estimated_cost": "−8 mph exit velocity",
            "fix": "Med-ball rotational throws, focus on lower-half initiation.",
        })

    if feature_scores["bat_speed_proxy"]["z_score"] <= -1.0:
        r = RULES["bat_speed_proxy"]
        diagnoses.append({
            "severity": "moderate",
            "feature": "bat_speed_proxy",
            "message": r["low_diagnosis"].format(value=bat_speed),
            "estimated_cost": r["low_cost"],
            "fix": r["low_fix"],
        })

    if feature_scores["swing_tempo"]["z_score"] >= 1.0:
        r = RULES["swing_tempo"]
        diagnoses.append({
            "severity": "moderate",
            "feature": "swing_tempo",
            "message": r["high_diagnosis"].format(value=tempo),
            "estimated_cost": r["high_cost"],
            "fix": r["high_fix"],
        })

    # Overall score: 100 - 10 per critical diagnosis - 5 per moderate
    penalty = sum(15 if d["severity"] == "critical" else 7 for d in diagnoses)
    score = max(40, min(98, 95 - penalty + rng.randint(-3, 3)))

    comp_name, comp_sim = rng.choice(MLB_COMPS)

    return {
        "score": score,
        "mlb_comp": comp_name,
        "similarity": comp_sim,
        "feature_scores": feature_scores,
        "diagnoses": diagnoses,
        "strengths": strengths,
    }


def analyze_swing(video_path: Optional[str] = None, seed_key: str = "default") -> Dict[str, Any]:
    """Analyze a swing.

    If `video_path` is given and the real MediaPipe pipeline is available, run it.
    On any failure (CV libs missing, no swing detected, decode error) fall back to
    the deterministic mock keyed by `seed_key` so the response shape is always valid.
    """
    if video_path:
        try:
            from swing import analyze_swing_real
            result = analyze_swing_real(video_path)
            log.info("biomech: real analysis ok (score=%s, comp=%s)", result["score"], result["mlb_comp"])
            return result
        except Exception as e:
            log.warning("biomech: real analysis failed (%s); using mock fallback", e)
    return _mock_analyze(seed_key)
