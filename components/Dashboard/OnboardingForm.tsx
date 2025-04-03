'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { X } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';

interface OnboardingFormProps {
  onClose: () => void;
}

export default function OnboardingForm({ onClose }: OnboardingFormProps) {
  const router = useRouter();
  const { userId } = useAuth();
  const [formData, setFormData] = useState({
    companyName: '',
    businessType: '',
    role: '',
    phoneNumber: '',
    pincode: '',
    gstin: '',
    interestedMetals: [] as string[],
  });

  const businessTypes = ['Manufacturer', 'Trader', 'Distributor', 'Stockist', 'End User', 'Other'];
  const roles = ['Procurement Manager', 'Supply Chain Manager', 'Business Owner', 'Trader', 'Other'];
  const metals = ['Aluminium', 'Copper', 'Zinc', 'Lead', 'Nickel', 'Other'];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/onboarding', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId,
          ...formData,
        }),
      });

      if (response.ok) {
        localStorage.setItem('onboardingCompleted', 'true');
        onClose();
        router.push('/dashboard');
      } else {
        throw new Error('Failed to save onboarding data');
      }
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  const handleMetalToggle = (metal: string) => {
    setFormData(prev => ({
      ...prev,
      interestedMetals: prev.interestedMetals.includes(metal)
        ? prev.interestedMetals.filter(m => m !== metal)
        : [...prev.interestedMetals, metal]
    }));
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 overflow-y-auto max-h-[90vh] border border-gray-100">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Welcome to <span className="text-blue-600">NOVEX PRO</span>
              </h2>
              <div className="w-12 h-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full mt-2"></div>
            </div>
            {/* <button
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              aria-label="Close"
            >
              <X className="w-5 h-5 text-gray-500 hover:text-gray-700" />
            </button> */}
          </div>

          <p className="text-sm text-gray-500 mb-6">
            Complete your profile to unlock personalized features and recommendations.
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Company Information */}
            <div className="space-y-4">
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">
                  Company Name
                </label>
                <input
                  type="text"
                  required
                  value={formData.companyName}
                  onChange={(e) => setFormData(prev => ({ ...prev, companyName: e.target.value }))}
                  className="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter company name"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="block text-sm font-medium text-gray-700">
                    Business Type
                  </label>
                  <select
                    required
                    value={formData.businessType}
                    onChange={(e) => setFormData(prev => ({ ...prev, businessType: e.target.value }))}
                    className="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-500 appearance-none bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoZXZyb24tZG93biI+PHBhdGggZD0ibTYgOSA2IDYgNi02Ii8+PC9zdmc+')] bg-no-repeat bg-[center_right_1rem] bg-[length:16px_16px]"
                  >
                    <option value="">Select</option>
                    {businessTypes.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="block text-sm font-medium text-gray-700">
                    Your Role
                  </label>
                  <select
                    required
                    value={formData.role}
                    onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                    className="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-500 appearance-none bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoZXZyb24tZG93biI+PHBhdGggZD0ibTYgOSA2IDYgNi02Ii8+PC9zdmc+')] bg-no-repeat bg-[center_right_1rem] bg-[length:16px_16px]"
                  >
                    <option value="">Select</option>
                    {roles.map(role => (
                      <option key={role} value={role}>{role}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Contact & Location Details */}
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="block text-sm font-medium text-gray-700">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    required
                    value={formData.phoneNumber}
                    onChange={(e) => setFormData(prev => ({ ...prev, phoneNumber: e.target.value }))}
                    className="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-500 transition-all duration-200"
                    placeholder="Enter phone number"
                  />
                </div>

                <div className="space-y-1">
                  <label className="block text-sm font-medium text-gray-700">
                    Plant/Warehouse Pincode
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.pincode}
                    onChange={(e) => setFormData(prev => ({ ...prev, pincode: e.target.value }))}
                    className="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-500 transition-all duration-200"
                    placeholder="Enter pincode"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">
                  GSTIN
                </label>
                <input
                  type="text"
                  required
                  value={formData.gstin}
                  onChange={(e) => setFormData(prev => ({ ...prev, gstin: e.target.value }))}
                  className="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter GSTIN"
                />
              </div>
            </div>

            {/* Interested Metals */}
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">
                Interested Metals
              </label>
              <div className="grid grid-cols-2 gap-3">
                {metals.map(metal => (
                  <button
                    key={metal}
                    type="button"
                    onClick={() => handleMetalToggle(metal)}
                    className={`p-3 text-sm rounded-xl border transition-all duration-200 flex items-center justify-center ${
                      formData.interestedMetals.includes(metal)
                        ? 'bg-blue-50 border-blue-300 text-blue-700 font-medium shadow-sm'
                        : 'border-gray-200 hover:bg-gray-50 hover:border-gray-300'
                    }`}
                  >
                    {metal}
                  </button>
                ))}
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-600 to-blue-500 text-white py-3 text-sm font-medium rounded-lg hover:from-blue-700 hover:to-blue-600 transition-all duration-200 shadow-sm hover:shadow-md"
            >
              Complete Setup
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}