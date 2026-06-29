"""Seed data: 50 fabricated college baseball recruits (real D1 program names) + 5 real MLB reference players.

DATA PROVENANCE
- Amateur players: NAMES and PER-PLAYER STATS are fabricated. Player-level Statcast data
  for college baseball is not publicly available (TrackMan/Rapsodo feeds are paid B2B only).
  However, SCHOOL NAMES and CONFERENCES are real D1 programs.
- MLB reference: Names + IDs are real. Career batting (AVG/OBP/SLG/OPS) is fetched LIVE
  via MLB-StatsAPI at startup. Statcast metrics (exit velo, bat speed, sprint) are real
  2024 Baseball Savant public numbers, hard-coded.
"""
import random
from typing import List, Dict, Any

# Real D1 programs grouped by state for the region filter.
# Format: (player_name, age 18-22, position, school, region, height_in, weight_lb, bats, throws, lat, lng)
RAW_AMATEURS_BIO: List[tuple] = [
    # --- TEXAS ---
    ("Jake Morrison",   20, "OF", "University of Texas",          "TX", 73, 195, "R", "R", 30.28, -97.74),
    ("Tyler Banks",     21, "SS", "Texas A&M University",         "TX", 72, 188, "L", "R", 30.62, -96.34),
    ("Mason Hill",      20, "OF", "Texas Tech University",        "TX", 75, 205, "R", "R", 33.58, -101.87),
    ("Owen Brooks",     21, "SS", "TCU",                          "TX", 72, 182, "L", "R", 32.71, -97.36),
    ("Dalton Pierce",   22, "1B", "Houston Christian University", "TX", 76, 220, "R", "R", 29.72, -95.41),
    ("Brett Holloway",  19, "C",  "Dallas Baptist University",    "TX", 71, 200, "R", "R", 32.66, -96.86),
    ("Cole Whitfield",  20, "3B", "Rice University",              "TX", 73, 192, "R", "R", 29.71, -95.40),
    ("Sam Calderon",    21, "OF", "Sam Houston State",            "TX", 74, 198, "S", "R", 30.71, -95.55),
    # --- CALIFORNIA ---
    ("Diego Ramirez",   21, "OF", "UCLA",                         "CA", 74, 198, "L", "L", 34.07, -118.45),
    ("Lucas Park",      20, "OF", "Stanford University",          "CA", 71, 180, "R", "R", 37.43, -122.17),
    ("Noah Sanchez",    22, "1B", "Cal State Fullerton",          "CA", 75, 215, "L", "L", 33.88, -117.88),
    ("Marcus Reyes",    20, "C",  "USC",                          "CA", 71, 205, "R", "R", 34.02, -118.29),
    ("Ryan Caldwell",   21, "2B", "UC Santa Barbara",             "CA", 70, 178, "R", "R", 34.41, -119.84),
    ("Aiden Park",      19, "OF", "Cal Poly",                     "CA", 73, 190, "L", "L", 35.30, -120.66),
    ("Jameson Cole",    22, "3B", "San Diego State",              "CA", 74, 202, "R", "R", 32.78, -117.07),
    ("Trent Maddox",    21, "SS", "Loyola Marymount",             "CA", 72, 185, "R", "R", 33.97, -118.42),
    # --- FLORIDA ---
    ("Connor O'Brien",  21, "1B", "University of Florida",        "FL", 76, 220, "R", "R", 29.65, -82.34),
    ("Brayden Cole",    20, "3B", "Florida State University",     "FL", 74, 208, "R", "R", 30.44, -84.30),
    ("Ethan Cooper",    19, "2B", "University of Miami",          "FL", 70, 175, "R", "R", 25.72, -80.28),
    ("Garrett Lee",     22, "3B", "USF",                          "FL", 74, 205, "L", "R", 28.06, -82.41),
    ("Mateo Vasquez",   21, "OF", "Florida Atlantic",             "FL", 73, 192, "S", "R", 26.37, -80.10),
    ("Hudson Walsh",    20, "C",  "Stetson University",           "FL", 72, 208, "R", "R", 29.03, -81.30),
    ("Carson Whitlock", 19, "SS", "Jacksonville University",      "FL", 71, 180, "R", "R", 30.34, -81.60),
    ("Devin Brooks",    22, "OF", "FIU",                          "FL", 75, 200, "L", "L", 25.76, -80.37),
    # --- GEORGIA ---
    ("Eli Carter",      20, "2B", "University of Georgia",        "GA", 70, 172, "S", "R", 33.95, -83.37),
    ("Xavier Thomas",   21, "OF", "Georgia Tech",                 "GA", 75, 198, "R", "R", 33.78, -84.40),
    ("Jordan Foster",   20, "OF", "Mercer University",            "GA", 73, 185, "S", "R", 32.83, -83.65),
    ("Caleb Whitley",   22, "1B", "Kennesaw State",               "GA", 76, 218, "R", "R", 34.04, -84.58),
    ("Reese Hampton",   19, "C",  "Georgia Southern",             "GA", 72, 210, "R", "R", 32.42, -81.78),
    ("Drew Mallory",    21, "3B", "Georgia State",                "GA", 74, 205, "R", "R", 33.75, -84.39),
    # --- NORTH CAROLINA ---
    ("Logan Pierce",    20, "SS", "UNC Chapel Hill",              "NC", 71, 178, "R", "R", 35.91, -79.05),
    ("Aaron Mitchell",  21, "OF", "Wake Forest University",       "NC", 73, 192, "L", "L", 36.13, -80.27),
    ("Brooks Tanner",   22, "OF", "NC State",                     "NC", 74, 196, "R", "R", 35.78, -78.68),
    ("Jaxon Reed",      19, "SS", "Duke University",              "NC", 72, 185, "R", "R", 35.99, -78.94),
    ("Tate Burnham",    20, "1B", "East Carolina",                "NC", 75, 215, "L", "L", 35.60, -77.37),
    ("Wyatt Garrison",  21, "3B", "UNC Charlotte",                "NC", 74, 202, "R", "R", 35.30, -80.73),
    ("Knox Calloway",   22, "C",  "Campbell University",          "NC", 71, 208, "R", "R", 35.40, -78.73),
    # --- OHIO ---
    ("Hunter Davis",    20, "3B", "Ohio State University",        "OH", 73, 200, "R", "R", 40.00, -83.02),
    ("Caleb Wright",    21, "C",  "University of Cincinnati",     "OH", 72, 208, "R", "R", 39.13, -84.51),
    ("Riley Henderson", 22, "SS", "Miami University (OH)",        "OH", 72, 185, "R", "R", 39.51, -84.74),
    ("Bennett Cross",   19, "OF", "Wright State",                 "OH", 73, 188, "L", "R", 39.78, -84.06),
    ("Sawyer Lange",    20, "2B", "Bowling Green State",          "OH", 70, 175, "R", "R", 41.38, -83.65),
    # --- TENNESSEE ---
    ("Walker Kingston", 21, "OF", "University of Tennessee",      "TN", 74, 200, "R", "R", 35.95, -83.93),
    ("Cash Buchanan",   20, "1B", "Vanderbilt University",        "TN", 76, 220, "L", "L", 36.15, -86.80),
    ("Holden Briggs",   22, "3B", "Memphis University",           "TN", 74, 205, "R", "R", 35.12, -89.94),
    # --- LOUISIANA ---
    ("Beau Thibodeaux", 21, "C",  "LSU",                          "LA", 72, 215, "R", "R", 30.41, -91.18),
    ("Pierre Landry",   20, "OF", "Tulane University",            "LA", 73, 192, "L", "L", 29.94, -90.12),
    ("Levi Castille",   19, "SS", "University of Louisiana-Lafayette", "LA", 71, 178, "R", "R", 30.21, -92.02),
    # --- VIRGINIA ---
    ("Carter Vaughn",   22, "OF", "University of Virginia",       "VA", 74, 195, "R", "R", 38.03, -78.51),
    ("Maddox Eastwood", 20, "3B", "Virginia Tech",                "VA", 73, 200, "S", "R", 37.23, -80.42),
    ("Grant Belmont",   21, "2B", "Old Dominion",                 "VA", 70, 178, "R", "R", 36.89, -76.31),
]
# 50 entries

