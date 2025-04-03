import React, { useState } from 'react';
import { Clock, TrendingUp, TrendingDown, Maximize2, X, BarChart2, RefreshCw, Calendar } from 'lucide-react';
import { format } from 'date-fns';

export default function LMEAluminium() {
  const [isReversed, setIsReversed] = useState(false);
  const [showExpanded, setShowExpanded] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const SPOT_PRICE = 2700.00;
  const THREE_MONTH_PRICE = 2622.00;
  const CHANGE = 13.00;
  const CHANGE_PERCENT = 0.48;
  const MARKET_TREND = THREE_MONTH_PRICE < SPOT_PRICE ? 'backwardation' : 'contango';
  const SPREAD = Math.abs(SPOT_PRICE - THREE_MONTH_PRICE).toFixed(2);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      setLastUpdated(new Date());
    }, 800);
  };

  const PriceSection = ({ isSpot = true, expanded = false, mobile = false }) => {
    const price = isSpot ? SPOT_PRICE : THREE_MONTH_PRICE;
    const label = isSpot ? 'Spot Price' : '3-Month';

    return (
      <div className={expanded ? 'space-y-4' : mobile ? 'space-y-2' : 'space-y-3'}>
        <div className="flex items-center justify-between">
          <span className={`font-medium text-gray-700 ${
            expanded ? 'text-lg' : 
            mobile ? 'text-xs' : 
            'text-sm'
          }`}>
            {label}
          </span>
        </div>
        
        <div className="flex items-baseline gap-2 sm:gap-3">
          <span className={`font-mono font-bold bg-gradient-to-r ${
            isSpot ? 'from-blue-600 to-purple-600' : 'from-purple-600 to-pink-600'
          } bg-clip-text text-transparent ${
            expanded ? 'text-5xl' : 
            mobile ? 'text-2xl' : 
            'text-3xl sm:text-4xl'
          }`}>
            ${price.toFixed(2)}
          </span>
          <span className={`text-gray-500 ${
            expanded ? 'text-sm' : 
            mobile ? 'text-xs' : 
            'text-xs'
          }`}>/MT</span>
          
          {isSpot ? (
            <span className={`text-gray-500 ml-auto flex items-center gap-1 ${
              expanded ? 'text-sm' : 
              mobile ? 'text-xs' : 
              'text-xs'
            }`}>
              <Clock className="w-3.5 h-3.5" />
              {expanded ? 'Delayed (30 mins)' : mobile ? 'Delayed' : 'Delayed (30 mins)'}
            </span>
          ) : (
            <span className={`ml-auto px-2 py-1 rounded-full font-medium flex items-center gap-1 ${
              expanded ? 'bg-green-100 text-green-800 text-sm' : 
              mobile ? 'bg-green-100 text-green-800 text-xs' : 
              'bg-green-100 text-green-800 text-xs'
            }`}>
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              Live
            </span>
          )}
        </div>
        
        {isSpot && (
          <div className={`flex items-center gap-1.5 ${CHANGE >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            <div className={`p-1 rounded-full ${CHANGE >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
              {CHANGE >= 0 ? (
                <TrendingUp className={expanded ? 'w-5 h-5' : mobile ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
              ) : (
                <TrendingDown className={expanded ? 'w-5 h-5' : mobile ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
              )}
            </div>
            <span className={`font-medium ${
              expanded ? 'text-base' : 
              mobile ? 'text-xs' : 
              'text-sm'
            }`}>
              {CHANGE >= 0 ? '+' : ''}{CHANGE.toFixed(2)} ({CHANGE_PERCENT >= 0 ? '+' : ''}{CHANGE_PERCENT.toFixed(2)}%)
            </span>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="w-full">
      {/* LME Card */}
      <div className="relative bg-white rounded-xl p-4 border border-gray-100 shadow-[0_4px_12px_rgba(0,0,0,0.05)] hover:shadow-lg transition-all duration-200 min-h-[260px] group">
        {/* Glow effect on hover - desktop only */}
        <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none bg-gradient-to-br from-blue-50/30 via-purple-50/30 to-pink-50/30 hidden sm:block"></div>
        
        <div className="flex items-center justify-between mb-4 relative z-10">
          <div className="flex items-center gap-2 sm:gap-3">
            <h2 className="text-lg sm:text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent flex items-center gap-2">
              <BarChart2 className="w-4 h-4 sm:w-5 sm:h-5 text-purple-600" />
              LME Aluminium
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={handleRefresh}
              className="p-1.5 sm:p-2 hover:bg-gray-100 rounded-full transition-colors"
              aria-label="Refresh data"
            >
              <RefreshCw className={`w-3.5 h-3.5 sm:w-4 sm:h-4 text-gray-600 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={() => setShowExpanded(true)}
              className="p-1.5 sm:p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-600"
              aria-label="Expand view"
            >
              <Maximize2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            </button>
          </div>
        </div>

        {/* Mobile: Vertical layout */}
        <div className="sm:hidden flex flex-col space-y-4">
          <PriceSection isSpot={!isReversed} mobile={true} />
          <div className="w-full h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent" />
          <PriceSection isSpot={isReversed} mobile={true} />
        </div>

        {/* Desktop: Original layout */}
        <div className="hidden sm:flex flex-col h-[calc(100%-4rem)] relative z-10">
          <div className="flex-1 flex flex-col justify-evenly">
            <PriceSection isSpot={!isReversed} />
            <div className="w-full h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent my-2" />
            <PriceSection isSpot={isReversed} />
          </div>
        </div>

        <div className="pt-3 border-t border-gray-100 mt-auto">
          <div className="flex items-center justify-start">
            <div className="flex items-center gap-1.5 text-xs text-gray-500">
              <RefreshCw className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
              <span>Updated: {format(lastUpdated, 'MMM d, HH:mm')}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Expanded Modal View */}
      {showExpanded && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl p-6 sm:p-8 shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-auto border border-gray-200">
            <div className="flex items-center justify-between w-full mb-6 sm:mb-8">
              <div className="flex items-center gap-3 sm:gap-4">
                <h2 className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  LME Aluminium
                </h2>
                <span className="bg-green-100 text-green-800 text-xs sm:text-sm px-2.5 py-1 rounded-full">Live</span>
              </div>
              <button
                onClick={() => setShowExpanded(false)}
                className="w-8 h-8 sm:w-10 sm:h-10 flex items-center justify-center rounded-full bg-gray-200 hover:bg-gray-300 transition text-gray-700"
                aria-label="Close expanded view"
              >
                <X className="w-4 h-4 sm:w-5 sm:h-5" />
              </button>
            </div>

            <div className="flex flex-col sm:flex-row items-stretch gap-4 sm:gap-8">
              {/* Spot Price Box */}
              <div className="flex-1 bg-blue-50/50 p-4 sm:p-6 rounded-xl border border-blue-100">
                <div className="flex flex-col h-full">
                  <div className="flex items-center gap-2 mb-3 sm:mb-4">
                    <Calendar className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-800">Spot Price</span>
                  </div>
                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="font-mono font-bold text-3xl sm:text-4xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                      ${SPOT_PRICE.toFixed(2)}
                    </span>
                    <span className="text-gray-500 text-sm">/MT</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-500 text-xs mb-4 sm:mb-6">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Delayed (30 mins)</span>
                  </div>
                  <div className={`flex items-center gap-2 ${CHANGE >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {CHANGE >= 0 ? (
                      <TrendingUp className="w-4 h-4" />
                    ) : (
                      <TrendingDown className="w-4 h-4" />
                    )}
                    <span className="font-medium">
                      {CHANGE >= 0 ? '+' : ''}{CHANGE.toFixed(2)} ({CHANGE_PERCENT >= 0 ? '+' : ''}{CHANGE_PERCENT.toFixed(2)}%)
                    </span>
                  </div>
                </div>
              </div>

              {/* Vertical Divider - Desktop only */}
              <div className="hidden sm:block w-px bg-gradient-to-b from-transparent via-gray-200 to-transparent my-4" />

              {/* 3-Month Price Box */}
              <div className="flex-1 bg-purple-50/50 p-4 sm:p-6 rounded-xl border border-purple-100">
                <div className="flex flex-col h-full">
                  <div className="flex items-center gap-2 mb-3 sm:mb-4">
                    <Calendar className="w-4 h-4 text-purple-600" />
                    <span className="text-sm font-medium text-purple-800">3-Month Futures</span>
                  </div>
                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="font-mono font-bold text-3xl sm:text-4xl bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                      ${THREE_MONTH_PRICE.toFixed(2)}
                    </span>
                    <span className="text-gray-500 text-sm">/MT</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-500 text-xs mb-4 sm:mb-6">
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Real-time data</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600 text-sm">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span>Live</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Horizontal Divider */}
            <div className="w-full h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent my-4 sm:my-6"></div>

            {/* Market Status */}
            <div className={`text-center py-2 px-4 rounded-md ${
              MARKET_TREND === 'backwardation' 
                ? 'bg-green-100 border border-green-200 text-green-800'
                : 'bg-red-100 border border-red-200 text-red-800'
            }`}>
              <div className="flex items-center justify-center gap-2 text-sm font-medium">
                <span>{MARKET_TREND === 'backwardation' ? 'BACKWARDATION' : 'CONTANGO'}</span>
                <span>${SPREAD}</span>
                {MARKET_TREND === 'backwardation' ? (
                  <TrendingDown className="w-4 h-4" />
                ) : (
                  <TrendingUp className="w-4 h-4" />
                )}
              </div>
            </div>

            {/* Description Boxes */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 mt-4 sm:mt-6">
              <div className="bg-blue-100 p-3 sm:p-4 rounded-lg border border-blue-200">
                <h3 className="text-sm font-medium text-blue-800 mb-2">Spot Price Analysis</h3>
                <p className="text-xs sm:text-sm text-gray-700">
                  The current spot price reflects immediate market conditions for aluminium delivery. 
                  Today's {CHANGE >= 0 ? 'increase' : 'decrease'} indicates {CHANGE >= 0 ? 'strengthening' : 'weakening'} demand in the physical market.
                </p>
              </div>
              <div className="bg-purple-100 p-3 sm:p-4 rounded-lg border border-purple-200">
                <h3 className="text-sm font-medium text-purple-800 mb-2">3-Month Futures Outlook</h3>
                <p className="text-xs sm:text-sm text-gray-700">
                  The {MARKET_TREND} of ${SPREAD} suggests the market expects {MARKET_TREND === 'backwardation' ? 
                  'near-term supply constraints' : 'future supply increases or demand softening'} in the aluminium sector.
                </p>
              </div>
            </div>

            <div className="mt-4 sm:mt-6 pt-3 sm:pt-4 border-t border-gray-200">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-2">
                <div className="flex items-center gap-2 text-gray-600">
                  <Clock className="w-4 h-4" />
                  <span className="text-xs sm:text-sm">
                    Last updated: {format(lastUpdated, 'MMM d, yyyy HH:mm:ss')}
                  </span>
                </div>
                <button 
                  onClick={handleRefresh}
                  className="text-xs sm:text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                >
                  <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                  Refresh Data
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}