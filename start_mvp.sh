#!/bin/bash
# Start the complete MVP - Backend + Frontend

echo "🚀 Starting Gies Sustainability Impact Dashboard MVP"
echo "===================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: backend or frontend directory not found"
    echo "Please run this script from the case_competition directory"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "${BLUE}📡 Starting Backend API...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing backend dependencies..."
    pip install -q -r requirements.txt
    pip install -q sentence-transformers openai
fi

# Start backend in background
uvicorn app.main:app --reload --reload-dir app --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!

echo "✓ Backend starting on http://localhost:8000"
echo "  Logs: backend.log"
echo "  API Docs: http://localhost:8000/docs"

cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo ""
echo "${BLUE}🎨 Starting Frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo "✓ Frontend starting on http://localhost:3000"
echo "  Logs: frontend.log"

cd ..

echo ""
echo "===================================================="
echo "${GREEN}✅ MVP is running!${NC}"
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "===================================================="
echo ""

# Monitor logs
tail -f frontend.log backend.log

# Keep script running
wait
