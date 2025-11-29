#!/bin/bash

# Gies Sustainability Impact Dashboard - Backend Setup Script

echo "🚀 Setting up Gies Sustainability Impact Dashboard Backend..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Create virtual environment
echo -e "${YELLOW}1. Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
echo -e "${YELLOW}2. Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 3. Set up environment file
echo -e "${YELLOW}3. Setting up environment variables...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file. Please update with your API keys!${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# 4. Check PostgreSQL
echo -e "${YELLOW}4. Checking PostgreSQL...${NC}"
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL is installed${NC}"
    
    # Try to create database
    echo -e "${YELLOW}   Creating database 'gies_sustainability'...${NC}"
    createdb gies_sustainability 2>/dev/null && echo -e "${GREEN}✓ Database created${NC}" || echo -e "${YELLOW}⚠ Database may already exist${NC}"
    
    # Run schema
    echo -e "${YELLOW}   Running database schema...${NC}"
    psql gies_sustainability < database/schema.sql && echo -e "${GREEN}✓ Schema applied${NC}" || echo -e "${YELLOW}⚠ Error applying schema${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL not found. Please install:${NC}"
    echo "   macOS: brew install postgresql@15"
    echo "   Ubuntu: sudo apt-get install postgresql-15"
    echo "   Or use Docker: docker run --name gies-postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15"
fi

# 5. Check Redis (optional)
echo -e "${YELLOW}5. Checking Redis (optional)...${NC}"
if command -v redis-cli &> /dev/null; then
    echo -e "${GREEN}✓ Redis is installed${NC}"
else
    echo -e "${YELLOW}⚠ Redis not found (optional). Install for caching:${NC}"
    echo "   macOS: brew install redis"
    echo "   Ubuntu: sudo apt-get install redis-server"
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Run: uvicorn app.main:app --reload"
echo "4. Open: http://localhost:8000/docs"
echo ""
echo "Happy coding! 🎉"
