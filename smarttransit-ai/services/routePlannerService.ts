import { Route, RoutePreferences } from '../types';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

export interface RouteRequest {
  start: {
    lat: number;
    lon: number;
    name: string;
  };
  end: {
    lat: number;
    lon: number;
    name: string;
  };
  preference: string;
}

/**
 * Plan a route using real transit data from the backend
 * This replaces the AI-generated fake routes with real route planning
 */
export const planRouteWithRealData = async (
  startName: string,
  endName: string,
  preferences: RoutePreferences
): Promise<Route[]> => {
  try {
    // For now, use approximate coordinates for Delhi locations
    // In a full implementation, you'd geocode the location names
    const startCoords = getApproximateCoordinates(startName);
    const endCoords = getApproximateCoordinates(endName);

    const request: RouteRequest = {
      start: {
        lat: startCoords.lat,
        lon: startCoords.lon,
        name: startName
      },
      end: {
        lat: endCoords.lat,
        lon: endCoords.lon,
        name: endName
      },
      preference: preferences.priority.toLowerCase()
    };

    const response = await fetch(`${BACKEND_URL}/api/plan-route`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Route planning failed: ${response.status}`);
    }

    const data = await response.json();
    
    console.log('Backend response:', data);

    if (data.error) {
      throw new Error(data.error);
    }

    if (!data.routes || data.routes.length === 0) {
      throw new Error('No routes found');
    }

    console.log('Returning routes:', data.routes);
    return data.routes as Route[];

  } catch (error) {
    console.error('Error planning route:', error);
    throw new Error('Failed to plan route with real data. Please try again.');
  }
};

/**
 * Get approximate coordinates for common Delhi locations
 * In a full implementation, use a geocoding service
 */
function getApproximateCoordinates(locationName: string): { lat: number; lon: number } {
  const locations: Record<string, { lat: number; lon: number }> = {
    // Central Delhi
    'connaught place': { lat: 28.6315, lon: 77.2167 },
    'india gate': { lat: 28.6129, lon: 77.2295 },
    'red fort': { lat: 28.6562, lon: 77.2410 },
    'chandni chowk': { lat: 28.6506, lon: 77.2303 },
    'rajiv chowk': { lat: 28.6328, lon: 77.2197 },
    
    // South Delhi
    'nehru place': { lat: 28.5494, lon: 77.2501 },
    'saket': { lat: 28.5244, lon: 77.2066 },
    'hauz khas': { lat: 28.5494, lon: 77.2001 },
    'greater kailash': { lat: 28.5494, lon: 77.2428 },
    
    // North Delhi
    'kashmere gate': { lat: 28.6692, lon: 77.2289 },
    'civil lines': { lat: 28.6778, lon: 77.2244 },
    
    // East Delhi
    'laxmi nagar': { lat: 28.6345, lon: 77.2767 },
    'preet vihar': { lat: 28.6097, lon: 77.2956 },
    
    // West Delhi
    'rajouri garden': { lat: 28.6410, lon: 77.1214 },
    'janakpuri': { lat: 28.6219, lon: 77.0831 },
    
    // Airports
    'igi airport': { lat: 28.5562, lon: 77.1000 },
    'airport': { lat: 28.5562, lon: 77.1000 },
  };

  const normalized = locationName.toLowerCase().trim();
  
  // Try exact match
  if (locations[normalized]) {
    return locations[normalized];
  }

  // Try partial match
  for (const [key, coords] of Object.entries(locations)) {
    if (normalized.includes(key) || key.includes(normalized)) {
      return coords;
    }
  }

  // Default to Connaught Place if no match
  console.warn(`Location "${locationName}" not found, using default coordinates`);
  return { lat: 28.6315, lon: 77.2167 };
}

/**
 * Get nearby buses for a location
 */
export const getNearbyBuses = async (lat: number, lon: number, radius: number = 1.0) => {
  try {
    const response = await fetch(
      `${BACKEND_URL}/api/nearby-buses?lat=${lat}&lon=${lon}&radius=${radius}`
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch nearby buses: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching nearby buses:', error);
    return { buses: [], count: 0 };
  }
};

/**
 * Get list of active routes
 */
export const getActiveRoutes = async () => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/routes`);

    if (!response.ok) {
      throw new Error(`Failed to fetch routes: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching routes:', error);
    return { routes: [], total_routes: 0, total_buses: 0 };
  }
};
