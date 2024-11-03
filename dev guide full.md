# DealAutomator Development Guide

## Project Overview
DealAutomator is a full-stack system for processing affiliate marketing deals using Telegram as the interface, with automated parsing and storage in Notion.

## Tech Stack
- FastAPI web application
- Redis for queue management
- PostgreSQL for data storage
- Claude API for deal parsing
- Notion API for deal storage
- Telegram API for user interface

## Quick Start

### 1. One-Click Setup

```bash
# Clone and setup
git clone <repo>
cd DealAutomator
./setup.sh  # Creates .env from template

# Start services
make up

# Monitor logs
make logs

# Run tests
make test

# Stop everything
make down
```

### 2. Environment Setup
Copy `env.example` to `.env` and fill in:

```bash
# API Keys
TELEGRAM_BOT_TOKEN=your_token
ANTHROPIC_API_KEY=your_claude_key
NOTION_API_KEY=your_notion_key
NOTION_DATABASE_ID=your_database_id

# Database
DATABASE_URL=postgresql://dealuser:dealpass@localhost:5432/deals_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
MAX_RETRIES=3
WEBHOOK_SECRET=your_secret
```

## Core Components

### 1. Database Schema

#### Message Processing Table
```sql
CREATE TABLE message_processing (
    id SERIAL PRIMARY KEY,
    telegram_message_id TEXT,
    raw_text TEXT,
    status VARCHAR(20),
    attempts INT DEFAULT 0,
    partner_name TEXT,
    processed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Parsed Deals Table
```sql
CREATE TABLE parsed_deals (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES message_processing(id),
    geo VARCHAR(2),
    language_code VARCHAR(5),
    is_native BOOLEAN,
    pricing_model VARCHAR(3),
    cpa_amount DECIMAL,
    crg_percentage DECIMAL,
    cpl_amount DECIMAL,
    deduction_limit TEXT,
    conversion_rate TEXT,
    conversion_current TEXT,
    conversion_details TEXT,
    sources TEXT[],
    funnels TEXT[],
    notion_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Docker Configuration

#### Development Setup
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - .:/app
    depends_on:
      - postgres
      - redis
    command: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

  worker:
    build: .
    env_file:
      - .env
    depends_on:
      - app
      - redis
      - postgres
    command: python -m app.worker

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=dealuser
      - POSTGRES_PASSWORD=dealpass
      - POSTGRES_DB=deals_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 3. Natural Language Processing

#### Query Handler
```python
QUERY_PATTERNS = {
    "show_deals": [
        "what are the deals for today",
        "show me today's deals",
        "current deals",
        "active deals"
    ],
    "verify_mapping": [
        "check column mapping",
        "verify database structure",
        "show me where data goes"
    ]
}

class DealBot:
    async def handle_message(self, message: str, chat_id: int):
        if looks_like_deal(message):
            return await self.handle_deal_message(message, chat_id)
            
        query_type = identify_query_type(message)
        if query_type:
            if query_type == "show_deals":
                return await self.show_active_deals(chat_id)
            elif query_type == "verify_mapping":
                return await self.verify_database_mapping(chat_id)
                
        return await self.handle_conversation(message, chat_id)
```

### 4. Notion Integration

#### Database Schema Verification
```python
async def verify_notion_schema(notion_client, database_id):
    expected_columns = {
        "Geo": ["select", "rich_text"],
        "Language": ["select"],
        "Is_Native": ["checkbox"],
        "Partner": ["select"],
        "Sources": ["multi_select"],
        "Price_Model": ["select"],
        "CPA_Amount": ["number"],
        "CRG_Percentage": ["number"],
        "CPL_Amount": ["number"],
        "Deduction_Limit": ["rich_text"],
        "Conversion_Rate": ["rich_text"],
        "Conversion_Current": ["rich_text"],
        "Conversion_Details": ["rich_text"],
        "Funnels": ["multi_select"],
        "Status": ["select"],
        "Created_At": ["date"],
        "Updated_At": ["date"],
        "Original_Message": ["rich_text"],
        "Processing_Status": ["select"]
    }
    
    # Implementation details...
```

### 5. Deal Verification Flow

```python
class DealVerificationFlow:
    async def start_verification(self, parsed_deals: List[Deal], chat_id: int):
        summary = self.format_deals_summary(parsed_deals)
        await self.bot.send_message(
            chat_id,
            f"I found {len(parsed_deals)} deals:\n\n{summary}\n\n"
            f"Should I save these? (Reply with numbers to edit specific deals, or 'yes' to confirm all)"
        )
        self.state[chat_id] = {
            "deals": parsed_deals,
            "stage": "awaiting_initial_confirmation"
        }
```

## Important Implementation Details

### 1. Rate Limiting
```python
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
```

### 2. Error Handling
- Implement retries for API failures
- Dead letter queue for failed messages
- Error notifications via Telegram
- Validation before storage
- Regular health checks

### 3. Monitoring
- Processing time tracking
- Success/failure rates
- Queue size monitoring
- API response times
- Memory usage
- Database query times

## Development Guidelines

1. Always use async/await for I/O operations
2. Implement proper logging at all levels
3. Add type hints for better code maintainability
4. Write tests for all new features
5. Document API endpoints and function signatures
6. Handle edge cases in deal parsing
7. Implement proper error handling and recovery
8. Use meaningful commit messages
9. Keep the code DRY (Don't Repeat Yourself)
10. Follow PEP 8 style guide

## Testing

1. Unit tests for each component
2. Integration tests for API endpoints
3. End-to-end tests for complete flows
4. Load testing for rate limits
5. Edge case testing for deal parsing

## Deployment

### Production Setup
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    image: dealautomator:latest
    restart: always
    environment:
      - ENVIRONMENT=production
    deploy:
      replicas: 2

  worker:
    image: dealautomator:latest
    restart: always
    environment:
      - ENVIRONMENT=production
    deploy:
      replicas: 2

  prometheus:
    image: prom/prometheus
    
  grafana:
    image: grafana/grafana
```

## Maintenance Tasks

1. Regular database backups
2. Log rotation
3. Monitoring alert setup
4. Performance optimization
5. Security updates
6. API key rotation

## Support and Troubleshooting

1. Check logs: `make logs`
2. Verify service health: `/health` endpoint
3. Monitor queue size
4. Check API rate limits
5. Verify database connections

For additional support, contact the development team or refer to the internal documentation.