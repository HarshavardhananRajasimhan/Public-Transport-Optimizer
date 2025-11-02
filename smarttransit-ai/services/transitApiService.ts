import { TransportMode, VehiclePosition } from "../types";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

export const fetchLiveVehiclePositions = async (): Promise<VehiclePosition[]> => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/live`);
    if (!response.ok) {
      throw new Error(`Failed to fetch live vehicle data. Status: ${response.status}`);
    }

    const data = await response.json();
    const vehiclePositions: VehiclePosition[] = data.map((bus: any) => ({
      id: bus.vehicle_id || bus.id,
      lat: bus.latitude,
      lng: bus.longitude,
      mode: TransportMode.BUS,
    }));

    console.log(`Fetched ${vehiclePositions.length} live bus positions.`);
    return vehiclePositions;
  } catch (error) {
    console.error("Error fetching live vehicle data:", error);
    return [];
  }
};
