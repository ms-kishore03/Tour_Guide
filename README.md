# AI Tour Guide 🌍✈️



## 📋 Overview

**AI Tour Guide** is a full-stack, AI-powered travel planning platform that assists users across the **entire travel lifecycle** — from destination discovery to itinerary planning, real-time assistance during trips, and expense tracking.

The system combines:
- **Streamlit-based frontend** for intuitive user interaction
- **Multi-agent LLM orchestration** for intelligent decision-making
- **Real-time external APIs** for live travel data
- **RAG (Retrieval-Augmented Generation)** for grounded, factual answers
- **MongoDB** for persistent, multi-session memory

The project is designed as a **modular, agent-driven system**, not a single chatbot — ensuring scalability, maintainability, and clear separation of concerns.

---

## ✨ Key Features

### 🔍 Destination Exploration
- Theme-based and activity-based place discovery
- Gemini and Llama-powered intelligent recommendations
- MongoDB caching to optimize performance and reduce LLM calls

### 🗓️ AI-Driven Trip Planning
- Conversational itinerary creation through natural language
- Multi-day itinerary editing and refinement
- Draft vs finalized plan separation for safer workflows
- Automated date/time normalization and sorting

### 🤖 Multi-Agent System (Cognix AI)
Each responsibility is handled by a **specialized agent**:
- **Itinerary Agent** – stores, updates, and finalizes travel plans
- **Attractions Agent** – curates top attractions using Geoapify data
- **Weather Agent** – transforms raw weather data into actionable travel advice
- **Hotel Agent** – filters and ranks accommodation options
- **RAG Agent** – answers food, dining, and local culture queries using Wikivoyage knowledge

A central **CognixAI orchestrator** performs:
- Intent detection and classification
- Dynamic tool selection and routing
- Response synthesis and generation
- Memory management and updates

### 📚 Retrieval-Augmented Generation (RAG)
- Wikivoyage travel data ingested and processed
- Embedded using `sentence-transformers` for semantic search
- Stored in ChromaDB for fast vector retrieval
- Context-aware routing to minimize unnecessary queries

### 🧳 Ongoing Trip Assistant
- Real-time weather insights for your destination
- Nearby attractions and points of interest
- Expense logging with automatic categorization
- To-do tracking per destination

### 💾 Persistent Memory
- MongoDB-backed user sessions for continuity
- Saved trips and itineraries across devices
- Ongoing trip state management
- Complete expense history and analytics

---

## 🏗️ Architecture

### System Flow Diagram

```mermaid
flowchart TD
    U["User (Browser)"] --> UI["Streamlit Web UI"]

    UI --> AR["Agent Router<br/>(CognixAI Brain)"]
    AR --> LLM["LLM Orchestrator<br/>(Groq/Gemini)"]

    LLM --> T1["Flight Search Tool"]
    LLM --> T2["Accommodation Tool"]
    LLM --> T3["Itinerary Tool"]
    LLM --> T4["Weather Tool"]
    LLM --> T5["Attractions Tool"]
    LLM --> T6["Knowledge Tool<br/>(RAG)"]

    T1 --> API1["SERP API<br/>(Google Flights)"]
    T2 --> API2["Booking.com API"]
    T4 --> API3["OpenWeather API"]
    T5 --> API4["Geoapify Places API"]

    T3 --> DB["MongoDB<br/>(Trips & Itineraries)"]
    UI --> DB

    T6 --> VDB["ChromaDB<br/>(Vector Store)"]

    style UI fill:#4A90E2,color:#fff
    style AR fill:#E94B3C,color:#fff
    style LLM fill:#50C878,color:#fff
    style DB fill:#F39C12,color:#fff
    style VDB fill:#9B59B6,color:#fff
```

### Component Breakdown

**Frontend Layer**
- Streamlit UI with multi-page navigation
- Session state management
- Real-time user interaction

**AI Orchestration Layer**
- CognixAI brain for intent detection
- Dynamic tool routing based on context
- Draft vs final itinerary lifecycle control

**Agent Layer (Specialized Tools)**
- Modular, single-responsibility agents
- Independent testing and maintenance
- Clear API contracts

**Data Layer**
- MongoDB for structured persistence
- ChromaDB for semantic search
- Caching layer for performance optimization

**External Integration Layer**
- OpenWeather for real-time weather data
- Geoapify for places and attractions
- SerpAPI for flight search
- Booking.com for accommodations

---

## 🛠️ Tech Stack

### Frontend
- **Streamlit** - Interactive web interface

