import asyncio
import logging
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.services.queue_service import QueueService
from app.services.claude_service import ClaudeService
from app.services.notion_service import NotionService
from app.models.message import MessageProcessing, ParsedDeal
from datetime import datetime
import signal

logger = logging.getLogger(__name__)

class DealWorker:
    def __init__(self):
        self.queue_service = QueueService()
        self.claude_service = ClaudeService()
        self.notion_service = NotionService()
        self.should_exit = False
        
    async def shutdown(self, sig, loop):
        print(f"\nReceived exit signal {sig.name}...")
        self.should_exit = True
        
    async def process_message(self, message_data: dict, db: Session):
        """Process a single message"""
        try:
            # Update message status
            message = db.query(MessageProcessing).filter_by(id=message_data['db_id']).first()
            if not message:
                logger.error(f"Message not found in database: {message_data['db_id']}")
                return False
                
            message.status = "processing"
            message.attempts += 1
            db.commit()
            
            # Parse deal using Claude
            parsed_data = await self.claude_service.parse_deal(message_data['text'])
            if not parsed_data:
                raise Exception("Failed to parse deal data")
                
            # Create Notion page
            notion_url = await self.notion_service.create_deal_page({
                **parsed_data,
                "raw_text": message_data['text']
            })
            
            if not notion_url:
                raise Exception("Failed to create Notion page")
                
            # Save parsed deal to database
            deal = ParsedDeal(
                message_id=message.id,
                **parsed_data,
                notion_url=notion_url
            )
            db.add(deal)
            
            # Update message status
            message.status = "completed"
            message.processed_at = datetime.utcnow()
            db.commit()
            
            # Mark as completed in queue
            await self.queue_service.mark_completed(message_data['telegram_message_id'])
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            
            if message:
                message.status = "failed"
                message.error_message = str(e)
                db.commit()
                
            # Move to dead letter queue if max retries reached
            if message and message.attempts >= 3:
                await self.queue_service.move_to_dead_letter(message_data, str(e))
                
            return False

    async def run(self):
        """Main worker loop"""
        logger.info("Starting deal worker...")
        
        # Setup signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(s, loop))
            )
            
        # Main worker loop
        while not self.should_exit:
            try:
                # Get message from queue
                message = await self.queue_service.dequeue_message()
                if not message:
                    await asyncio.sleep(1)
                    continue
                    
                # Process message
                db = SessionLocal()
                try:
                    await self.process_message(message, db)
                finally:
                    db.close()
                    
            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
                
        print("Shutdown complete.")

if __name__ == "__main__":
    worker = DealWorker()
    asyncio.run(worker.run())
