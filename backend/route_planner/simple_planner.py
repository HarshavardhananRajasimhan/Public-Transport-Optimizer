"""
Simplified route planner using real-time bus data
This works WITHOUT GTFS static data as an interim solution
"""

import requests
from geopy.distance import geodesic
from datetime import datetime, timedelta
import math
from .gtfs_route_mapper import get_route_mapper
from .metro_planner import get_metro_planner
from .arrival_predictor import get_arrival_predictor

REALTIME_API = "https://otd.delhi.gov.in/api/realtime/VehiclePositions.pb?key=mt2giIBCJY1tOjhmMIwfTaTwAXTfPpYR"

class SimpleRoutePlanner:
    """
    Simple route planner that uses only real-time bus positions
    This is a temporary solution until GTFS static data is loaded
    """
    
    def __init__(self):
        self.buses = []
        self.routes = {}
        self.last_update = None
        self.route_mapper = get_route_mapper()
        self.metro_planner = get_metro_planner()
        self.arrival_predictor = get_arrival_predictor()
    
    def update_realtime_data(self):
        """Fetch latest bus positions"""
        try:
            from google.transit import gtfs_realtime_pb2
            
            response = requests.get(REALTIME_API, timeout=10)
            if response.status_code != 200:
                return False
            
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)
            
            self.buses = []
            self.routes = {}
            
            for entity in feed.entity:
                if entity.HasField("vehicle"):
                    v = entity.vehicle
                    bus_data = {
                        "id": v.vehicle.id,
                        "lat": v.position.latitude,
                        "lon": v.position.longitude,
                        "route_id": v.trip.route_id,
                        "timestamp": v.timestamp,
                    }
                    self.buses.append(bus_data)
                    
                    # Group by route
                    route_id = v.trip.route_id
                    if route_id not in self.routes:
                        self.routes[route_id] = []
                    self.routes[route_id].append(bus_data)
            
            self.last_update = datetime.now()
            return True
            
        except Exception as e:
            print(f"Error updating realtime data: {e}")
            return False
    
    def find_nearby_buses(self, lat, lon, radius_km=2.0):
        """Find buses within radius of a location"""
        nearby = []
        
        for bus in self.buses:
            distance = geodesic((lat, lon), (bus['lat'], bus['lon'])).km
            if distance <= radius_km:
                nearby.append({
                    **bus,
                    'distance_km': round(distance, 2)
                })
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_km'])
        return nearby
    
    def find_routes_between_points(self, start_lat, start_lon, end_lat, end_lon, max_distance_km=3.0):
        """Find routes that pass near both start and end points"""
        routes_near_start = {}
        routes_near_end = {}
        
        # Calculate bearing from start to end (to check if bus is going in right direction)
        def calculate_bearing(lat1, lon1, lat2, lon2):
            """Calculate bearing between two points"""
            import math
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlon = lon2 - lon1
            x = math.sin(dlon) * math.cos(lat2)
            y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
            bearing = math.atan2(x, y)
            return (math.degrees(bearing) + 360) % 360
        
        desired_bearing = calculate_bearing(start_lat, start_lon, end_lat, end_lon)
        
        # Find all routes near start
        for bus in self.buses:
            distance_to_start = geodesic((start_lat, start_lon), (bus['lat'], bus['lon'])).km
            if distance_to_start <= max_distance_km:
                route_id = bus['route_id']
                if route_id not in routes_near_start:
                    routes_near_start[route_id] = []
                routes_near_start[route_id].append({
                    **bus,
                    'distance_to_start': distance_to_start
                })
        
        # Find all routes near end
        for bus in self.buses:
            distance_to_end = geodesic((end_lat, end_lon), (bus['lat'], bus['lon'])).km
            if distance_to_end <= max_distance_km:
                route_id = bus['route_id']
                if route_id not in routes_near_end:
                    routes_near_end[route_id] = []
                routes_near_end[route_id].append({
                    **bus,
                    'distance_to_end': distance_to_end
                })
        
        # Find routes that appear in both
        common_routes = set(routes_near_start.keys()) & set(routes_near_end.keys())
        
        results = []
        for route_id in common_routes:
            start_buses = routes_near_start[route_id]
            end_buses = routes_near_end[route_id]
            
            # Get closest bus to start
            closest_to_start = min(start_buses, key=lambda x: x['distance_to_start'])
            closest_to_end = min(end_buses, key=lambda x: x['distance_to_end'])
            
            # Check if buses are positioned correctly (start bus should be before end bus)
            bus_bearing = calculate_bearing(
                closest_to_start['lat'], closest_to_start['lon'],
                closest_to_end['lat'], closest_to_end['lon']
            )
            
            # Calculate bearing difference (should be similar to desired bearing)
            bearing_diff = abs(bus_bearing - desired_bearing)
            if bearing_diff > 180:
                bearing_diff = 360 - bearing_diff
            
            # Only include if buses are roughly in the right direction (within 90 degrees)
            if bearing_diff < 90:
                results.append({
                    'route_id': route_id,
                    'start_bus': closest_to_start,
                    'end_bus': closest_to_end,
                    'total_buses': len(self.routes.get(route_id, [])),
                    'bearing_match': 1.0 - (bearing_diff / 90.0)  # Score 0-1
                })
        
        # Sort by bearing match (best directional match first)
        results.sort(key=lambda x: x['bearing_match'], reverse=True)
        
        return results
    
    def plan_route(self, start_lat, start_lon, end_lat, end_lon, preference='fastest'):
        """
        Plan a route using available real-time bus data
        
        This is a simplified version that:
        1. Finds buses near the start location
        2. Checks if any go towards the end location
        3. Estimates travel time and cost
        """
        
        # Update data if stale
        if not self.last_update or (datetime.now() - self.last_update).seconds > 60:
            self.update_realtime_data()
        
        # Calculate direct distance
        direct_distance = geodesic((start_lat, start_lon), (end_lat, end_lon)).km
        
        # Find routes that pass near both points
        candidate_routes = self.find_routes_between_points(start_lat, start_lon, end_lat, end_lon, max_distance_km=2.0)
        
        if not candidate_routes:
            # Try with larger radius
            candidate_routes = self.find_routes_between_points(start_lat, start_lon, end_lat, end_lon, max_distance_km=4.0)
        
        if not candidate_routes:
            # No direct routes found - provide alternatives
            return self._create_no_route_response(start_lat, start_lon, end_lat, end_lon, direct_distance)
        
        # Create route options from candidates (up to 3)
        routes = []
        for i, candidate in enumerate(candidate_routes[:3]):
            route = self._create_bus_route_v2(
                candidate, 
                start_lat, start_lon, 
                end_lat, end_lon,
                direct_distance,
                i + 1
            )
            routes.append(route)
        
        # Also try to find metro routes
        try:
            metro_routes = self.metro_planner.plan_metro_route(
                start_lat, start_lon, 
                end_lat, end_lon
            )
            routes.extend(metro_routes)
        except Exception as e:
            print(f"Metro planning error: {e}")
        
        # Sort by preference
        if preference == 'fastest':
            routes.sort(key=lambda x: x['totalDuration'])
        elif preference == 'cheapest':
            routes.sort(key=lambda x: x['totalCost'])
        elif preference == 'balanced':
            # Balance between time and cost
            routes.sort(key=lambda x: x['totalDuration'] * 0.6 + x['totalCost'] * 0.4)
        
        # Return top 5 routes (mix of bus and metro)
        return {'routes': routes[:5]}
    
    def _create_bus_route_v2(self, candidate, start_lat, start_lon, end_lat, end_lon, distance, route_num):
        """Create a route object from a candidate (v2 with improved data)"""
        
        route_id = candidate['route_id']
        start_bus = candidate['start_bus']
        end_bus = candidate['end_bus']
        
        # Calculate actual bus travel distance (between the two bus positions)
        bus_distance = geodesic(
            (start_bus['lat'], start_bus['lon']),
            (end_bus['lat'], end_bus['lon'])
        ).km
        
        # Calculate walking distance to boarding point
        walk_to_start = start_bus['distance_to_start']
        walk_from_end = end_bus['distance_to_end']
        
        # Estimate travel time (assuming 20 km/h average speed in Delhi traffic)
        travel_time_min = int((bus_distance / 20.0) * 60)
        wait_time_min = 5  # Assume 5 min wait
        walk_time_start = int(walk_to_start * 12)  # 12 min per km walking
        walk_time_end = int(walk_from_end * 12)
        
        total_duration = travel_time_min + wait_time_min + walk_time_start + walk_time_end
        
        # Estimate cost (₹10 base + ₹5 per km for bus)
        cost = 10 + int(bus_distance * 5)
        
        # Get route name from GTFS data
        route_info = self.route_mapper.get_route_info(route_id, mode='bus')
        route_name = route_info.get('name', f'Bus {route_id}')
        route_long_name = route_info.get('long_name', '')
        route_number = route_info.get('route_number', route_id)
        
        # Create a clear route name
        if route_number and route_number != route_id:
            display_name = f"DTC Bus {route_number}"
        else:
            display_name = f"DTC Bus {route_id}"
        
        # Build segments
        segments = []
        
        # Walking to start
        if walk_to_start > 0.1:  # Only add if more than 100m
            segments.append({
                'mode': 'WALK',
                'details': f'Walk to bus stop ({walk_to_start:.2f} km)',
                'duration': walk_time_start,
                'distance': walk_to_start,
                'path': [
                    {'lat': start_lat, 'lng': start_lon},
                    {'lat': start_bus['lat'], 'lng': start_bus['lon']}
                ]
            })
        
        # Bus journey
        segments.append({
            'mode': 'BUS',
            'details': f'{display_name}',
            'duration': travel_time_min,
            'distance': bus_distance,
            'realtimeInfo': f'✓ Live tracking: {candidate["total_buses"]} buses on this route',
            'path': [
                {'lat': start_bus['lat'], 'lng': start_bus['lon']},
                {'lat': end_bus['lat'], 'lng': end_bus['lon']}
            ],
            'stopsList': [
                {
                    'name': f'Board near {self._get_area_name(start_bus["lat"], start_bus["lon"])}',
                    'arrivalTime': 'Now',
                    'platform': f'Look for bus {route_number}'
                },
                {
                    'name': f'Alight near {self._get_area_name(end_bus["lat"], end_bus["lon"])}',
                    'arrivalTime': f'~{travel_time_min} min',
                    'platform': ''
                }
            ]
        })
        
        # Walking from end
        if walk_from_end > 0.1:  # Only add if more than 100m
            segments.append({
                'mode': 'WALK',
                'details': f'Walk to destination ({walk_from_end:.2f} km)',
                'duration': walk_time_end,
                'distance': walk_from_end,
                'path': [
                    {'lat': end_bus['lat'], 'lng': end_bus['lon']},
                    {'lat': end_lat, 'lng': end_lon}
                ]
            })
        
        # Calculate confidence based on bearing match and distance
        confidence = candidate.get('bearing_match', 0.5) * 0.7 + 0.3
        
        return {
            'id': f'route-{route_num}',
            'routeName': display_name,
            'totalDuration': total_duration,
            'totalCost': cost,
            'comfortScore': 7,  # Good comfort
            'confidenceScore': round(confidence, 2),
            'summary': f'{display_name} - {bus_distance:.1f} km journey with {candidate["total_buses"]} buses currently running',
            'realtimeInfo': f'✓ {candidate["total_buses"]} buses tracked live',
            'routeDetails': {
                'route_id': route_id,
                'route_name': display_name,
                'route_long_name': route_long_name,
                'route_number': route_number,
                'is_realtime': True,
                'buses_tracked': candidate["total_buses"],
                'bearing_match': candidate.get('bearing_match', 0)
            },
            'segments': segments
        }
    
    def _get_area_name(self, lat, lon):
        """Get approximate area name based on coordinates (simplified)"""
        # This is a simplified version - in production, use reverse geocoding
        # For now, just return coordinates
        return f"({lat:.4f}, {lon:.4f})"
    
    def get_realtime_arrivals(self, lat, lon, route_id=None, limit=5):
        """
        Get real-time arrival predictions for buses near a location
        
        Args:
            lat, lon: User location
            route_id: Optional - filter by specific route
            limit: Number of arrivals to return
        
        Returns:
            List of arrival predictions with ETA
        """
        # Update data if stale
        if not self.last_update or (datetime.now() - self.last_update).seconds > 60:
            self.update_realtime_data()
        
        # Find nearby buses
        nearby_buses = self.find_nearby_buses(lat, lon, radius_km=3.0)
        
        # Filter by route if specified
        if route_id:
            nearby_buses = [b for b in nearby_buses if b['route_id'] == route_id]
        
        # Get arrival predictions
        arrivals = []
        for bus in nearby_buses[:limit * 2]:  # Get more to filter
            prediction = self.arrival_predictor.predict_arrival_time(bus, lat, lon)
            
            # Only include buses that are approaching or have reasonable ETA
            if prediction['status'] in ['approaching', 'unknown'] and prediction['eta_minutes'] < 60:
                route_info = self.route_mapper.get_route_info(bus['route_id'], mode='bus')
                
                arrivals.append({
                    'route_id': bus['route_id'],
                    'route_name': route_info.get('name', f"Bus {bus['route_id']}"),
                    'bus_id': bus['id'],
                    'eta_minutes': prediction['eta_minutes'],
                    'eta_formatted': self.arrival_predictor.format_arrival_time(prediction['eta_minutes']),
                    'confidence': prediction['confidence'],
                    'status': prediction['status'],
                    'speed_kmh': prediction['speed_kmh'],
                    'distance_km': prediction['distance_km'],
                    'current_position': {
                        'lat': bus['lat'],
                        'lon': bus['lon']
                    }
                })
        
        # Sort by ETA
        arrivals.sort(key=lambda x: x['eta_minutes'])
        
        return arrivals[:limit]
    
    def _create_no_route_response(self, start_lat, start_lon, end_lat, end_lon, distance):
        """Create response when no direct routes are found"""
        
        walk_time = int(distance * 12)  # 12 min per km
        
        # Find nearby buses at start
        nearby_start = self.find_nearby_buses(start_lat, start_lon, radius_km=2.0)
        nearby_end = self.find_nearby_buses(end_lat, end_lon, radius_km=2.0)
        
        routes = []
        
        # Walking route
        routes.append({
            'id': 'route-walk',
            'routeName': 'Walking Route',
            'totalDuration': walk_time,
            'totalCost': 0,
            'comfortScore': 4,
            'confidenceScore': 1.0,
            'summary': f'Walk {distance:.1f} km to destination',
            'realtimeInfo': f'⚠️ No direct bus routes found. {len(nearby_start)} buses near start, {len(nearby_end)} buses near destination.',
            'routeDetails': {
                'note': 'Consider using Delhi Metro or auto-rickshaw for this route',
                'nearby_buses_start': len(nearby_start),
                'nearby_buses_end': len(nearby_end)
            },
            'segments': [
                {
                    'mode': 'WALK',
                    'details': f'Walk {distance:.1f} km',
                    'duration': walk_time,
                    'distance': distance,
                    'path': [
                        {'lat': start_lat, 'lng': start_lon},
                        {'lat': end_lat, 'lng': end_lon}
                    ]
                }
            ]
        })
        
        return {'routes': routes}

# Singleton instance
_planner = None

def get_planner():
    """Get or create planner instance"""
    global _planner
    if _planner is None:
        _planner = SimpleRoutePlanner()
    return _planner
