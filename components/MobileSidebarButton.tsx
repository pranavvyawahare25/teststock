"use client";

import { Menu, X } from "lucide-react";

interface MobileSidebarButtonProps {
  isOpen: boolean;
  onClick: () => void;
}

export default function MobileSidebarButton({ isOpen, onClick }: MobileSidebarButtonProps) {
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onClick();
  };

  return (
    <button
      onClick={handleClick}
      className={`fixed top-4 right-4 z-50 p-2.5 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-xl transition-all duration-300 md:hidden ${
        isOpen ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800' : ''
      }`}
      aria-label={isOpen ? "Close sidebar" : "Open sidebar"}
    >
      {isOpen ? (
        <X className="w-5 h-5 text-red-500 dark:text-red-400" />
      ) : (
        <Menu className="w-5 h-5 text-gray-600 dark:text-gray-400" />
      )}
    </button>
  );
} 