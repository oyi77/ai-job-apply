import React, { useState, useEffect } from 'react';
import { XMarkIcon, CheckCircleIcon, ExclamationTriangleIcon, InformationCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

export type AppNotificationType = 'success' | 'error' | 'warning' | 'info';

export interface AppNotification {
  id: string;
  type: AppNotificationType;
  title: string;
  message?: string;
  duration?: number; // in milliseconds, 0 = persistent
  read?: boolean; // For app-level notifications
}

interface NotificationProps {
  notification: AppNotification;
  onDismiss: (id: string) => void;
}

const NotificationItem: React.FC<NotificationProps> = ({ notification, onDismiss }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (notification.duration && notification.duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(() => onDismiss(notification.id), 300); // Wait for fade out
      }, notification.duration);

      return () => clearTimeout(timer);
    }
  }, [notification.duration, notification.id, onDismiss]);

  const icons = {
    success: CheckCircleIcon,
    error: XCircleIcon,
    warning: ExclamationTriangleIcon,
    info: InformationCircleIcon,
  };

  const colors = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  };

  const Icon = icons[notification.type];
  const colorClass = colors[notification.type];

  if (!isVisible) return null;

  return (
    <div
      className={`${colorClass} border rounded-lg p-4 shadow-lg mb-2 transition-opacity duration-300 ${isVisible ? 'opacity-100' : 'opacity-0'
        }`}
      role="alert"
    >
      <div className="flex items-start">
        <Icon className="h-5 w-5 mt-0.5 mr-3 flex-shrink-0" />
        <div className="flex-1">
          <h4 className="font-medium">{notification.title}</h4>
          {notification.message && (
            <p className="mt-1 text-sm opacity-90">{notification.message}</p>
          )}
        </div>
        <button
          onClick={() => {
            setIsVisible(false);
            setTimeout(() => onDismiss(notification.id), 300);
          }}
          className="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-600"
          aria-label="Dismiss notification"
          data-testid={`notification-dismiss-${notification.id}`}
        >
          <XMarkIcon className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
};

interface NotificationContainerProps {
  notifications: AppNotification[];
  onDismiss: (id: string) => void;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center';
}

export const NotificationContainer: React.FC<NotificationContainerProps> = ({
  notifications,
  onDismiss,
  position = 'top-right',
}) => {
  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
  };

  if (notifications.length === 0) return null;

  return (
    <div
      className={`fixed ${positionClasses[position]} z-50 w-full max-w-sm space-y-2`}
      role="region"
      aria-label="Notifications"
    >
      {notifications.map((notification) => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          onDismiss={onDismiss}
        />
      ))}
    </div>
  );
};

// Hook for managing notifications
export const useNotifications = () => {
  const [notifications, setNotifications] = useState<AppNotification[]>([]);

  const addNotification = (notification: Omit<AppNotification, 'id'>) => {
    const id = `notification-${Date.now()}-${Math.random()}`;
    const newNotification: AppNotification = {
      id,
      duration: 5000, // Default 5 seconds
      ...notification,
    };
    setNotifications((prev) => [...prev, newNotification]);
    return id;
  };

  const dismissNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const showSuccess = (title: string, message?: string, duration?: number) => {
    return addNotification({ type: 'success', title, message, duration });
  };

  const showError = (title: string, message?: string, duration?: number) => {
    return addNotification({ type: 'error', title, message, duration: duration ?? 0 }); // Errors persist by default
  };

  const showWarning = (title: string, message?: string, duration?: number) => {
    return addNotification({ type: 'warning', title, message, duration });
  };

  const showInfo = (title: string, message?: string, duration?: number) => {
    return addNotification({ type: 'info', title, message, duration });
  };

  return {
    notifications,
    addNotification,
    dismissNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };
};

interface NotificationDropdownProps {
  notifications: AppNotification[];
  onMarkAsRead: (id: string) => void;
  onDelete: (id: string) => void;
  onMarkAllAsRead: () => void;
}

export const NotificationDropdown: React.FC<NotificationDropdownProps> = ({
  notifications,
  onMarkAsRead,
  onDelete,
  onMarkAllAsRead,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-400 hover:text-gray-500"
        aria-label="Open notifications"
        data-testid="notification-dropdown-trigger"
      >
        <InformationCircleIcon className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 block h-4 w-4 rounded-full bg-red-500 text-[10px] font-bold text-white flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg py-1 border border-gray-200 z-20">
            <div className="px-4 py-2 border-b border-gray-100 flex justify-between items-center">
              <span className="text-sm font-medium text-gray-900">Notifications</span>
              <button
                onClick={onMarkAllAsRead}
                className="text-xs text-primary-600 hover:text-primary-700 font-medium"
              >
                Mark all as read
              </button>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="px-4 py-6 text-center text-gray-500 text-sm">
                  No notifications
                </div>
              ) : (
                notifications.map(notif => (
                  <div
                    key={notif.id}
                    className={`px-4 py-3 hover:bg-gray-50 transition-colors border-b border-gray-50 flex items-start space-x-3 ${!notif.read ? 'bg-primary-50' : ''}`}
                  >
                    <div className="flex-1 min-w-0" onClick={() => onMarkAsRead(notif.id)}>
                      <p className={`text-sm ${!notif.read ? 'font-semibold text-gray-900' : 'text-gray-600'}`}>
                        {notif.title}
                      </p>
                      {notif.message && (
                        <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                          {notif.message}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => onDelete(notif.id)}
                      className="text-gray-400 hover:text-gray-600 p-1"
                      aria-label="Delete notification"
                      data-testid={`notification-item-delete-${notif.id}`}
                    >
                      <XMarkIcon className="h-4 w-4" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

// Default export is for the dropdown used in Header
export default NotificationDropdown;
