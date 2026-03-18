# Jellycraft Roadmap — Source of Truth

## Purpose
This document is the canonical architectural and execution plan for Jellycraft.

It captures what we are building, what we are intentionally not building, and in what order we will deliver value.

---

## North Star
Build **Jellycraft Command Center**: an intelligence and automation control layer on top of Jellyfin.

Jellycraft does **not** replace Jellyfin playback/transcoding/server fundamentals. Jellycraft adds:
- library intelligence
- playback intelligence
- automation
- search and recommendations

---

## Target Architecture

### A) Core Services

1. **Jellyfin Server (System of Record)**
   Jellyfin remains source of truth for:
   - libraries
   - users
   - watch history
   - playback state
   - existing metadata
   - transcoding and playback compatibility
   - device/client interoperability

   Jellycraft should integrate via official API/OpenAPI, plugins, and webhooks.

2. **Jellycraft API (FastAPI)**
   Python backend for:
   - dashboard endpoints
   - quality scoring endpoints
   - recommendation endpoints
   - automation endpoints
   - webhook receivers
   - admin orchestration
   - search aggregation
   - collection generation

3. **Jellycraft Worker**
   Background jobs for:
   - library sync
   - duplicate detection
   - metadata scoring
   - subtitle/transcript jobs
   - poster/artwork audits
   - recommendation refresh
   - notifications
   - watch-next precomputation

   Use APScheduler/simple async jobs first. Move to Celery + Redis only when required.

4. **Jellycraft DB**
   - Start: SQLite
   - Upgrade to Postgres when needed for multi-user usage, heavier jobs, analytics, richer recommendations, or higher concurrent writes.

5. **Frontend (Next.js + React + TypeScript)**
   Chosen for fast UI iteration, straightforward session handling, component ecosystem, and clean dashboard/"Netflix shell" UX.

---

## Hybrid Stack Policy

### Keep from Jellyfin
- media scanning
- user/session foundation
- playback compatibility
- transcoding baseline
- official API/OpenAPI
- plugin + webhook integrations
- media-segment support (Intro/Outro/Recap/Preview/Commercial)

### Borrow from MediaCMS (as reference only)
- transcript pipeline ideas
- rich media processing patterns
- video portal UX patterns
- admin workflow patterns

### Borrow from Owncast
- simple event flow
- WebSocket live UI updates
- compact operations model

### Borrow later from Ant Media / Red5
- low-latency live path
- protocol expansion
- scalable live ingestion
- multi-protocol broadcast patterns

---

## Product Scope — Phase 1 Shape

Do **not** build a full Netflix clone.

Build **Jellycraft Command Center** with four pillars:
1. **Library Intelligence**
   - duplicates
   - filename quality issues
   - missing posters/backdrops
   - missing subtitles
   - low metadata confidence
   - resolution/bitrate quality flags
   - best-version picker
   - broken collections
   - unmatched episodes/movies

2. **Playback Intelligence**
   - continue watching hub
   - tonight's pick
   - smart collections by runtime/mood/genre/year
   - intro/outro-aware UX
   - precomputed watch-next
   - cross-device resume dashboard

3. **Automation**
   - new media webhook flows
   - metadata refresh
   - subtitle fetch jobs
   - quality re-score jobs
   - Discord/Home Assistant notifications
   - auto-tagging collections

4. **Search + Recommendations**
   - better-than-stock search
   - transcript-aware search (later)
   - content-based recommendations
   - user taste profile
   - family-safe / kid-safe filtering

---

## Repository Structure (Target)

```text
jellycraft/
├─ apps/
│  ├─ api/
│  │  ├─ main.py
│  │  ├─ config.py
│  │  ├─ deps.py
│  │  ├─ middleware/
│  │  ├─ routes/
│  │  └─ schemas/
│  ├─ worker/
│  │  ├─ main.py
│  │  ├─ scheduler.py
│  │  ├─ tasks/
│  │  └─ pipelines/
│  └─ web/
│     ├─ app/
│     ├─ components/
│     ├─ lib/
│     └─ styles/
├─ core/
│  ├─ domain/
│  ├─ services/
│  ├─ engines/
│  └─ policies/
├─ integrations/
├─ data/
├─ tests/
├─ scripts/
├─ docker/
├─ docs/
├─ .github/workflows/
├─ pyproject.toml
└─ README.md
```

---

## Core Service Responsibilities

### `core/services/jellyfin_client.py` (critical)
Anti-corruption layer between Jellycraft and Jellyfin.

Must own:
- auth token handling
- typed API calls
- retries
- pagination helpers
- response normalization
- error mapping
- rate limiting/backoff

No other service should depend on raw Jellyfin response shapes.

### `core/services/library_service.py`
Aggregates and serves:
- libraries
- recently added
- unwatched/in-progress
- per-user state
- metadata completeness
- duplicate groups

### `core/engines/metadata_score_engine.py`
Calculates 0–100 metadata quality score using factors like title/year/overview/artwork/genres/cast/subtitles/runtime/duplicate suspicion/path quality.

### `core/engines/smart_collection_engine.py`
Rule-driven smart collections (runtime, mood, genre, behavior patterns).

### `core/engines/recommendation_engine.py`
Start simple:
- library popularity
- watch-similarity
- genre overlap
- runtime preference
- decade preference
- rewatch behavior
- time-of-day preference

Evolve later toward matrix factorization/embedding/collaborative filtering when justified.

