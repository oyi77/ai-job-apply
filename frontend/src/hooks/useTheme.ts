import { useEffect } from 'react';
import { useAppStore } from '../stores/appStore';

/**
 * Hook to apply theme to the document
 * Handles light, dark, and system theme preferences
 */
export const useTheme = () => {
  const theme = useAppStore((state) => state.theme);

  useEffect(() => {
    const root = window.document.documentElement;
    
    const applyTheme = (themeToApply: 'light' | 'dark') => {
      // Remove existing theme classes
      root.classList.remove('light', 'dark');
      // Add the new theme class
      root.classList.add(themeToApply);
    };

    if (theme === 'system') {
      // Check system preference
      const systemPreference = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';
      applyTheme(systemPreference);

      // Listen for system theme changes
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = (e: MediaQueryListEvent) => {
        applyTheme(e.matches ? 'dark' : 'light');
      };

      // Modern browsers
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleChange);
        return () => mediaQuery.removeEventListener('change', handleChange);
      } 
      // Fallback for older browsers
      else {
        mediaQuery.addListener(handleChange);
        return () => mediaQuery.removeListener(handleChange);
      }
    } else {
      // Apply the selected theme directly
      applyTheme(theme);
    }
  }, [theme]);
};

