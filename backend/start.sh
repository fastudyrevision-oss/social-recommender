#!/bin/bash

# Social Media Recommender - Quick Start Script

echo "================================"
echo "Social Media Recommender Setup"
echo "================================"
echo ""

# Check Python
echo "✓ Python version:"
python3 --version
echo ""

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate
echo "  venv activated"
echo ""

# Show installed packages
echo "✓ Key dependencies installed:"
pip list | grep -E "(fastapi|faiss|sentence|redis|pydantic|sqlalchemy)" | head -10
echo ""

# Start backend
echo "✓ Starting backend server on port 8000..."
echo "  Command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Once running, you can:"
echo "  • Visit API docs: http://localhost:8000/docs"
echo "  • Check health: http://localhost:8000/health"
echo "  • View stats: http://localhost:8000/stats"
echo ""
echo "To test with sample data:"
echo "  python test_recommender.py"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
