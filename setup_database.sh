#!/bin/bash
# ============================================================================
# EdTech MVP Database Integration Setup Script
# 
# This script sets up the entire system:
# 1. Installs PostgreSQL and required Python packages
# 2. Creates the database and schemas
# 3. Seeds curriculum data
# 4. Initializes the backend server
# ============================================================================

set -e  # Exit on error

echo "=================================="
echo "🚀 EdTech MVP Database Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check if Python venv is activated
echo -e "${BLUE}Step 1: Checking Python environment...${NC}"
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not activated${NC}"
    echo "Please run: source venv/bin/activate"
    exit 1
fi
echo -e "${GREEN}✅ Virtual environment activated: $VIRTUAL_ENV${NC}"
echo ""

# Step 2: Install Python dependencies
echo -e "${BLUE}Step 2: Installing Python packages...${NC}"
pip install -r requirements.txt --quiet
echo -e "${GREEN}✅ Python packages installed${NC}"
echo ""

# Step 3: Check if PostgreSQL is running
echo -e "${BLUE}Step 3: Checking PostgreSQL connection...${NC}"
if ! psql -U kunalranjan -d postgres -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  PostgreSQL not responding${NC}"
    echo "Make sure PostgreSQL is running:"
    echo "  macOS (Homebrew): brew services start postgresql@15"
    echo "  Linux: sudo systemctl start postgresql"
    echo "  Docker: docker run -d -e POSTGRES_PASSWORD=password postgres"
    exit 1
fi
echo -e "${GREEN}✅ PostgreSQL is running${NC}"
echo ""

# Step 4: Initialize database
echo -e "${BLUE}Step 4: Initializing database...${NC}"
python init_database.py
echo ""

# Step 5: Seed curriculum
echo -e "${BLUE}Step 5: Seeding curriculum data...${NC}"
python init_curriculum.py
echo ""

# Step 6: Summary
echo -e "${GREEN}=================================="
echo "✅ Setup completed successfully!"
echo "==================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Start the backend server:"
echo "   python app_refactored.py"
echo ""
echo "2. Access the frontend:"
echo "   Open http://localhost:5002 in your browser"
echo ""
echo "3. Register a student:"
echo "   - Enter your name"
echo "   - Select a chapter"
echo "   - Click 'Start Learning'"
echo ""
echo -e "${BLUE}Database Info:${NC}"
echo "   Database: edtech_mvp"
echo "   Schemas: users, curriculum, analytics"
echo "   Connection: postgresql://kunalranjan@localhost:5432/edtech_mvp"
echo ""
