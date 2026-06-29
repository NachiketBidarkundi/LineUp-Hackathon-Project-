# LINEUP — Baseball Recruiting Platform · PRD

## Problem Statement (original)
A recruiting platform that combines Statcast-style stats with biomechanical swing analysis,
giving high school and college coaches MLB-grade scouting tools on amateur players.
D1 programs spend $200K+ a year on scouting tech. Everyone else flies blind. Lineup gives any
coach pro-level analytics — real metrics, biomechanical comparison to MLB swings, ranked
recruit lists, exportable scouting reports — for the price of an iPhone.

## Architecture
- React (CRA, react-router v7, recharts, lucide, shadcn/ui, sonner) + Tailwind dark theme
- FastAPI (Python) under `/api` prefix, motor (async Mongo), CORS
- MongoDB collections: `players`, `mlb_reference`, `shortlists`
- Live MLB Stats API via `MLB-StatsAPI` for 5 reference players (career career batting overlay)
- Mock biomech analyzer — deterministic results keyed by player_id/filename
- ReportLab + matplotlib for one-page PDF scouting reports

## User Personas
- Head coach at HS / D2 / D3 / JUCO — needs MLB-grade scouting without a $200K budget
- Recruiting coordinator — needs ranked shortlists + exportable PDF packets for ADs/booster club
- Player development coach — uses biomech lab to diagnose swing issues + prescribe drills

## Core Requirements (static)
- 20 amateur recruits across 6 regions and 6 positions
- 5 MLB reference players (Judge, Trout, Betts, Soto, Freeman) with live stats overlay
- Statcast-style percentiles vs MLB population (power, contact, speed, exit velo, bat speed, discipline)
- Biomechanical swing analyzer: score, MLB comp, 5 feature breakdown, diagnoses with cost+fix, strengths
- Ranked recruit search with filters (position, region, bats, min OPS, min Max EV)
- Player profile with radar chart + bento grid + shortlist toggle + PDF export
- Side-by-side compare with overlay radar + head-to-head winner highlighting
- Scouting board (persistent shortlist) with per-card and bulk PDF export
- One-page polished PDF scouting report with header banner, stats card, radar, biomech, MLB comp

## What's been implemented (2026-06-28)
- ✅ FastAPI backend with 12 endpoints, auto-seeded MongoDB
- ✅ Landing page (hero, stat strip, features, CTA)
- ✅ Recruit Search with filters + sortable table
- ✅ Player Profile (bento grid, radar, percentile bars, biomech diagnostics)
- ✅ Compare page (overlay radar + head-to-head)
- ✅ Scouting Board with shortlist persistence
- ✅ Biomech Lab (drag-drop upload + analysis results)
- ✅ MLB Reference page (live + cached badges)
- ✅ PDF scouting report (77KB, full layout: header, stats card, radar chart, biomech, fit)
- ✅ Performance Pro dark theme (Barlow Condensed + Outfit + JetBrains Mono)
- ✅ Tested end-to-end (testing_agent_v3 iteration_1.json — 100% pass)

## Backlog / Next phase
### P1
- Real MediaPipe pose extraction (replace mock biomech) — needs `mediapipe`, `opencv-python` and real swing videos
- Nearest-neighbor MLB comp from feature vectors (currently random from a curated pool)
- Map view of US showing recruit locations (lat/lng already in data)
- Coach user accounts (Emergent Google Auth) — multi-tenant shortlists
- Compare 2+ amateurs vs MLB benchmark (not just A vs B)

### P2
- AI-generated scouting blurbs (Claude Sonnet) per player
- Bulk CSV import of recruits
- Video clip storage (object storage integration)
- Email a scouting packet to boosters
- Notification when a shortlisted player hits a new exit velo PR
