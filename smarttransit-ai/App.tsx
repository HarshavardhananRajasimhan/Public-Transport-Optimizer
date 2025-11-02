import React, { useState, useCallback } from 'react';
import { RoutePlanner } from './components/RoutePlanner';
import { RouteResults } from './components/RouteResults';
import { planRouteWithRealData } from './services/routePlannerService';
import { Route, RoutePreferences } from './types';
import { LogoIcon } from './components/icons/LogoIcon';

const App: React.FC = () => {
  const [routes, setRoutes] = useState<Route[] | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);


  const handleOptimizeRoute = useCallback(async (start: string, end: string, preferences: RoutePreferences) => {
    setIsLoading(true);
    setError(null);
    setRoutes(null);
    setSelectedRouteId(null);

    try {
      const plannedRoutes = await planRouteWithRealData(start, end, preferences);
      setRoutes(plannedRoutes);
      if (plannedRoutes && plannedRoutes.length > 0) {
        setSelectedRouteId(plannedRoutes[0].id);
      }
    } catch (err) {
      console.error(err);
      setError('Failed to plan route. Please check that the backend server is running and try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className="min-h-screen font-sans text-slate-900">
      <header className="bg-gradient-to-r from-indigo-600 via-indigo-500 to-blue-500 shadow-md">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center gap-4">
          <LogoIcon className="w-10 h-10 text-white"/>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            SmartTransit AI
          </h1>
        </div>
      </header>
      <main className="container mx-auto p-4 sm:p-6 lg:p-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-4 xl:col-span-3">
            <RoutePlanner onOptimize={handleOptimizeRoute} isLoading={isLoading} />
          </div>
          <div className="lg:col-span-8 xl:col-span-9">
            <RouteResults 
              routes={routes} 
              isLoading={isLoading} 
              error={error}
              selectedRouteId={selectedRouteId}
              onSelectRoute={setSelectedRouteId}
            />
          </div>
        </div>
      </main>
      <footer className="text-center py-6 text-slate-500 text-sm mt-8">
        <p>Powered by Delhi Open Transit Data. Tracking 2,400+ live buses with real-time GPS positions.</p>
        <p className="text-xs mt-1">Route IDs are real-time identifiers from DTC buses currently in service.</p>
      </footer>
    </div>
  );
};

export default App;