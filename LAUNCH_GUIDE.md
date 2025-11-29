# 🚀 Final Setup & Launch Guide

## You're Almost There!

Your MVP is complete. Here's how to get it running:

---

## ✅ Step 1: Check Your System

Run the verification script:
```bash
./check_system.sh
```

This will check for:
- Python 3
- Node.js
- PostgreSQL
- Database creation
- Virtual environment
- Dependencies

Fix any issues it reports before proceeding!

---

## 🔧 Step 2: Initial Setup (First Time Only)

### Configure Environment
```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-...your-key-here
```

### Create Database & Load Data
```bash
# Create database
createdb gies_sustainability

# Apply schema
psql gies_sustainability < database/schema.sql

# Load your data
source venv/bin/activate
python scripts/load_data.py ../data.csv

# Generate impact cards
python scripts/generate_sdg7_cards.py --limit 10
```

---

## 🚀 Step 3: Start the MVP

### Option A: Use the Startup Script (Easiest!)
```bash
./start_mvp.sh
```

This will:
- Start the backend on http://localhost:8000
- Start the frontend on http://localhost:3000
- Display logs from both
- Press Ctrl+C to stop both

### Option B: Manual Start (2 Terminals)

**Terminal 1: Backend**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2: Frontend**
```bash
cd frontend
npm install  # First time only
npm run dev
```

---

## 🌐 Step 4: Open the Dashboard

Visit: **http://localhost:3000**

You'll see:
1. **Homepage** - Hero section with persona cards
2. **Click "Donor View"** - See your impact cards!
3. **Filter by SDG** - Try the filtering
4. **Explore** - Check out the metrics and outcomes

---

## 🎯 What to Demo

### Homepage
- Beautiful landing page
- 3 persona cards
- Mission statement
- Key stats

### Donor View (Fully Functional!)
- Impact card grid
- SDG filtering
- Funding metrics
- Key outcomes
- Portfolio summary

### Backend API (http://localhost:8000/docs)
- Interactive Swagger UI
- Test all 52 endpoints
- See request/response examples

---

## 🔍 Quick Tests

### Test 1: Check Backend Health
```bash
curl http://localhost:8000/
```

### Test 2: Get Dashboard Stats
```bash
curl http://localhost:8000/api/v1/decision-support/stats
```

### Test 3: List Impact Cards
```bash
curl http://localhost:8000/api/v1/impact-cards?sdg=7
```

---

## 🐛 Troubleshooting

### Backend won't start?
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
pip install sentence-transformers openai
```

### Frontend won't start?
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database errors?
```bash
dropdb gies_sustainability
createdb gies_sustainability
psql gies_sustainability < backend/database/schema.sql
```

### No impact cards showing?
```bash
cd backend
source venv/bin/activate
python scripts/generate_sdg7_cards.py --limit 10
```

---

## 📊 Expected Results

After setup, you should have:
- ✅ Backend running on port 8000
- ✅ Frontend running on port 3000
- ✅ Database with ~85 faculty
- ✅ ~1500 publications loaded
- ✅ 10 impact cards generated
- ✅ Beautiful donor dashboard working

---

## 🎉 You Did It!

Your complete MVP is ready with:
- ✅ Full backend API (52 endpoints)
- ✅ AI/ML pipeline (classification, matching, generation)
- ✅ React frontend dashboard
- ✅ Impact cards with GPT-4 narratives
- ✅ Complete documentation

**Time to show it off!** 🚀🎓✨

---

## 📞 Quick Reference

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main dashboard |
| Backend | http://localhost:8000 | API server |
| API Docs | http://localhost:8000/docs | Interactive API docs |

**Logs**:
- Backend: `backend.log`
- Frontend: `frontend.log`

---

**Need help?** Check the documentation:
- [MVP_COMPLETE.md](MVP_COMPLETE.md) - Full guide
- [QUICK_START.md](QUICK_START.md) - Commands cheat sheet
- [backend/README.md](backend/README.md) - Backend docs
- [frontend/README.md](frontend/README.md) - Frontend docs
