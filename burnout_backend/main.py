from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from burnout_backend.app.routes.dashboard_routes import router as dashboard_router


app = FastAPI(
    title="Burnout Prevention Dashboard API",
    description=(
        "A beginner-friendly FastAPI backend that estimates burnout risk "
        "based on daily habit patterns."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)


@app.get("/")
def read_root() -> dict:
    return {
        "message": "Burnout Prevention Dashboard API is running.",
        "docs": "/docs",
    }
