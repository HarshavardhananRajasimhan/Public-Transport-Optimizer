from flask import Flask, jsonify
from flask_cors import CORS
import requests
from google.transit import gtfs_realtime_pb2
import io

app = Flask(__name__)
CORS(app)

# Delhi Transit API endpoint with your API key
DELHI_API_URL = "https://otd.delhi.gov.in/api/realtime/VehiclePositions.pb?key=mt2giIBCJY1tOjhmMIwfTaTwAXTfPpYR"

@app.route("/api/live", methods=["GET"])
def get_live_bus_data():
    try:
        response = requests.get(DELHI_API_URL)
        if response.status_code != 200:
            return jsonify({"error": f"Delhi API returned {response.status_code}"}), 500

        # Parse .pb binary data
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

if __name__ == "__main__":
    app.run(debug=True, port=5000)