### Backend / AI
- **Python 3.10+** - Core language
- **LangChain** - LLM orchestration framework
- **Groq** - Fast inference (Llama-3.1-8B)
- **Google Gemini** - Destination recommendations

### Databases
- **MongoDB** - Primary data persistence
- **ChromaDB** - Vector store for RAG

### External APIs
- **OpenWeather API** - Weather data
- **Geoapify Places API** - Attractions and POIs
- **SerpAPI** - Google Flights integration
- **Booking.com API** (via RapidAPI) - Hotel search

### Libraries
- `sentence-transformers` - Text embeddings
- `pymongo` - MongoDB driver
- `chromadb` - Vector database
- `python-dotenv` - Environment management

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- MongoDB (local installation or cloud URI)
- API Keys (see configuration below)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ms-kishore03/Tour_Guide.git
   cd Tour_Guide
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key
   GEMINI_API_KEY=your_gemini_api_key
   Accomodation_API_KEY=your_rapid_api_key
   MONGODB_URI=your_mongodb_connection_string
   OpenWeatherMap_API_Key=your_openweather_key
   GEOAPIFY_API_KEY=your_geoapify_key
   SERPAPI_API_KEY=your_serpapi_key
   ```

4. **Build the RAG vector index** (one-time setup)
   ```bash
   python cognix_ai/src/embeddings/build_index.py
   ```

5. **Run the application**
   ```bash
   streamlit run trip_planner/Login_Register.py
   ```

6. **Access the application**
   
   Open your browser and navigate to `http://localhost:8501`

---

## 📁 Project Structure

```
Tour_Guide/
├── trip_planner/           # Streamlit UI pages (legacy app)
│   ├── Login_Register.py   # Entry point
│   ├── Explore.py          # Destination discovery
│   ├── Planner.py          # Trip planning interface
│   └── Trip.py             # Ongoing trip management
├── cognix_ai/              # Agent brain and tools (shared by legacy app + new backend)
│   ├── brain/cognix.py     # CognixAI orchestrator (run() + run_stream())
│   ├── tools/              # Specialized agents
│   └── src/embeddings/     # RAG pipeline
├── API_Handlers/           # External API integrations (sync, used by legacy app)
├── Utilities/              # Database, auth, helpers (shared by legacy app + new backend)
├── vectorstore/            # ChromaDB storage
├── config/                 # Legacy app configuration
├── requirements.txt
├── Dockerfile               # Legacy Streamlit app image
├── backend/                 # FastAPI service (Phase 1/2 rewrite)
│   ├── app/{core,db,schemas,services,routers}/
│   ├── observability/        # Prometheus, Tempo, Grafana provisioning
│   ├── tests/{unit,integration}/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # React 18 + TypeScript SPA (Phase 1/2 rewrite)
│   └── src/{pages,components,api,store,hooks,types}/
├── .github/workflows/ci.yml  # pytest + vitest + build on push/PR
├── docker-compose.yml         # mongo + backend + prometheus + tempo + grafana
└── README.md
```

---

## 🐳 Deployment

The application is fully containerized using **Docker** and deployed on **Render**.

**Live Demo:** `https://tour-guide-ph2i.onrender.com`

---

## 🎯 Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Draft vs Final Itinerary** | LLM suggestions are never authoritative until normalized and explicitly saved by the user |
| **Agent Isolation** | Each tool has a single responsibility, enabling independent testing and maintenance |
| **RAG Only When Needed** | Context-aware routing prevents unnecessary vector queries and reduces latency |
| **MongoDB as Memory Layer** | Enables multi-session continuity and rich query capabilities |
| **UI-Safe Helpers** | Ensures consistent return types for Streamlit to prevent runtime errors |

---

## ⚠️ Current Limitations (legacy Streamlit app)

- ⏱️ Synchronous API calls (no async implementation yet)
- 📊 No centralized logging/observability framework
- 🧪 Minimal automated test coverage
- 🔐 Secrets managed via `.env` only (not production-ready secret management)
- 👥 No role-based access control (RBAC)

The items above are what motivated the React/FastAPI rewrite below. The Streamlit app
(`trip_planner/`) is kept running unmodified alongside it during the migration.

---

## 🆕 React + FastAPI Rewrite (Phase 1 & 2)

`backend/` and `frontend/` are a parallel, from-scratch rewrite of the same product on a modern
stack, built to demonstrate production patterns the Streamlit app couldn't: a typed REST API,
streaming agent responses, JWT auth, and real observability. The old app is untouched and still
works — nothing under `trip_planner/`, `cognix_ai/`, `API_Handlers/`, or `Utilities/` was deleted,
only a few functions there were made Streamlit-independent so the new backend could reuse them.

