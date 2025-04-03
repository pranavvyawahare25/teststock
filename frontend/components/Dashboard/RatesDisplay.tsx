import React, { useState, useEffect } from "react";
import { Maximize2, RefreshCw, ArrowUpRight, Banknote } from "lucide-react";
import { format } from "date-fns";

interface RatesDisplayProps {
  className?: string;
}

export default function RatesDisplay({ className = "" }: RatesDisplayProps) {
  const [showExpanded, setShowExpanded] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [rbiRate, setRbiRate] = useState<number | null>(null);
  const [sbiRate, setSbiRate] = useState<number | null>(null);

  // Fetch RBI rate from Next.js API
  const fetchRbiRate = async () => {
    try {
      const response = await fetch("/api/rbi"); // Calls your Next.js API
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Failed to fetch data");
      }

      if (result.data && result.data.length > 0) {
        setRbiRate(parseFloat(result.data[0].rate)); // Convert string to number
        setLastUpdated(new Date());
      }
    } catch (error) {
      console.error("Error fetching RBI rate:", error);
    }
  };

  // Fetch SBI TT rate from Next.js API
  const fetchSbiRate = async () => {
    try {
      const response = await fetch("/api/sbitt"); // Calls your Next.js API
      const text = await response.text(); // Read raw response

      console.log("🔍 Raw response from Next.js API:", text); // Debugging output

      const result = JSON.parse(text); // Convert text to JSON

      if (!response.ok) {
        throw new Error(result.error || "Failed to fetch SBI data");
      }

      if (result.data && result.data.length > 0) {
        setSbiRate(parseFloat(result.data[0].sbi_tt_sell)); // Convert string to number
      }
    } catch (error) {
      console.error("🚨 Error fetching SBI rate:", error);
    }
  };

  useEffect(() => {
    fetchRbiRate(); // Fetch RBI data on mount
    fetchSbiRate(); // Fetch SBI data on mount
  }, []);

  const handleRefresh = () => {
    setIsRefreshing(true);
    Promise.all([fetchRbiRate(), fetchSbiRate()]).finally(() =>
      setIsRefreshing(false)
    );
  };

  const RateSection = ({ isRBI = true, expanded = false }) => {
    const rate = isRBI ? rbiRate : sbiRate;
    const label = isRBI ? "RBI Rate" : "SBI Rate";

    return (
      <div className={expanded ? "space-y-4" : "space-y-3"}>
        <div className="flex items-center justify-between">
          <span
            className={`font-medium text-gray-700 ${
              expanded ? "text-lg" : "text-sm"
            }`}
          >
            {label}
          </span>
          {expanded && (
            <a
              href={isRBI ? "https://www.rbi.org.in" : "https://www.sbi.co.in"}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-blue-600 hover:text-blue-800 transition-colors flex items-center gap-1"
            >
              Source <ArrowUpRight className="w-3 h-3" />
            </a>
          )}
        </div>

        <div className="flex items-baseline gap-3">
          <span
            className={`font-mono font-bold bg-gradient-to-r ${
              isRBI
                ? "from-blue-600 to-purple-600"
                : "from-purple-600 to-pink-600"
            } bg-clip-text text-transparent ${
              expanded ? "text-5xl" : "text-4xl"
            }`}
          >
            ₹{rate !== null ? rate.toFixed(4) : "Loading..."}
          </span>
          <span className={`text-gray-500 ${expanded ? "text-sm" : "text-xs"}`}>
            /USD
          </span>

          {!isRBI && (
            <span
              className={`ml-auto px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1 bg-green-100 text-green-800`}
            >
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
              Live
            </span>
          )}
        </div>

        {isRBI && <div className="h-[24px]"></div>}
      </div>
    );
  };

  return (
    <div
      className={`relative bg-white rounded-xl p-4 border border-gray-100 shadow transition-all duration-300 h-[calc(41.67vh-2rem)] flex flex-col group ${className}`}
    >
      <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none bg-gradient-to-br from-blue-50/30 via-purple-50/30 to-pink-50/30"></div>

      <div className="flex items-center justify-between mb-4 relative z-10">
        <div className="flex items-center gap-3">
          <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent flex items-center gap-2">
            <Banknote className="w-5 h-5 text-purple-600" />
            Exchange Rates
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            aria-label="Refresh rates"
          >
            <RefreshCw
              className={`w-4 h-4 text-gray-600 ${
                isRefreshing ? "animate-spin" : ""
              }`}
            />
          </button>
          <button
            onClick={() => setShowExpanded(true)}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-600"
            aria-label="Expand view"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex flex-col h-[calc(100%-4rem)] relative z-10">
        <div className="flex-1 flex flex-col justify-evenly">
          <RateSection isRBI={true} />
          <div className="w-full h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent my-2" />
          <RateSection isRBI={false} />
        </div>

        <div className="pt-3 border-t border-gray-100">
          <div className="flex items-center justify-start">
            <div className="flex items-center gap-1.5 text-xs text-gray-500">
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Updated: {format(lastUpdated, "MMM d, HH:mm")}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// alternative code for this page

// import React, { useState, useEffect } from "react";
// import { Maximize2, RefreshCw, ArrowUpRight, Banknote } from "lucide-react";
// import { format } from "date-fns";

// interface RatesDisplayProps {
//   className?: string;
// }

// export default function RatesDisplay({ className = "" }: RatesDisplayProps) {
//   const [showExpanded, setShowExpanded] = useState(false);
//   const [isRefreshing, setIsRefreshing] = useState(false);
//   const [lastUpdated, setLastUpdated] = useState(new Date());
//   const [rbiRate, setRbiRate] = useState<number | null>(null);

//   const SBI_TT_RATE = 84.65; // Hardcoded SBI TT rate

//   // Fetch RBI rate from Next.js API
//   const fetchRbiRate = async () => {
//     try {
//       const response = await fetch("/api/rbi"); // Calls your Next.js API
//       const result = await response.json();

//       if (!response.ok) {
//         throw new Error(result.error || "Failed to fetch data");
//       }

//       if (result.data && result.data.length > 0) {
//         setRbiRate(parseFloat(result.data[0].rate)); // Convert string to number
//         setLastUpdated(new Date());
//       }
//     } catch (error) {
//       console.error("Error fetching RBI rate:", error);
//     }
//   };

//   useEffect(() => {
//     fetchRbiRate(); // Fetch data on mount
//   }, []);

//   const handleRefresh = () => {
//     setIsRefreshing(true);
//     fetchRbiRate().finally(() => setIsRefreshing(false));
//   };

//   const RateSection = ({ isRBI = true, expanded = false }) => {
//     const rate = isRBI ? rbiRate : SBI_TT_RATE;
//     const label = isRBI ? "RBI Rate" : "SBI Rate";

//     return (
//       <div className={expanded ? "space-y-4" : "space-y-3"}>
//         <div className="flex items-center justify-between">
//           <span
//             className={`font-medium text-gray-700 ${
//               expanded ? "text-lg" : "text-sm"
//             }`}
//           >
//             {label}
//           </span>
//           {expanded && (
//             <a
//               href={isRBI ? "https://www.rbi.org.in" : "https://www.sbi.co.in"}
//               target="_blank"
//               rel="noopener noreferrer"
//               className="text-xs text-blue-600 hover:text-blue-800 transition-colors flex items-center gap-1"
//             >
//               Source <ArrowUpRight className="w-3 h-3" />
//             </a>
//           )}
//         </div>

//         <div className="flex items-baseline gap-3">
//           <span
//             className={`font-mono font-bold bg-gradient-to-r ${
//               isRBI
//                 ? "from-blue-600 to-purple-600"
//                 : "from-purple-600 to-pink-600"
//             } bg-clip-text text-transparent ${
//               expanded ? "text-5xl" : "text-4xl"
//             }`}
//           >
//             ₹{rate !== null ? rate.toFixed(4) : "Loading..."}
//           </span>
//           <span className={`text-gray-500 ${expanded ? "text-sm" : "text-xs"}`}>
//             /USD
//           </span>

//           {!isRBI && (
//             <span
//               className={`ml-auto px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1 bg-green-100 text-green-800`}
//             >
//               <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
//               Live
//             </span>
//           )}
//         </div>

//         {isRBI && <div className="h-[24px]"></div>}
//       </div>
//     );
//   };

//   return (
//     <div
//       className={`relative bg-white rounded-xl p-4 border border-gray-100 shadow transition-all duration-300 h-[calc(41.67vh-2rem)] flex flex-col group ${className}`}
//     >
//       <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none bg-gradient-to-br from-blue-50/30 via-purple-50/30 to-pink-50/30"></div>

//       <div className="flex items-center justify-between mb-4 relative z-10">
//         <div className="flex items-center gap-3">
//           <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent flex items-center gap-2">
//             <Banknote className="w-5 h-5 text-purple-600" />
//             Exchange Rates
//           </h2>
//         </div>
//         <div className="flex items-center gap-2">
//           <button
//             onClick={handleRefresh}
//             className="p-2 hover:bg-gray-100 rounded-full transition-colors"
//             aria-label="Refresh rates"
//           >
//             <RefreshCw
//               className={`w-4 h-4 text-gray-600 ${
//                 isRefreshing ? "animate-spin" : ""
//               }`}
//             />
//           </button>
//           <button
//             onClick={() => setShowExpanded(true)}
//             className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-600"
//             aria-label="Expand view"
//           >
//             <Maximize2 className="w-4 h-4" />
//           </button>
//         </div>
//       </div>

//       <div className="flex flex-col h-[calc(100%-4rem)] relative z-10">
//         <div className="flex-1 flex flex-col justify-evenly">
//           <RateSection isRBI={true} />
//           <div className="w-full h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent my-2" />
//           <RateSection isRBI={false} />
//         </div>

//         <div className="pt-3 border-t border-gray-100">
//           <div className="flex items-center justify-start">
//             <div className="flex items-center gap-1.5 text-xs text-gray-500">
//               <RefreshCw className="w-3.5 h-3.5" />
//               <span>Updated: {format(lastUpdated, "MMM d, HH:mm")}</span>
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }
