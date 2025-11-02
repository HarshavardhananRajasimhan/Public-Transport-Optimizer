# GTFS Data Setup

The GTFS data files are not included in this repository due to GitHub's file size limits (some files exceed 100MB).

## Required Data Files

You need to download and place the following GTFS data in the project:

### 1. Delhi Bus GTFS Data
- Create a folder: `GTFS/`
- Download Delhi DTC bus GTFS data from: https://otd.delhi.gov.in/data/static/
- Extract the following files into `GTFS/`:
  - agency.txt
  - routes.txt
  - trips.txt
  - stop_times.txt
  - stops.txt
  - calendar.txt
  - fare_attributes.txt
  - fare_rules.txt

### 2. Delhi Metro GTFS Data
- Create a folder: `DMRC_GTFS/`
- Download Delhi Metro GTFS data from: https://otd.delhi.gov.in/data/static/
- Extract the following files into `DMRC_GTFS/`:
  - agency.txt
  - routes.txt
  - trips.txt
  - stop_times.txt
  - stops.txt
  - calendar.txt
  - shapes.txt

## Folder Structure

After setup, your project should have:
```
delhi-bus-tracker/
├── GTFS/
│   ├── agency.txt
│   ├── routes.txt
│   ├── trips.txt
│   ├── stop_times.txt
│   ├── stops.txt
│   ├── calendar.txt
│   ├── fare_attributes.txt
│   └── fare_rules.txt
├── DMRC_GTFS/
│   ├── agency.txt
│   ├── routes.txt
│   ├── trips.txt
│   ├── stop_times.txt
│   ├── stops.txt
│   ├── calendar.txt
│   └── shapes.txt
└── ... (other project files)
```

## Verification

After downloading the data, you can verify it's working by:
1. Starting the backend: `cd backend && python route_planning_server.py`
2. Check the routes endpoint: `curl http://localhost:5001/api/routes`
3. You should see actual Delhi bus and metro routes loaded

## Note

These GTFS files are static data that provide route information, stop locations, and schedules. The real-time bus tracking uses a separate API from Delhi's Open Transit Data portal.
