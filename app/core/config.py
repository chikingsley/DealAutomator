import os
from pydantic import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    # API Keys
    TELEGRAM_BOT_TOKEN: str
    ANTHROPIC_API_KEY: str
    NOTION_API_KEY: str
    NOTION_DATABASE_ID: str
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Application
    ENVIRONMENT: str
    LOG_LEVEL: str
    MAX_RETRIES: int
    WEBHOOK_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()

RATE_LIMITS = {
    'claude': {
        'requests_per_minute': 50,
        'retry_after': 60
    },
    'notion': {
        'requests_per_second': 3,
        'retry_after': 30
    },
    'telegram': {
        'messages_per_second': 30,
        'retry_after': 15
    }
}

SOURCE_MAPPING = {
    'FB': ['facebook', 'fb', 'Facebook'],
    'GG': ['google', 'Google', 'gg'],
    'NativeAds': ['native', 'nativeads', 'native-ads'],
    'Bing': ['bing', 'microsoft'],
    'SEO': ['seo', 'organic'],
    'MSN': ['msn', 'microsoft news'],
}

LOGGING_CONFIG = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'deals.log',
            'maxBytes': 5242880,  # 5MB
            'backupCount': 3,
            'formatter': 'detailed',
            'level': 'DEBUG'
        }
    },
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d %(message)s'
        }
    }
}
