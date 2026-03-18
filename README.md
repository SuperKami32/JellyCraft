# JellyCraft

JellyCraft is a **Command Center** for Jellyfin: it layers library intelligence, recommendations, automation, and operational visibility on top of an existing Jellyfin server.

## Documentation
- [Roadmap Source of Truth](docs/roadmap_source_of_truth.md)

## Current Repository Architecture

The codebase is currently organized into three runnable surfaces:

- **API (`apps/api`)**: FastAPI service with domain-focused routes for auth, dashboard, library, collections, recommendations, playback, automation, and webhooks.
- **Worker (`apps/worker`)**: scheduler and task runners for sync/audit/scan/recommendation refresh workflows.
- **Web (`apps/web`)**: Next.js app shell for dashboard/library UX.

Domain logic is centralized in `core/` (services + engines), with placeholder persistence and models in `data/`.

### Architecture Flow (Mermaid)

```mermaid
flowchart LR
    subgraph Clients
        WB[Web App\nNext.js / React]
        APIConsumer[External API Consumers\nCLI / integrations]
        JFClient[Jellyfin Clients\nTV / mobile / web]
    end

    subgraph JellyCraft
        APIGW[FastAPI Service\napps/api/main.py]

        subgraph Routes
            RAuth[/auth/*]
            RDash[/dashboard/*]
            RLib[/library/*]
            RCol[/collections/*]
            RRec[/recommendations/*]
            RPlay[/playback/*]
            RAuto[/automation/*]
            RHook[/webhooks/*]
            RSys[/health /config /system/status]
        end

        subgraph Domain_Core[Core Domain]
            LibSvc[LibraryService]
            JF[ JellyfinClient ]
            MSE[MetadataScoreEngine]
            RCE[RecommendationEngine]
            SCE[SmartCollectionEngine]
        end

        subgraph Worker
            Sched[Scheduler\nrun_scheduler()]
            TSync[sync_library]
            TMeta[metadata_audit]
            TDup[duplicate_scan]
            TRec[recommendation_refresh]
        end

        subgraph Data
            Cache[In-memory media cache\nMediaCacheItem list]
            DBCfg[DatabaseConfig\nSQLite URL placeholder]
        end
    end

    subgraph External
        Jellyfin[Jellyfin Server\nSystem of Record]
        Hooks[Webhook Producers]
    end

    WB --> APIGW
    APIConsumer --> APIGW

    APIGW --> RAuth
    APIGW --> RDash
    APIGW --> RLib
    APIGW --> RCol
    APIGW --> RRec
    APIGW --> RPlay
    APIGW --> RAuto
    APIGW --> RHook
    APIGW --> RSys

    RAuth --> JF
    RAuth --> Jellyfin
    RDash --> LibSvc
    RLib --> LibSvc
    RCol --> LibSvc
    RRec --> LibSvc
    RPlay --> LibSvc

    LibSvc --> Cache
    LibSvc --> MSE
    LibSvc --> RCE
    LibSvc --> SCE

    RHook --> Hooks
    RAuto -. queues / triggers .-> Sched

    Sched --> TSync
    Sched --> TMeta
    Sched --> TDup
    Sched --> TRec

    TSync --> Jellyfin
    TMeta --> Cache
    TDup --> Cache
    TRec --> Cache

    APIGW --> DBCfg
    JFClient --> Jellyfin
```

## Fully Inclusive Data Flow

The diagram below expands end-to-end data movement for all currently defined entry points and major internal transformations.

