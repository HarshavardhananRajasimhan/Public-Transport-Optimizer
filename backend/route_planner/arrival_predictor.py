"""
Real-time arrival prediction for buses
Calculates when buses will reach user's location based on:
- Current bus position
- Historical speed tracking
- Distance to user
- Time of day patterns
"""

from datetime import datetime, timedelta
from geopy.distance import geodesic
from collections import defaultdict
import math

class ArrivalPredictor:
    """Predicts when buses will arrive at user's location"""
    
    def __init__(self):
        self.bus_history = defaultdict(list)  # Track bus positions over time
        self.speed_cache = {}  # Cache calculated speeds
        self.last_cleanup = datetime.now()
    
    def update_bus_position(self, bus_id, lat, lon, timestamp):
        """Track bus position over time to calculate speed"""
        self.bus_history[bus_id].append({
            'lat': lat,
            'lon': lon,
            'timestamp': timestamp,
            'time': datetime.now()
        })
        
        # Keep only last 10 positions (last ~10 minutes)
        if len(self.bus_history[bus_id]) > 10:
            self.bus_history[bus_id] = self.bus_history[bus_id][-10:]
        
        # Cleanup old data every hour
        if (datetime.now() - self.last_cleanup).seconds > 3600:
            self._cleanup_old_data()
    
    def _cleanup_old_data(self):
        """Remove buses that haven't been seen in 30 minutes"""
        cutoff = datetime.now() - timedelta(minutes=30)
        buses_to_remove = []
        
        for bus_id, history in self.bus_history.items():
            if not history or history[-1]['time'] < cutoff:
                buses_to_remove.append(bus_id)
        
        for bus_id in buses_to_remove:
            del self.bus_history[bus_id]
            if bus_id in self.speed_cache:
                del self.speed_cache[bus_id]
        
        self.last_cleanup = datetime.now()
    
    def calculate_bus_speed(self, bus_id):
        """
        Calculate bus's current speed based on recent positions
        Returns speed in km/h
        """
        if bus_id not in self.bus_history:
            return None
        
        history = self.bus_history[bus_id]
        
        if len(history) < 2:
            return None
        
        # Calculate speed from last 2-3 positions
        recent = history[-3:] if len(history) >= 3 else history[-2:]
        
        total_distance = 0
        total_time = 0
        
        for i in range(len(recent) - 1):
            pos1 = recent[i]
            pos2 = recent[i + 1]
            
            # Distance in km
            distance = geodesic(
                (pos1['lat'], pos1['lon']),
                (pos2['lat'], pos2['lon'])
            ).km
            
            # Time in hours
            time_diff = (pos2['time'] - pos1['time']).seconds / 3600.0
            
            if time_diff > 0:
                total_distance += distance
                total_time += time_diff
        
        if total_time > 0:
            speed = total_distance / total_time  # km/h
            self.speed_cache[bus_id] = speed
            return speed
        
        return None
    
    def calculate_bearing(self, lat1, lon1, lat2, lon2):
        """Calculate bearing between two points"""
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlon = lon2 - lon1
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        bearing = math.atan2(x, y)
        return (math.degrees(bearing) + 360) % 360
    
    def is_bus_approaching(self, bus_lat, bus_lon, user_lat, user_lon):
        """
        Check if bus is moving towards user or away
        Returns: 'approaching', 'moving_away', or 'unknown'
        """
        bus_id = f"{bus_lat}_{bus_lon}"  # Temporary ID
        
        if bus_id not in self.bus_history or len(self.bus_history[bus_id]) < 2:
            return 'unknown'
        
        history = self.bus_history[bus_id]
        
        # Get previous position
        prev_pos = history[-2]
        curr_pos = history[-1]
        
        # Distance from previous position to user
        prev_distance = geodesic(
            (prev_pos['lat'], prev_pos['lon']),
            (user_lat, user_lon)
        ).km
        
        # Distance from current position to user
        curr_distance = geodesic(
            (curr_pos['lat'], curr_pos['lon']),
            (user_lat, user_lon)
        ).km
        
        # If getting closer, it's approaching
        if curr_distance < prev_distance:
            return 'approaching'
        else:
            return 'moving_away'
    
    def predict_arrival_time(self, bus, user_lat, user_lon):
        """
        Predict when bus will arrive at user's location
        
        Returns:
        {
            'eta_minutes': int,
            'eta_time': datetime,
            'confidence': float (0-1),
            'status': 'approaching' | 'moving_away' | 'stationary',
            'speed_kmh': float
        }
        """
        bus_id = bus.get('id')
        bus_lat = bus.get('lat')
        bus_lon = bus.get('lon')
        
        # Calculate distance to user
        distance_km = geodesic((bus_lat, bus_lon), (user_lat, user_lon)).km
        
        # Update position history
        self.update_bus_position(
            bus_id, 
            bus_lat, 
            bus_lon, 
            bus.get('timestamp', 0)
        )
        
        # Calculate bus speed
        speed = self.calculate_bus_speed(bus_id)
        
        # Determine if approaching
        status = self.is_bus_approaching(bus_lat, bus_lon, user_lat, user_lon)
        
        # Default values
        default_speed = self._get_default_speed_by_time()
        
        if speed is None:
            # No history, use default speed
            speed = default_speed
            confidence = 0.3  # Low confidence
        elif speed < 1:
            # Bus is stationary or very slow
            status = 'stationary'
            speed = default_speed  # Assume it will start moving
            confidence = 0.2
        else:
            # We have real speed data
            confidence = min(0.9, 0.5 + (len(self.bus_history[bus_id]) * 0.05))
        
        # Adjust speed based on status
        if status == 'moving_away':
            # Bus is going away, might come back on route
            # Assume it needs to complete loop
            speed = speed * 0.5  # Will take longer
            confidence = confidence * 0.5
        
        # Calculate ETA
        if speed > 0:
            eta_hours = distance_km / speed
            eta_minutes = int(eta_hours * 60)
            
            # Add buffer for stops (1 min per km)
            stop_buffer = int(distance_km * 1)
            eta_minutes += stop_buffer
            
            # Cap at reasonable values
            eta_minutes = max(1, min(eta_minutes, 120))  # 1-120 minutes
            
            eta_time = datetime.now() + timedelta(minutes=eta_minutes)
        else:
            eta_minutes = 999
            eta_time = None
            confidence = 0
        
        return {
            'eta_minutes': eta_minutes,
            'eta_time': eta_time,
            'confidence': round(confidence, 2),
            'status': status,
            'speed_kmh': round(speed, 1) if speed else 0,
            'distance_km': round(distance_km, 2)
        }
    
    def _get_default_speed_by_time(self):
        """Get default speed based on time of day (traffic patterns)"""
        hour = datetime.now().hour
        
        # Peak hours: slower
        if 8 <= hour <= 10 or 17 <= hour <= 20:
            return 15  # km/h (heavy traffic)
        # Mid-day: moderate
        elif 10 < hour < 17:
            return 22  # km/h (moderate traffic)
        # Night: faster
        else:
            return 30  # km/h (light traffic)
    
    def get_next_buses_at_stop(self, user_lat, user_lon, route_id, buses, limit=3):
        """
        Get next N buses arriving at user's location for a specific route
        
        Returns list of buses with arrival predictions, sorted by ETA
        """
        predictions = []
        
        for bus in buses:
            if bus.get('route_id') != route_id:
                continue
            
            prediction = self.predict_arrival_time(bus, user_lat, user_lon)
            
            # Only include approaching or unknown buses
            if prediction['status'] in ['approaching', 'unknown']:
                predictions.append({
                    'bus_id': bus.get('id'),
                    'vehicle_label': bus.get('vehicle_id', bus.get('id')),
                    **prediction
                })
        
        # Sort by ETA
        predictions.sort(key=lambda x: x['eta_minutes'])
        
        return predictions[:limit]
    
    def format_arrival_time(self, eta_minutes):
        """Format ETA in human-readable form"""
        if eta_minutes < 1:
            return "Arriving now"
        elif eta_minutes == 1:
            return "1 minute"
        elif eta_minutes < 60:
            return f"{eta_minutes} minutes"
        else:
            hours = eta_minutes // 60
            mins = eta_minutes % 60
            if mins == 0:
                return f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                return f"{hours}h {mins}m"

# Singleton instance
_predictor = None

def get_arrival_predictor():
    """Get or create arrival predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = ArrivalPredictor()
    return _predictor
