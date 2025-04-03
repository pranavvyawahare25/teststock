import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface LiveSpotPriceCardProps {
  priceName?: string;
  basePrice: number;
  spread: number;
  exchangeRate?: number;
  lastUpdated?: Date;
}

export default function LiveSpotPriceCard({
  basePrice = 2650,
  spread = 40,
  exchangeRate = 83.5,
  lastUpdated
}: LiveSpotPriceCardProps) {
  const CURRENT_DATE = '20. March 2025';
  const totalPrice = basePrice + spread;
  const percentageChange = ((spread / basePrice) * 100).toFixed(2);
  const isIncrease = spread >= 0;
  const trendColor = isIncrease ? "text-green-600" : "text-red-600";
  const TrendIcon = isIncrease ? TrendingUp : TrendingDown;
  const spreadINR = (Math.abs(spread) * exchangeRate).toFixed(2);

  return (
    <div className="bg-white rounded-xl p-4 border border-gray-100 
      shadow-md hover:shadow-lg transition-all duration-200 w-full 
      max-w-xs sm:max-w-sm
      relative overflow-hidden
      will-change-transform group" // Optimizes for performance
    >
      {/* Background effect - separated from text layer */}
      <div className={`absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity 
        ${isIncrease ? 'bg-green-500' : 'bg-red-500'}
        -z-10`} // Ensures it stays behind text
      ></div>
      
      {/* Text container with forced GPU layer */}
      <div className="relative flex flex-col h-full gap-1.5 transform-gpu">
        {/* Date */}
        <div className="text-sm text-gray-600 font-medium">{CURRENT_DATE}</div>

        {/* Price Display */}
        <div className="flex items-baseline justify-between mt-1">
          <span className="font-mono text-2xl font-bold bg-gradient-to-r from-indigo-600 to-blue-600 bg-clip-text text-transparent
            leading-tight tracking-tight"> {/* Tight letter spacing */}
            ${totalPrice.toFixed(2)}
          </span>
        </div>

        {/* Change Indicators */}
        <div className={`flex items-center gap-1.5 text-sm ${trendColor} mt-2 font-medium`}>
          <TrendIcon className="w-4 h-4 flex-shrink-0" />
          <span className="whitespace-nowrap">
            {isIncrease ? '+' : '-'}${Math.abs(spread).toFixed(2)} ({percentageChange}%)
          </span>
        </div>
        <div className={`flex items-center gap-1.5 text-sm ${trendColor} font-medium`}>
          <TrendIcon className="w-4 h-4 flex-shrink-0" />
          <span className="whitespace-nowrap">
            {isIncrease ? '+' : '-'}₹{spreadINR}
          </span>
        </div>
      </div>
    </div>
  );
}