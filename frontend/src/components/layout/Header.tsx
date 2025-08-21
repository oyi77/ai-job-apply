import React from 'react';
import { useAppStore } from '../../stores/appStore';
import { Notification, ThemeToggle } from '../ui';
import {
  UserCircleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline';

const Header: React.FC = () => {
  const { user, setUser, setAuthenticated, notifications, theme, setTheme } = useAppStore();

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
    setAuthenticated(false);
    window.location.href = '/login';
  };

  const handleMarkAsRead = () => {
    // TODO: Implement mark as read
  };

  const handleDeleteNotification = () => {
    // TODO: Implement delete notification
  };

  const handleMarkAllAsRead = () => {
    // TODO: Implement mark all as read
  };

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-gray-200">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center">
          <h1 className="text-2xl font-semibold text-gray-900">AI Job Application Assistant</h1>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Theme Toggle */}
          <ThemeToggle
            theme={theme}
            onThemeChange={setTheme}
          />

          {/* Notifications */}
          <Notification
            notifications={notifications}
            onMarkAsRead={handleMarkAsRead}
            onDelete={handleDeleteNotification}
            onMarkAllAsRead={handleMarkAllAsRead}
          />

          {/* User menu */}
          <div className="relative group">
            <button
              type="button"
              className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 p-2 rounded-md hover:bg-gray-100"
            >
              <UserCircleIcon className="h-8 w-8 text-gray-400" />
              <span className="hidden md:block text-sm font-medium">
                {user?.name || 'Guest User'}
              </span>
            </button>
            
            {/* Dropdown menu */}
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
              <button
                onClick={() => window.location.href = '/settings'}
                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                <Cog6ToothIcon className="mr-3 h-4 w-4" />
                Settings
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                <ArrowRightOnRectangleIcon className="mr-3 h-4 w-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
