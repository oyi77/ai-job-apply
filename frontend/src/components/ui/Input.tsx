import React, { forwardRef } from 'react';
import type { InputProps } from '../../types';

const Input = forwardRef<HTMLInputElement | HTMLTextAreaElement, InputProps>(({
  name,
  label,
  type = 'text',
  placeholder,
  value,
  onChange,
  error,
  required = false,
  disabled = false,
  className = '',
  size = 'md',
  success = false,
  icon,
  rightIcon,
  as = 'input',
  rows = 4,
  helpText,
  ...props
}, ref) => {
  const inputId = `input-${name}`;

  const baseClasses = 'block w-full border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-0 transition-colors duration-200';
  const stateClasses = error
    ? 'border-danger-300 focus:ring-danger-500 focus:border-danger-500'
    : success
      ? 'border-success-300 focus:ring-success-500 focus:border-success-500'
      : 'border-gray-300 focus:ring-primary-500 focus:border-primary-500';
  const disabledClasses = disabled ? 'bg-gray-50 cursor-not-allowed' : 'bg-white';

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-lg',
  };

  const classes = `${baseClasses} ${stateClasses} ${disabledClasses} ${sizeClasses[size]} ${className}`;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (onChange) {
      onChange(e.target.value);
    }
  };

  if (as === 'textarea') {
    return (
      <div className="space-y-1">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-gray-700">
            {label}
            {required && <span className="text-danger-500 ml-1">*</span>}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              {icon}
            </div>
          )}
          <textarea
            id={inputId}
            name={name}
            value={value || ''}
            onChange={handleChange}
            placeholder={placeholder}
            required={required}
            disabled={disabled}
            rows={rows}
            className={`${classes} ${icon ? 'pl-10' : ''} ${rightIcon ? 'pr-10' : ''}`}
            ref={ref as React.Ref<HTMLTextAreaElement>}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              {rightIcon}
            </div>
          )}
        </div>
        {error && (
          <p className="text-sm text-danger-600">{error}</p>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-danger-500 ml-1">*</span>}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            {icon}
          </div>
        )}
        <input
          id={inputId}
          name={name}
          type={type}
          value={value || ''}
          onChange={handleChange}
          placeholder={placeholder}
          required={required}
          disabled={disabled}
          className={`${classes} ${icon ? 'pl-10' : ''} ${rightIcon ? 'pr-10' : ''}`}
          ref={ref as React.Ref<HTMLInputElement>}
          {...props}
        />
        {rightIcon && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            {rightIcon}
          </div>
        )}
      </div>
      {error && (
        <p className="text-sm text-danger-600">{error}</p>
      )}
      {!error && helpText && (
        <p className="text-xs text-gray-500">{helpText}</p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
