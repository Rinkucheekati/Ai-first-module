# AI First CRM HCP Module - Backend

A production-ready FastAPI backend for an AI-first CRM system focused on Healthcare Professional (HCP) management.

## Tech Stack

- **Python 3.12** - Programming language
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy 2.0** - SQL toolkit and ORM
- **MySQL 8** - Relational database
- **Alembic** - Database migration tool
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server
- **python-dotenv** - Environment variable management

## Features

### Database Models

#### HCP (Healthcare Professional)
- `id` - Primary key
- `doctor_name` - Doctor's full name
- `hospital` - Hospital/organization name
- `specialization` - Medical specialization
- `city` - City location
- `phone` - Phone number
- `email` - Email address (unique)
- `created_at` - Timestamp of creation
- `updated_at` - Timestamp of last update

#### Interaction
- `id` - Primary key
- `hcp_id` - Foreign key to HCP
- `interaction_date` - Date and time of interaction
- `discussion` - Detailed discussion notes
- `summary` - Optional summary of the interaction
- `follow_up_date` - Optional follow-up date
- `created_at` - Timestamp of creation
- `updated_at` - Timestamp of last update

### API Endpoints

#### HCP Endpoints

- **GET /hcp** - Get all HCPs with search and pagination
  - Query params: `skip`, `limit`, `search`
  - Returns: List of HCPs with total count

- **GET /hcp/{hcp_id}** - Get a single HCP by ID
  - Returns: HCP details

- **POST /hcp** - Create a new HCP
  - Body: HCP data (doctor_name, hospital, specialization, city, phone, email)
  - Returns: Created HCP

- **PUT /hcp/{hcp_id}** - Update an existing HCP
  - Body: Partial HCP data (all fields optional)
  - Returns: Updated HCP

- **DELETE /hcp/{hcp_id}** - Delete an HCP
  - Returns: 204 No Content

#### Interaction Endpoints

- **GET /interactions** - Get all interactions with filtering and pagination
  - Query params: `skip`, `limit`, `hcp_id`
  - Returns: List of interactions with total count

- **GET /interactions/{interaction_id}** - Get a single interaction by ID
  - Returns: Interaction details

- **POST /interactions** - Create a new interaction
  - Body: Interaction data (hcp_id, interaction_date, discussion, summary, follow_up_date)
  - Returns: Created interaction

- **PUT /interactions/{interaction_id}** - Update an existing interaction
  - Body: Partial interaction data (all fields optional)
  - Returns: Updated interaction

- **DELETE /interactions/{interaction_id}** - Delete an interaction
  - Returns: 204 No Content

- **GET /interactions/hcp/{hcp_id}** - Get all interactions for a specific HCP
  - Query params: `skip`, `limit`
  - Returns: List of interactions for the HCP

#### System Endpoints

