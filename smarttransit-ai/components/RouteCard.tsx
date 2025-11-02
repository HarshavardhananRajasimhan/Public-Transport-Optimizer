import React, { useState, useEffect } from 'react';
import { Route, TransportMode } from '../types';
import { WalkIcon } from './icons/WalkIcon';
import { BusIcon } from './icons/BusIcon';
import { TrainIcon } from './icons/TrainIcon';
import { ClockIcon } from './icons/ClockIcon';
import { DollarIcon } from './icons/DollarIcon';
import { ComfortIcon } from './icons/ComfortIcon';
import { AlertIcon } from './icons/AlertIcon';
import { AutoRickshawIcon } from './icons/AutoRickshawIcon';
import { StopByStopDisplay } from './StopByStopDisplay';
import { useVehicleSimulation } from '../hooks/useVehicleSimulation';

interface RouteCardProps {
  route: Route;
  isBestOption: boolean;
  isSelected: boolean;
  onSelect: () => void;
}

export const transportInfo: { [key in TransportMode]: { icon: React.ReactNode; color: string; bgColor: string } } = {
  [TransportMode.WALK]: { icon: <WalkIcon className="w-5 h-5" />, color: 'text-green-700', bgColor: 'bg-green-100' },
  [TransportMode.BUS]: { icon: <BusIcon className="w-5 h-5" />, color: 'text-red-700', bgColor: 'bg-red-100' },
  [TransportMode.METRO]: { icon: <TrainIcon className="w-5 h-5" />, color: 'text-purple-700', bgColor: 'bg-purple-100' },
  [TransportMode.AUTO_RICKSHAW]: { icon: <AutoRickshawIcon className="w-5 h-5" />, color: 'text-amber-700', bgColor: 'bg-amber-100' },
};


export const RouteCard: React.FC<RouteCardProps> = ({ route, isBestOption, isSelected, onSelect }) => {
  const simulatedVehicles = useVehicleSimulation(isSelected ? route.segments : []);

  return (
    <div 
      className={`bg-white rounded-2xl shadow-lg overflow-hidden transition-all duration-300 relative border ${isSelected ? 'border-indigo-500 shadow-indigo-200/50' : 'border-slate-200/50 hover:border-indigo-300'}`}
      onClick={onSelect}
      role="button"
      tabIndex={0}
      aria-expanded={isSelected}
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onSelect()}
    >
       {isBestOption && (
        <div className="absolute top-0 right-0 bg-indigo-600 text-white text-xs font-bold px-4 py-1.5 rounded-bl-xl z-10">
          Best Option
        </div>
      )}
      <div className="p-5">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center mb-2">
          <h3 className="text-xl font-bold text-slate-900 pr-28">{route.routeName}</h3>
          <p className="text-sm text-slate-400 font-medium mt-1 sm:mt-0 whitespace-nowrap">AI Confidence: {(route.confidenceScore * 100).toFixed(0)}%</p>
        </div>

        <p className="text-slate-600 mb-4 text-sm">{route.summary}</p>
        
        {route.realtimeInfo && (
          <div className="bg-amber-50 border border-amber-200 text-amber-800 p-3 rounded-lg mb-5 flex items-start gap-3">
            <AlertIcon className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p className="text-sm font-medium">{route.realtimeInfo}</p>
          </div>
        )}

        <div className="flex flex-wrap items-center gap-2 mb-5 pb-5 border-b border-slate-200">
            <div className="flex items-center gap-1.5 bg-slate-100 rounded-full px-3 py-1.5 text-sm" title="Total Duration">
                <ClockIcon className="w-5 h-5 text-slate-500" />
                <span className="font-bold text-slate-800">{route.totalDuration}</span>
                <span className="text-slate-600">min</span>
            </div>
            <div className="flex items-center gap-1.5 bg-green-100 rounded-full px-3 py-1.5 text-sm" title="Estimated Cost">
                <DollarIcon className="w-5 h-5 text-green-600" />
                <span className="font-bold text-green-800">₹{route.totalCost.toFixed(0)}</span>
            </div>
            <div className="flex items-center gap-1.5 bg-blue-100 rounded-full px-3 py-1.5 text-sm" title="Comfort Score">
                <ComfortIcon className="w-5 h-5 text-blue-600" />
                <span className="font-bold text-blue-800">{route.comfortScore}/10</span>
            </div>
        </div>

        <div className="relative pl-5">
           {/* Timeline Line */}
           <div className="absolute left-5 top-0 h-full w-0.5 bg-slate-200" aria-hidden="true"></div>

            <div className="space-y-4">
                {route.segments.map((segment, index) => {
                 const info = transportInfo[segment.mode];
                 return (
                    <div 
                        key={index} 
                        className="flex items-start gap-4 relative rounded-lg -ml-3 p-2"
                    >
                        <div className={`flex-shrink-0 z-10 w-10 h-10 rounded-full flex items-center justify-center ${info.bgColor} ${info.color} border-4 border-white`}>
                            {info.icon}
                        </div>
                        <div className="flex-grow pt-1">
                        <p className="font-semibold text-slate-800">{segment.details}</p>
                        <p className="text-sm text-slate-500">
                            {segment.duration} min
                            {segment.distance && ` • ${segment.distance.toFixed(1)} km`}
                            {segment.stops && ` • ${segment.stops} stops`}
                        </p>
                        {segment.realtimeInfo && (
                            <div className="mt-2 flex items-center gap-2 text-xs text-amber-800 bg-amber-50 border border-amber-200 rounded-md p-2">
                                <AlertIcon className="w-3.5 h-3.5 flex-shrink-0" />
                                <span>{segment.realtimeInfo}</span>
                            </div>
                        )}
                        </div>
                    </div>
                )})}
            </div>
        </div>
      </div>
      <div className={`transition-all duration-500 ease-in-out ${isSelected ? 'max-h-[1000px] opacity-100' : 'max-h-0 opacity-0'}`}>
        {isSelected && (
          <div className="p-4 sm:p-5 bg-slate-50/70">
            <StopByStopDisplay 
              route={route} 
              simulatedVehicles={simulatedVehicles} 
            />
          </div>
        )}
      </div>
    </div>
  );
};