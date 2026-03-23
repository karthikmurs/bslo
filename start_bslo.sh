#!/bin/bash

# BSLO Startup Script
# Starts both the API server and Streamlit dashboard

echo "======================================================================"
echo "  BSLO - Bengaluru Strategic Logistics Optimizer"
echo "  Starting API Server and Dashboard"
echo "======================================================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Creating..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Check if models exist
if [ ! -f "models/xgboost_tuned.pkl" ]; then
    echo "❌ Error: Trained model not found!"
    echo "Please run the XGBoost modeling notebook first:"
    echo "  jupyter notebook notebooks/03_xgboost_modeling.ipynb"
    exit 1
fi

echo "✅ Models found"
echo ""

# Start API server in background
echo "🚀 Starting API Server on http://localhost:8000"
uvicorn src.api:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait for API to start
sleep 3

# Check if API is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API Server is running"
else
    echo "❌ API Server failed to start"
    kill $API_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎨 Starting Streamlit Dashboard on http://localhost:8501"
echo ""
echo "======================================================================"
echo "  Access Points:"
echo "  - API Documentation: http://localhost:8000/docs"
echo "  - Dashboard: http://localhost:8501"
echo "  - API Health: http://localhost:8000/health"
echo "======================================================================"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start Streamlit (this will block)
streamlit run app/streamlit_app.py

# Cleanup on exit
echo ""
echo "Stopping API Server..."
kill $API_PID 2>/dev/null
echo "✅ Shutdown complete"
