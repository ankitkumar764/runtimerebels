import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("digital-twin-autopilot")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # App startup logic
    logger.info("Starting Digital Twin Autopilot Backend...")
    yield
    # App shutdown logic
    logger.info("Shutting down Digital Twin Autopilot Backend...")


app = FastAPI(
    title="Digital Twin Autopilot API",
    version="1.0-dev",
    lifespan=lifespan,
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include webhook routers
from app.api.webhooks.telegram import router as telegram_router
app.include_router(telegram_router, prefix="/webhook")


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "1.0-dev",
        "config": {
            "formality_level": settings.FORMALITY_LEVEL,
            "reply_delay_range": f"{settings.REPLY_DELAY_MIN}s - {settings.REPLY_DELAY_MAX}s",
        },
    }
