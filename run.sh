#!/bin/bash

# Quick start script for the reorganized Indonesian Shipping Price Checker

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚚 Indonesian Shipping Price Checker${NC}"
echo -e "${BLUE}======================================${NC}"

# Check if we're in the right directory
if [ ! -d "Core_Application" ] || [ ! -d "AI_And_Tools" ]; then
    echo -e "${YELLOW}⚠️  Please run this script from the project root directory${NC}"
    exit 1
fi

# Set Python path
export PYTHONPATH="$(pwd):$(pwd)/Core_Application:$(pwd)/AI_And_Tools"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install requirements
echo -e "${BLUE}📚 Installing requirements...${NC}"
pip install -r "Data_And_Config/requirements.txt"

# Copy environment file if it doesn't exist
if [ ! -f "Data_And_Config/.env" ]; then
    if [ -f "Data_And_Config/.env.example" ]; then
        echo -e "${YELLOW}⚙️  Copying .env.example to .env${NC}"
        cp "Data_And_Config/.env.example" "Data_And_Config/.env"
        echo -e "${YELLOW}Please edit Data_And_Config/.env with your API credentials${NC}"
    fi
fi

# Ask user what to run
echo -e "${GREEN}Choose an option:${NC}"
echo "1. 🌐 Run Streamlit Web App"
echo "2. 💻 Run CLI Interface"
echo "3. 🐳 Run with Docker"

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo -e "${GREEN}🌐 Starting Streamlit Web App...${NC}"
        echo -e "${BLUE}Access the app at: http://localhost:8501${NC}"
        cd "Core_Application"
        streamlit run streamlit_app.py
        ;;
    2)
        echo -e "${GREEN}💻 Starting CLI Interface...${NC}"
        cd "Core_Application"
        python cli.py
        ;;
    3)
        echo -e "${GREEN}🐳 Starting Docker...${NC}"
        cd Deployment
        chmod +x docker.sh
        ./docker.sh build
        ./docker.sh start
        ;;
    *)
        echo -e "${YELLOW}Invalid option. Please run the script again.${NC}"
        exit 1
        ;;
esac
