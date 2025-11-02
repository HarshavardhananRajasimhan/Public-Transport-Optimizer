# Real Route Planner Implementation Plan

## Goal
Replace AI-generated fake routes with real route planning using actual Delhi transit data.

## Architecture Overview

```
User Input (Start/End)
        ↓
Route Planning Engine (Backend)
        ↓
    ┌───┴───┐
    ↓       ↓
GTFS Static   GTFS Realtime
(Routes,      (Live positions,
 Stops,        delays)
 Schedules)
    ↓       ↓
    └───┬───┘
        ↓
Optimized Routes
        ↓
Frontend Display
```

## Phase 1: Data Infrastructure (Week 1)

### 1.1 Download GTFS Static Data
- [ ] Get Delhi GTFS feed from https://otd.delhi.gov.in
- [ ] Parse GTFS files (routes.txt, stops.txt, trips.txt, stop_times.txt, etc.)
- [ ] Store in SQLite database for fast queries

### 1.2 Set Up Database Schema
```sql
- routes (route_id, route_short_name, route_long_name, route_type)
- stops (stop_id, stop_name, stop_lat, stop_lon)
- trips (trip_id, route_id, service_id, direction_id)
- stop_times (trip_id, stop_id, arrival_time, departure_time, stop_sequence)
- calendar (service_id, days of week, start_date, end_date)
```

### 1.3 Create Data Loading Scripts
- [ ] GTFS parser
- [ ] Database populator
- [ ] Data validation

## Phase 2: Route Planning Algorithm (Week 2-3)

### 2.1 Implement Core Algorithm
Choose one approach:
- **Option A**: Dijkstra's algorithm (simpler, good for basic routing)
- **Option B**: A* algorithm (faster, better for large networks)
- **Option C**: RAPTOR algorithm (best for public transit, handles transfers well)

**Recommendation**: Start with RAPTOR (Round-Based Public Transit Optimized Router)

### 2.2 Algorithm Components
- [ ] Graph builder (stops as nodes, trips as edges)
- [ ] Transfer detection (walking between stops)
- [ ] Multi-criteria optimization (time, cost, transfers)
- [ ] Time-dependent routing (schedules matter!)

### 2.3 Handle Different Preferences
- [ ] Fastest route (minimize total time)
- [ ] Cheapest route (minimize cost)
- [ ] Least transfers (minimize changes)
- [ ] Most comfortable (prefer metro over bus)

## Phase 3: Real-Time Integration (Week 3-4)

### 3.1 Merge Static + Real-Time Data
- [ ] Match real-time positions to scheduled trips
- [ ] Calculate delays
- [ ] Update ETAs dynamically
- [ ] Handle service disruptions

### 3.2 Live Updates
- [ ] Cache real-time data (refresh every 30s)
- [ ] Predict arrival times based on current positions
- [ ] Show "Bus arriving in X minutes"

## Phase 4: API Development (Week 4)

### 4.1 New Backend Endpoints
```python
POST /api/plan-route
  Input: {start_lat, start_lon, end_lat, end_lon, preferences}
  Output: [{route_id, segments[], duration, cost, transfers}]

GET /api/stops/nearby?lat=X&lon=Y&radius=500
  Output: [stops within radius]

GET /api/route/{route_id}/schedule
  Output: [upcoming trips for this route]

GET /api/trip/{trip_id}/realtime
  Output: {current_position, delay, next_stops[]}
```

### 4.2 Caching Strategy
- [ ] Cache GTFS data in memory
- [ ] Cache route calculations (5 min TTL)
- [ ] Cache real-time data (30 sec TTL)

## Phase 5: Frontend Integration (Week 5)

### 5.1 Replace Gemini Service
- [ ] Remove `geminiService.ts` AI calls
- [ ] Create `routePlannerService.ts`
- [ ] Call backend `/api/plan-route`

### 5.2 Enhanced UI
- [ ] Show real stop names
- [ ] Display actual schedules
- [ ] Show live ETAs
- [ ] Indicate delays/disruptions

## Phase 6: Metro & Train Integration (Week 6+)

### 6.1 Delhi Metro
- [ ] Get Delhi Metro GTFS data
- [ ] Integrate metro routes
- [ ] Handle metro-bus transfers
- [ ] Show metro line colors

