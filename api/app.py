"""FastAPI application for I3-IoT-Edge-Cloud-Orchestrator.

Provides REST endpoints exposing current simulation state to the React dashboard.
"""

from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.state import simulation_state

app = FastAPI(
    title="I3 Predictive IoT-Edge-Cloud Resource Orchestration API",
    version="1.0.0",
    description="REST API providing real simulation state and orchestration decisions.",
)

# CORS configuration suitable for local React development server (e.g., Vite/CRA)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/state", response_model=Dict[str, Any])
def get_state() -> Dict[str, Any]:
    """Return the current consistent snapshot of the simulation state."""
    return simulation_state.get_snapshot()


@app.post("/api/simulation/step", response_model=Dict[str, Any])
def simulation_step() -> Dict[str, Any]:
    """Perform one simulation cycle and return the updated state snapshot."""
    return simulation_state.step()


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)
