/**
 * Error message component
 * Displays user-friendly error messages
 */

import React from 'react';
import { ExclamationCircleIcon, XCircleIcon, InformationCircleIcon } from '@heroicons/react/24/outline';

export interface ErrorMessageProps {
  /** Error message to display */
  message: string;
  /** Error title (optional) */
  title?: string;
  /** Error type */
  type?: 'error' | 'warning' | 'info';
  /** Callback to dismiss the error */
  onDismiss?: () => void;
  /** Additional CSS classes */
  className?: string;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  title,
  type = 'error',
  onDismiss,
  className = '',
}) => {
  const styles = {
    error: {
      container: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
      icon: 'text-red-500',
      text: 'text-red-800 dark:text-red-200',
      title: 'text-red-900 dark:text-red-100',
    },
    warning: {
      container: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800',
      icon: 'text-yellow-500',
      text: 'text-yellow-800 dark:text-yellow-200',
      title: 'text-yellow-900 dark:text-yellow-100',
    },
    info: {
      container: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
      icon: 'text-blue-500',
      text: 'text-blue-800 dark:text-blue-200',
      title: 'text-blue-900 dark:text-blue-100',
    },
  };

  const currentStyle = styles[type];

  const icons = {
    error: ExclamationCircleIcon,
    warning: ExclamationCircleIcon,
    info: InformationCircleIcon,
  };

  const Icon = icons[type];

  return (
    <div
      className={`rounded-lg border p-4 ${currentStyle.container} ${className}`}
      role="alert"
    >
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <Icon className={`h-5 w-5 ${currentStyle.icon}`} aria-hidden="true" />
        </div>
        <div className="ml-3 flex-1">
          {title && (
            <h3 className={`text-sm font-medium ${currentStyle.title}`}>
              {title}
            </h3>
          )}
          <div className={`text-sm ${currentStyle.text}`}>
            <p>{message}</p>
          </div>
        </div>
        {onDismiss && (
          <div className="ml-auto pl-3">
            <button
              type="button"
              className={`inline-flex rounded-md p-1.5 ${currentStyle.text} hover:bg-white dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2`}
              onClick={onDismiss}
            >
              <span className="sr-only">Dismiss</span>
              <XCircleIcon className="h-5 w-5" aria-hidden="true" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;