ALL_REGIONS = sorted(set(b[4] for b in RAW_AMATEURS_BIO))


def _stat_for_bio(idx: int, bio: tuple) -> Dict[str, float]:
    """Deterministic realistic college stats from a seeded RNG."""
    rng = random.Random(1000 + idx)
    pos = bio[2]
    height = bio[5]
    weight = bio[6]

    # College stat ranges (a touch higher than HS, below MLB)
    is_power_bat = pos in ("1B", "3B", "OF") and weight >= 195
    is_speed_bat = pos in ("2B", "SS", "OF") and weight <= 190

    avg  = round(rng.uniform(0.295, 0.420), 3)
    obp  = round(min(0.500, avg + rng.uniform(0.050, 0.120)), 3)
    slg_boost = rng.uniform(0.180, 0.330) + (0.05 if is_power_bat else 0)
    slg  = round(min(0.760, avg + slg_boost), 3)
    ops  = round(obp + slg, 3)

    ev_avg = round(rng.uniform(84.0, 93.5) + (1.5 if is_power_bat else 0), 1)
    ev_max = round(ev_avg + rng.uniform(7.5, 11.5), 1)
    bat_speed = round(rng.uniform(66.5, 75.5) + (1.0 if is_power_bat else 0), 1)
    sprint = round(rng.uniform(25.5, 30.0) + (0.8 if is_speed_bat else 0), 1)
    biomech = rng.randint(64, 92)

    return {
        "avg": avg, "obp": obp, "slg": slg, "ops": ops,
        "exit_velo_avg": ev_avg, "exit_velo_max": ev_max,
        "bat_speed": bat_speed, "sprint_speed": sprint,
        "_biomech_score": biomech,
    }


