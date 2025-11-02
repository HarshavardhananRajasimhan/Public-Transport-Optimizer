from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import random
import datetime
import os

app = Flask(__name__, static_folder="../smarttransit-ai/dist", static_url_path="/")
CORS(app)  # Allow React frontend to access this API (port 3000)

# -------------------------------
# Example Bus Data (Mock Realtime)
# -------------------------------
def generate_mock_vehicle_positions():
    """Simulate live vehicle position data"""
    vehicles = []
    routes = ["Route 120", "Route 45B", "Route 12C", "Route 29D"]

    for i in range(6):
        vehicles.append({
            "id": i + 1,
            "route": random.choice(routes),
            "latitude": 28.61 + random.uniform(-0.02, 0.02),   # near Delhi lat
            "longitude": 77.23 + random.uniform(-0.02, 0.02),  # near Delhi lon
            "speed": random.randint(10, 50),
            "timestamp": datetime.datetime.now().isoformat()
        })
    return vehicles

# -------------------------------
# API Routes
# -------------------------------
@app.route("/api/live", methods=["GET"])
def get_live_data():
    """Return live vehicle data"""
    return jsonify(generate_mock_vehicle_positions())

# -------------------------------
# Serve React Frontend (Production)
# -------------------------------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    """Serve built React app"""
    dist_dir = os.path.join(os.path.dirname(__file__), "../smarttransit-ai/dist")

    # If frontend is built (dist exists), serve index.html
    if os.path.exists(os.path.join(dist_dir, "index.html")):
        if path != "" and os.path.exists(os.path.join(dist_dir, path)):
            return send_from_directory(dist_dir, path)
        else:
            return send_from_directory(dist_dir, "index.html")
    else:
        # During development, show a message instead
        return jsonify({
            "message": "Frontend not built yet. Run `npm run build` in smarttransit-ai/ first."
        }), 404

# -------------------------------
# Run Server
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
