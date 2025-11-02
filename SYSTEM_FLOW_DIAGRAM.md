# System Flow Diagram - How Everything Works Together

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                     (React Frontend - Port 5173)                │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ User enters:
                                 │ - Start: "Kashmere Gate"
                                 │ - End: "Nehru Place"
                                 │ - Preference: "Fastest"
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LOCATION LOOKUP (Frontend)                   │
│                  routePlannerService.ts                         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Converts names to coordinates:
                                 │ "Kashmere Gate" → (28.6692, 77.2289)
                                 │ "Nehru Place" → (28.5494, 77.2501)
                                 │
                                 │ Hardcoded lookup table:
                                 │ const locations = {
                                 │   'kashmere gate': {lat: 28.6692, lon: 77.2289},
                                 │   'nehru place': {lat: 28.5494, lon: 77.2501},
                                 │   ...
                                 │ }
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HTTP POST REQUEST                            │
│                  /api/plan-route                                │
│                                                                 │
│  {                                                              │
│    "start": {"lat": 28.6692, "lon": 77.2289, "name": "..."},  │
│    "end": {"lat": 28.5494, "lon": 77.2501, "name": "..."},    │
│    "preference": "fastest"                                      │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Network request
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND SERVER                               │
│              (Flask - Port 5000)                                │
│           route_planning_server.py                              │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Calls planner
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ROUTE PLANNER                                │
│              simple_planner.py                                  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌───────────────────┐     ┌───────────────────┐
        │   BUS PLANNING    │     │  METRO PLANNING   │
        │                   │     │                   │
        │ 1. Fetch live     │     │ 1. Load stations  │
        │    bus data       │     │    from GTFS      │
        │                   │     │                   │
        │ 2. Find buses     │     │ 2. Find nearest   │
        │    near start     │     │    stations       │
        │                   │     │                   │
        │ 3. Find buses     │     │ 3. Calculate      │
        │    near end       │     │    shortest path  │
        │                   │     │                   │
        │ 4. Validate       │     │ 4. Calculate      │
        │    direction      │     │    time & cost    │
        │                   │     │                   │
        │ 5. Calculate      │     │ 5. Return metro   │
        │    metrics        │     │    routes         │
        └───────────────────┘     └───────────────────┘
                    │                         │
                    └────────────┬────────────┘
                                 │
                                 │ Combine results
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ROUTE COMPARISON                             │
│                                                                 │
│  All Routes = Bus Routes + Metro Routes                         │
│                                                                 │
│  Sort by preference:                                            │
│  - Fastest: sort by duration                                    │
│  - Cheapest: sort by cost                                       │
│  - Balanced: sort by (duration*0.6 + cost*0.4)                  │
│                                                                 │
│  Return top 5 routes                                            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ JSON response
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE TO FRONTEND                         │
│                                                                 │
│  {                                                              │
│    "routes": [                                                  │
│      {                                                          │
│        "routeName": "Delhi Metro (Yellow+Magenta)",            │
│        "totalDuration": 48,                                     │
│        "totalCost": 40,                                         │
│        "comfortScore": 9,                                       │
│        "segments": [...]                                        │
│      },                                                         │
│      {                                                          │
│        "routeName": "DTC Bus 531",                             │
│        "totalDuration": 67,                                     │
│        "totalCost": 64,                                         │
│        "comfortScore": 7,                                       │
│        "segments": [...]                                        │
│      }                                                          │
│    ]                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Display results
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USER SEES RESULTS                            │
│                                                                 │
│  Route 1: Metro (Yellow+Magenta) - 48 min, ₹40 ⭐             │
│  Route 2: Bus 531 - 67 min, ₹64                               │
│  Route 3: Metro (Yellow+Violet) - 51 min, ₹40                 │
│                                                                 │
│  User clicks on a route to see details                          │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Bus Planning Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              STEP 1: FETCH LIVE BUS DATA                        │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ HTTP GET Request
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│         Delhi Open Transit Data API                             │
│  https://otd.delhi.gov.in/api/realtime/VehiclePositions.pb     │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Returns protobuf data
                                 │ with 2,600+ bus positions
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              PARSE PROTOBUF DATA                                │
│                                                                 │
│  For each bus:                                                  │
│    - id: "DL1PC1234"                                           │
│    - lat: 28.6520                                              │
│    - lon: 77.2180                                              │
│    - route_id: "207"                                           │
│    - timestamp: 1699012345                                      │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Store in memory
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 2: FIND BUSES NEAR START                      │
│                                                                 │
│  Start location: (28.6692, 77.2289) - Kashmere Gate           │
│  Search radius: 2 km                                            │
│                                                                 │
│  For each bus:                                                  │
│    distance = geodesic(start, bus.position)                    │
│    if distance <= 2 km:                                         │
│      routes_near_start[bus.route_id].append(bus)              │
│                                                                 │
│  Result:                                                        │
│    Route 207: [bus1, bus2, bus3] (3 buses)                    │
│    Route 531: [bus4, bus5] (2 buses)                          │
│    Route 588: [bus6] (1 bus)                                  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 3: FIND BUSES NEAR END                        │
│                                                                 │
│  End location: (28.5494, 77.2501) - Nehru Place               │
│  Search radius: 2 km                                            │
│                                                                 │
│  For each bus:                                                  │
│    distance = geodesic(end, bus.position)                      │
│    if distance <= 2 km:                                         │
│      routes_near_end[bus.route_id].append(bus)                │
│                                                                 │
│  Result:                                                        │
│    Route 207: [bus7, bus8] (2 buses)                          │
│    Route 531: [bus9] (1 bus)                                  │
│    Route 999: [bus10, bus11] (2 buses)                        │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 4: FIND COMMON ROUTES                         │
│                                                                 │
│  common = routes_near_start ∩ routes_near_end                  │
│                                                                 │
│  Result:                                                        │
│    Route 207 ✅ (appears at both start and end)               │
│    Route 531 ✅ (appears at both start and end)               │
│    Route 588 ❌ (only at start)                               │
│    Route 999 ❌ (only at end)                                 │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 5: DIRECTION VALIDATION                       │
│                                                                 │
│  For Route 207:                                                 │
│    start_bus = closest bus to start (bus1)                     │
│    end_bus = closest bus to end (bus7)                         │
│                                                                 │
│    desired_bearing = bearing(start → end)                      │
│                    = bearing(Kashmere Gate → Nehru Place)      │
│                    = 165° (South-Southeast)                     │
│                                                                 │
│    bus_bearing = bearing(bus1 → bus7)                          │
│               = bearing((28.6520, 77.2180) → (28.5500, 77.2490))│
│               = 170° (South-Southeast)                          │
│                                                                 │
│    bearing_diff = |170° - 165°| = 5°                          │
│                                                                 │
│    if bearing_diff < 90°:                                       │
│      ✅ ACCEPT (buses going right direction)                   │
│      confidence = 1.0 - (5/90) = 0.94 = 94%                   │
│                                                                 │
│  For Route 531:                                                 │
│    bearing_diff = 23°                                           │
│    ✅ ACCEPT with 74% confidence                               │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 6: CALCULATE METRICS                          │
│                                                                 │
│  For Route 207:                                                 │
│    bus_distance = distance(bus1, bus7) = 12.5 km              │
│    walk_to_start = distance(start, bus1) = 0.8 km             │
│    walk_from_end = distance(bus7, end) = 1.2 km               │
│                                                                 │
│    bus_time = (12.5 / 20) * 60 = 37 min (20 km/h)            │
│    walk_time_start = (0.8 / 5) * 60 = 10 min (5 km/h)        │
│    walk_time_end = (1.2 / 5) * 60 = 14 min                    │
│    wait_time = 5 min (assumed)                                 │
│    total_time = 37 + 10 + 14 + 5 = 66 min                     │
│                                                                 │
│    cost = 10 + (12.5 * 5) = ₹72.50 ≈ ₹73                     │
│                                                                 │
│    comfort = 7/10 (bus comfort)                                │
│    confidence = 94% (from bearing match)                        │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Metro Planning Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              STEP 1: LOAD METRO DATA (One-time)                 │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Read GTFS files
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│         DMRC_GTFS/stops.txt                                     │
│                                                                 │
│  stop_id,stop_name,stop_lat,stop_lon                           │
│  1,Dilshad Garden,28.675991,77.321495                          │
│  2,Jhilmil,28.675648,77.312393                                 │
│  8,Kashmere Gate,28.667879,77.228012                           │
│  ...                                                            │
│  286 stations total                                             │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│         DMRC_GTFS/routes.txt                                    │
│                                                                 │
│  route_id,route_long_name                                       │
│  1,RED_Rithala to Shaheed Sthal                                │
│  2,YELLOW_Huda City Centre to Samaypur Badli                   │
│  12,MAGENTA_Janak Puri West to Botanical Garden                │
│  ...                                                            │
│  36 lines total                                                 │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│         BUILD NETWORK GRAPH                                     │
│                                                                 │
│  Using NetworkX:                                                │
│    graph.add_edge(station1, station2, distance=X)              │
│                                                                 │
│  Result: Graph with 286 nodes, 1200+ edges                     │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 2: FIND NEAREST STATIONS                      │
│                                                                 │
│  Start: (28.6692, 77.2289) - Kashmere Gate                    │
│  Search radius: 2 km                                            │
│                                                                 │
│  For each station:                                              │
│    distance = geodesic(start, station.position)                │
│    if distance <= 2 km:                                         │
│      add to candidates                                          │
│                                                                 │
│  Result:                                                        │
│    Kashmere Gate Metro: 0.2 km ✅                              │
│    New Delhi Metro: 0.96 km ✅                                 │
│    Chawri Bazar Metro: 0.94 km ✅                              │
│                                                                 │
│  End: (28.5494, 77.2501) - Nehru Place                        │
│  Result:                                                        │
│    Kalkaji Mandir Metro: 0.85 km ✅                            │
│    Nehru Place Metro: 0.3 km ✅                                │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 3: FIND SHORTEST PATH                         │
│                                                                 │
│  For each start-end station pair:                              │
│    path = nx.shortest_path(                                     │
│      graph,                                                     │
│      source=start_station,                                      │
│      target=end_station,                                        │
│      weight='distance'                                          │
│    )                                                            │
│                                                                 │
│  Example: Kashmere Gate → Nehru Place                          │
│    Path: [Kashmere Gate, Rajiv Chowk, Hauz Khas,              │
│           Kalkaji Mandir, Nehru Place]                          │
│    Lines: Yellow Line → Magenta Line                            │
│    Stations: 14                                                 │
│    Distance: 14.1 km                                            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 4: CALCULATE METRICS                          │
│                                                                 │
│  metro_distance = 14.1 km                                       │
│  walk_to_start = 0.2 km                                         │
│  walk_from_end = 0.3 km                                         │
│                                                                 │
│  metro_time = (14.1 / 40) * 60 = 21 min (40 km/h)            │
│  walk_time_start = (0.2 / 5) * 60 = 2 min                     │
│  walk_time_end = (0.3 / 5) * 60 = 4 min                       │
│  wait_time = 3 min (assumed)                                    │
│  total_time = 21 + 2 + 4 + 3 = 30 min                         │
│                                                                 │
│  cost = ₹40 (12-21 km fare bracket)                           │
│                                                                 │
│  comfort = 9/10 (metro comfort)                                │
│  confidence = 95% (metro is reliable)                           │
└─────────────────────────────────────────────────────────────────┘
```

## What Happens When You Click "Find Best Route"

```
1. User Input
   ↓
2. Frontend validates input
   ↓
3. Frontend looks up coordinates (hardcoded table)
   ↓
4. Frontend sends POST request to backend
   ↓
5. Backend receives request
   ↓
6. Backend calls SimpleRoutePlanner.plan_route()
   ↓
7. Planner checks if bus data is stale (> 60 seconds)
   ├─ If stale: Fetch new data from Delhi API
   └─ If fresh: Use cached data
   ↓
8. Planner finds buses near start (2 km radius)
   ↓
9. Planner finds buses near end (2 km radius)
   ↓
10. Planner finds common routes
   ↓
11. Planner validates direction (bearing check)
   ↓
12. Planner calculates metrics for each bus route
   ↓
13. Planner calls MetroPlanner.plan_metro_route()
   ↓
14. Metro planner finds nearest stations
   ↓
15. Metro planner calculates shortest paths
   ↓
16. Metro planner calculates metrics for each metro route
   ↓
17. Planner combines bus + metro routes
   ↓
18. Planner sorts by preference (fastest/cheapest/balanced)
   ↓
19. Planner returns top 5 routes
   ↓
20. Backend sends JSON response to frontend
   ↓
21. Frontend displays routes to user
   ↓
22. User sees results and can click for details
```

## Key Takeaways

1. **Location Input**: Manual text input, converted via hardcoded lookup table
2. **Bus Data**: Fetched live from Delhi API every 60 seconds
3. **Metro Data**: Loaded once from GTFS files, never changes
4. **Distance Calculation**: Geodesic formula (accurate)
5. **Time Estimation**: Average speeds (20 km/h bus, 40 km/h metro)
6. **Arrival Prediction**: None - just assumes 5 min wait for bus, 3 min for metro
7. **Route Optimization**: Compares all options, sorts by preference
8. **Direction Validation**: Uses bearing calculations to filter wrong-way buses

The system is a **smart route finder** that uses real data but makes educated guesses about timing. It's not a real-time arrival predictor.
