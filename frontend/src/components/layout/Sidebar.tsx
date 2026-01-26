import React, { useRef, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAppStore } from '../../stores/appStore';
import { useNavigation } from '../../hooks/useNavigation';
import {
  HomeIcon,
  BriefcaseIcon,
  DocumentTextIcon,
  EnvelopeIcon,
  MagnifyingGlassIcon,
  SparklesIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  Bars3Icon,
  XMarkIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Applications', href: '/applications', icon: BriefcaseIcon },
  { name: 'Resumes', href: '/resumes', icon: DocumentTextIcon },
  { name: 'Cover Letters', href: '/cover-letters', icon: EnvelopeIcon },
  { name: 'Job Search', href: '/job-search', icon: MagnifyingGlassIcon },
  { name: 'AI Services', href: '/ai-services', icon: SparklesIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
  { name: 'Admin Settings', href: '/admin-settings', icon: UserCircleIcon },
];

const Sidebar: React.FC = () => {
  const { sidebarOpen, setSidebarOpen } = useAppStore();
  const location = useLocation();
  const mobileMenuRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const openButtonRef = useRef<HTMLButtonElement>(null);

  const { trapFocus } = useNavigation({
    items: navigation,
    onCloseMobileMenu: () => setSidebarOpen(false),
    mobileMenuOpen: sidebarOpen
  });

  // Manage focus when sidebar state changes
  useEffect(() => {
    if (sidebarOpen) {
      // Small timeout to ensure DOM is rendered and transition started
      setTimeout(() => {
        closeButtonRef.current?.focus();
      }, 100);
    } else {
      // Return focus to the trigger button when closed
      // Check if the focus is currently inside the mobile menu before moving it
      if (mobileMenuRef.current && mobileMenuRef.current.contains(document.activeElement)) {
         openButtonRef.current?.focus();
      }
    }
  }, [sidebarOpen]);

  const handleMobileMenuKeyDown = (e: React.KeyboardEvent) => {
    trapFocus(mobileMenuRef.current, e);
  };

  return (
    <>
      {/* Mobile sidebar */}
      <div 
        id="mobile-sidebar"
        className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}
        role="region"
        aria-label="Mobile Navigation"
        aria-modal="true"
        aria-expanded={sidebarOpen}
        ref={mobileMenuRef}
        onKeyDown={handleMobileMenuKeyDown}
      >
        <div 
          className="fixed inset-0 bg-gray-600 dark:bg-gray-900 bg-opacity-75 dark:bg-opacity-75 transition-opacity" 
          onClick={() => setSidebarOpen(false)} 
          aria-hidden="true"
        />
        
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-white dark:bg-gray-800 transform transition-transform duration-300 ease-in-out">
          <div className="flex h-16 items-center justify-between px-4">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg" aria-hidden="true">AI</span>
              </div>
              <span className="ml-2 text-lg font-semibold text-gray-900 dark:text-white">Job Apply</span>
            </div>
            <button
              ref={closeButtonRef}
              type="button"
              className="ml-1 flex h-10 w-10 items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"
              onClick={() => setSidebarOpen(false)}
              aria-label="Close sidebar"
            >
              <XMarkIcon className="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          
          <nav className="flex-1 space-y-1 px-2 py-4" role="navigation" aria-label="Mobile main navigation">
            {navigation.map((item, index) => {
              // NavLink isActive handling
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) => `group flex items-center px-2 py-2 text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                    isActive
                      ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-900 dark:text-primary-200'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                  }`}
                  onClick={() => setSidebarOpen(false)}
                  aria-label={`${item.name} (Alt+${index + 1})`}
                >
                  {({ isActive }) => (
                    <>
                      <item.icon
                        className={`mr-3 h-5 w-5 flex-shrink-0 ${
                          isActive ? 'text-primary-500 dark:text-primary-400' : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-300'
                        }`}
                        aria-hidden="true"
                      />
                      {item.name}
                    </>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-72 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
          <div className="flex items-center h-16 px-4 border-b border-gray-200 dark:border-gray-700">
            <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg" aria-hidden="true">AI</span>
            </div>
            <span className="ml-2 text-lg font-semibold text-gray-900 dark:text-white">Job Apply</span>
          </div>
          <nav className="flex-1 space-y-1 px-2 py-4" role="navigation" aria-label="Main navigation">
            {navigation.map((item, index) => {
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) => `group flex items-center px-2 py-2 text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                    isActive
                      ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-900 dark:text-primary-200'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                  }`}
                  aria-label={`${item.name} (Alt+${index + 1})`}
                >
                  {({ isActive }) => (
                    <>
                      <item.icon
                        className={`mr-3 h-5 w-5 flex-shrink-0 ${
                          isActive ? 'text-primary-500 dark:text-primary-400' : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-300'
                        }`}
                        aria-hidden="true"
                      />
                      {item.name}
                    </>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-40">
        <button
          ref={openButtonRef}
          type="button"
          className="bg-white dark:bg-gray-800 p-2 rounded-md text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          onClick={() => setSidebarOpen(true)}
          aria-label="Open sidebar navigation"
          aria-expanded={sidebarOpen}
          aria-controls="mobile-sidebar"
        >
          <Bars3Icon className="h-6 w-6" aria-hidden="true" />
        </button>
      </div>
    </>
  );
};

export default Sidebar;
