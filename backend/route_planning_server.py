"""
Route planning server with real transit data
This replaces the AI-generated fake routes with real route planning
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from google.transit import gtfs_realtime_pb2
import sys
from pathlib import Path

# Add route_planner to path
sys.path.insert(0, str(Path(__file__).parent))

from route_planner.simple_planner import get_planner

app = Flask(__name__)
CORS(app)

# Delhi Transit API endpoint
DELHI_API_URL = "https://otd.delhi.gov.in/api/realtime/VehiclePositions.pb?key=mt2giIBCJY1tOjhmMIwfTaTwAXTfPpYR"

@app.route("/api/live", methods=["GET"])
def get_live_bus_data():
    """Get live bus positions (existing endpoint)"""
    try:
        response = requests.get(DELHI_API_URL)
        if response.status_code != 200:
            return jsonify({"error": f"Delhi API returned {response.status_code}"}), 500

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        buses = []
        for entity in feed.entity:
            if entity.HasField("vehicle"):
                v = entity.vehicle
                buses.append({
                    "id": v.vehicle.id,
                    "latitude": v.position.latitude,
                    "longitude": v.position.longitude,
                    "route_id": v.trip.route_id,
                    "timestamp": v.timestamp,
                    "trip_id": v.trip.trip_id,
                    "vehicle_id": v.vehicle.label or v.vehicle.id
                })

        return jsonify(buses)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/plan-route", methods=["POST"])
def plan_route():
    """
    Plan a route using real transit data
    
    Request body:
    {
        "start": {"lat": 28.6129, "lon": 77.2295, "name": "Connaught Place"},
        "end": {"lat": 28.5517, "lon": 77.1983, "name": "India Gate"},
        "preference": "fastest" | "cheapest" | "balanced"
    }
    
    Response:
    {
        "routes": [
            {
                "id": "route-1",
                "route_name": "Bus Route 505",
                "total_duration": 45,
                "total_cost": 20,
                "comfort_score": 7,
                "confidence_score": 0.85,
                "summary": "Take bus 505 - 5.2 km journey",
                "realtime_info": "3 buses currently running",
                "segments": [...]
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'start' not in data or 'end' not in data:
            return jsonify({"error": "Missing start or end location"}), 400
        
        start = data['start']
        end = data['end']
        preference = data.get('preference', 'fastest')
        
        # Get planner instance
        planner = get_planner()
        
        # Plan route
        result = planner.plan_route(
            start['lat'], start['lon'],
            end['lat'], end['lon'],
            preference=preference
        )
        
        # Add metadata
        result['metadata'] = {
            'start_name': start.get('name', 'Start Location'),
            'end_name': end.get('name', 'End Location'),
            'preference': preference,
            'data_source': 'Delhi Open Transit Data (Real-time)',
            'last_updated': planner.last_update.isoformat() if planner.last_update else None
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/nearby-buses", methods=["GET"])
def get_nearby_buses():
    """
    Get buses near a location
    
    Query params:
    - lat: latitude
    - lon: longitude
    - radius: radius in km (default: 1.0)
    """
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        radius = float(request.args.get('radius', 1.0))
        
        planner = get_planner()
        planner.update_realtime_data()
        
        nearby = planner.find_nearby_buses(lat, lon, radius)
        
        return jsonify({
            'buses': nearby,
            'count': len(nearby),
            'radius_km': radius
        })
        
    except ValueError:
        return jsonify({"error": "Invalid lat/lon parameters"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/routes", methods=["GET"])
def get_active_routes():
    """Get list of currently active bus routes"""
    try:
        planner = get_planner()
        planner.update_realtime_data()
        
        routes_info = []
        for route_id, buses in planner.routes.items():
            routes_info.append({
                'route_id': route_id,
                'active_buses': len(buses),
                'coverage': 'Active'
            })
        
        routes_info.sort(key=lambda x: x['active_buses'], reverse=True)
        
        return jsonify({
            'routes': routes_info,
            'total_routes': len(routes_info),
            'total_buses': len(planner.buses)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    planner = get_planner()
    
    return jsonify({
        'status': 'healthy',
        'buses_tracked': len(planner.buses),
        'routes_active': len(planner.routes),
        'last_update': planner.last_update.isoformat() if planner.last_update else None,
        'data_source': 'Delhi Open Transit Data',
        'mode': 'Real-time (Simple Planner)'
    })

if __name__ == "__main__":
    print("=" * 60)
    print("🚌 Delhi Transit Route Planning Server")
    print("=" * 60)
    print("\nEndpoints:")
    print("  GET  /api/live          - Live bus positions")
    print("  POST /api/plan-route    - Plan a route")
    print("  GET  /api/nearby-buses  - Find nearby buses")
    print("  GET  /api/routes        - Active routes")
    print("  GET  /api/health        - Health check")
    print("\nMode: Simple Planner (using real-time data only)")
    print("Note: For full route planning, load GTFS static data")
    print("\nStarting server on http://localhost:5000")
    print("=" * 60)
    print()
    
    app.run(debug=True, port=5000)
