from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import initialize_database
from .routes.health import router as health_router
from .routes.requests import router as requests_router
from .routes.government import router as government_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Foundation API for the JanSetu AI hackathon MVP.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for api_prefix in ("/api", "/jan-setu-api/api"):
    app.include_router(health_router, prefix=api_prefix)
    app.include_router(requests_router, prefix=api_prefix)
    app.include_router(government_router, prefix=api_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {"name": settings.app_name, "status": "ready"}