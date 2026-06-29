"""MLB Stats API wrapper. Tries live fetch, falls back gracefully."""
import logging
from typing import Optional, Dict, Any

log = logging.getLogger(__name__)

try:
    import statsapi  # MLB-StatsAPI
    HAS_STATSAPI = True
except ImportError:
    HAS_STATSAPI = False


def fetch_live_career(mlbam_id: int) -> Optional[Dict[str, Any]]:
    """Try to pull career hitting stats from MLB Stats API. Returns None on failure."""
    if not HAS_STATSAPI:
        return None
    try:
        data = statsapi.player_stat_data(mlbam_id, group="hitting", type="career")
        # Find the most recent hitting season-aggregated career line
        for s in data.get("stats", []):
            if s.get("group") == "hitting":
                stats = s.get("stats", {})
                return {
                    "avg": float(stats.get("avg", 0) or 0),
                    "obp": float(stats.get("obp", 0) or 0),
                    "slg": float(stats.get("slg", 0) or 0),
                    "ops": float(stats.get("ops", 0) or 0),
                    "hr": int(stats.get("homeRuns", 0) or 0),
                    "rbi": int(stats.get("rbi", 0) or 0),
                }
    except Exception as e:
        log.warning(f"MLB Stats API fetch failed for {mlbam_id}: {e}")
    return None


def enrich_mlb_player(player: Dict[str, Any]) -> Dict[str, Any]:
    """Merge live stats into player dict if available."""
    live = fetch_live_career(player.get("mlbam_id"))
    if live:
        # Overlay live AVG/OBP/SLG; keep Statcast-derived fields (exit velo, bat speed) since API doesn't expose them
        player["stats"]["avg"] = round(live["avg"], 3)
        player["stats"]["obp"] = round(live["obp"], 3)
        player["stats"]["slg"] = round(live["slg"], 3)
        player["stats"]["ops"] = round(live["ops"], 3)
        player["live_stats_loaded"] = True
    else:
        player["live_stats_loaded"] = False
    return player
