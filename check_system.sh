#!/bin/bash
# Quick verification script to check if everything is ready

echo "🔍 Gies Sustainability Dashboard - System Check"
echo "================================================"
echo ""

# Check Python
echo "✓ Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  ✓ $PYTHON_VERSION found"
else
    echo "  ✗ Python 3 not found"
    exit 1
fi

# Check Node
echo "✓ Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "  ✓ Node $NODE_VERSION found"
else
    echo "  ✗ Node.js not found"
    exit 1
fi

# Check PostgreSQL
echo "✓ Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    PSQL_VERSION=$(psql --version)
    echo "  ✓ $PSQL_VERSION found"
else
    echo "  ✗ PostgreSQL not found"
    echo "  Install with: brew install postgresql@15"
fi

# Check database
echo "✓ Checking database..."
if psql -lqt | cut -d \| -f 1 | grep -qw gies_sustainability; then
    echo "  ✓ Database 'gies_sustainability' exists"
else
    echo "  ✗ Database 'gies_sustainability' not found"
    echo "  Create with: createdb gies_sustainability"
fi

# Check backend venv
echo "✓ Checking backend virtual environment..."
if [ -d "backend/venv" ]; then
    echo "  ✓ Virtual environment found"
else
    echo "  ✗ Virtual environment not found"
    echo "  Create with: cd backend && python3 -m venv venv"
fi

# Check backend .env
echo "✓ Checking backend .env file..."
if [ -f "backend/.env" ]; then
    echo "  ✓ .env file found"
    if grep -q "OPENAI_API_KEY=sk-" backend/.env; then
        echo "  ✓ OpenAI API key configured"
    else
        echo "  ⚠ OpenAI API key not set (needed for ML features)"
    fi
else
    echo "  ✗ .env file not found"
    echo "  Copy from: cp backend/.env.example backend/.env"
fi

# Check frontend node_modules
echo "✓ Checking frontend dependencies..."
if [ -d "frontend/node_modules" ]; then
    echo "  ✓ Node modules installed"
else
    echo "  ✗ Node modules not found"
    echo "  Install with: cd frontend && npm install"
fi

echo ""
echo "================================================"
echo "System check complete!"
echo ""
echo "Next steps:"
echo "1. Fix any ✗ or ⚠ items above"
echo "2. Run: ./start_mvp.sh"
echo ""
