"""
Map route IDs to human-readable names using GTFS data
"""

import csv
from pathlib import Path

class GTFSRouteMapper:
    """Maps route IDs to route names from GTFS data"""
    
    def __init__(self):
        self.bus_routes = {}
        self.bus_routes_by_number = {}  # Map route numbers to route info
        self.metro_routes = {}
        self.load_routes()
    
    def load_routes(self):
        """Load route data from GTFS files"""
        # Load bus routes from GTFS folder
        bus_gtfs_dir = Path(__file__).parent.parent.parent / "GTFS"
        if (bus_gtfs_dir / "routes.txt").exists():
            self._load_bus_routes(bus_gtfs_dir / "routes.txt")
        else:
            # Try alternative location
            bus_gtfs_dir = Path(__file__).parent.parent / "gtfs_data"
            if (bus_gtfs_dir / "routes.txt").exists():
                self._load_bus_routes(bus_gtfs_dir / "routes.txt")
        
        # Load metro routes
        metro_gtfs_dir = Path(__file__).parent.parent.parent / "DMRC_GTFS"
        if (metro_gtfs_dir / "routes.txt").exists():
            self._load_metro_routes(metro_gtfs_dir / "routes.txt")
    
    def _load_bus_routes(self, routes_file):
        """Load bus route names"""
        try:
            import re
            with open(routes_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    route_id = row.get('route_id', '')
                    route_short_name = row.get('route_short_name', '').strip()
                    route_long_name = row.get('route_long_name', '').strip()
                    
                    # Extract route number from long name (e.g., "828AUP" -> "828A")
                    route_number = None
                    direction = ''
                    
                    if route_long_name:
                        # Extract just the number part (e.g., "828AUP" -> "828")
                        match = re.match(r'(\d+)([A-Z]*)', route_long_name)
                        if match:
                            route_number = match.group(1)  # Just the number
                            suffix = match.group(2) if match.group(2) else ''
                            
                            # Determine direction
                            if 'UP' in route_long_name:
                                direction = 'UP'
                            elif 'DOWN' in route_long_name or 'DWN' in route_long_name:
                                direction = 'DOWN'
                            
                            # Create display name
                            if suffix and suffix not in ['UP', 'DOWN', 'DWN', 'STL', 'STLUP', 'STLDOWN', 'STLDOWN2']:
                                name = f"Route {route_number}{suffix}"
                            else:
                                name = f"Route {route_number}"
                            
                            if direction:
                                name += f" ({direction})"
                        else:
                            name = f"Route {route_long_name}"
                            route_number = route_long_name
                    elif route_short_name:
                        name = f"Route {route_short_name}"
                        route_number = route_short_name
                    else:
                        name = f"Bus {route_id}"
                    
                    route_info = {
                        'name': name,
                        'long_name': route_long_name,
                        'short_name': route_short_name,
                        'route_number': route_number,
                        'direction': direction,
                        'type': 'bus'
                    }
                    
                    # Store by GTFS route_id
                    self.bus_routes[route_id] = route_info
                    
                    # Also store by route number for easier lookup
                    if route_number:
                        if route_number not in self.bus_routes_by_number:
                            self.bus_routes_by_number[route_number] = []
                        self.bus_routes_by_number[route_number].append(route_info)
                    
            print(f"✓ Loaded {len(self.bus_routes)} bus routes from GTFS")
            print(f"✓ Indexed {len(self.bus_routes_by_number)} unique route numbers")
        except Exception as e:
            print(f"⚠ Could not load bus routes: {e}")
    
    def _load_metro_routes(self, routes_file):
        """Load metro route names and colors"""
        try:
            with open(routes_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    route_id = row.get('route_id', '')
                    route_short_name = row.get('route_short_name', '')
                    route_long_name = row.get('route_long_name', '')
                    route_color = row.get('route_color', '')
                    
                    # Parse the route name (e.g., "R_RS" -> "RED Line")
                    line_name = self._parse_metro_line_name(route_short_name, route_long_name)
                    
                    self.metro_routes[route_id] = {
                        'name': line_name,
                        'long_name': route_long_name,
                        'color': f'#{route_color}' if route_color else None,
                        'type': 'metro'
                    }
            print(f"✓ Loaded {len(self.metro_routes)} metro routes")
        except Exception as e:
            print(f"⚠ Could not load metro routes: {e}")
    
    def _parse_metro_line_name(self, short_name, long_name):
        """Parse metro line name from GTFS data"""
        # Extract color from long_name (e.g., "RED_Rithala to Shaheed Sthal")
        if long_name and '_' in long_name:
            parts = long_name.split('_')
            color = parts[0]
            return f"{color.title()} Line"
        
        # Fallback to short name
        if short_name:
            return short_name
        
        return "Metro Line"
    
    def get_route_name(self, route_id, mode='bus'):
        """Get human-readable route name"""
        if mode == 'metro':
            route_info = self.metro_routes.get(str(route_id))
            if route_info:
                return route_info['name']
        else:
            # Try exact match first
            route_info = self.bus_routes.get(str(route_id))
            if route_info:
                return route_info['name']
            
            # Try matching by route number (real-time ID might match route number)
            route_info = self.bus_routes_by_number.get(str(route_id))
            if route_info and len(route_info) > 0:
                # If multiple routes with same number, return the first one
                return route_info[0]['name']
        
        # Fallback
        return f"{'Metro' if mode == 'metro' else 'Bus'} {route_id}"
    
    def get_route_info(self, route_id, mode='bus'):
        """Get full route information"""
        if mode == 'metro':
            return self.metro_routes.get(str(route_id), {
                'name': f'Metro {route_id}',
                'type': 'metro'
            })
        else:
            # Try exact match first
            route_info = self.bus_routes.get(str(route_id))
            if route_info:
                return route_info
            
            # Try matching by route number
            route_list = self.bus_routes_by_number.get(str(route_id))
            if route_list and len(route_list) > 0:
                return route_list[0]
            
            # Fallback
            return {
                'name': f'Bus {route_id}',
                'long_name': '',
                'type': 'bus'
            }

# Singleton instance
_mapper = None

def get_route_mapper():
    """Get or create route mapper instance"""
    global _mapper
    if _mapper is None:
        _mapper = GTFSRouteMapper()
    return _mapper
