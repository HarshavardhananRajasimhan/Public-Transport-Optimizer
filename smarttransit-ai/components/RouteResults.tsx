import React from 'react';
import { Route } from '../types';
import { RouteCard } from './RouteCard';
import { JourneyIcon } from './icons/JourneyIcon';
import { IllustrativeErrorIcon } from './icons/IllustrativeErrorIcon';

interface RouteResultsProps {
  routes: Route[] | null;
  isLoading: boolean;
  error: string | null;
  selectedRouteId: string | null;
  onSelectRoute: (id: string | null) => void;
}

const LoadingSkeleton: React.FC = () => (
    <div className="bg-white p-5 rounded-2xl shadow-lg animate-pulse relative overflow-hidden border border-slate-200/50">
        <div className="absolute top-4 right-4 h-5 bg-slate-200 rounded-full w-24"></div>
        <div className="h-6 bg-slate-200 rounded w-3/4 mb-3"></div>
        <div className="h-4 bg-slate-200 rounded w-full mb-5"></div>
        <div className="flex items-center gap-3 mb-5 pb-5 border-b border-slate-200">
            <div className="h-8 bg-slate-200 rounded-full w-1/4"></div>
            <div className="h-8 bg-slate-200 rounded-full w-1/4"></div>
            <div className="h-8 bg-slate-200 rounded-full w-1/4"></div>
        </div>
        <div className="space-y-4">
            <div className="flex gap-4 items-center">
                <div className="w-8 h-8 rounded-full bg-slate-200"></div>
                <div className="flex-1 space-y-2">
                    <div className="h-4 bg-slate-200 rounded w-3/4"></div>
                    <div className="h-3 bg-slate-200 rounded w-1/2"></div>
                </div>
            </div>
             <div className="flex gap-4 items-center">
                <div className="w-8 h-8 rounded-full bg-slate-200"></div>
                <div className="flex-1 space-y-2">
                    <div className="h-4 bg-slate-200 rounded w-3/4"></div>
                    <div className="h-3 bg-slate-200 rounded w-1/2"></div>
                </div>
            </div>
        </div>
    </div>
);


export const RouteResults: React.FC<RouteResultsProps> = ({ routes, isLoading, error, selectedRouteId, onSelectRoute }) => {
  if (isLoading) {
    return (
        <div className="space-y-4">
            <LoadingSkeleton />
            <LoadingSkeleton />
            <LoadingSkeleton />
        </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-lg border border-slate-200/50 text-center">
        <div className="mx-auto h-24 w-24 flex items-center justify-center">
           <IllustrativeErrorIcon className="w-24 h-24" />
        </div>
        <h3 className="mt-4 text-xl font-bold text-slate-800">Oops! Something went wrong.</h3>
        <p className="mt-2 text-slate-600 max-w-md mx-auto">{error}</p>
      </div>
    );
  }

  if (!routes) {
    return (
       <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-lg border border-slate-200/50 text-center">
        <div className="mx-auto h-32 w-32 flex items-center justify-center">
          <JourneyIcon className="w-32 h-32 text-indigo-500 opacity-80"/>
        </div>
        <h3 className="mt-6 text-2xl font-bold text-slate-800">Your Journey Awaits</h3>
        <p className="mt-2 text-slate-600 max-w-md mx-auto">Ready to explore? Enter your start and end locations, and let our AI find the perfect route for you.</p>
      </div>
    );
  }
  
  if (routes.length === 0) {
      return (
        <div className="bg-white p-8 rounded-2xl shadow-lg text-center">
             <h3 className="text-xl font-bold text-slate-800">No Routes Found</h3>
             <p className="mt-2 text-slate-500">Our AI couldn't find any suitable routes for your request. Please try different locations.</p>
        </div>
      );
  }

  return (
    <div className="space-y-6">
      {routes.map((route, index) => (
        <RouteCard 
            key={route.id} 
            route={route} 
            isBestOption={index === 0} 
            isSelected={selectedRouteId === route.id}
            onSelect={() => onSelectRoute(route.id === selectedRouteId ? null : route.id)}
        />
      ))}
    </div>
  );
};