### `core/services/transcript_service.py`
Phase 3+ concern (Whisper/faster-whisper): caption generation and transcript indexing for quote/scene search.

### `core/services/notification_service.py`
Pushes to Discord/Slack/email/Home Assistant/local dashboard.

---

## Core Data Models
Define these first:
- `MediaItem`
- `UserProfile`
- `PlaybackProgress`
- `QualityScore`
- `DuplicateCluster`
- `RecommendationRow`
- `CollectionRule`

Model definitions should preserve normalized domain types and avoid leaking external payload schemas.

---

## API Surface (Initial)

### Health/System
- `GET /health`
- `GET /config`
- `GET /system/status`

### Auth
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

### Dashboard
- `GET /dashboard/home`
- `GET /dashboard/recently-added`
- `GET /dashboard/continue-watching`
- `GET /dashboard/tonights-pick`
- `GET /dashboard/library-health`

### Library
- `GET /library/items`
- `GET /library/items/{id}`
- `GET /library/duplicates`
- `GET /library/missing-metadata`
- `GET /library/quality-report`

### Collections
- `GET /collections`
- `POST /collections/generate`
- `POST /collections/refresh/{slug}`

### Recommendations
- `GET /recommendations/me`
- `GET /recommendations/explain/{media_id}`
- `POST /recommendations/rebuild`

### Playback
- `GET /playback/in-progress`
- `GET /playback/history`
- `POST /playback/pick-tonight`

### Automation
- `POST /automation/refresh-library`
- `POST /automation/refresh-metadata`
- `POST /automation/fetch-subtitles`
- `POST /automation/run-quality-scan`

### Webhooks
- `POST /webhooks/jellyfin`
- `POST /webhooks/test`

---

## Event Architecture
Use event-driven processing for mutable state.

### Core Events
- `media.added`
- `media.updated`
- `media.removed`
- `user.playback.started`
- `user.playback.progress`
- `user.playback.stopped`
- `user.playback.completed`
- `metadata.refreshed`
- `subtitle.added`
- `collection.refreshed`

### Event Consumers
- quality scan consumer
- recommendation refresh consumer
- notification consumer
- collection update consumer
- transcript queue consumer

---

## Implementation Principles

### Do
- build a robust Jellyfin wrapper
- normalize into internal domain models
- own the dashboard/rules/automation intelligence layer
- deliver useful outcomes each phase

### Do Not
- rewrite player first
- build custom transcoding stack early
- chase DRM early
- overbuild recommendations before curation basics
- split into many microservices on day one
- overengineer auth while Jellyfin already owns user/session reality

---

## Phase Plan

### Phase 1 — Command Center (MVP)
Build:
- Jellyfin auth bridge
- dashboard
- recently added
- continue watching
- duplicates
- missing metadata
- tonight's pick
- manual trigger buttons

Goal: immediate user value.

### Phase 2 — Library Quality Manager
Build:
- metadata scoring
- artwork/subtitle audit
- duplicate clustering
- quality reports
- auto-fix suggestions

Goal: cleaner/smarter library.

### Phase 3 — Recommendation Engine
Build:
- taste profile
- runtime preference
- genre similarity
- rewatch-aware suggestions
- explainable recommendation reasons

Goal: personalized value.

### Phase 4 — Automation Hub
Build:
- Jellyfin webhook receiver
- Discord/Home Assistant integrations
- event-triggered jobs
- scheduled collection rebuilds
- new-content notifications

Goal: active autonomous media system.

### Phase 5 — Advanced Experience
Build:
- transcript search
- intro/outro-aware features
- watch-party hooks
- live-stream module
- mobile-focused UX
- optional custom launcher/client shell

Goal: premium experience.

---

## First Sprint Files (Lean Start)

### Backend (10)
- `apps/api/main.py`
- `apps/api/config.py`
- `apps/api/routes/auth.py`
- `apps/api/routes/dashboard.py`
- `apps/api/routes/library.py`
- `core/services/jellyfin_client.py`
- `core/services/library_service.py`
- `core/engines/metadata_score_engine.py`
- `data/db.py`
- `data/models/media_cache.py`

### Frontend (8)
- `apps/web/app/page.tsx`
- `apps/web/app/dashboard/page.tsx`
- `apps/web/app/library/page.tsx`
- `apps/web/components/cards/MediaCard.tsx`
- `apps/web/components/cards/IssueCard.tsx`
- `apps/web/components/carousels/ContinueWatchingRow.tsx`
- `apps/web/lib/api-client.ts`
- `apps/web/lib/auth.ts`

### Worker (5)
- `apps/worker/main.py`
- `apps/worker/tasks/sync_library.py`
- `apps/worker/tasks/metadata_audit.py`
- `apps/worker/tasks/duplicate_scan.py`
- `apps/worker/tasks/recommendation_refresh.py`

---

## MVP Definition (Highest ROI)
The minimal product that is still truly useful:
- sign in with Jellyfin
- show recently added
- show continue watching
- show unwatched gems
- show duplicates
- show missing metadata
- show quality score per item
- button: refresh library
- button: refresh metadata
- button: build “best 90–120 minute unwatched” collection
- one recommendation card: “Tonight’s Pick”

---

## Explicit Cuts (Remove Now)
Cut these from initial scope:
- custom login system
- standalone JWT/session stack
- multi-user profile system (beyond Jellyfin identities)
- role-based access matrix
- refresh-token architecture
- OAuth/SSO expansion
- complex permission matrix

Rationale: Jellyfin already provides session and user identity reality for Phase 1.