```mermaid
flowchart TD
    %% -----------------------------------------------------------------
    %% Entry points
    %% -----------------------------------------------------------------
    U1[User in Web UI]
    U2[Automation client / scripts]
    U3[Webhook senders]

    U1 --> WRoutes[Next.js routes\n/ /dashboard /library]
    WRoutes --> WebFetch[web/lib/api-client.ts\napiGet(path)]

    U2 --> HTTPAPI[HTTP calls to FastAPI]
    WebFetch --> HTTPAPI
    U3 --> HTTPAPI

    %% -----------------------------------------------------------------
    %% API dispatch
    %% -----------------------------------------------------------------
    HTTPAPI --> MainApp[apps/api/main.py\nFastAPI app + include_router]
    MainApp --> Health[System endpoints\n/health /config /system/status]
    MainApp --> AuthRoute[/auth/login /auth/logout /auth/me]
    MainApp --> DashRoute[/dashboard/*]
    MainApp --> LibraryRoute[/library/*]
    MainApp --> CollectionsRoute[/collections/*]
    MainApp --> RecRoute[/recommendations/*]
    MainApp --> PlaybackRoute[/playback/*]
    MainApp --> AutomationRoute[/automation/*]
    MainApp --> WebhookRoute[/webhooks/*]

    %% -----------------------------------------------------------------
    %% Config / dependencies
    %% -----------------------------------------------------------------
    MainApp --> Settings[get_settings()\napp/env/jellyfin URL]
    MainApp --> DBConfig[get_database_config()\nDatabaseConfig URL]
    AuthRoute --> Deps[get_jellyfin_client() dependency]
    Deps --> JFClient[JellyfinClient\nrequests.Session + Retry]

    %% -----------------------------------------------------------------
    %% External system integration
    %% -----------------------------------------------------------------
    JFClient --> JFAuth[/Users/AuthenticateByName]
    JFClient --> JFMe[/Users/Me]
    JFClient --> JFLogout[/Sessions/Logout]
    JFClient --> JFRecent[/Users/{id}/Items/Latest]
    JFClient --> JFViews[/Users/{id}/Views]
    JFClient --> JFSystem[/System/Info/Public]

    JFAuth --> Jellyfin[(Jellyfin Server)]
    JFMe --> Jellyfin
    JFLogout --> Jellyfin
    JFRecent --> Jellyfin
    JFViews --> Jellyfin
    JFSystem --> Jellyfin

    %% -----------------------------------------------------------------
    %% Library intelligence core
    %% -----------------------------------------------------------------
    DashRoute --> LibraryService[LibraryService]
    LibraryRoute --> LibraryService
    CollectionsRoute --> LibraryService
    RecRoute --> LibraryService
    PlaybackRoute --> LibraryService

    LibraryService --> MediaCache[(MediaCacheItem in-memory list)]
    LibraryService --> ScoreSignals[MetadataSignals derivation]
    ScoreSignals --> MetadataEngine[MetadataScoreEngine\nweighted score + penalties]
    LibraryService --> SmartCollections[SmartCollectionEngine\nrule filtering]
    LibraryService --> RecoEngine[RecommendationEngine\nheuristic ranking/explanations]

    MetadataEngine --> QualityScored[Items + quality_score]
    SmartCollections --> CollectionRows[Collection candidates]
    RecoEngine --> RecommendationRows[Personalized candidate list]

    QualityScored --> DashResp[Dashboard payloads\nrecent / continue / tonight / health]
    QualityScored --> LibraryResp[Library payloads\nitems / duplicates / missing metadata / quality report]
    CollectionRows --> CollectionResp[Collection payloads\nlist/generate]
    RecommendationRows --> RecResp[Recommendation payloads\n/me + /explain]
    QualityScored --> PlaybackResp[Playback payloads\nin-progress/history/pick-tonight]

    %% -----------------------------------------------------------------
    %% Automation + worker execution
    %% -----------------------------------------------------------------
    AutomationRoute --> QueueAck[Queued acknowledgement payload]
    QueueAck -. logical handoff .-> Scheduler[run_scheduler()]

    Scheduler --> TaskSync[run_sync_library()]
    Scheduler --> TaskMeta[run_metadata_audit()]
    Scheduler --> TaskDup[run_duplicate_scan()]
    Scheduler --> TaskReco[run_recommendation_refresh()]

    TaskSync --> WorkerOut1[task=status ok]
    TaskMeta --> WorkerOut2[task=status ok]
    TaskDup --> WorkerOut3[task=status ok]
    TaskReco --> WorkerOut4[task=status ok]

    %% -----------------------------------------------------------------
    %% Webhooks
    %% -----------------------------------------------------------------
    WebhookRoute --> HookParse[event.type extraction]
    HookParse --> HookResp[accepted / test echo response]

    %% -----------------------------------------------------------------
    %% Responses
    %% -----------------------------------------------------------------
    Health --> APIJSON[(JSON responses)]
    AuthRoute --> APIJSON
    DashResp --> APIJSON
    LibraryResp --> APIJSON
    CollectionResp --> APIJSON
    RecResp --> APIJSON
    PlaybackResp --> APIJSON
    QueueAck --> APIJSON
    HookResp --> APIJSON

    APIJSON --> WebFetch
    APIJSON --> HTTPAPI
    WebFetch --> U1
```

## API Surface Snapshot

### System
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
- `GET /library/items/{item_id}`
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

## Development Notes

- Current data persistence is represented by `DatabaseConfig` (SQLite URL placeholder) and in-memory domain cache fixtures.
- Worker scheduling currently runs as a single-pass local development sequence.
- The architecture and flows above intentionally reflect the **current implementation footprint**, while the roadmap describes the longer-term target shape.
