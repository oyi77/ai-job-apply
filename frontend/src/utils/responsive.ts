import { useState, useEffect } from 'react';
import { breakpoints } from '../styles/design-tokens';

/**
 * Utility functions to check current viewport state imperatively
 */
const parseValue = (val: string) => parseInt(val.replace('px', ''), 10);

export const isMobile = (): boolean => {
  if (typeof window === 'undefined') return false;
  return window.innerWidth < parseValue(breakpoints.md);
};

export const isTablet = (): boolean => {
  if (typeof window === 'undefined') return false;
  const width = window.innerWidth;
  return width >= parseValue(breakpoints.md) && width < parseValue(breakpoints.lg);
};

export const isDesktop = (): boolean => {
  if (typeof window === 'undefined') return true;
  return window.innerWidth >= parseValue(breakpoints.lg);
};

/**
 * Hook to track the current active breakpoint
 * Uses matchMedia for performance
 */
export const useBreakpoint = () => {
  const [breakpoint, setBreakpoint] = useState<keyof typeof breakpoints | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const queries = {
      sm: window.matchMedia(`(min-width: ${breakpoints.sm})`),
      md: window.matchMedia(`(min-width: ${breakpoints.md})`),
      lg: window.matchMedia(`(min-width: ${breakpoints.lg})`),
      xl: window.matchMedia(`(min-width: ${breakpoints.xl})`),
      '2xl': window.matchMedia(`(min-width: ${breakpoints['2xl']})`),
    };

    const getActiveBreakpoint = () => {
      if (queries['2xl'].matches) return '2xl';
      if (queries.xl.matches) return 'xl';
      if (queries.lg.matches) return 'lg';
      if (queries.md.matches) return 'md';
      if (queries.sm.matches) return 'sm';
      return null;
    };

    const handleChange = () => {
      setBreakpoint(getActiveBreakpoint());
    };

    // Initial check
    handleChange();

    // Add listeners
    Object.values(queries).forEach(query => {
      query.addEventListener('change', handleChange);
    });

    return () => {
      Object.values(queries).forEach(query => {
        query.removeEventListener('change', handleChange);
      });
    };
  }, []);

  return breakpoint;
};
