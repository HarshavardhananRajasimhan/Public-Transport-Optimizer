import React from 'react';
import { Route, RouteSegment, SimulatedVehicle, StopDetail, TransportMode } from '../types';
import { transportInfo } from './RouteCard';
import { BusIcon } from './icons/BusIcon';
import { TrainIcon } from './icons/TrainIcon';

interface StopByStopDisplayProps {
  route: Route;
  simulatedVehicles: SimulatedVehicle[];
}

const getVehicleIcon = (mode: TransportMode) => {
    switch (mode) {
        case TransportMode.BUS:
            return <BusIcon className="w-full h-full text-white" />;
        case TransportMode.METRO:
            return <TrainIcon className="w-full h-full text-white" />;
        default:
            return null;
    }
}

const SegmentTimeline: React.FC<{ segment: RouteSegment, vehicle?: SimulatedVehicle }> = ({ segment, vehicle }) => {
    if (!segment.stopsList || segment.stopsList.length === 0) {
        return null;
    }

    const info = transportInfo[segment.mode];
    const stopCount = segment.stopsList.length;

    const vehicleProgress = vehicle?.progress ?? -1;
    let vehiclePositionStyle = {};
    if (vehicleProgress >= 0 && stopCount > 1) {
        // Calculate the position based on progress between stops
        const progressBetweenStops = vehicleProgress * (stopCount - 1);
        const currentStopIndex = Math.floor(progressBetweenStops);
        const nextStopIndex = Math.ceil(progressBetweenStops);
        const progressWithinSegment = progressBetweenStops - currentStopIndex;
        
        const topPerStop = 100 / (stopCount - 1);
        const top = (currentStopIndex * topPerStop) + (progressWithinSegment * topPerStop);

        vehiclePositionStyle = {
            top: `calc(${top}% - 12px)`, // Adjust for icon size
            transition: 'top 2s linear',
        };
    }

    return (
        <div className="ml-12 pl-8 pr-4 py-4 relative border-l-2 border-slate-300">
            {/* Vehicle Icon */}
            {vehicle && (
                <div
                    className={`absolute left-[-13px] w-6 h-6 rounded-full flex items-center justify-center p-0.5 z-20 ${info.bgColor} shadow-lg`}
                    style={vehiclePositionStyle}
                >
                    <div className={`${info.bgColor} rounded-full p-0.5`}>
                      {getVehicleIcon(segment.mode)}
                    </div>
                </div>
            )}
            
            {segment.stopsList.map((stop, index) => (
                <div key={index} className={`relative pb-8 ${index === stopCount - 1 ? 'pb-0' : ''}`}>
                    {/* Stop Dot */}
                    <div className="absolute left-[-37px] top-1 w-4 h-4 rounded-full bg-white border-4 border-slate-400 z-10"></div>
                    
                    <div className="flex justify-between items-center">
                        <p className="font-bold text-slate-800">{stop.name}</p>
                        {stop.platform && (
                            <div className="text-xs font-bold text-slate-600 bg-slate-200 px-2 py-0.5 rounded-md">
                                Platform {stop.platform}
                            </div>
                        )}
                    </div>

                    <div className="flex justify-between items-center text-sm text-slate-500 mt-1">
                        <span>Arrival: {stop.arrivalTime || ' --:--'}</span>
                        <span className="text-red-600 font-semibold">{stop.departureTime || ' --:--'} :Departure</span>
                    </div>
                </div>
            ))}
        </div>
    );
};

export const StopByStopDisplay: React.FC<StopByStopDisplayProps> = ({ route, simulatedVehicles }) => {
    return (
        <div className="bg-white p-4 rounded-lg border border-slate-200">
            <h4 className="text-lg font-bold text-slate-800 mb-4">Live Journey View</h4>
            <div className="space-y-2">
                {route.segments.map((segment, index) => {
                    const info = transportInfo[segment.mode];
                    const vehicle = simulatedVehicles.find(v => v.segmentIndex === index);
                    const hasStops = segment.stopsList && segment.stopsList.length > 0;

                    return (
                        <div key={index}>
                            <div className="flex items-center gap-3 bg-slate-100 p-3 rounded-t-lg">
                                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${info.bgColor} ${info.color}`}>
                                    {info.icon}
                                </div>
                                <div>
                                    <p className="font-semibold text-slate-800">{segment.details}</p>
                                    <p className="text-xs text-slate-500">{segment.duration} min</p>
                                </div>
                            </div>
                            {hasStops ? (
                                <div className="bg-slate-50 rounded-b-lg">
                                    <SegmentTimeline segment={segment} vehicle={vehicle} />
                                </div>
                            ) : (
                                <div className="h-2"></div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
