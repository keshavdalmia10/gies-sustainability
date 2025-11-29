# 🎯 GETTING STARTED - 3 Easy Steps

Your complete MVP is ready! Here's how to get it running in 3 simple steps:

---

## Step 1: Run Setup (5-10 minutes)

```bash
./setup_mvp.sh
```

This will automatically:
- ✅ Install PostgreSQL
- ✅ Create database
- ✅ Set up backend (Python venv + dependencies)
- ✅ Set up frontend (npm install)
- ✅ Apply database schema

---

## Step 2: Configure & Load Data (2-3 minutes)

### A. Add your OpenAI API key

Edit `backend/.env`:
```bash
OPENAI_API_KEY=sk-...your-key-here
```

### B. Load your data

```bash
cd backend
source venv/bin/activate
python scripts/load_data.py ../data.csv
```

### C. Generate impact cards

```bash
python scripts/generate_sdg7_cards.py --limit 10
cd ..
```

---

## Step 3: Launch! (30 seconds)

```bash
./start_mvp.sh
```

Then visit: **http://localhost:3000**

---

## ✅ That's It!

Your MVP will be running with:
- Backend API: http://localhost:8000
- Frontend Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## 🎮 What to Try

1. **Homepage** - See the beautiful landing page
2. **Click "Donor View"** - Browse your impact cards
3. **Filter by SDG** - Try SDG 7, 13, or All
4. **API Docs** - Explore all 52 endpoints

---

## 📚 Need Help?

- **[LAUNCH_GUIDE.md](LAUNCH_GUIDE.md)** - Detailed instructions
- **[MVP_COMPLETE.md](MVP_COMPLETE.md)** - Complete documentation
- **[QUICK_START.md](QUICK_START.md)** - Command cheat sheet

---

## 🚨 Quick Troubleshooting

**Backend won't start?**
```bash
cd backend && source venv/bin/activate
pip install -r requirements.txt sentence-transformers openai
```

**Frontend won't start?**
```bash
cd frontend && npm install
```

**No impact cards?**
```bash
cd backend && source venv/bin/activate
python scripts/generate_sdg7_cards.py --limit 10
```

---

## 🎉 You're Ready!

**3 simple steps** and you have a complete, AI-powered sustainability dashboard!

Questions? Check the docs above or run `./check_system.sh` to verify your setup.

**Happy demoing! 🚀🎓✨**
