#!/bin/bash

# AI Heuristic Evaluation Service Launcher
# Starts only the AI heuristic evaluation FastAPI service

set -e

echo "Starting AI Heuristic Evaluation Service..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt

echo -e "${BLUE}Starting AI Heuristic Evaluation API...${NC}"
python main.py
