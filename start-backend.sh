#!/bin/bash

echo "🚀 Starting SmartTransit AI Backend..."
echo ""

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Start the server
echo ""
echo "✅ Starting backend server on http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""
python server.py
