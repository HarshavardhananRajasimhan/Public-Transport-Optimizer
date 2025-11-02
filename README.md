# SmartTransit AI - Delhi Bus Tracker

An AI-powered transit route planner for Delhi that provides optimized routes using real-time bus data and Gemini AI.

## Features

- 🤖 AI-powered route optimization using Google Gemini
- 🚌 Real-time bus tracking from Delhi Transit API
- 🗺️ Interactive map with route visualization
- ⚡ Multiple route options (fastest, cheapest, most comfortable)
- 📍 Live vehicle positions updated every 15 seconds

## Quick Start

### Option 1: Using the startup scripts (Recommended)

**Terminal 1 - Start Backend:**
```bash
./start-backend.sh
```

**Terminal 2 - Start Frontend:**
```bash
./start-frontend.sh
```

### Option 2: Manual setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

**Frontend:**
```bash
cd smarttransit-ai
npm install
npm run dev
```

## How It Works

1. **Frontend** (React + TypeScript + Vite)
   - User enters start and end locations
   - Gemini AI generates optimized route options
   - Map displays routes with live bus positions

2. **Backend** (Python + Flask)
   - Fetches real-time bus data from Delhi Transit API
   - Parses GTFS Realtime Protocol Buffer format
   - Serves data to frontend via REST API

3. **Integration**
   - Frontend polls backend every 15 seconds
   - Live buses appear as markers on the map
   - Toggle live tracking on/off as needed

## Project Structure

```
delhi-bus-tracker/
├── backend/
│   ├── server.py              # Real Delhi Transit API backend
│   ├── bus_realtime_server.py # Mock data backend (for testing)
│   └── requirements.txt       # Python dependencies
├── smarttransit-ai/
│   ├── components/            # React components
│   ├── services/              # API services
│   │   ├── geminiService.ts   # AI route optimization
│   │   └── transitApiService.ts # Live vehicle data
│   ├── hooks/                 # Custom React hooks
│   └── types.ts               # TypeScript types
├── start-backend.sh           # Backend startup script
├── start-frontend.sh          # Frontend startup script
└── README.md                  # This file
```

## Configuration

### Backend URL
The frontend connects to the backend via the `VITE_BACKEND_URL` environment variable in `smarttransit-ai/.env`:

```env
VITE_BACKEND_URL=http://localhost:5000
```

### Gemini API Key
Add your Gemini API key to `smarttransit-ai/.env`:

```env
API_KEY=your_gemini_api_key_here
```

## Using Mock Data

For testing without the real Delhi Transit API, use the mock backend:

1. Run the mock server:
```bash
cd backend
python bus_realtime_server.py
```

2. Update `smarttransit-ai/.env`:
```env
VITE_BACKEND_URL=http://localhost:5001
```

## Troubleshooting

**No live buses appearing:**
- Check that the backend is running on port 5000
- Open browser console to see API errors
- Verify CORS is not blocking requests

**Backend errors:**
- Ensure all Python dependencies are installed
- Check that the Delhi Transit API is accessible
- Verify the API key in server.py is valid

**Frontend not connecting:**
- Confirm `VITE_BACKEND_URL` in `.env` is correct
- Restart the frontend dev server after changing `.env`
- Check network tab in browser dev tools

## Tech Stack

**Frontend:**
- React 18
- TypeScript
- Vite
- Leaflet (maps)
- Google Gemini AI

**Backend:**
- Python 3
- Flask
- GTFS Realtime bindings
- Flask-CORS

## License

MIT
