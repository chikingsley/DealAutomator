import redis
import json
import logging
from typing import Optional, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)

class QueueService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
        self.queue_key = "deal_processing_queue"
        self.processing_set = "processing_messages"
        self.dead_letter_queue = "dead_letter_queue"

    async def enqueue_message(self, message_data: Dict) -> bool:
        """Add a message to the processing queue"""
        try:
            self.redis.lpush(self.queue_key, json.dumps(message_data))
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue message: {str(e)}")
            return False

    async def dequeue_message(self) -> Optional[Dict]:
        """Get next message from queue"""
        try:
            message = self.redis.rpop(self.queue_key)
            if message:
                message_data = json.loads(message)
                # Mark as processing
                self.redis.sadd(self.processing_set, message_data['telegram_message_id'])
                return message_data
            return None
        except Exception as e:
            logger.error(f"Failed to dequeue message: {str(e)}")
            return None

    async def mark_completed(self, telegram_message_id: str) -> bool:
        """Mark message as completed"""
        try:
            self.redis.srem(self.processing_set, telegram_message_id)
            return True
        except Exception as e:
            logger.error(f"Failed to mark message as completed: {str(e)}")
            return False

    async def move_to_dead_letter(self, message_data: Dict, error: str) -> bool:
        """Move failed message to dead letter queue"""
        try:
            message_data['error'] = str(error)
            self.redis.lpush(self.dead_letter_queue, json.dumps(message_data))
            self.redis.srem(self.processing_set, message_data['telegram_message_id'])
            return True
        except Exception as e:
            logger.error(f"Failed to move message to dead letter queue: {str(e)}")
            return False

    async def get_queue_size(self) -> Dict[str, int]:
        """Get current queue sizes"""
        try:
            return {
                'main_queue': self.redis.llen(self.queue_key),
                'processing': self.redis.scard(self.processing_set),
                'dead_letter': self.redis.llen(self.dead_letter_queue)
            }
        except Exception as e:
            logger.error(f"Failed to get queue sizes: {str(e)}")
            return {'error': str(e)}
