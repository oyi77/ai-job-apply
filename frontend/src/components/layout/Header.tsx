import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../../stores/appStore';
import { Notification, ThemeToggle } from '../ui';
import { authService } from '../../services/api';
import {
  UserCircleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout, notifications, setNotifications, theme, setTheme } = useAppStore();

  const handleLogout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await authService.logout();
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      logout();
      navigate('/login');
    }
  };

  const handleMarkAsRead = (id: string) => {
    setNotifications(
      notifications.map(notif =>
        notif.id === id ? { ...notif, read: true } : notif
      )
    );
  };

  const handleDeleteNotification = (id: string) => {
    setNotifications(notifications.filter(notif => notif.id !== id));
  };

  const handleMarkAllAsRead = () => {
    setNotifications(notifications.map(notif => ({ ...notif, read: true })));
  };

  return (
    <header className="sticky top-0 z-40 bg-white/70 backdrop-blur-md border-b border-gray-100">
      <div className="max-w-7xl mx-auto flex h-20 items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center space-x-3">
          <div className="bg-primary-600 p-2 rounded-xl shadow-lg shadow-primary-600/20">
            <BriefcaseIcon className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-xl font-extrabold text-gray-900 tracking-tight hidden sm:block">
            AI Job <span className="text-primary-600">Assists</span>
          </h1>
        </div>

        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-4 border-r border-gray-100 pr-6">
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
          </div>

          {/* User menu */}
          <div className="relative group">
            <button
              type="button"
              className="flex items-center space-x-3 text-gray-700 hover:text-gray-900 p-1.5 rounded-xl hover:bg-gray-50 transition-all duration-300"
            >
              <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center border border-primary-50">
                <UserCircleIcon className="h-7 w-7 text-primary-600" />
              </div>
              <div className="hidden md:block text-left">
                <p className="text-sm font-bold text-gray-900 leading-none">
                  {user?.name || 'Guest User'}
                </p>
                <p className="text-[10px] font-semibold text-gray-400 mt-1 uppercase tracking-wider">
                  Pro Member
                </p>
              </div>
            </button>

            {/* Dropdown menu */}
            <div className="absolute right-0 mt-3 w-56 bg-white/90 backdrop-blur-xl rounded-2xl shadow-2xl py-2 border border-gray-100 opacity-0 scale-95 invisible group-hover:opacity-100 group-hover:visible group-hover:scale-100 transition-all duration-300 origin-top-right z-50">
              <div className="px-4 py-2 border-b border-gray-50 mb-1">
                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Account</p>
              </div>
              <button
                onClick={() => window.location.href = '/settings'}
                className="flex items-center w-full px-4 py-2.5 text-sm font-semibold text-gray-700 hover:bg-primary-50 hover:text-primary-700 transition-colors"
              >
                <Cog6ToothIcon className="mr-3 h-4 w-4" />
                Settings
              </button>
              <div className="my-1 border-t border-gray-50"></div>
              <button
                onClick={handleLogout}
                className="flex items-center w-full px-4 py-2.5 text-sm font-semibold text-danger-600 hover:bg-danger-50 transition-colors"
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
