#!/bin/bash
# One-command setup for the complete MVP

echo "🔧 Setting up Gies Sustainability Impact Dashboard MVP"
echo "======================================================"
echo ""

# 1. Install PostgreSQL
echo "📦 Step 1: Installing PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "  Installing PostgreSQL with Homebrew..."
    brew install postgresql@15
    brew services start postgresql@15
    echo "  ✓ PostgreSQL installed and started"
else
    echo "  ✓ PostgreSQL already installed"
fi

echo ""

# 2. Create database
echo "📊 Step 2: Creating database..."
if psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw gies_sustainability; then
    echo "  ⚠ Database already exists, skipping"
else
    createdb gies_sustainability
    echo "  ✓ Database created"
fi

echo ""

# 3. Backend setup
echo "🐍 Step 3: Setting up backend..."
cd backend

# Create venv
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate

# Install dependencies
echo "  Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q sentence-transformers openai
echo "  ✓ Backend dependencies installed"

# Create .env
if [ ! -f ".env" ]; then
    echo ""
    echo "  Creating .env file..."
    cp .env.example .env
    echo "  ⚠ IMPORTANT: Edit backend/.env and add your OPENAI_API_KEY"
    echo ""
fi

# Apply schema
echo "  Applying database schema..."
psql gies_sustainability < database/schema.sql > /dev/null 2>&1
echo "  ✓ Database schema applied"

cd ..

echo ""

# 4. Frontend setup
echo "⚛️  Step 4: Setting up frontend..."
cd frontend

echo "  Installing Node dependencies (this may take a minute)..."
npm install --silent
echo "  ✓ Frontend dependencies installed"

cd ..

echo ""
echo "======================================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo ""
echo "1. Add your OpenAI API key to backend/.env:"
echo "   OPENAI_API_KEY=sk-...your-key-here"
echo ""
echo "2. Load your data:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python scripts/load_data.py ../data.csv"
echo ""
echo "3. Generate impact cards:"
echo "   python scripts/generate_sdg7_cards.py --limit 10"
echo ""
echo "4. Start the MVP:"
echo "   cd .."
echo "   ./start_mvp.sh"
echo ""
echo "======================================================"
