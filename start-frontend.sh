#!/bin/bash

echo "🚀 Starting SmartTransit AI Frontend..."
echo ""

cd smarttransit-ai

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo ""
echo "✅ Starting frontend on http://localhost:5173"
echo "   Press Ctrl+C to stop"
echo ""
npm run dev