### Stack

- **Frontend**: React 18 + TypeScript, Vite, Mantine v7, React Router v7, Zustand, TanStack Query,
  Vitest + React Testing Library.
- **Backend**: FastAPI, Motor (async MongoDB driver), Pydantic v2 schemas on every route, JWT auth,
  pytest + pytest-asyncio.
- **Observability**: OpenTelemetry traces → Tempo, Prometheus metrics, a provisioned Grafana
  dashboard.
- **Local infra**: `docker-compose.yml` at the repo root — `mongo`, `backend`, `prometheus`,
  `tempo`, `grafana`.

### Why SSE, not WebSocket, for chat

Chat is one request → one streamed response per turn — no server-initiated pushes and no
client-to-server messages mid-stream, so there's no duplex requirement WebSocket would justify.
`POST /api/v1/chat/{place}/stream` returns `text/event-stream`: plain HTTP/1.1, reconnects
natively, and doesn't need sticky sessions across uvicorn workers the way WS would. Frames carry
`event: token|tool_call|final|error` plus a sequence id. Because `EventSource` can't send custom
headers, the frontend (`useChatStream`) uses `fetch` + a manual `ReadableStream` reader so it can
attach `Authorization: Bearer <token>`. Partial assistant text is upserted into MongoDB every ~40
characters, so a dropped connection can resume from `GET /chat/{place}/history` — that's the
backpressure/reconnect/partial-state story: the generator only produces as fast as the LLM
streams tokens, and state is durable enough to survive a disconnect mid-turn.

### Running the new stack locally

```bash
# backend + observability
docker compose up -d          # mongo, backend, prometheus, tempo, grafana
curl http://localhost:8000/api/v1/healthz
open http://localhost:3000    # Grafana, anonymous admin — dashboard: "Tour Guide — Backend Overview"
open http://localhost:9090    # Prometheus

# frontend (outside compose this phase)
cd frontend && npm install && npm run dev   # http://localhost:5173
```

`docker-compose.yml` maps the compose Mongo to host port `27018` (not `27017`) so it doesn't
collide with a locally-installed MongoDB the Streamlit app might already be using; the backend
talks to it over the compose network by service name (`mongo:27017`) regardless.

### Tests

```bash
cd backend && pytest          # 72 tests: unit + integration (httpx AsyncClient, mongomock-motor,
                               # respx-mocked external APIs, and a real Mongo instance where
                               # mongomock has known bugs)
cd frontend && npx vitest run # 16 tests: RTL component/page tests, mocked SSE stream
```

### Phase 2 (should-have) — done

- **Async external calls**: `weather_service`, `attractions_service` (`get_geo`), `hotel_service`,
  and `flight_service` now call OpenWeatherMap / Geoapify / Booking.com / SerpApi directly over
  `httpx.AsyncClient`, natively async — no more `run_in_threadpool`-wrapped sync `requests` calls
  on these hot paths. `API_Handlers/*.py` (the `requests`/`serpapi`-SDK versions) are untouched and
  still used by the Streamlit app and by the chat-tool path (already threadpool-wrapped as a whole
  turn there, so unaffected).
- **CI**: `.github/workflows/ci.yml` — `pytest` (with a Mongo service container) and
  `vitest run` + `tsc -b && vite build` on every push/PR to `main`.
- **Secure coding pass**:
  - Rate limiting via `slowapi` on `/auth/register` (5/min), `/auth/login` (10/min),
    `/auth/refresh` (20/min), `/chat/{place}` and `/chat/{place}/stream` (20/min each).
  - CORS allowlist already read from `settings.cors_origins` (never `*`).
  - Mongo filter audit: every query filter value is a typed path param or JWT-derived username,
    never a raw request-body dict, so there's no NoSQL-operator-injection surface.
  - `app/core/secrets.py` — a `SECRETS_PROVIDER` swap point (`aws` implemented via
    `boto3.client("secretsmanager")`, no-op by default) called before `Settings()` reads the
    environment, so `.env` can be replaced by a real secrets backend without touching call sites.

### Not built yet (Phase 3, deferred)

Docker Compose extended to include the frontend itself, and a k8s manifest story
(Deployment/Service/Ingress, ConfigMap/Secret).

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧Support

For support, suggestions or code related errors [raise an issue](https://github.com/ms-kishore03/Tour_Guide/issues).

---

<p align="center">Made with ❤️ for travelers worldwide</p>