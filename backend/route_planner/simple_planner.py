"""
Simplified route planner using real-time bus data
This works WITHOUT GTFS static data as an interim solution
"""

import requests
from geopy.distance import geodesic
from datetime import datetime, timedelta
import math
from .gtfs_route_mapper import get_route_mapper

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
            
            results.append({
                'route_id': route_id,
                'start_bus': closest_to_start,
                'end_bus': closest_to_end,
                'total_buses': len(self.routes.get(route_id, []))
            })
        
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
        candidate_routes = self.find_routes_between_points(start_lat, start_lon, end_lat, end_lon, max_distance_km=3.0)
        
        if not candidate_routes:
            # Try with larger radius
            candidate_routes = self.find_routes_between_points(start_lat, start_lon, end_lat, end_lon, max_distance_km=5.0)
        
        if not candidate_routes:
            # No routes found - suggest walking
            return self._create_walking_route(start_lat, start_lon, end_lat, end_lon, direct_distance)
        
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
        
        # Sort by preference
        if preference == 'fastest':
            routes.sort(key=lambda x: x['totalDuration'])
        elif preference == 'cheapest':
            routes.sort(key=lambda x: x['totalCost'])
        
        return {'routes': routes}
    
    def _create_bus_route_v2(self, candidate, start_lat, start_lon, end_lat, end_lon, distance, route_num):
        """Create a route object from a candidate (v2 with improved data)"""
        
        route_id = candidate['route_id']
        start_bus = candidate['start_bus']
        end_bus = candidate['end_bus']
        
        # Calculate walking distance to boarding point
        walk_to_start = start_bus['distance_to_start']
        walk_from_end = end_bus['distance_to_end']
        
        # Estimate travel time (assuming 20 km/h average speed in Delhi traffic)
        travel_time_min = int((distance / 20.0) * 60)
        wait_time_min = 5  # Assume 5 min wait
        walk_time_start = int(walk_to_start * 12)  # 12 min per km walking
        walk_time_end = int(walk_from_end * 12)
        
        total_duration = travel_time_min + wait_time_min + walk_time_start + walk_time_end
        
        # Estimate cost (₹10 base + ₹5 per km for bus)
        cost = 10 + int(distance * 5)
        
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
            'details': f'DTC Bus Route {route_id}',
            'duration': travel_time_min,
            'distance': distance,
            'realtimeInfo': f'✓ Live tracking: {candidate["total_buses"]} buses on this route',
            'path': [
                {'lat': start_bus['lat'], 'lng': start_bus['lon']},
                {'lat': end_bus['lat'], 'lng': end_bus['lon']}
            ],
            'stopsList': [
                {
                    'name': f'Board at nearest stop (Route {route_id})',
                    'arrivalTime': 'Now',
                    'platform': 'Check local signage'
                },
                {
                    'name': f'Alight near destination',
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
        
        # Get route name from GTFS data
        route_info = self.route_mapper.get_route_info(route_id, mode='bus')
        route_name = route_info.get('name', f'Bus {route_id}')
        route_long_name = route_info.get('long_name', '')
        
        # Create a clear route name showing the real route ID
        display_name = f"DTC Route {route_id}"
        
        return {
            'id': f'route-{route_num}',
            'routeName': display_name,
            'totalDuration': total_duration,
            'totalCost': cost,
            'comfortScore': 7,  # Good comfort
            'confidenceScore': 0.8,
            'summary': f'Take DTC bus route {route_id} - {distance:.1f} km journey with {candidate["total_buses"]} buses currently running',
            'realtimeInfo': f'✓ {candidate["total_buses"]} buses tracked live on this route',
            'routeDetails': {
                'route_id': route_id,
                'route_name': display_name,
                'route_long_name': route_long_name,
                'is_realtime': True,
                'buses_tracked': candidate["total_buses"]
            },
            'segments': segments
        }
    
    def _create_walking_route(self, start_lat, start_lon, end_lat, end_lon, distance):
        """Create a walking-only route when no buses are found"""
        
        walk_time = int(distance * 12)  # 12 min per km
        
        return {
            'routes': [{
                'id': 'route-walk',
                'routeName': 'Walking Route',
                'totalDuration': walk_time,
                'totalCost': 0,
                'comfortScore': 4,
                'confidenceScore': 1.0,
                'summary': f'Walk {distance:.1f} km to destination',
                'realtimeInfo': 'No buses found nearby - walking suggested',
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
            }]
        }

# Singleton instance
_planner = None

def get_planner():
    """Get or create planner instance"""
    global _planner
    if _planner is None:
        _planner = SimpleRoutePlanner()
    return _planner
