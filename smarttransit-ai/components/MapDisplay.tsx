/// <reference types="leaflet" />

import React, { useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  Tooltip,
  useMap,

} from "react-leaflet";
import L from "leaflet";
import ReactDOMServer from "react-dom/server";
import { Route, TransportMode, VehiclePosition } from "../types";
import { useLiveTransit } from "../hooks/useLiveTransit";
import { MapBusIcon } from "./icons/MapBusIcon";
import { MapMetroIcon } from "./icons/MapMetroIcon";
import { StartPinIcon } from "./icons/StartPinIcon";
import { EndPinIcon } from "./icons/EndPinIcon";

interface MapDisplayProps {
  route: Route;
  vehiclePositions: VehiclePosition[];
  highlightedSegmentIndex?: number | null;
}

const createDivIcon = (component: React.ReactElement) => {
  return L.divIcon({
    html: ReactDOMServer.renderToString(component),
    className: "bg-transparent border-0",
    iconSize: [32, 32] as [number, number],
    iconAnchor: [16, 32] as [number, number],
    popupAnchor: [0, -32] as [number, number],
  });
};

const startIcon = createDivIcon(<StartPinIcon />);
const endIcon = createDivIcon(<EndPinIcon />);

const getVehicleIcon = (mode: TransportMode, isLiveGlobal: boolean = false) => {
  const component =
    mode === TransportMode.BUS ? (
      <MapBusIcon isLive={isLiveGlobal} />
    ) : (
      <MapMetroIcon isLive={isLiveGlobal} />
    );
  return createDivIcon(component);
};

const segmentColors: Record<TransportMode, string> = {
  [TransportMode.WALK]: "#10b981",
  [TransportMode.BUS]: "#3b82f6",
  [TransportMode.METRO]: "#8b5cf6",
  [TransportMode.AUTO_RICKSHAW]: "#f59e0b",
};

const MapEffect: React.FC<{
  route: Route;
  highlightedSegmentIndex: number | null | undefined;
}> = ({ route, highlightedSegmentIndex }) => {
  const map = useMap();

  useEffect(() => {
    if (
      highlightedSegmentIndex !== null &&
      highlightedSegmentIndex !== undefined &&
      route.segments[highlightedSegmentIndex]?.path?.length > 0
    ) {
      const segment = route.segments[highlightedSegmentIndex];
      const bounds = L.latLngBounds(
        segment.path!.map((p) => [p.lat, p.lng] as [number, number])
      );
      map.flyToBounds(bounds, {
        padding: [80, 80] as [number, number],
        duration: 0.8,
        maxZoom: 15,
      });
    } else {
      const allPaths = route.segments.flatMap((s) => s.path || []);
      if (allPaths.length > 1) {
        const bounds = L.latLngBounds(
          allPaths.map((p) => [p.lat, p.lng] as [number, number])
        );
        map.flyToBounds(bounds, {
          padding: [80, 80] as [number, number],
          duration: 0.8,
        });
      }
    }
  }, [highlightedSegmentIndex, route, map]);

  return null;
};

