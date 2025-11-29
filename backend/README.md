# Gies Sustainability Impact Dashboard - Backend

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up Database

```bash
# Install PostgreSQL (if not already installed)
brew install postgresql@15  # macOS
# or use docker: docker run --name gies-postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15

# Create database
createdb gies_sustainability

# Run schema
psql gies_sustainability < database/schema.sql
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual API keys and database URL
```

### 4. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database connection & session management
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic schemas for validation
│   ├── routers/             # API endpoints
│   │   ├── __init__.py
│   │   ├── faculty.py       # Faculty CRUD operations
│   │   ├── publications.py  # Publications endpoints
│   │   ├── impacts.py       # Grants, patents, policies
│   │   ├── impact_cards.py  # Impact cards management
│   │   ├── evaluation.py    # Precision@k & model metrics
│   │   ├── feedback.py      # Faculty feedback system
│   │   └── decision_support.py  # Dean/Donor/Student views
│   └── services/            # Business logic (to be added)
├── database/
│   └── schema.sql           # PostgreSQL schema
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
└── README.md               # This file
```

## API Endpoints

### Faculty
- `GET /api/v1/faculty` - List all faculty
- `GET /api/v1/faculty/{id}` - Get faculty with stats
- `POST /api/v1/faculty` - Create faculty
- `PATCH /api/v1/faculty/{id}` - Update faculty
- `DELETE /api/v1/faculty/{id}` - Delete faculty
- `GET /api/v1/faculty/{id}/publications` - Get faculty publications

### Publications
- `GET /api/v1/publications` - List publications (filterable)
- `GET /api/v1/publications/{id}` - Get single publication
- `POST /api/v1/publications` - Create publication
- `GET /api/v1/publications/sdg/{sdg_number}` - Publications by SDG

### Impacts
- `GET /api/v1/impacts` - List all impacts
- `GET /api/v1/impacts/{id}` - Get single impact
- `POST /api/v1/impacts` - Create impact
- `POST /api/v1/impacts/grants` - Create grant
- `GET /api/v1/impacts/grants` - List grants
- `POST /api/v1/impacts/patents` - Create patent
- `POST /api/v1/impacts/match` - Match publication to impacts (ML)

### Impact Cards
- `GET /api/v1/impact-cards` - List impact cards
- `GET /api/v1/impact-cards/{id}` - Get detailed card
- `POST /api/v1/impact-cards` - Create card
- `PATCH /api/v1/impact-cards/{id}` - Update card
- `POST /api/v1/impact-cards/{id}/publish` - Publish card

### Evaluation
- `GET /api/v1/evaluation/metrics` - Get evaluation metrics
- `POST /api/v1/evaluation/metrics` - Store evaluation results
- `GET /api/v1/evaluation/metrics/latest` - Latest metrics for SDG
- `POST /api/v1/evaluation/ground-truth` - Add ground truth
- `GET /api/v1/evaluation/ground-truth/stats` - Ground truth statistics

### Feedback
- `POST /api/v1/feedback` - Submit faculty feedback
- `GET /api/v1/feedback` - List feedback submissions
- `PATCH /api/v1/feedback/{id}/resolve` - Resolve feedback

### Decision Support
- `GET /api/v1/decision-support/dean` - Dean dashboard data
- `GET /api/v1/decision-support/donor` - Donor view data
- `GET /api/v1/decision-support/student` - Student mentor search
- `GET /api/v1/decision-support/stats` - Overall statistics
- `GET /api/v1/decision-support/sdg/{number}/summary` - SDG summary

### Machine Learning
- `POST /api/v1/ml/classify-sdg` - Classify text for SDG relevance
- `POST /api/v1/ml/classify-publication/{id}` - Classify existing publication
- `POST /api/v1/ml/match-impacts` - Match publication to impacts
- `POST /api/v1/ml/batch-classify` - Batch classify publications

## Environment Variables

Required environment variables (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/gies_sustainability
DATABASE_ASYNC_URL=postgresql+asyncpg://user:pass@localhost:5432/gies_sustainability

# Vector DB (optional - can use FAISS locally)
VECTOR_DB=pinecone  # or 'faiss'
PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=us-west1-gcp

# OpenAI (for LLM summaries)
OPENAI_API_KEY=your_key

# External APIs (no keys required - all public)
NIH_API_BASE=https://api.reporter.nih.gov/v2
NSF_API_BASE=https://www.nsf.gov/awardsearch/
USPTO_API_BASE=https://api.patentsview.org/patents/query

# Cache
REDIS_URL=redis://localhost:6379/0
```

## Next Steps

1. **Load Initial Data**: Import data from `data.csv`
2. **Implement ML Services**: SDG classification, impact matching
3. **Add External API Integration**: NIH, NSF, USPTO data ingestion
4. **Build Frontend**: React dashboard connecting to these APIs
5. **Deploy**: AWS, Google Cloud, or your preferred platform

## Development

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
isort app/
```

### Database Migrations
```bash
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Support

For questions or issues, contact the Gies Analytics Team.
