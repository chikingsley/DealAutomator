from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.services.queue_service import QueueService
from app.models.message import MessageProcessing
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
queue_service = QueueService()

@router.post("/webhook/telegram")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle incoming Telegram messages"""
    try:
        data = await request.json()
        
        # Extract message data
        message = data.get("message", {})
        message_id = message.get("message_id")
        text = message.get("text", "")
        
        if not message_id or not text:
            raise HTTPException(status_code=400, detail="Invalid message format")
            
        # Create database record
        db_message = MessageProcessing(
            telegram_message_id=str(message_id),
            raw_text=text,
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(db_message)
        db.commit()
        
        # Add to processing queue
        await queue_service.enqueue_message({
            "telegram_message_id": str(message_id),
            "text": text,
            "db_id": db_message.id
        })
        
        return {"status": "success", "message": "Message queued for processing"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check database connection
        db.execute("SELECT 1")
        
        # Get queue stats
        queue_stats = await queue_service.get_queue_size()
        
        return {
            "status": "healthy",
            "queue_stats": queue_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Service unhealthy")