# A curated pool of MLB comps to assign deterministically
MLB_COMP_POOL = [
    ("Mookie Betts", 0.81), ("Aaron Judge", 0.78), ("Juan Soto", 0.79),
    ("Mike Trout", 0.74), ("Freddie Freeman", 0.76), ("Corey Seager", 0.77),
    ("Manny Machado", 0.83), ("Ronald Acuña Jr.", 0.75), ("Trea Turner", 0.74),
    ("Pete Alonso", 0.74), ("J.T. Realmuto", 0.72), ("Marcus Semien", 0.69),
    ("Bo Bichette", 0.70), ("Corbin Carroll", 0.81), ("Austin Riley", 0.73),
    ("Rafael Devers", 0.77), ("Ozzie Albies", 0.71), ("Will Smith", 0.66),
    ("Gunnar Henderson", 0.75), ("Cody Bellinger", 0.72),
]


# --- MLB reference (real names, real MLBAM IDs, real Statcast numbers) ---
RAW_MLB: List[Dict[str, Any]] = [
    {"player_id": "mlb_judge",   "name": "Aaron Judge",     "mlbam_id": 592450, "position": "OF", "team": "NYY", "exit_velo_avg": 95.8, "exit_velo_max": 119.9, "bat_speed": 78.4, "sprint_speed": 27.4, "avg": 0.322, "obp": 0.458, "slg": 0.701},
    {"player_id": "mlb_trout",   "name": "Mike Trout",      "mlbam_id": 545361, "position": "OF", "team": "LAA", "exit_velo_avg": 93.5, "exit_velo_max": 116.2, "bat_speed": 75.8, "sprint_speed": 28.1, "avg": 0.285, "obp": 0.387, "slg": 0.572},
    {"player_id": "mlb_betts",   "name": "Mookie Betts",    "mlbam_id": 605141, "position": "SS", "team": "LAD", "exit_velo_avg": 90.4, "exit_velo_max": 110.1, "bat_speed": 72.7, "sprint_speed": 28.5, "avg": 0.304, "obp": 0.405, "slg": 0.488},
    {"player_id": "mlb_soto",    "name": "Juan Soto",       "mlbam_id": 665742, "position": "OF", "team": "NYM", "exit_velo_avg": 92.7, "exit_velo_max": 114.5, "bat_speed": 74.1, "sprint_speed": 27.0, "avg": 0.288, "obp": 0.419, "slg": 0.569},
    {"player_id": "mlb_freeman", "name": "Freddie Freeman", "mlbam_id": 518692, "position": "1B", "team": "LAD", "exit_velo_avg": 92.1, "exit_velo_max": 112.3, "bat_speed": 73.0, "sprint_speed": 26.5, "avg": 0.282, "obp": 0.378, "slg": 0.476},
]


