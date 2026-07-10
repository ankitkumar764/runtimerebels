# Digital Twin Autopilot 🚀

**Digital Twin Autopilot** is a personal AI clone that integrates with popular communication platforms (Telegram, Discord, Gmail) to automatically reply to messages on your behalf. The system mimics your voice texture, casual slang, catchphrases, and typing patterns by utilizing a hybrid orchestration of LangGraph routing, Temporal RAG memories, and dynamic styling dials.

Designed with a premium, corporate **BMW-inspired design system** (clean cream canvas background, corporate blue CTAs, sharp layout grids, and dark navy elevated displays), it provides a complete control center to monitor and audit your digital clone.

---

## 🛠️ Key Features

*   **Global Kill Switch & platform Lockouts**: A master autopilot override switch that instantly silences all replies on all platforms, disabling child configuration toggles immediately.
*   **Turing Test Arena**: A side-by-side comparison panel allowing you to type a prompt and stream the Clone's casual, slang-rich response (with character keypress simulation delay) next to ChatGPT's formal, verbose paragraphs.
*   **Human-in-the-Loop Override Queue**: Messages that the verifier flags as low-confidence (<60%) are intercepted, placed in a review queue (`approvals.json`), and presented as editable textcards for manual correction and approval.
*   **Live Activity Feed**: A scrollable dashboard feed displaying incoming queries, generated replies, fact-checked validation badges, and clipboard copying utilities.
*   **Temporal Memory decaying**: Searches Qdrant vectors and decays older history records exponentially to prioritize fresh contextual matches.

---

## 📁 Repository Structure

```text
digital-twin-autopilot/
│
├── backend/                         # FastAPI + Celery backend
│   ├── app/
│   │   ├── api/                     # Webhooks (Telegram, Gmail) & Dashboard REST APIs
│   │   ├── core/                    # LangGraph Router, RAG, Verifier & Approval Queue
│   │   ├── models/                  # Pydantic validation schemas
│   │   ├── services/                # Platform Clients (Telegram Bot API, Discord REST, Gmail API)
│   │   └── workers/                 # Celery async tasks & delay calculators
│   ├── data/                        # Identity Core, Local Configs, and Approvals DB
│   └── requirements.txt             # Python requirements
│
├── frontend/                        # React 18 + Vite Web Application
│   ├── src/
│   │   ├── components/              # Sidebar, Navbar, Toggles, and feeds widgets
│   │   ├── pages/                   # Dashboard Control Center, Turing Arena, Override Queue
│   │   ├── lib/                     # Fetch API client
│   │   └── index.css                # BMW corporate design style tokens
│
├── docker-compose.yml               # Dev stack orchestrator (Redis, Qdrant, Backend)
├── .env.example                     # Environment setup template
└── README.md                        # Project documentation
```

---

## ⚙️ Local Development Setup

### Prerequisites
*   Docker & Docker Compose
*   Node.js (v18+) & NPM

### Step 1: Set up Environment Variables
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Ensure you provide a valid **`GROQ_API_KEY`** (from console.groq.com) to allow AI generations.

### Step 2: Spin up backend services
Start the Redis broker, Qdrant database, and the FastAPI application containers:
```bash
docker compose up --build
```
This launches:
*   **FastAPI Backend Server**: `http://localhost:8000` (API status at `http://localhost:8000/health`)
*   **Qdrant Vector DB Console**: `http://localhost:6333/dashboard`
*   **Redis Cache Broker**: Local port `6379`

### Step 3: Run the Dashboard UI
Navigate to the `frontend/` directory, install packages, and start the Vite dev server:
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 🔌 API Endpoints Reference

### Dashboard REST APIs
*   `GET /api/stats` — Fetches aggregate auto-replies, avg delay, and queue depths.
*   `GET /api/activity` — Retrieves recent conversations logs history.
*   `GET /api/config` / `POST /api/config` — Reads and writes personality dials (Formality level, delay ranges).
*   `POST /api/platforms/{name}/toggle` — Enables or disables a channel (Telegram, Discord, Gmail).
*   `POST /api/compare` — Performs side-by-side matches (Clone prompt response vs standard LLM).

### Human Overrides
*   `GET /api/approvals` — Retrieves pending low-confidence override cards.
*   `POST /api/approvals/{id}/approve` — Sends the edited reply to the platform client.
*   `POST /api/approvals/{id}/reject` — Discards the reply from queue.