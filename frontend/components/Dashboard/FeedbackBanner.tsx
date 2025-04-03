import React, { useState } from 'react';
import { X } from 'lucide-react';

export default function FeedbackBanner() {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 rounded-lg p-4 mb-4 relative">
      <button
        onClick={() => setIsVisible(false)}
        className="absolute top-2 right-2 text-gray-400 hover:text-gray-600"
      >
        <X size={16} />
      </button>
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex-1">
          <h3 className="text-sm font-medium text-gray-900">Help us improve!</h3>
          <p className="text-sm text-gray-600">We'd love to hear your feedback about our platform.</p>
        </div>
        <div className="ml-auto sm:mr-8"> {/* Added left margin for spacing */}
          <a
            href="mailto:feedback@example.com"
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Share Feedback
          </a>
        </div>
      </div>
    </div>
  );
}