# Percentile reference points (MLB-wide distributions, hand-curated)
MLB_DISTRIBUTIONS = {
    "exit_velo_max": [102, 104, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121],
    "bat_speed":     [65,  67,  69,  70,  71,  72,  73,  74,  75,  76,  77,  78,  79,  80],
    "sprint_speed":  [25,  25.5,26,  26.5,27,  27.2,27.5,27.8,28,  28.3,28.6,29,  29.3,29.6,30,  30.5],
}


def _percentile(value: float, distribution: List[float]) -> int:
    if not distribution:
        return 50
    below = sum(1 for d in distribution if d < value)
    return int(round(100 * below / len(distribution)))


def compute_percentiles(stats: Dict[str, float]) -> Dict[str, int]:
    p = {
        "exit_velo_max": _percentile(stats["exit_velo_max"], MLB_DISTRIBUTIONS["exit_velo_max"]),
        "bat_speed":     _percentile(stats["bat_speed"],     MLB_DISTRIBUTIONS["bat_speed"]),
        "sprint_speed":  _percentile(stats["sprint_speed"],  MLB_DISTRIBUTIONS["sprint_speed"]),
    }
    p["contact_pct"] = max(0, min(100, int((stats["avg"] - 0.22) / (0.42 - 0.22) * 100)))
    p["power"]       = max(0, min(100, int((stats["slg"] - 0.38) / (0.70 - 0.38) * 100)))
    gap = stats["obp"] - stats["avg"]
    p["discipline"]  = max(0, min(100, int((gap - 0.04) / (0.13 - 0.04) * 100)))
    return p


def build_player_documents() -> List[Dict[str, Any]]:
    players: List[Dict[str, Any]] = []
    for i, bio in enumerate(RAW_AMATEURS_BIO):
        (name, age, pos, school, region, h, w, bats, throws, lat, lng) = bio
        s = _stat_for_bio(i, bio)
        biomech_score = s.pop("_biomech_score")

        # Deterministic comp choice
        comp_name, comp_sim = MLB_COMP_POOL[i % len(MLB_COMP_POOL)]

        percentiles = compute_percentiles(s)
        fit_score = int(round(
            0.4 * percentiles["power"]
            + 0.3 * percentiles["contact_pct"]
            + 0.2 * percentiles["sprint_speed"]
            + 0.1 * biomech_score
        ))
        pid = f"college_{i+1:03d}"
        players.append({
            "player_id": pid,
            "name": name,
            "type": "college",
            "age": age,
            "position": pos,
            "school": school,
            "height_in": h,
            "weight_lb": w,
            "bats": bats,
            "throws": throws,
            "stats": s,
            "percentiles_vs_mlb": percentiles,
            "biomech_score": biomech_score,
            "mlb_comp": comp_name,
            "mlb_comp_similarity": comp_sim,
            "video_url": f"/data/videos/{pid}.mp4",
            "fit_score": fit_score,
            "region": region,
            "lat": lat,
            "lng": lng,
        })
    return players


def build_mlb_reference() -> List[Dict[str, Any]]:
    refs = []
    for raw in RAW_MLB:
        refs.append({
            "player_id": raw["player_id"],
            "name": raw["name"],
            "type": "mlb",
            "mlbam_id": raw["mlbam_id"],
            "position": raw["position"],
            "team": raw["team"],
            "stats": {
                "avg": raw["avg"],
                "obp": raw["obp"],
                "slg": raw["slg"],
                "ops": round(raw["obp"] + raw["slg"], 3),
                "exit_velo_avg": raw["exit_velo_avg"],
                "exit_velo_max": raw["exit_velo_max"],
                "bat_speed": raw["bat_speed"],
                "sprint_speed": raw["sprint_speed"],
            },
            "video_url": f"/data/videos/{raw['player_id']}.mp4",
        })
    return refs
