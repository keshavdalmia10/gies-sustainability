# 🚀 Quick Start Cheat Sheet

## Setup (5 minutes)

```bash
cd /Users/keshavdalmia/Documents/case_competition/backend

# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
pip install sentence-transformers openai  # For ML

# 3. Set up database
brew install postgresql@15  # If needed
createdb gies_sustainability
psql gies_sustainability < database/schema.sql

# 4. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 5. Load data
python scripts/load_data.py ../data.csv

# 6. Run server
uvicorn app.main:app --reload
```

**Access**: http://localhost:8000/docs

---

## Common Commands

### Load Data
```bash
python scripts/load_data.py ../data.csv
```

### Classify Publications
```bash
# Batch classify 100 publications
curl -X POST "http://localhost:8000/api/v1/ml/batch-classify?limit=100"

# Classify single publication
curl -X POST "http://localhost:8000/api/v1/ml/classify-publication/{pub_id}"
```

### Test SDG Classification
```bash
curl -X POST "http://localhost:8000/api/v1/ml/classify-sdg" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This research focuses on affordable solar energy for rural communities.",
    "title": "Solar Energy for Rural Development",
    "top_k": 3
  }'
```

### Get Dashboard Stats
```bash
curl "http://localhost:8000/api/v1/decision-support/stats"
```

### Match Publication to Impacts
```bash
curl -X POST "http://localhost:8000/api/v1/ml/match-impacts" \
  -H "Content-Type: application/json" \
  -d '{
    "publication_id": "your-publication-uuid",
    "threshold": 0.75
  }'
```

---

## Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application entry point |
| `app/models.py` | Database ORM models (16 tables) |
| `app/schemas.py` | Request/response validation |
| `app/routers/ml.py` | ML service endpoints |
| `app/services/ml/sdg_classifier.py` | SDG classification |
| `app/services/ml/impact_matcher.py` | Impact matching |
| `scripts/load_data.py` | CSV data loader |
| `database/schema.sql` | PostgreSQL schema |

---

## Environment Variables

Required in `.env`:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/gies_sustainability
DATABASE_ASYNC_URL=postgresql+asyncpg://postgres:password@localhost:5432/gies_sustainability

# OpenAI (required for classification)
OPENAI_API_KEY=sk-...your-key-here

# Optional
VECTOR_DB=faiss  # or pinecone
EMBEDDING_MODEL=all-mpnet-base-v2
```

---

## API Endpoints Quick Reference

### Core Data
- `GET /api/v1/faculty` - List faculty
- `GET /api/v1/publications` - List publications
- `GET /api/v1/impacts` - List impacts
- `GET /api/v1/impact-cards` - List impact cards

### ML Services
- `POST /api/v1/ml/classify-sdg` - Classify text
- `POST /api/v1/ml/classify-publication/{id}` - Classify publication
- `POST /api/v1/ml/match-impacts` - Match impacts
- `POST /api/v1/ml/batch-classify` - Batch classify

### Decision Support
- `GET /api/v1/decision-support/stats` - Dashboard stats
- `GET /api/v1/decision-support/donor?sdg=7` - Donor view
- `GET /api/v1/decision-support/student` - Student view

### Evaluation
- `GET /api/v1/evaluation/metrics/latest?sdg=7` - Latest P@k
- `POST /api/v1/evaluation/ground-truth` - Add validation

---

## Troubleshooting

### Database connection error
```bash
# Check if PostgreSQL is running
brew services start postgresql@15

# Recreate database
dropdb gies_sustainability
createdb gies_sustainability
psql gies_sustainability < database/schema.sql
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
pip install sentence-transformers openai
```

### OpenAI API error
```bash
# Check `.env` file has valid key
echo $OPENAI_API_KEY
```

---

## Next Steps

1. ✅ **Load data**: `python scripts/load_data.py ../data.csv`
2. ✅ **Classify publications**: Batch classify endpoint
3. ✅ **Fetch external grants**: Use NIH/NSF clients
4. ✅ **Create impact cards**: POST to `/impact-cards`
5. 🔄 **Build frontend**: React dashboard
6. 🔄 **Deploy**: AWS/GCP/Azure

---

## Support

- **API Docs**: http://localhost:8000/docs
- **Main README**: [backend/README.md](backend/README.md)
- **Full Guide**: [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)
