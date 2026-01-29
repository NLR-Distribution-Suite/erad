"""Main FastAPI application for the ERAD REST API."""

from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from .models import DistributionModelInfo, HazardModelInfo
from .cache import refresh_models_from_cache, refresh_hazard_models_from_cache
from . import distribution_models, hazard_models, simulation, utility


# Initialize FastAPI app
app = FastAPI(
    title="ERAD Hazard Simulator API",
    description="API for running hazard simulations on distribution systems",
    version="1.0.0",
)


# ========== In-memory Storage ==========
# Shared storage dictionaries
uploaded_models: Dict[str, DistributionModelInfo] = {}
uploaded_hazard_models: Dict[str, HazardModelInfo] = {}


# ========== Initialize Module Storage References ==========
# Share the storage dictionaries with all modules
distribution_models.uploaded_models = uploaded_models
hazard_models.uploaded_hazard_models = uploaded_hazard_models
simulation.uploaded_models = uploaded_models
simulation.uploaded_hazard_models = uploaded_hazard_models
utility.uploaded_models = uploaded_models
utility.uploaded_hazard_models = uploaded_hazard_models


# ========== Startup Event ==========


@app.on_event("startup")
async def startup_event():
    """Load models from cache on startup."""
    logger.info("Starting ERAD API...")
    refresh_models_from_cache(uploaded_models)
    refresh_hazard_models_from_cache(uploaded_hazard_models)
    logger.info(
        f"API ready with {len(uploaded_models)} distribution models "
        f"and {len(uploaded_hazard_models)} hazard models"
    )


# ========== Register Routers ==========


app.include_router(utility.router)
app.include_router(distribution_models.router)
app.include_router(hazard_models.router)
app.include_router(simulation.router)


# ========== Error Handlers ==========


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler for uncaught exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred", "status_code": 500},
    )


# ========== Main ==========


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)  # noqa: B104
