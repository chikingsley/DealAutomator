from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from app.core.config import LOGGING_CONFIG
from app.api.routes import router as api_router
from app.core.logging import setup_logging
from app.bot.client import bot  # Make sure this import matches your bot instance location

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Deal Automator",
    description="Affiliate Marketing Deal Processing System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def setup_webhook():
    """Configure Telegram webhook on startup"""
    try:
        # Render sets RENDER_EXTERNAL_HOSTNAME automatically
        RENDER_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
        if RENDER_HOSTNAME:
            WEBHOOK_URL = f"https://{RENDER_HOSTNAME}/api/webhook/telegram"  # Note: added https://
            await bot.set_webhook(WEBHOOK_URL)
            logger.info(f"Webhook set to {WEBHOOK_URL}")
        else:
            logger.warning("RENDER_EXTERNAL_HOSTNAME not found - webhook not set")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)