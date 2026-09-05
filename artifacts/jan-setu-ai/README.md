# JanSetu AI

JanSetu AI is a 24-hour hackathon MVP foundation for turning citizen requests into transparent development priorities for policymakers. The attached concept focuses on multilingual citizen feedback, AI-assisted classification, demand hotspots, and decision support using synthetic demo data.

This first slice intentionally focuses on a clean, runnable foundation:

- React + Vite frontend shell with citizen and policymaker routes
- FastAPI backend with health, request analysis preview, request creation, listing, and summary endpoints
- SQLite persistence with demo seed data
- Deterministic mock AI service that can be replaced later through the `AI_PROVIDER` setting
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

## Run the frontend

From the repository root:

```bash
pnpm --filter @workspace/jan-setu-ai run dev
```

The managed preview uses the correct port and base path automatically. For a plain local shell, Vite can be started with:

```bash
PORT=5173 BASE_PATH=/ pnpm --filter @workspace/jan-setu-ai run dev
```

## Run the backend

From `artifacts/jan-setu-ai`:

```bash
python3 -m pip install -r backend/requirements.txt
python3 -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

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

The AI layer is deterministic by design for this MVP. It detects English versus Devanagari Hindi, classifies common civic categories, extracts a simple location hint, and calculates a transparent score. A later iteration can add a hosted model behind the same service interface.

## Next build slice

The next feature pass should connect the frontend intake form to `/api/requests/preview` and `/api/requests/analyze`, add Leaflet and Recharts to the policymaker dashboard, and add the browser Speech Recognition adapter with a text fallback.