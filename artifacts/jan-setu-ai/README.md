# JanSetu AI

JanSetu AI is a 24-hour hackathon MVP foundation for turning citizen requests into transparent development priorities for policymakers. The attached concept focuses on multilingual citizen feedback, AI-assisted classification, demand hotspots, and decision support using synthetic demo data.

This first slice intentionally focuses on a clean, runnable foundation:

- React + Vite frontend shell with citizen and policymaker routes
- Separate citizen and government portals with demo role authentication
- FastAPI backend with health, request analysis preview, request creation, listing, and summary endpoints
- SQLite persistence with demo seed data, indexes, constraints, and WAL mode
- OpenAI-compatible LLM analysis through `LLM_API_URL`, with deterministic rules fallback
- Browser-ready environment examples

## Project layout

```text
jan-setu-ai/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   └── services/
│   ├── .env.example
│   └── requirements.txt
├── data/
│   ├── demo_requests.json
│   └── jan-setu-ai.db          # created on first backend start
├── src/                         # React + Vite frontend
├── .env.example
└── README.md
```

## Run locally

From the repository root, start the API and frontend in separate terminals:

```bash
pnpm --filter @workspace/jan-setu-ai run dev
```

The frontend is available at `http://localhost:5173` and proxies API calls to
`http://localhost:8000`.

Open `/` to choose a portal. Citizen demo access accepts any mobile number with
OTP `123456`. Government demo access is `gov@jansetu.demo` with password
`jansetu123`. This is prototype authentication for the hackathon demo, not
production identity verification.

Citizen requests are stored in the real SQLite database at
`artifacts/jan-setu-ai/data/jan-setu-ai.db`. The API creates and migrates the
`citizen_requests` table on startup and uses parameterized SQL for writes.

```bash
$env:PORT="5173"; $env:BASE_PATH="/"; pnpm --filter @workspace/jan-setu-ai run dev
```

## Run the backend

From `artifacts/jan-setu-ai`:

```bash
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

To enable an LLM, copy `backend/.env.example` to `backend/.env` and set
`LLM_API_KEY`. Any OpenAI-compatible endpoint can be used by changing
`LLM_API_URL` and `LLM_MODEL`. If no key is set, the local rules analyzer is used.

Useful checks:

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/requests
curl http://localhost:8000/api/requests/summary
```

Interactive API documentation is available at `http://localhost:8000/docs`.

## Demo API surface

- `GET /api/health` — backend and AI provider status
- `GET /api/requests` — seeded citizen requests ordered by priority
- `POST /api/requests/preview` — analyze text without saving it
- `POST /api/requests/analyze` — analyze and save a citizen request
- `GET /api/requests/summary` — dashboard-ready aggregate values

Each analysis exposes the detected language, an internal common-language translation, the system's understanding of the request, extracted location, one or more development categories, urgency, severity, confidence, and a transparent priority score. The policymaker dashboard reads these fields from the live SQLite-backed API and shows completed versus pending work.

The AI layer is deterministic by design for this MVP. It detects English versus Devanagari Hindi, classifies common civic categories, extracts a simple location hint, and calculates a transparent score. A later iteration can add a hosted model behind the same service interface.

## Next build slice

The remaining prototype limitation is that demographic, infrastructure and
investment context is represented by the current synthetic request feed rather
than a separate production data service.