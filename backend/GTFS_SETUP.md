# GTFS Data Setup Guide

## Option 1: Manual Download (Recommended for now)

1. Visit: https://otd.delhi.gov.in/data/static/
2. Click "Download All Static Data" button
3. Fill in the purpose form (e.g., "Transit app development")
4. Download the ZIP file
5. Extract to: `backend/gtfs_data/`

The extracted folder should contain these files:
- `routes.txt` - Bus route information
- `stops.txt` - Stop locations and names
- `trips.txt` - Trip schedules
- `stop_times.txt` - Arrival/departure times at each stop
- `calendar.txt` - Service days (weekday/weekend)
- `shapes.txt` - Route paths (optional)
- `agency.txt` - Transit agency info

## Option 2: Use Sample Data (For Testing)

If you can't download the full dataset, I can create a small sample dataset for testing the route planner logic.

## Option 3: Alternative Data Sources

### Google Transit Data
- Check: https://transitfeeds.com/
- Search for "Delhi" GTFS feeds

### OpenStreetMap
- Extract transit data from OSM
- Less complete but freely available

## Next Steps

Once you have the GTFS data:

```bash
cd backend
python3 route_planner/gtfs_loader.py
```

This will:
1. Parse all GTFS files
2. Load data into SQLite database
3. Create indexes for fast queries
4. Validate data integrity

## File Sizes (Approximate)

- routes.txt: ~100 KB (hundreds of routes)
- stops.txt: ~5 MB (thousands of stops)
- trips.txt: ~50 MB (hundreds of thousands of trips)
- stop_times.txt: ~500 MB (millions of stop times)
- Total: ~600 MB uncompressed

## Database Size

After loading into SQLite: ~400-500 MB

## Memory Requirements

- Loading: ~2 GB RAM
- Running: ~500 MB RAM (with caching)
