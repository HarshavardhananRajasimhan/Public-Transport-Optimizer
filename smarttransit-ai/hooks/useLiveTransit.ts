import { useState, useEffect } from 'react';
import { fetchLiveVehiclePositions } from '../services/transitApiService';
import { VehiclePosition } from '../types';

const POLLING_INTERVAL_MS = 15000; // Fetch new data every 15 seconds

export const useLiveTransit = (isEnabled: boolean): VehiclePosition[] => {
  const [liveVehicles, setLiveVehicles] = useState<VehiclePosition[]>([]);

  useEffect(() => {
    if (!isEnabled) {
      console.log("Live tracking disabled — clearing vehicle data.");
      setLiveVehicles([]);
      return;
    }

    let isMounted = true;

    const getPositions = async () => {
      if (!isMounted) return;
      try {
        const positions = await fetchLiveVehiclePositions();
        if (isMounted) {
          setLiveVehicles(positions);
          console.log(`✅ Updated ${positions.length} live vehicles on map.`);
        }
      } catch (error) {
        console.error("❌ Failed to fetch live vehicle positions:", error);
      }
    };

    // Fetch immediately when enabled
    getPositions();

    // Re-fetch periodically (polling)
    const intervalId = setInterval(getPositions, POLLING_INTERVAL_MS);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
      console.log("🧹 Cleaned up live tracking interval.");
    };
  }, [isEnabled]);

  return liveVehicles;
};
