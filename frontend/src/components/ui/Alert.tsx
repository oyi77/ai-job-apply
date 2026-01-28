import React from 'react';
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  InformationCircleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

interface AlertProps {
  type?: 'success' | 'warning' | 'error' | 'info';
  title?: string;
  message: string;
  dismissible?: boolean;
  onDismiss?: () => void;
  className?: string;
}

const Alert: React.FC<AlertProps> = ({
  type = 'info',
  title,
  message,
  dismissible = false,
  onDismiss,
  className = '',
}) => {
  const config = {
    success: {
      icon: CheckCircleIcon,
      bgColor: 'bg-success-50',
      borderColor: 'border-success-200',
      iconColor: 'text-success-400',
      titleColor: 'text-success-800',
      messageColor: 'text-success-700',
    },
    warning: {
      icon: ExclamationTriangleIcon,
      bgColor: 'bg-warning-50',
      borderColor: 'border-warning-200',
      iconColor: 'text-warning-400',
      titleColor: 'text-warning-800',
      messageColor: 'text-warning-700',
    },
    error: {
      icon: XCircleIcon,
      bgColor: 'bg-danger-50',
      borderColor: 'border-danger-200',
      iconColor: 'text-danger-400',
      titleColor: 'text-danger-800',
      messageColor: 'text-danger-700',
    },
    info: {
      icon: InformationCircleIcon,
      bgColor: 'bg-primary-50',
      borderColor: 'border-primary-200',
      iconColor: 'text-primary-400',
      titleColor: 'text-primary-800',
      messageColor: 'text-primary-700',
    },
  };

  const { icon: Icon, bgColor, borderColor, iconColor, titleColor, messageColor } = config[type];

  return (
    <div
      className={`rounded-md border p-4 ${bgColor} ${borderColor} ${className}`}
      role="alert"
    >
      <div className="flex">
        <div className="flex-shrink-0">
          <Icon className={`h-5 w-5 ${iconColor}`} aria-hidden="true" />
        </div>
        <div className="ml-3 flex-1">
          {title && (
            <h3 className={`text-sm font-medium ${titleColor}`}>
              {title}
            </h3>
          )}
          <div className={`${title ? 'mt-2' : ''} text-sm ${messageColor}`}>
            <p>{message}</p>
          </div>
        </div>
        {dismissible && onDismiss && (
          <div className="ml-auto pl-3">
            <div className="-mx-1.5 -my-1.5">
               <button
                 type="button"
                 className={`inline-flex rounded-md p-1.5 ${messageColor} hover:${bgColor} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-${type}-50 focus:ring-${type}-600`}
                 onClick={onDismiss}
                 aria-label="Dismiss alert"
                 data-testid="alert-dismiss"
               >
                 <span className="sr-only">Dismiss</span>
                 <XMarkIcon className="h-5 w-5" aria-hidden="true" />
               </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Alert;
