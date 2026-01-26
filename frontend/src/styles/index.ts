/**
 * Design System Exports
 * 
 * Centralized export point for all design tokens and theme values.
 * Provides utilities for accessing design values in code and generating
 * CSS custom properties for runtime access.
 */

// Design Tokens
import { 
  colors, 
  typography, 
  spacing, 
  borderRadius, 
  shadows, 
  animations, 
  breakpoints, 
  zIndex,
  designTokens,
} from './design-tokens';

import type {
  DesignTokens,
  ColorPalette,
} from './design-tokens';

// Light Theme
import { lightTheme } from './themes/light';
import type { LightTheme } from './themes/light';

export { 
  colors, 
  typography, 
  spacing, 
  borderRadius, 
  shadows, 
  animations, 
  breakpoints, 
  zIndex,
  designTokens,
  lightTheme,
};

export type {
  DesignTokens,
  ColorPalette,
  LightTheme,
};

/**
 * Generate CSS custom properties from design tokens
 * for runtime access in CSS-in-JS solutions
 */
export function generateCSSCustomProperties(): Record<string, string> {
  const properties: Record<string, string> = {};
  
  // Colors
  for (const [colorName, palette] of Object.entries(colors)) {
    if (typeof palette === 'object') {
      for (const [shade, value] of Object.entries(palette)) {
        properties[`--color-${colorName}-${shade}`] = value as string;
      }
    } else {
      properties[`--color-${colorName}`] = palette;
    }
  }
  
  // Typography
  for (const [prop, value] of Object.entries(typography.fontSize)) {
    properties[`--font-size-${prop}`] = value;
  }
  
  // Spacing
  for (const [size, value] of Object.entries(spacing)) {
    properties[`--spacing-${size}`] = value;
  }
  
  // Border Radius
  for (const [size, value] of Object.entries(borderRadius)) {
    properties[`--radius-${size}`] = value;
  }
  
  return properties;
}

/**
 * Get a token value by dot-notation path
 * Example: getToken('colors.primary.500') returns '#3b82f6'
 */
export function getToken(path: string): unknown {
  const parts = path.split('.');
  let current: unknown = designTokens;
  
  for (const part of parts) {
    if (current === null || current === undefined) {
      return undefined;
    }
    if (typeof current === 'object' && current !== null) {
      current = (current as Record<string, unknown>)[part];
    } else {
      return undefined;
    }
  }
  
  return current;
}

/**
 * Theme-aware color getter
 * Returns the appropriate color based on theme context
 */
export function getThemeColor(
  theme: typeof lightTheme,
  colorPath: string
): string {
  const parts = colorPath.split('.');
  let current: unknown = theme.colors;
  
  for (const part of parts) {
    if (current === null || current === undefined) {
      return '';
    }
    if (typeof current === 'object' && current !== null) {
      current = (current as Record<string, unknown>)[part];
    } else {
      return '';
    }
  }
  
  return current as string;
}

export default {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  animations,
  breakpoints,
  zIndex,
  designTokens,
  lightTheme,
  generateCSSCustomProperties,
  getToken,
  getThemeColor,
};
