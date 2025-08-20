import React from 'react';
import { SunIcon, MoonIcon, ComputerDesktopIcon } from '@heroicons/react/24/outline';

interface ThemeToggleProps {
  theme: 'light' | 'dark' | 'system';
  onThemeChange: (theme: 'light' | 'dark' | 'system') => void;
  className?: string;
}

const ThemeToggle: React.FC<ThemeToggleProps> = ({ 
  theme, 
  onThemeChange, 
  className = '' 
}) => {
  const themes = [
    { value: 'light', label: 'Light', icon: SunIcon },
    { value: 'dark', label: 'Dark', icon: MoonIcon },
    { value: 'system', label: 'System', icon: ComputerDesktopIcon },
  ];

  return (
    <div className={`flex items-center space-x-1 bg-gray-100 rounded-lg p-1 ${className}`}>
      {themes.map((themeOption) => {
        const Icon = themeOption.icon;
        const isActive = theme === themeOption.value;
        
        return (
          <button
            key={themeOption.value}
            onClick={() => onThemeChange(themeOption.value as 'light' | 'dark' | 'system')}
            className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              isActive
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            <Icon className="h-4 w-4" />
            <span className="hidden sm:inline">{themeOption.label}</span>
          </button>
        );
      })}
    </div>
  );
};

export default ThemeToggle;
