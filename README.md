# Deal Automator

A robust automation system designed to streamline deal processing by integrating with Claude AI and Notion. This service automates the analysis and processing of deal-related documents, providing intelligent insights and organized data management.

## Features

### Core Features
- Automated deal document analysis using Claude AI
- Seamless integration with Notion for data organization
- Asynchronous task processing with message queue
- RESTful API endpoints for deal management
- Containerized deployment support
- Database migrations using Alembic

### Natural Language Processing
- Intelligent conversation handling for deal queries
- Natural language understanding for deal-related questions
- Context-aware responses and follow-ups
- Two-way deal verification with user confirmation
- Interactive deal editing and confirmation

### Enhanced Notion Integration
- Automated database schema verification
- Missing field detection and validation
- Smart column type checking
- Select/multi-select option management
- Active deals tracking and management
- Deal expiration handling
- Geographic and temporal relevance filtering

### Error Handling & Monitoring
- Comprehensive error logging and tracking
- API rate limit management
- Database access verification
- Clear user feedback messages
- Operation retry mechanisms
- Performance monitoring
- User interaction tracking
- Processing success rate analytics

### Security
- User permission verification
- Secure API key management
- Access logging and auditing
- Authentication timeout handling
- Sensitive data protection

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLAlchemy ORM
- **Queue System**: Message Queue for async processing
- **AI Integration**: Claude API
- **Data Management**: Notion API
- **Containerization**: Docker
- **Migration**: Alembic

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Make (for using Makefile commands)
- Claude API credentials
- Notion API credentials

## Setup

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DealAutomator.git
cd DealAutomator
```

2. Create and configure environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

3. Run the setup script:
```bash
./setup.sh
```

### Docker Setup

1. Build and start the containers:
```bash
docker-compose up --build
```

For production deployment:
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## Environment Configuration

Required environment variables (see env.example):
- Database configuration
- Claude API credentials
- Notion API credentials
- Queue configuration
- Application settings
- Monitoring settings
- Security parameters

## Development Commands

The project includes a Makefile with common commands:

```bash
# Start the application
make run

# Run tests
make test

# Apply database migrations
make migrate

# Generate new migration
make migration message="migration message"

# Build Docker images
make build

# Deploy to production
make deploy

# Run monitoring dashboard
make monitor

# Verify database schema
make verify-schema
```

## API Documentation

Once the application is running, access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
├── alembic/            # Database migrations
├── app/
│   ├── api/           # API routes
│   ├── core/          # Core configuration
│   ├── db/            # Database setup
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   │   ├── claude_service.py    # AI conversation handling
│   │   ├── notion_service.py    # Notion integration
│   │   └── queue_service.py     # Async processing
│   └── utils/         # Utility functions
├── tests/             # Test suite
└── docker/            # Docker configuration
```

## Monitoring & Analytics

The system provides comprehensive monitoring through:
- User interaction logs
- Processing success rates
- API response times
- Queue performance metrics
- Error tracking and alerts
- Schema validation status

## Security Considerations

- API keys are stored securely using environment variables
- All database access is permission-controlled
- User actions are logged for audit purposes
- Regular security updates are applied
- Rate limiting is implemented for API endpoints

## Deployment

The project includes deployment scripts for production:

1. Configure production environment variables
2. Run the deployment script:
```bash
./deploy.sh
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[License Type] - See LICENSE file for details
