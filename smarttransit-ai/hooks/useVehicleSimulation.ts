import { useState, useEffect } from 'react';
import { RouteSegment, TransportMode, SimulatedVehicle } from '../types';

const SIMULATION_INTERVAL_MS = 2000; // Update every 2 seconds

export const useVehicleSimulation = (segments: RouteSegment[]): SimulatedVehicle[] => {
  const [simulatedVehicles, setSimulatedVehicles] = useState<SimulatedVehicle[]>([]);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    if (segments.length === 0) {
      setSimulatedVehicles([]);
      return;
    }

    const transitSegments = segments
      .map((segment, index) => ({ ...segment, originalIndex: index }))
      .filter(
        (seg) => (seg.mode === TransportMode.BUS || seg.mode === TransportMode.METRO)
      );
    
    if (transitSegments.length === 0) {
        setSimulatedVehicles([]);
        return;
    }

    const intervalId = setInterval(() => {
      const elapsedMs = Date.now() - startTime;

      const newPositions = transitSegments.map((segment): SimulatedVehicle => {
        // Loop the vehicle along its path for the duration of the simulation
        const progress = (elapsedMs % (segment.duration * 60 * 1000)) / (segment.duration * 60 * 1000);
        
        return {
          id: `vehicle-${segment.originalIndex}-${segment.mode}`,
          segmentIndex: segment.originalIndex,
          progress: progress,
          mode: segment.mode,
        };
      });

      setSimulatedVehicles(newPositions);
    }, SIMULATION_INTERVAL_MS);

    // Initial position set
    setSimulatedVehicles(transitSegments.map(segment => ({
        id: `vehicle-${segment.originalIndex}-${segment.mode}`,
        segmentIndex: segment.originalIndex,
        progress: 0,
        mode: segment.mode,
    })));

    return () => clearInterval(intervalId);
  }, [segments, startTime]);

  return simulatedVehicles;
};