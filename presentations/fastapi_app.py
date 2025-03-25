from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Path, Response, status
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from presentations.routers.event_router import event_router
from presentations.routers.coworking_router import coworking_router
from services.mock_data_service import MockDataService

# Lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle handler.
    Used to initialize data at startup and clean up resources at shutdown.
    """
    # Initialize mock data for testing
    mock_data_service = MockDataService()
    await mock_data_service.initialize_mock_data()

    yield  # Return control to the application

    logger.info("Application shutdown: cleaning up...")  # Shutdown actions


# Create FastAPI application with lifespan
app = FastAPI(
    title="Event Management and Coworking System",
    description="API for event management and coworking space booking",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(event_router)
app.include_router(coworking_router)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "Event Management and Coworking API",
        "version": "1.0.0",
        "documentation": "/docs",
    }
