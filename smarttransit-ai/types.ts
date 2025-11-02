
export enum TransportMode {
  WALK = 'WALK',
  BUS = 'BUS',
  METRO = 'METRO',
  AUTO_RICKSHAW = 'AUTO_RICKSHAW',
}

export interface StopDetail {
  name: string;
  platform?: string;
  arrivalTime?: string;
  departureTime?: string;
}

export interface RouteSegment {
  mode: TransportMode;
  details: string; // e.g., "Bus 505" or "Walk to Rajiv Chowk Station"
  duration: number; // in minutes
  distance?: number; // in km, optional
  stops?: number; // number of stops, optional
  realtimeInfo?: string; // e.g., "Running 10 minutes late"
  path?: { lat: number; lng: number }[]; // Array of coordinates for map polyline
  stopsList?: StopDetail[]; // List of key stops in the segment
}

export interface Route {
  id: string;
  routeName: string;
  totalDuration: number; // in minutes
  totalCost: number; // in INR
  comfortScore: number; // 1 to 10
  confidenceScore: number; // 0.0 to 1.0
  segments: RouteSegment[];
  summary: string;
  realtimeInfo?: string; // A top-level summary of real-time conditions affecting the route
}

export enum Preference {
  FASTEST = 'FASTEST',
  CHEAPEST = 'CHEAPEST',
  BALANCED = 'BALANCED',
  COMFORT = 'COMFORT',
}

export interface RoutePreferences {
  priority: Preference;
  // Future preferences can be added here
  // e.g. maxWalkingMinutes: number;
  // avoidTransfers: boolean;
}

export interface VehiclePosition {
  id: string;
  lat: number;
  lng: number;
  mode: TransportMode;
}

export interface SimulatedVehicle {
  id: string;
  segmentIndex: number;
  progress: number; // 0.0 to 1.0 progress within the segment
  mode: TransportMode;
}