- **GET /** - Root endpoint with API information
- **GET /health** - Health check endpoint
- **GET /docs** - Interactive API documentation (Swagger UI)
- **GET /redoc** - Alternative API documentation (ReDoc)

## Project Structure

```
backend/
├── app/
│   ├── api/                    # API endpoints (future use)
│   ├── database/
│   │   ├── __init__.py
│   │   └── session.py         # Database session management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── hcp.py             # HCP SQLAlchemy model
│   │   └── interaction.py     # Interaction SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── hcp.py             # HCP Pydantic schemas
│   │   └── interaction.py     # Interaction Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── hcp_service.py     # HCP business logic
│   │   └── interaction_service.py  # Interaction business logic
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── hcp.py             # HCP API routes
│   │   └── interaction.py     # Interaction API routes
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Application configuration
│   ├── agents/                # LangGraph agents (future AI integration)
│   ├── tools/                 # AI tools (future AI integration)
│   ├── __init__.py
│   └── main.py                # FastAPI application entry point
├── alembic/
│   ├── versions/              # Database migration files
│   ├── env.py                # Alembic environment configuration
│   ├── script.py.mako        # Migration script template
│   └── README                # Alembic documentation
├── alembic.ini               # Alembic configuration
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Installation

### Prerequisites

- Python 3.12 or higher
- MySQL 8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository and navigate to the backend directory:**
```bash
cd ai-first-crm-hcp-module/backend
```

2. **Create a virtual environment:**
```bash
python -m venv venv
```

3. **Activate the virtual environment:**

On Windows:
```bash
venv\Scripts\activate
```

On macOS/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` and update the following values:
- `DATABASE_URL` - MySQL connection string
- `SECRET_KEY` - Generate a secure secret key
- `CORS_ORIGINS` - Update with your frontend URL

6. **Set up MySQL database:**
```bash
# Create database using MySQL Workbench or command line
mysql -u root -p
CREATE DATABASE ai_first_crm;
EXIT;

# Or using MySQL Workbench:
# 1. Open MySQL Workbench
# 2. Connect to your local MySQL server
# 3. Execute: CREATE DATABASE ai_first_crm;
```

7. **Run database migrations:**
```bash
alembic upgrade head
```

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or using Python:
```bash
python -m app.main
```

The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Alternative Documentation: http://localhost:8000/redoc

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback one migration
```bash
alembic downgrade -1
```

### View migration history
```bash
alembic history
```

### View current version
```bash
alembic current
```

## API Usage Examples

### Create an HCP
```bash
curl -X POST "http://localhost:8000/hcp" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_name": "Dr. Sarah Johnson",
    "hospital": "City Hospital",
    "specialization": "Cardiology",
    "city": "New York",
    "phone": "+1 555-0101",
    "email": "sarah.johnson@cityhospital.com"
  }'
```

### Get all HCPs
```bash
curl -X GET "http://localhost:8000/hcp?skip=0&limit=10&search=cardiology"
```

### Get HCP by ID
```bash
curl -X GET "http://localhost:8000/hcp/1"
```

### Update an HCP
```bash
curl -X PUT "http://localhost:8000/hcp/1" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1 555-9999"
  }'
```

### Delete an HCP
```bash
curl -X DELETE "http://localhost:8000/hcp/1"
```

### Create an Interaction
```bash
curl -X POST "http://localhost:8000/interactions" \
  -H "Content-Type: application/json" \
  -d '{
    "hcp_id": 1,
    "interaction_date": "2024-01-15T10:30:00",
    "discussion": "Discussed new product features and upcoming conference presentation.",
    "summary": "Productive call with Dr. Johnson",
    "follow_up_date": "2024-01-22T10:30:00"
  }'
```

### Get all Interactions
```bash
curl -X GET "http://localhost:8000/interactions?skip=0&limit=10"
```

### Get Interactions by HCP
```bash
curl -X GET "http://localhost:8000/interactions/hcp/1"
```

## CORS Configuration

The backend is configured to accept requests from the React frontend. Update the `CORS_ORIGINS` in `.env` to match your frontend URL:

```env
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

## Testing

### Run tests (when implemented)
```bash
pytest
```

### Run with coverage (when implemented)
```bash
pytest --cov=app --cov-report=html
```

## Security Considerations

- **Environment Variables**: Never commit `.env` file to version control
- **Secret Key**: Use a strong, randomly generated secret key in production
- **Database Credentials**: Use strong passwords and restrict database access
- **CORS**: Restrict CORS origins to trusted domains in production
- **HTTPS**: Use HTTPS in production environments
- **Authentication**: Add JWT or OAuth authentication (to be implemented)

## Future Enhancements

- **Authentication & Authorization**: JWT-based authentication
- **Rate Limiting**: API rate limiting to prevent abuse
- **Logging**: Structured logging with log levels
- **Monitoring**: Application performance monitoring
- **Caching**: Redis caching for frequently accessed data
- **LangGraph Integration**: AI-powered interaction analysis
- **Groq API Integration**: AI model integration for insights
- **File Upload**: Support for document attachments
- **Advanced Search**: Full-text search with filters
- **Export**: Data export functionality (CSV, PDF)
- **Webhooks**: Webhook notifications for events

## Troubleshooting

### Database Connection Issues
- Verify MySQL is running
- Check DATABASE_URL in `.env`
- Ensure database exists: `mysql -u root -p -e "SHOW DATABASES LIKE 'ai_first_crm';"`

### Migration Issues
- Check Alembic configuration in `alembic.ini`
- Verify database connection string
- Run `alembic current` to check migration status

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version (requires 3.12+)

## License

This project is part of the AI First CRM HCP Module.

## Support

For issues and questions, please refer to the project documentation or contact the development team.