export const MapDisplay: React.FC<MapDisplayProps> = ({
  route,
  vehiclePositions,
  highlightedSegmentIndex,
}) => {
  const [showLiveTransit, setShowLiveTransit] = useState(true);
  const liveVehicles = useLiveTransit(showLiveTransit);

  const allPaths = route.segments.flatMap((s) => s.path || []);
  if (allPaths.length < 2) {
    return (
      <div className="h-96 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl border border-slate-200">
        <p className="text-slate-400 font-medium">Map data unavailable</p>
      </div>
    );
  }

  const bounds = L.latLngBounds(
    allPaths.map((p) => [p.lat, p.lng] as [number, number])
  );
  const startPoint = allPaths[0];
  const endPoint = allPaths[allPaths.length - 1];

  return (
    <div className="relative">
      {/* Toggle Live Transit */}
      <div className="absolute top-4 right-4 z-10 bg-white/95 backdrop-blur-md rounded-xl shadow-lg border border-slate-200/50 px-4 py-2.5">
        <label
          htmlFor="live-transit-toggle"
          className="flex items-center cursor-pointer gap-3"
        >
          <span className="text-sm font-semibold text-slate-700">
            Live Transit
          </span>
          <div className="relative">
            <input
              type="checkbox"
              id="live-transit-toggle"
              className="sr-only peer"
              checked={showLiveTransit}
              onChange={() => setShowLiveTransit(!showLiveTransit)}
            />
            <div className="w-11 h-6 bg-slate-200 rounded-full peer-checked:bg-blue-500 transition-all duration-300 shadow-inner"></div>
            <div className="absolute left-0.5 top-0.5 bg-white w-5 h-5 rounded-full transition-all duration-300 peer-checked:translate-x-5 shadow-md"></div>
          </div>
        </label>
      </div>

      {/* Map */}
      <div className="rounded-2xl overflow-hidden shadow-2xl border border-slate-200/50 bg-white">
        <MapContainer
          bounds={bounds}
          className="z-0"
          zoomControl={false}
          //zoomControl={false}
        >
          <MapEffect
            route={route}
            highlightedSegmentIndex={highlightedSegmentIndex}
          />

          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            subdomains={["a", "b", "c", "d"]}
          />

          {/* Route Segments */}
          {route.segments.map((segment, index) => {
            if (segment.path && segment.path.length > 0) {
              const isHighlighted = index === highlightedSegmentIndex;
              return (
                <React.Fragment key={index}>
                  <Polyline
                    positions={segment.path.map(
                      (p) => [p.lat, p.lng] as [number, number]
                    )}
                    color="white"
                    weight={isHighlighted ? 11 : 7}
                    opacity={0.5}
                  />
                  <Polyline
                    positions={segment.path.map(
                      (p) => [p.lat, p.lng] as [number, number]
                    )}
                    color={segmentColors[segment.mode] || "#94a3b8"}
                    weight={isHighlighted ? 7 : 4}
                    opacity={isHighlighted ? 1.0 : 0.85}
                    className="transition-all"
                  />
                </React.Fragment>
              );
            }
            return null;
          })}

          {/* Start and End Markers */}
          <Marker
            position={[startPoint.lat, startPoint.lng] as [number, number]}
            icon={startIcon}
          >
            <Tooltip
              permanent
              direction="top"
              offset={[0, -32] as [number, number]}
              className="font-semibold"
            >
              Start
            </Tooltip>
          </Marker>

          <Marker
            position={[endPoint.lat, endPoint.lng] as [number, number]}
            icon={endIcon}
          >
            <Tooltip
              permanent={true}
              direction="top"
              offset={[0, -32] as [number, number]}
              className="font-semibold"
            >
              End
            </Tooltip>
          </Marker>

          {/* Vehicle Positions */}
          {vehiclePositions.map((vehicle) => (
            <Marker
              key={vehicle.id}
              position={[vehicle.lat, vehicle.lng] as [number, number]}
              icon={getVehicleIcon(vehicle.mode)}
            >
              <Tooltip
                direction="top"
                offset={[0, -28] as [number, number]}
                className="font-medium"
              >
                Your {vehicle.mode === TransportMode.BUS ? "Bus" : "Metro"}
              </Tooltip>
            </Marker>
          ))}

          {/* Live Vehicles */}
          {liveVehicles.map((vehicle) => (
            <Marker
              key={vehicle.id}
              position={[vehicle.lat, vehicle.lng] as [number, number]}
              icon={getVehicleIcon(vehicle.mode, true)}
            >
              <Tooltip
                direction="top"
                offset={[0, -28] as [number, number]}
                className="font-medium"
              >
                Live {vehicle.mode === TransportMode.BUS ? "Bus" : "Metro"}
              </Tooltip>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
};