"""Lineup — Baseball Recruiting Platform Backend."""
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import Response
from fastapi.concurrency import run_in_threadpool
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import tempfile
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

from seed_data import build_player_documents, build_mlb_reference
from mlb_api import enrich_mlb_player
from biomech import analyze_swing
from report import generate_report

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

PRODUCT_NAME = "LINEUP"

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="Lineup API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger("lineup")


@app.on_event("startup")
async def seed_on_startup():
    existing = await db.players.count_documents({})
    if existing == 0:
        amateurs = build_player_documents()
        await db.players.insert_many(amateurs)
        log.info(f"Seeded {len(amateurs)} amateur players")
    refs = build_mlb_reference()
    for r in refs:
        try:
            enrich_mlb_player(r)
        except Exception as e:
            log.warning(f"MLB enrich failed for {r['name']}: {e}")
    await db.mlb_reference.delete_many({})
    await db.mlb_reference.insert_many(refs)
    log.info(f"Seeded {len(refs)} MLB reference players")

    if not await db.shortlists.find_one({"owner": "default"}):
        await db.shortlists.insert_one({"owner": "default", "player_ids": [], "updated_at": datetime.now(timezone.utc).isoformat()})


@api_router.get("/")
async def root():
    return {"product": PRODUCT_NAME, "status": "ok"}


@api_router.get("/players")
async def list_players(
    position: Optional[str] = None,
    region: Optional[str] = None,
    min_ops: Optional[float] = None,
    min_exit_velo: Optional[float] = None,
    bats: Optional[str] = None,
    sort_by: str = Query("fit_score", regex="^(fit_score|name|biomech_score|stats.ops|stats.exit_velo_max|stats.avg)$"),
):
    q: dict = {}
    if position and position != "ALL":
        q["position"] = position
    if region and region != "ALL":
        q["region"] = region
    if bats and bats != "ALL":
        q["bats"] = bats
    if min_ops is not None:
        q["stats.ops"] = {"$gte": min_ops}
    if min_exit_velo is not None:
        q.setdefault("stats.exit_velo_max", {})
        q["stats.exit_velo_max"]["$gte"] = min_exit_velo

    cursor = db.players.find(q, {"_id": 0}).sort(sort_by, -1 if sort_by != "name" else 1)
    docs = await cursor.to_list(500)
    return {"players": docs, "count": len(docs)}


@api_router.get("/players/{player_id}")
async def get_player(player_id: str):
    doc = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Player not found")
    return doc


@api_router.get("/mlb-reference")
async def list_mlb_reference():
    docs = await db.mlb_reference.find({}, {"_id": 0}).to_list(50)
    return {"mlb_reference": docs}


@api_router.get("/mlb-reference/{player_id}")
async def get_mlb_reference(player_id: str):
    doc = await db.mlb_reference.find_one({"player_id": player_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "MLB player not found")
    return doc


async def _get_shortlist_doc():
    doc = await db.shortlists.find_one({"owner": "default"})
    if not doc:
        doc = {"owner": "default", "player_ids": []}
        await db.shortlists.insert_one(doc)
    return doc


@api_router.get("/shortlist")
async def get_shortlist():
    doc = await _get_shortlist_doc()
    ids = doc.get("player_ids", [])
    players = await db.players.find({"player_id": {"$in": ids}}, {"_id": 0}).to_list(100)
    by_id = {p["player_id"]: p for p in players}
    ordered = [by_id[i] for i in ids if i in by_id]
    return {"shortlist": ids, "players": ordered}


@api_router.post("/shortlist/{player_id}")
async def add_to_shortlist(player_id: str):
    p = await db.players.find_one({"player_id": player_id})
    if not p:
        raise HTTPException(404, "Player not found")
    await db.shortlists.update_one(
        {"owner": "default"},
        {"$addToSet": {"player_ids": player_id},
         "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return await get_shortlist()


@api_router.delete("/shortlist/{player_id}")
async def remove_from_shortlist(player_id: str):
    await db.shortlists.update_one(
        {"owner": "default"},
        {"$pull": {"player_ids": player_id},
         "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    return await get_shortlist()


@api_router.post("/biomech/analyze")
async def biomech_analyze(
    player_id: Optional[str] = Query(None),
    file: Optional[UploadFile] = File(None),
):
    seed_key = player_id or (file.filename if file else "default")
    video_path = None
    tmp_path = None
    if file:
        data = await file.read()
        suffix = Path(file.filename or "upload.mp4").suffix or ".mp4"
        fd, tmp_path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        video_path = tmp_path

    try:
        # Pose extraction is blocking CPU work — keep it off the event loop.
        result = await run_in_threadpool(analyze_swing, video_path, seed_key)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    if player_id:
        await db.players.update_one(
            {"player_id": player_id},
            {"$set": {
                "biomech_result": result,
                "biomech_score": result["score"],
                "mlb_comp": result["mlb_comp"],
                "mlb_comp_similarity": result["similarity"],
            }},
        )
    return result


@api_router.get("/players/{player_id}/report")
async def player_report(player_id: str):
    doc = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Player not found")
    pdf_bytes = generate_report(doc, product_name=PRODUCT_NAME)
    safe_name = doc["name"].replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{PRODUCT_NAME}_{safe_name}_Scouting_Report.pdf"'},
    )


@api_router.get("/stats/summary")
async def stats_summary():
    total = await db.players.count_documents({})
    regions = await db.players.distinct("region")
    positions = await db.players.distinct("position")
    summary = await db.players.aggregate([
        {"$group": {"_id": None,
                    "avg_biomech": {"$avg": "$biomech_score"},
                    "max_velo": {"$max": "$stats.exit_velo_max"},
                    "avg_fit": {"$avg": "$fit_score"}}}
    ]).to_list(1)
    s = summary[0] if summary else {}
    return {
        "total_players": total,
        "regions": sorted(regions),
        "positions": sorted(positions),
        "avg_biomech": round(s.get("avg_biomech", 0), 1),
        "max_exit_velo": round(s.get("max_velo", 0), 1),
        "avg_fit_score": round(s.get("avg_fit", 0), 1),
    }


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown():
    client.close()