### 6.2 Suburban Trains (if available)
- [ ] Get train schedules
- [ ] Integrate with route planner
- [ ] Handle train-bus-metro transfers

## Technical Stack

### Backend (Python)
```
- Flask (API server)
- SQLite (GTFS data storage)
- gtfs-realtime-bindings (real-time data)
- geopy (distance calculations)
- networkx (graph algorithms) OR custom RAPTOR implementation
```

### Data Processing
```
- pandas (GTFS parsing)
- numpy (calculations)
```

### Caching
```
- functools.lru_cache (in-memory)
- redis (optional, for production)
```

## Implementation Priority

### MVP (Minimum Viable Product) - 2 weeks
1. ✅ Download GTFS data
2. ✅ Parse and load into database
3. ✅ Implement basic route planning (single route, no transfers)
4. ✅ Create `/api/plan-route` endpoint
5. ✅ Update frontend to use real routes

### V1 (Full Featured) - 4-6 weeks
1. Multi-route planning with transfers
2. Real-time delay integration
3. Multiple optimization criteria
4. Metro integration
5. Walking directions

### V2 (Advanced) - 8+ weeks
1. Predictive ETAs using ML
2. Crowding predictions
3. Alternative routes during disruptions
4. User preferences (avoid certain routes)
5. Accessibility options

## Data Sources

### Delhi Transit Data
- **GTFS Static**: https://otd.delhi.gov.in/data/static/
- **GTFS Realtime**: https://otd.delhi.gov.in/api/realtime/VehiclePositions.pb
- **API Key**: Already have (in server.py)

### Delhi Metro
- Check if GTFS available
- Alternative: Scrape from DMRC website
- Or use OpenStreetMap data

## Challenges & Solutions

### Challenge 1: Large Dataset
**Problem**: GTFS data can be huge (millions of stop_times)
**Solution**: 
- Use SQLite with proper indexes
- Load only today's schedules into memory
- Pre-compute common routes

### Challenge 2: Transfer Detection
**Problem**: How to know which stops are walkable?
**Solution**:
- Calculate distances between all stops
- Mark stops within 500m as transfer points
- Use OpenStreetMap for walking paths

### Challenge 3: Time-Dependent Routing
**Problem**: Bus schedules change throughout the day
**Solution**:
- Always include current time in queries
- Filter trips that haven't departed yet
- Handle overnight trips (after midnight)

### Challenge 4: Real-Time Accuracy
**Problem**: Real-time positions might not match scheduled trips
**Solution**:
- Match by route_id and proximity
- Use trip_id when available
- Fall back to schedule if no real-time data

## File Structure

```
backend/
├── gtfs_data/
│   ├── routes.txt
│   ├── stops.txt
│   ├── trips.txt
│   ├── stop_times.txt
│   └── calendar.txt
├── database/
│   └── transit.db (SQLite)
├── route_planner/
│   ├── __init__.py
│   ├── gtfs_loader.py
│   ├── graph_builder.py
│   ├── raptor.py (or dijkstra.py)
│   ├── realtime_matcher.py
│   └── route_optimizer.py
├── api/
│   ├── __init__.py
│   ├── routes.py (Flask blueprints)
│   └── models.py
├── server.py (main Flask app)
└── requirements.txt (updated)
```

## Success Metrics

### Accuracy
- Routes match real DTC/Metro routes: 100%
- Stop names are correct: 100%
- Schedules within 5 min of actual: 90%+

### Performance
- Route calculation: < 2 seconds
- API response time: < 500ms
- Database queries: < 100ms

### User Experience
- Show 3+ route options
- Include real-time delays
- Display accurate ETAs
- Handle edge cases gracefully

## Next Steps

1. **Immediate**: Download and parse GTFS data
2. **Day 1-2**: Set up database and load data
3. **Day 3-5**: Implement basic route planning
4. **Day 6-7**: Create API endpoints
5. **Week 2**: Integrate with frontend
6. **Week 3+**: Add real-time features

## Resources

- GTFS Specification: https://gtfs.org/
- RAPTOR Algorithm Paper: https://www.microsoft.com/en-us/research/publication/round-based-public-transit-routing/
- Python GTFS Libraries: gtfs-kit, partridge
- Route Planning Libraries: pyroutelib3, osmnx

---

**Status**: Ready to begin implementation
**Estimated Time**: 4-6 weeks for full implementation
**Complexity**: High (but achievable!)
