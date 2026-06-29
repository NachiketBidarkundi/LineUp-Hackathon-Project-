# Biomech Integration — Real MediaPipe Swing Analyzer

Replaces the mock swing analyzer with the real Lane C MediaPipe pipeline
(pose → 5 kinematic features → z-score vs elite profile → diagnoses + nearest-neighbor MLB comp).

## What changed
- **`backend/swing/`** (new package): the real pipeline.
  - `pose_extract.py` — MediaPipe Tasks `PoseLandmarker` → `(frames, 33, 3)` world landmarks.
  - `features.py` — auto-crops to a single swing, computes the 5 features.
  - `analyzer.py` — `analyze_swing_real(video_path)` → `biomech_result` contract.
  - `mlb_comp.py` — nearest-neighbor MLB comp (real similarity %).
  - `data/` — `elite_profile.json`, `rules.json`, `mlb_reference_profiles.json`.
  - `models/pose_landmarker_full.task` — the pose model (9 MB).
- **`backend/biomech.py`** — `analyze_swing(video_path, seed_key)` now runs the real
  pipeline when a video is given, and **falls back to the original mock** on any failure
  (CV libs missing, no swing detected, decode error). The mock lives on as `_mock_analyze`.
- **`backend/server.py`** — `/api/biomech/analyze` saves the upload to a temp file and runs
  the (blocking) pipeline in a threadpool, then deletes the temp file.
- **`backend/build_profiles.py`** — offline: regenerates `elite_profile.json` +
  `mlb_reference_profiles.json` from labeled clips. Ship the JSON, not the videos.
- **`frontend/src/pages/Upload.js`** — corrected the loading log copy (was "240 fps").
  No data-shape changes — the UI already matched the `biomech_result` contract.

## MLB comp reference labels
`mlb_reference_profiles.json` was built from 5 labeled slow-mo clips:
Justin Upton, Andrew McCutchen, Miguel Cabrera, Javier Báez, Troy Tulowitzki.
These aren't the seed MLB-reference players (Judge/Trout/Betts/Soto/Freeman), so the
comp shows the name + real similarity but doesn't deep-link to a Compare profile. To
enable linking, add these players to `seed_data.py`'s MLB reference set.

## Run locally
```bash
# 1. Mongo (any local instance)
#    e.g. docker run -d -p 27017:27017 mongo:7   (or brew services start mongodb-community)

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-cv.txt        # enables REAL analysis; skip to stay on mock
uvicorn server:app --reload --port 8000    # reads backend/.env

# 3. Frontend (new shell)
cd frontend
yarn install        # or npm install
yarn start          # reads frontend/.env -> REACT_APP_BACKEND_URL=http://localhost:8000
```
Open the app → **Swing Analyzer** → upload a clip. With `requirements-cv.txt` installed
you get real analysis; without it (or on a swing it can't read) it returns the mock.

> First request is slow: MediaPipe loads the model and extracts pose per frame
> (~10–15 s on a ~30 s clip). Subsequent requests reuse the loaded libs.

## Regenerate profiles (only if you change the elite/reference clips)
```bash
cd backend
python build_profiles.py [VIDEOS_DIR]   # default: ~/biomech-swing/data/videos
```

## Deploy notes
- **Frontend → Vercel:** fine. Set `REACT_APP_BACKEND_URL` to the deployed backend URL.
- **Backend → NOT Vercel.** MediaPipe + OpenCV + the model exceed serverless limits and
  the per-frame extraction exceeds function timeouts. Host the backend on a container
  platform (Render / Railway / Fly.io) or keep Emergent. Wherever MediaPipe can't be
  installed, omit `requirements-cv.txt` and the analyzer auto-falls back to the mock.
