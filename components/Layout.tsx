"use client";

import React, { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import Sidebar from "./SideBar";
import MobileSidebarButton from "./MobileSidebarButton";
import { SignedIn, SignedOut, useAuth } from "@clerk/nextjs";

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const pathname = usePathname();
  const isHomePage = pathname === "/";
  const { isSignedIn } = useAuth();

  // Handle dark mode
  useEffect(() => {
    const isDark = localStorage.getItem("darkMode") === "true";
    setIsDarkMode(isDark);
    if (isDark) {
      document.documentElement.classList.add("dark");
    }
  }, []);

  const handleThemeChange = (isDark: boolean) => {
    setIsDarkMode(isDark);
    localStorage.setItem("darkMode", isDark.toString());
    if (isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  // Handle mobile sidebar state
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setIsMobileOpen(false);
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleMobileSidebarToggle = () => {
    // Use a timeout to ensure the state update happens after any other state changes
    setTimeout(() => {
      setIsMobileOpen(prev => !prev);
    }, 0);
  };

  // Prevent scrolling when mobile sidebar is open
  useEffect(() => {
    if (isMobileOpen) {
      document.body.classList.add("sidebar-open");
    } else {
      document.body.classList.remove("sidebar-open");
    }
    return () => {
      document.body.classList.remove("sidebar-open");
    };
  }, [isMobileOpen]);

  // For the homepage, render children directly without any wrapper
  if (isHomePage) {
    return <>{children}</>;
  }

  // For all other pages, use the standard layout with sidebar
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      <MobileSidebarButton
        isOpen={isMobileOpen}
        onClick={handleMobileSidebarToggle}
      />
      
      <Sidebar
        currentPage="dashboard"
        isCollapsed={isCollapsed}
        onCollapse={setIsCollapsed}
        isDarkMode={isDarkMode}
        onThemeChange={handleThemeChange}
        isMobileOpen={isMobileOpen}
        onMobileClose={() => setIsMobileOpen(false)}
      />

      <main
        className={`transition-all duration-300 p-4 md:p-6 lg:p-8 ${
          isCollapsed ? "md:ml-16" : "md:ml-64"
        }`}
      >
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
} 