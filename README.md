# SmartTransit AI - Delhi Public Transport Optimizer

A real-time transit route planner for Delhi that provides optimized routes using live bus tracking data from Delhi Open Transit Data.

## 🚀 Features

- 🚌 **Real-time Bus Tracking** - Track 2,600+ DTC buses with live GPS positions
- 🗺️ **Smart Route Planning** - Find actual bus routes between any two points
- 📊 **Multiple Options** - Compare routes by speed, cost, and comfort
- ✅ **Direction Validation** - Only suggests buses going the right way
- 📍 **Live Updates** - Bus positions updated every minute
- 🎯 **Confidence Scores** - Know how reliable each route suggestion is

## 📊 Current Status

### What's Working ✅
- Real-time tracking of 2,600+ DTC buses
- Actual route numbers (207, 531, 588, etc.)
- Direction-aware route planning
- Variable confidence scores (60-95%)
- Walking distance calculations
- Cost and time estimates

### Known Limitations ⚠️
- **Bus routes only** - Metro integration pending
- **No GTFS static data** - Must be downloaded separately (see DATA_SETUP.md)
- **Position-based routing** - Works best during peak hours
- **No multi-modal routes** - Can't combine bus + metro yet

See [ROUTE_PLANNER_STATUS.md](ROUTE_PLANNER_STATUS.md) for detailed information.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Option 1: Using Startup Scripts (Recommended)

**Terminal 1 - Start Backend:**
```bash
./start-backend.sh
```

**Terminal 2 - Start Frontend:**
```bash
./start-frontend.sh
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python route_planning_server.py
```

**Frontend:**
```bash
cd smarttransit-ai
npm install
npm run dev
```

The app will be available at `http://localhost:5173`

## 📁 Project Structure

```
delhi-bus-tracker/
├── backend/
│   ├── route_planning_server.py    # Main Flask server
│   ├── route_planner/
│   │   ├── simple_planner.py       # Route planning logic
│   │   └── gtfs_route_mapper.py    # GTFS data mapping
│   └── requirements.txt
├── smarttransit-ai/                # React frontend
│   ├── src/
│   │   ├── components/             # UI components
│   │   ├── services/               # API services
│   │   └── types/                  # TypeScript types
│   └── package.json
├── GTFS/                           # Bus GTFS data (not in git)
├── DMRC_GTFS/                      # Metro GTFS data (not in git)
└── DATA_SETUP.md                   # Instructions to download data
```

## 🔧 API Endpoints

### Backend Server (Port 5000)

- `GET /api/health` - Health check and system status
- `GET /api/live` - Get all live bus positions
- `POST /api/plan-route` - Plan a route between two points
- `GET /api/nearby-buses` - Find buses near a location
- `GET /api/routes` - Get list of active routes

### Example: Plan a Route

```bash
curl -X POST http://localhost:5000/api/plan-route \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"lat": 28.6500, "lon": 77.2167, "name": "Kashmere Gate"},
    "end": {"lat": 28.6289, "lon": 77.2065, "name": "Chandni Chowk"},
    "preference": "fastest"
  }'
```

## 📊 Data Sources

- **Real-time Bus Data**: [Delhi Open Transit Data](https://otd.delhi.gov.in/)
- **GTFS Static Data**: Available from Delhi Open Transit Data (must be downloaded separately)
- **Metro Data**: DMRC GTFS (available but not yet integrated)

### Setting Up GTFS Data

The GTFS data files are not included in this repository due to size constraints. Follow the instructions in [DATA_SETUP.md](DATA_SETUP.md) to download and set up the data.

## 🧪 Testing

### Test Backend Health
```bash
curl http://localhost:5000/api/health
```

### Test Route Planning
```bash
curl -X POST http://localhost:5000/api/plan-route \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"lat": 28.6129, "lon": 77.2295, "name": "Connaught Place"},
    "end": {"lat": 28.5517, "lon": 77.1983, "name": "India Gate"}
  }'
```

## 📚 Documentation

- [ROUTE_PLANNER_STATUS.md](ROUTE_PLANNER_STATUS.md) - Current implementation status and limitations
- [FIXES_APPLIED.md](FIXES_APPLIED.md) - Recent fixes and improvements
- [DATA_SETUP.md](DATA_SETUP.md) - How to download and set up GTFS data
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [PROJECT_WORKING.md](PROJECT_WORKING.md) - What's working and what's not

## 🔍 How It Works

1. **User enters start and end locations**
2. **Backend fetches live bus positions** (2,600+ buses)
3. **Algorithm finds buses near both points**
4. **Direction validation** ensures buses go the right way
5. **Route scoring** based on distance, time, and bearing match
6. **Returns top 3 routes** with confidence scores

See [ROUTE_PLANNER_STATUS.md](ROUTE_PLANNER_STATUS.md) for detailed algorithm explanation.

## 🐛 Known Issues

1. **Metro routes not shown** - Integration pending
2. **Stop names show coordinates** - Requires GTFS data or reverse geocoding
3. **Long-distance routes may not be found** - Limited to buses currently running
4. **No multi-modal routing** - Can't combine bus + metro

See [FIXES_APPLIED.md](FIXES_APPLIED.md) for recently fixed issues.

## 🚧 Roadmap

### Short Term
- [ ] Load GTFS static data for stop names
- [ ] Add reverse geocoding for area names
- [ ] Improve route caching

### Medium Term
- [ ] Integrate Delhi Metro real-time API
- [ ] Add multi-modal routing (bus + metro)
- [ ] Implement proper stop matching
- [ ] Add real-time arrival predictions

### Long Term
- [ ] Machine learning for route prediction
- [ ] Historical data analysis
- [ ] Traffic-aware routing
- [ ] Crowd-sourced route feedback

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Delhi Open Transit Data for providing real-time bus tracking API
- DMRC for metro GTFS data
- All contributors and testers

## 📞 Support

For issues and questions:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [ROUTE_PLANNER_STATUS.md](ROUTE_PLANNER_STATUS.md)
3. Open an issue on GitHub

---

**Note**: This project uses real Delhi Transit data. Route suggestions are based on live bus positions and may vary depending on time of day and bus availability.
