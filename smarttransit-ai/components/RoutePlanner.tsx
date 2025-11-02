import React, { useState } from 'react';
import { Preference, RoutePreferences } from '../types';
import { SparklesIcon } from './icons/SparklesIcon';
import { BalancedIcon } from './icons/BalancedIcon';
import { FastestIcon } from './icons/FastestIcon';
import { CheapestIcon } from './icons/CheapestIcon';
import { ComfortableIcon } from './icons/ComfortableIcon';


interface RoutePlannerProps {
  onOptimize: (start: string, end: string, preferences: RoutePreferences) => void;
  isLoading: boolean;
}

const preferenceOptions = [
  { id: Preference.BALANCED, label: 'Balanced', icon: <BalancedIcon className="w-8 h-8 mb-2" /> },
  { id: Preference.FASTEST, label: 'Fastest', icon: <FastestIcon className="w-8 h-8 mb-2" /> },
  { id: Preference.CHEAPEST, label: 'Cheapest', icon: <CheapestIcon className="w-8 h-8 mb-2" /> },
  { id: Preference.COMFORT, label: 'Comfort', icon: <ComfortableIcon className="w-8 h-8 mb-2" /> },
];

export const RoutePlanner: React.FC<RoutePlannerProps> = ({ onOptimize, isLoading }) => {
  const [start, setStart] = useState<string>('India Gate, Delhi');
  const [end, setEnd] = useState<string>('Hauz Khas Village, Delhi');
  const [preference, setPreference] = useState<Preference>(Preference.BALANCED);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (start.trim() && end.trim()) {
      onOptimize(start, end, { priority: preference });
    }
  };

  return (
    <div className="bg-white p-6 rounded-2xl shadow-lg border border-slate-200/50 sticky top-8">
      <h2 className="text-2xl font-bold text-slate-800 mb-5">Plan Your Journey</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="start" className="block text-sm font-semibold text-slate-600 mb-1.5">
            Start Location
          </label>
          <input
            type="text"
            id="start"
            value={start}
            onChange={(e) => setStart(e.target.value)}
            className="w-full px-4 py-2.5 bg-slate-100 border border-slate-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
            placeholder="e.g., Connaught Place"
            required
          />
        </div>
        <div>
          <label htmlFor="end" className="block text-sm font-semibold text-slate-600 mb-1.5">
            End Location
          </label>
          <input
            type="text"
            id="end"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
            className="w-full px-4 py-2.5 bg-slate-100 border border-slate-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
            placeholder="e.g., Qutub Minar"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-600 mb-2">
            Optimize For
          </label>
          <div className="grid grid-cols-2 gap-3">
            {preferenceOptions.map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => setPreference(opt.id)}
                className={`flex flex-col items-center justify-center p-3 text-sm font-bold rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 border-2
                  ${preference === opt.id 
                    ? 'bg-indigo-50 border-indigo-500 text-indigo-600 shadow-md' 
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300'}`}
              >
                {opt.icon}
                <span>{opt.label}</span>
              </button>
            ))}
          </div>
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 to-blue-500 text-white font-bold py-3 px-4 rounded-lg shadow-lg hover:shadow-indigo-500/50 disabled:bg-indigo-400 disabled:cursor-not-allowed disabled:shadow-none transform hover:-translate-y-0.5 transition-all duration-300"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Optimizing...
            </>
          ) : (
            <>
              <SparklesIcon className="w-5 h-5"/>
              Find Best Route
            </>
          )}
        </button>
      </form>
    </div>
  );
};