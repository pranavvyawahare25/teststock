'use client';

import React from 'react';
import { Wifi, Clock, TrendingUp, TrendingDown } from 'lucide-react';
import { format } from 'date-fns';
import dynamic from 'next/dynamic';

interface LiveSpotCardProps {
    lastUpdated?: Date;
    spotPrice?: number;
    change?: number;
    changePercent?: number;
    unit?: string;
    isDerived?: boolean;
}

const ClockComponent = dynamic(() => import('./Clock'), { 
    ssr: false,
    loading: () => <span className="text-sm text-gray-600">--:--:--</span>
});

export default function LiveSpotCard({
    lastUpdated,
    spotPrice = 2700.00,
    change = 13.00,
    changePercent = 0.48,
    unit = '/MT',
    isDerived = true
}: LiveSpotCardProps) {
    const displayTime = lastUpdated || new Date();
    const isIncrease = change >= 0;
    const trendColor = isIncrease ? "text-green-600" : "text-red-600";
    const TrendIcon = isIncrease ? TrendingUp : TrendingDown;

    return (
        <div className="price-card bg-white rounded-xl p-4 border border-gray-200 
          shadow-md hover:shadow-lg transition-all duration-200 w-full max-w-xs
          relative overflow-hidden gpu-render group">
            
            {/* Background effect - properly layered */}
            <div className={`absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity 
              ${isIncrease ? 'bg-green-500' : 'bg-red-500'} 
              -z-10`}></div>

            <div className="relative flex flex-col h-full gap-2">
                {/* Live Indicator Header */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="relative">
                            <Wifi className="w-4 h-4 text-green-600 crisp-text" />
                            <div className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-green-500 rounded-full animate-ping"></div>
                        </div>
                        <span className="text-sm font-medium text-green-700 crisp-text">LIVE</span>
                        {isDerived && (
                            <span className="text-sm text-gray-600 crisp-text">(Derived)</span>
                        )}
                    </div>
                    <div className="flex items-center gap-1.5 text-sm text-gray-600">
                        <Clock className="w-4 h-4 crisp-text" />
                        <ClockComponent />
                    </div>
                </div>

                {/* Price Content */}
                <div className="flex-1">
                    <div className="text-sm text-gray-600 mb-1.5 crisp-text">
                        {format(displayTime, 'd MMMM yyyy')}
                    </div>

                    <div className="flex items-baseline gap-2">
                        <span className="font-mono text-2xl font-bold bg-gradient-to-r from-indigo-600 to-blue-600 
                          bg-clip-text text-transparent gradient-text crisp-text">
                            ${spotPrice.toFixed(2)}
                        </span>
                        <span className="text-sm text-gray-600 crisp-text">{unit}</span>
                    </div>

                    <div className={`flex items-center gap-1.5 text-sm ${trendColor} mt-2 font-medium`}>
                        <TrendIcon className="w-4 h-4 flex-shrink-0 crisp-text" />
                        <span className="whitespace-nowrap crisp-text">
                            {isIncrease ? '+' : '-'}${Math.abs(change).toFixed(2)} ({changePercent.toFixed(2)}%)
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}