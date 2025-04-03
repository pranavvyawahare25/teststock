import React, { useState } from 'react';
import { Calendar, TrendingUp, TrendingDown, Clock, Maximize2, X, RefreshCw, BarChart2 } from 'lucide-react';
import { format } from 'date-fns';
import MCXClock from './MCXClock';

export default function MCXAluminium() {
  // Static data
  const priceData = {
    march: { price: 201.85, change: 0.42 },
    april: { price: 203.15, change: 0.38 },
    may: { price: 204.75, change: 0.45 }
  };

  const [showExpanded, setShowExpanded] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const spread = priceData.april.price - priceData.march.price;
  const isContango = spread > 0;

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      setLastUpdated(new Date());
    }, 800);
  };

  const ContractPrice = ({
    month,
    price,
    change,
    gradient,
    expanded = false,
    showDivider = true
  }: {
    month: string;
    price: number;
    change: number;
    gradient: string;
    expanded?: boolean;
    showDivider?: boolean;
  }) => (
    <div className={`flex-1 flex items-center ${expanded ? 'justify-center' : ''}`}>
      <div className="w-full">
        <div className={`flex flex-col ${expanded ? 'items-center' : 'items-center'}`}>
          <div className={`${expanded ? 'text-sm' : 'text-xs'} text-gray-600 flex items-center justify-center gap-1 mb-0.5 h-4`}>
            <Calendar className={`w-3 h-3 ${month === 'March' ? 'text-blue-600' :
              month === 'April' ? 'text-purple-600' : 'text-pink-600'
              }`} />
            <span>{month}</span>
          </div>
          <div className="flex flex-col items-center gap-0">
            <div className={`font-mono font-bold bg-gradient-to-r ${gradient} bg-clip-text text-transparent ${
              expanded ? 'text-4xl' : 'text-xl' // Changed from 'text-base' to 'text-xl'
            }`}>
              ₹{price.toFixed(2)}
            </div>
            <div className={`flex items-center justify-center gap-1 h-4 ${change >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
              {change >= 0 ? (
                <TrendingUp className="w-3 h-3" />
              ) : (
                <TrendingDown className="w-3 h-3" />
              )}
              <span className="text-xs">
                {change >= 0 ? '+' : ''}{change}%
              </span>
            </div>
          </div>
        </div>
      </div>
      {showDivider && !expanded && (
        <div className="h-10 w-px bg-gradient-to-b from-transparent via-gray-200 to-transparent mx-1" />
      )}
    </div>
  );

  const ContractPriceBox = ({ month, price, change, gradient }: {
    month: string;
    price: number;
    change: number;
    gradient: string;
  }) => (
    <div className={`flex-1 p-3 rounded-lg border ${
      month === 'March' ? 'bg-blue-50/50 border-blue-100' : 
      month === 'April' ? 'bg-purple-50/50 border-purple-100' : 
      'bg-pink-50/50 border-pink-100'
    }`}>
      <div className="flex flex-col h-full">
        <div className="flex items-center gap-1.5 mb-2">
          <Calendar className={`w-3 h-3 ${
            month === 'March' ? 'text-blue-600' : 
            month === 'April' ? 'text-purple-600' : 
            'text-pink-600'
          }`} />
          <span className={`text-xs font-medium ${
            month === 'March' ? 'text-blue-800' : 
            month === 'April' ? 'text-purple-800' : 
            'text-pink-800'
          }`}>
            {month} Contract
          </span>
        </div>
        <div className="flex items-baseline gap-1 mb-1">
          <span className={`font-mono font-bold text-2xl bg-gradient-to-r ${gradient} bg-clip-text text-transparent`}>
            ₹{price.toFixed(2)}
          </span>
        </div>
        <div className="flex items-center gap-1 text-gray-500 text-2xs mb-2">
          <Clock className="w-2.5 h-2.5" />
          <span>Near-month price</span>
        </div>
        <div className={`flex items-center gap-1 ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {change >= 0 ? (
            <TrendingUp className="w-3 h-3" />
          ) : (
            <TrendingDown className="w-3 h-3" />
          )}
          <span className="text-xs">
            {change >= 0 ? '+' : ''}{change}%
          </span>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Compact Card View */}
      <div className="relative bg-white rounded-lg p-2 border border-gray-100 shadow-[0_2px_8px_rgba(0,0,0,0.05)] hover:shadow-md transition-all duration-200 min-h-[160px]">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 sm:gap-3">
            <h2 className="text-base sm:text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent flex items-center gap-2">
              <BarChart2 className="w-4 h-4 sm:w-5 sm:h-5 text-purple-600" />
              MCX Aluminium
            </h2>
            <span className="bg-green-100 text-green-800 text-xs px-1.5 py-0.5 rounded-full">Live</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="flex items-center text-gray-500 mr-1">
              <MCXClock />
            </div>
            <button 
              onClick={handleRefresh}
              className="p-1 hover:bg-gray-100/50 rounded-full transition-colors text-gray-600"
              aria-label="Refresh data"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={() => setShowExpanded(true)}
              className="p-1 hover:bg-gray-100/50 rounded-full transition-colors text-gray-600"
              aria-label="Expand view"
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        <div className="flex flex-col">
          {/* Mobile: Vertical layout */}
          <div className="sm:hidden flex flex-col justify-between space-y-1.5 mb-1">
            <ContractPrice
              month="March"
              price={priceData.march.price}
              change={priceData.march.change}
              gradient="from-blue-600 to-purple-600"
              showDivider={false}
            />
            <ContractPrice
              month="April"
              price={priceData.april.price}
              change={priceData.april.change}
              gradient="from-purple-600 to-pink-600"
              showDivider={false}
            />
            <ContractPrice
              month="May"
              price={priceData.may.price}
              change={priceData.may.change}
              gradient="from-pink-600 to-rose-600"
              showDivider={false}
            />
          </div>

          {/* Desktop: Horizontal layout */}
          <div className="hidden sm:flex flex-1 items-center my-1">
            <div className="w-full flex">
              <ContractPrice
                month="March"
                price={priceData.march.price}
                change={priceData.march.change}
                gradient="from-blue-600 to-purple-600"
              />
              <ContractPrice
                month="April"
                price={priceData.april.price}
                change={priceData.april.change}
                gradient="from-purple-600 to-pink-600"
              />
              <ContractPrice
                month="May"
                price={priceData.may.price}
                change={priceData.may.change}
                gradient="from-pink-600 to-rose-600"
                showDivider={false}
              />
            </div>
          </div>

          {/* Contango section */}
          <div className={`text-center py-1.5 px-3 rounded-md ${
            isContango
              ? 'bg-green-100 border border-green-200 text-green-800'
              : 'bg-red-100 border border-red-200 text-red-800'
          }`}>
            <div className="flex items-center justify-center gap-2 text-xs font-medium">
              <span>{isContango ? 'CONTANGO' : 'BACKWARDATION'}</span>
              <span>₹{Math.abs(spread).toFixed(2)}</span>
              {isContango ? (
                <TrendingUp className="w-3 h-3" />
              ) : (
                <TrendingDown className="w-3 h-3" />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Expanded Modal View */}
      {showExpanded && priceData && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl p-4 shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-auto border border-gray-200">
            <div className="flex items-center justify-between w-full mb-4">
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent flex items-center gap-2">
                  <BarChart2 className="w-5 h-5 text-purple-600" />
                  MCX Aluminium
                </h2>
                <span className="bg-green-100 text-green-800 text-xs px-2 py-0.5 rounded-full">Live</span>
              </div>
              <button
                onClick={() => setShowExpanded(false)}
                className="w-6 h-6 flex items-center justify-center rounded-full bg-gray-200 hover:bg-gray-300 transition text-gray-700"
                aria-label="Close expanded view"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex flex-col sm:flex-row items-stretch gap-4">
              <ContractPriceBox 
                month="March"
                price={priceData.march.price}
                change={priceData.march.change}
                gradient="from-blue-600 to-purple-600"
              />
              
              <div className="hidden sm:block w-px bg-gradient-to-b from-transparent via-gray-200 to-transparent my-3" />

              <ContractPriceBox 
                month="April"
                price={priceData.april.price}
                change={priceData.april.change}
                gradient="from-purple-600 to-pink-600"
              />

              <div className="hidden sm:block w-px bg-gradient-to-b from-transparent via-gray-200 to-transparent my-3" />

              <ContractPriceBox 
                month="May"
                price={priceData.may.price}
                change={priceData.may.change}
                gradient="from-pink-600 to-rose-600"
              />
            </div>

            <div className={`mt-3 text-center py-1.5 px-3 rounded-md ${
              isContango
                ? 'bg-green-100 border border-green-200 text-green-800'
                : 'bg-red-100 border border-red-200 text-red-800'
            }`}>
              <div className="flex items-center justify-center gap-2 text-xs font-medium">
                <span>{isContango ? 'CONTANGO' : 'BACKWARDATION'}</span>
                <span>₹{Math.abs(spread).toFixed(2)}</span>
                {isContango ? (
                  <TrendingUp className="w-3.5 h-3.5" />
                ) : (
                  <TrendingDown className="w-3.5 h-3.5" />
                )}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-gray-200">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="bg-blue-100 p-2 rounded-md border border-blue-200">
                  <h3 className="text-xs font-medium text-blue-800 mb-1">March Contract</h3>
                  <p className="text-2xs text-gray-700">
                    Near-month contract price reflecting current market conditions.
                  </p>
                </div>
                <div className="bg-purple-100 p-2 rounded-md border border-purple-200">
                  <h3 className="text-xs font-medium text-purple-800 mb-1">April Contract</h3>
                  <p className="text-2xs text-gray-700">
                    Next-month contract showing short-term market expectations.
                  </p>
                </div>
                <div className="bg-pink-100 p-2 rounded-md border border-pink-200">
                  <h3 className="text-xs font-medium text-pink-800 mb-1">May Contract</h3>
                  <p className="text-2xs text-gray-700">
                    Further-out contract indicating longer-term market trends.
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-3 pt-2 border-t border-gray-200">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-1">
                <div className="flex items-center gap-1 text-gray-600">
                  <Clock className="w-3 h-3" />
                  <span className="text-2xs">
                    Last updated: {format(lastUpdated, 'MMM d, yyyy HH:mm:ss')}
                  </span>
                </div>
                <button 
                  onClick={handleRefresh}
                  className="text-2xs text-blue-600 hover:text-blue-800 flex items-center gap-0.5"
                >
                  <RefreshCw className={`w-3 h-3 ${isRefreshing ? 'animate-spin' : ''}`} />
                  Refresh Data
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}