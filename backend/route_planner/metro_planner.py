"""
Metro route planner for Delhi Metro (DMRC)
Integrates metro routes with bus routes for multi-modal journey planning
"""

import csv
from pathlib import Path
from geopy.distance import geodesic
from datetime import datetime, timedelta
import networkx as nx

class MetroPlanner:
    """Plans routes using Delhi Metro network"""
    
    def __init__(self):
        self.stations = {}  # station_id -> station info
        self.routes = {}    # route_id -> route info
        self.graph = nx.Graph()  # Network graph for pathfinding
        self.station_by_name = {}  # name -> station_id
        self.load_metro_data()
    
    def load_metro_data(self):
        """Load metro stations and routes from GTFS data"""
        metro_dir = Path(__file__).parent.parent.parent / "DMRC_GTFS"
        
        if not metro_dir.exists():
            print("⚠️  DMRC_GTFS folder not found - Metro integration disabled")
            return False
        
        try:
            # Load stations
            self._load_stations(metro_dir / "stops.txt")
            
            # Load routes
            self._load_routes(metro_dir / "routes.txt")
            
            # Build network graph
            self._build_network(metro_dir / "stop_times.txt", metro_dir / "trips.txt")
            
            print(f"✓ Loaded {len(self.stations)} metro stations")
            print(f"✓ Loaded {len(self.routes)} metro lines")
            print(f"✓ Built network with {self.graph.number_of_edges()} connections")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Error loading metro data: {e}")
            return False
    
    def _load_stations(self, stops_file):
        """Load metro stations"""
        with open(stops_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                station_id = row['stop_id']
                station_name = row['stop_name'].strip()
                
                self.stations[station_id] = {
                    'id': station_id,
                    'name': station_name,
                    'lat': float(row['stop_lat']),
                    'lon': float(row['stop_lon'])
                }
                
                # Index by name for easy lookup
                self.station_by_name[station_name.lower()] = station_id
    
    def _load_routes(self, routes_file):
        """Load metro lines"""
        with open(routes_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                route_id = row['route_id']
                route_long_name = row['route_long_name']
                
                # Parse line name (e.g., "RED_Rithala to Shaheed Sthal")
                if '_' in route_long_name:
                    parts = route_long_name.split('_', 1)
                    line_color = parts[0].title()
                    line_desc = parts[1] if len(parts) > 1 else ''
                else:
                    line_color = route_long_name
                    line_desc = ''
                
                self.routes[route_id] = {
                    'id': route_id,
                    'color': line_color,
                    'name': f"{line_color} Line",
                    'description': line_desc,
                    'short_name': row.get('route_short_name', '')
                }
    
    def _build_network(self, stop_times_file, trips_file):
        """Build network graph from stop sequences"""
        # First, load trip to route mapping
        trip_to_route = {}
        with open(trips_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                trip_to_route[row['trip_id']] = row['route_id']
        
        # Group stops by trip
        trip_stops = {}
        with open(stop_times_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                trip_id = row['trip_id']
                if trip_id not in trip_stops:
                    trip_stops[trip_id] = []
                trip_stops[trip_id].append({
                    'stop_id': row['stop_id'],
                    'sequence': int(row['stop_sequence'])
                })
        
        # Build graph edges
        for trip_id, stops in trip_stops.items():
            route_id = trip_to_route.get(trip_id)
            if not route_id:
                continue
            
            # Sort by sequence
            stops.sort(key=lambda x: x['sequence'])
            
            # Connect consecutive stops
            for i in range(len(stops) - 1):
                stop1 = stops[i]['stop_id']
                stop2 = stops[i + 1]['stop_id']
                
                if stop1 in self.stations and stop2 in self.stations:
                    # Calculate distance
                    s1 = self.stations[stop1]
                    s2 = self.stations[stop2]
                    distance = geodesic((s1['lat'], s1['lon']), (s2['lat'], s2['lon'])).km
                    
                    # Add edge (or update if shorter)
                    if self.graph.has_edge(stop1, stop2):
                        if distance < self.graph[stop1][stop2]['distance']:
                            self.graph[stop1][stop2]['distance'] = distance
                            self.graph[stop1][stop2]['route_id'] = route_id
                    else:
                        self.graph.add_edge(stop1, stop2, 
                                          distance=distance, 
                                          route_id=route_id)
    
    def find_nearest_stations(self, lat, lon, max_distance_km=1.5, limit=5):
        """Find nearest metro stations to a location"""
        distances = []
        
        for station_id, station in self.stations.items():
            distance = geodesic((lat, lon), (station['lat'], station['lon'])).km
            if distance <= max_distance_km:
                distances.append({
                    **station,
                    'distance': distance
                })
        
        # Sort by distance
        distances.sort(key=lambda x: x['distance'])
        return distances[:limit]
    
    def plan_metro_route(self, start_lat, start_lon, end_lat, end_lon):
        """
        Plan a metro route between two points
        
        Returns list of possible metro routes
        """
        # Find nearest stations to start and end
        start_stations = self.find_nearest_stations(start_lat, start_lon, max_distance_km=2.0, limit=3)
        end_stations = self.find_nearest_stations(end_lat, end_lon, max_distance_km=2.0, limit=3)
        
        if not start_stations or not end_stations:
            return []
        
        routes = []
        
        # Try to find paths between station pairs
        for start_station in start_stations:
            for end_station in end_stations:
                try:
                    # Find shortest path
                    path = nx.shortest_path(
                        self.graph, 
                        start_station['id'], 
                        end_station['id'],
                        weight='distance'
                    )
                    
                    if len(path) < 2:
                        continue
                    
                    # Calculate route details
                    route_info = self._create_metro_route(
                        path, 
                        start_lat, start_lon,
                        end_lat, end_lon,
                        start_station, 
                        end_station
                    )
                    
                    routes.append(route_info)
                    
                except nx.NetworkXNoPath:
                    continue
                except Exception as e:
                    print(f"Error finding path: {e}")
                    continue
        
        # Sort by total duration
        routes.sort(key=lambda x: x['totalDuration'])
        
        return routes[:3]  # Return top 3
    
    def _create_metro_route(self, path, start_lat, start_lon, end_lat, end_lon, 
                           start_station, end_station):
        """Create a route object from a metro path"""
        
        # Calculate distances
        walk_to_start = start_station['distance']
        walk_from_end = end_station['distance']
        
        # Calculate metro travel distance
        metro_distance = 0
        for i in range(len(path) - 1):
            if self.graph.has_edge(path[i], path[i+1]):
                metro_distance += self.graph[path[i]][path[i+1]]['distance']
        
        # Calculate times (metro average: 40 km/h, walking: 5 km/h)
        metro_time = int((metro_distance / 40.0) * 60)  # minutes
        walk_time_start = int((walk_to_start / 5.0) * 60)
        walk_time_end = int((walk_from_end / 5.0) * 60)
        wait_time = 3  # Metro is more frequent
        
        total_duration = metro_time + walk_time_start + walk_time_end + wait_time
        
        # Calculate cost (Metro: ₹10-60 based on distance)
        if metro_distance < 2:
            cost = 10
        elif metro_distance < 5:
            cost = 20
        elif metro_distance < 12:
            cost = 30
        elif metro_distance < 21:
            cost = 40
        elif metro_distance < 32:
            cost = 50
        else:
            cost = 60
        
        # Determine which lines are used
        lines_used = set()
        for i in range(len(path) - 1):
            if self.graph.has_edge(path[i], path[i+1]):
                route_id = self.graph[path[i]][path[i+1]]['route_id']
                if route_id in self.routes:
                    lines_used.add(self.routes[route_id]['name'])
        
        # Build segments
        segments = []
        
        # Walking to start
        if walk_to_start > 0.1:
            segments.append({
                'mode': 'WALK',
                'details': f'Walk to {start_station["name"]} Metro Station ({walk_to_start:.2f} km)',
                'duration': walk_time_start,
                'distance': walk_to_start,
                'path': [
                    {'lat': start_lat, 'lng': start_lon},
                    {'lat': start_station['lat'], 'lng': start_station['lon']}
                ]
            })
        
        # Metro journey
        metro_stops = []
        for stop_id in path:
            station = self.stations[stop_id]
            metro_stops.append({
                'name': station['name'],
                'lat': station['lat'],
                'lon': station['lon']
            })
        
        segments.append({
            'mode': 'METRO',
            'details': f'Delhi Metro: {" → ".join(lines_used)}',
            'duration': metro_time,
            'distance': metro_distance,
            'realtimeInfo': f'✓ {len(path)} stations, {len(lines_used)} line(s)',
            'path': [{'lat': s['lat'], 'lng': s['lon']} for s in metro_stops],
            'stopsList': [
                {
                    'name': start_station['name'],
                    'arrivalTime': 'Now',
                    'platform': 'Check station signage'
                },
                {
                    'name': end_station['name'],
                    'arrivalTime': f'~{metro_time} min',
                    'platform': ''
                }
            ],
            'stations': [s['name'] for s in metro_stops]
        })
        
        # Walking from end
        if walk_from_end > 0.1:
            segments.append({
                'mode': 'WALK',
                'details': f'Walk to destination ({walk_from_end:.2f} km)',
                'duration': walk_time_end,
                'distance': walk_from_end,
                'path': [
                    {'lat': end_station['lat'], 'lng': end_station['lon']},
                    {'lat': end_lat, 'lng': end_lon}
                ]
            })
        
        lines_str = ", ".join(lines_used)
        
        return {
            'id': f'metro-{start_station["id"]}-{end_station["id"]}',
            'routeName': f'Delhi Metro ({lines_str})',
            'totalDuration': total_duration,
            'totalCost': cost,
            'comfortScore': 9,  # Metro is very comfortable
            'confidenceScore': 0.95,  # High confidence for metro
            'summary': f'Take Delhi Metro {lines_str} - {metro_distance:.1f} km, {len(path)} stations',
            'realtimeInfo': f'✓ Metro route via {len(path)} stations',
            'routeDetails': {
                'mode': 'metro',
                'lines': list(lines_used),
                'stations': len(path),
                'distance': metro_distance,
                'start_station': start_station['name'],
                'end_station': end_station['name']
            },
            'segments': segments
        }

# Singleton instance
_metro_planner = None

def get_metro_planner():
    """Get or create metro planner instance"""
    global _metro_planner
    if _metro_planner is None:
        _metro_planner = MetroPlanner()
    return _metro_planner
