/**
 * Light Theme Configuration
 * 
 * Semantic theme values for the light color scheme.
 * These tokens reference design tokens and provide component-level
 * abstractions for consistent theming.
 */

import { 
  colors, 
  typography, 
  spacing, 
  borderRadius, 
  shadows, 
  animations,
  zIndex 
} from '../design-tokens';

export interface LightTheme {
  name: string;
  colors: {
    // Semantic color roles
    background: string;
    surface: string;
    surfaceHover: string;
    border: string;
    borderHover: string;
    text: {
      primary: string;
      secondary: string;
      muted: string;
      inverse: string;
    };
    // Interactive states
    primary: {
      DEFAULT: string;
      hover: string;
      active: string;
      subtle: string;
      subtleHover: string;
    };
    secondary: {
      DEFAULT: string;
      hover: string;
      active: string;
      subtle: string;
      subtleHover: string;
    };
    success: {
      DEFAULT: string;
      hover: string;
      active: string;
      subtle: string;
      subtleHover: string;
    };
    warning: {
      DEFAULT: string;
      hover: string;
      active: string;
      subtle: string;
      subtleHover: string;
    };
    danger: {
      DEFAULT: string;
      hover: string;
      active: string;
      subtle: string;
      subtleHover: string;
    };
    info: {
      DEFAULT: string;
      hover: string;
      active: string;
      subtle: string;
      subtleHover: string;
    };
  };
  typography: {
    fontFamily: {
      body: string[];
      heading: string[];
      mono: string[];
    };
    fontSize: {
      xs: string;
      sm: string;
      base: string;
      lg: string;
      xl: string;
      '2xl': string;
      '3xl': string;
      '4xl': string;
      '5xl': string;
    };
    fontWeight: {
      normal: number;
      medium: number;
      semibold: number;
      bold: number;
    };
    lineHeight: {
      tight: string;
      normal: string;
      relaxed: string;
    };
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
    '4xl': string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
    full: string;
  };
  shadows: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  animations: {
    fast: string;
    normal: string;
    slow: string;
    easing: {
      DEFAULT: string;
      in: string;
      out: string;
      'in-out': string;
    };
  };
  zIndex: {
    dropdown: number;
    modal: number;
    tooltip: number;
    overlay: number;
  };
}

export const lightTheme: LightTheme = {
  name: 'light',
  
  colors: {
    // Base colors
    background: colors.gray[50],
    surface: colors.white,
    surfaceHover: colors.gray[50],
    border: colors.gray[200],
    borderHover: colors.gray[300],
    
    // Text colors
    text: {
      primary: colors.gray[900],
      secondary: colors.gray[600],
      muted: colors.gray[400],
      inverse: colors.white,
    },
    
    // Primary interactive
    primary: {
      DEFAULT: colors.primary[500],
      hover: colors.primary[600],
      active: colors.primary[700],
      subtle: colors.primary[50],
      subtleHover: colors.primary[100],
    },
    
    // Secondary interactive
    secondary: {
      DEFAULT: colors.secondary[500],
      hover: colors.secondary[600],
      active: colors.secondary[700],
      subtle: colors.secondary[50],
      subtleHover: colors.secondary[100],
    },
    
    // Success state
    success: {
      DEFAULT: colors.success[500],
      hover: colors.success[600],
      active: colors.success[700],
      subtle: colors.success[50],
      subtleHover: colors.success[100],
    },
    
    // Warning state
    warning: {
      DEFAULT: colors.warning[500],
      hover: colors.warning[600],
      active: colors.warning[700],
      subtle: colors.warning[50],
      subtleHover: colors.warning[100],
    },
    
    // Danger state
    danger: {
      DEFAULT: colors.danger[500],
      hover: colors.danger[600],
      active: colors.danger[700],
      subtle: colors.danger[50],
      subtleHover: colors.danger[100],
    },
    
    // Info state
    info: {
      DEFAULT: colors.info[500],
      hover: colors.info[600],
      active: colors.info[700],
      subtle: colors.info[50],
      subtleHover: colors.info[100],
    },
  },
  
  typography: {
    fontFamily: {
      body: typography.fontFamily.sans,
      heading: typography.fontFamily.sans,
      mono: typography.fontFamily.mono,
    },
    fontSize: {
      xs: typography.fontSize.xs,
      sm: typography.fontSize.sm,
      base: typography.fontSize.base,
      lg: typography.fontSize.lg,
      xl: typography.fontSize.xl,
      '2xl': typography.fontSize['2xl'],
      '3xl': typography.fontSize['3xl'],
      '4xl': typography.fontSize['4xl'],
      '5xl': typography.fontSize['5xl'],
    },
    fontWeight: {
      normal: typography.fontWeight.normal,
      medium: typography.fontWeight.medium,
      semibold: typography.fontWeight.semibold,
      bold: typography.fontWeight.bold,
    },
    lineHeight: {
      tight: typography.lineHeight.tight,
      normal: typography.lineHeight.normal,
      relaxed: typography.lineHeight.relaxed,
    },
  },
  
  spacing: {
    xs: spacing[1],
    sm: spacing[2],
    md: spacing[4],
    lg: spacing[6],
    xl: spacing[8],
    '2xl': spacing[12],
    '3xl': spacing[16],
    '4xl': spacing[24],
  },
  
  borderRadius: {
    sm: borderRadius.sm,
    md: borderRadius.md,
    lg: borderRadius.lg,
    xl: borderRadius.xl,
    full: borderRadius.full,
  },
  
  shadows: {
    sm: shadows.sm,
    md: shadows.md,
    lg: shadows.lg,
    xl: shadows.xl,
  },
  
  animations: {
    fast: animations.durations[150],
    normal: animations.durations[300],
    slow: animations.durations[500],
    easing: {
      DEFAULT: animations.easings.DEFAULT,
      in: animations.easings.in,
      out: animations.easings.out,
      'in-out': animations.easings['in-out'],
    },
  },
  
  zIndex: {
    dropdown: zIndex.dropdown,
    modal: zIndex.modal,
    tooltip: zIndex.tooltip,
    overlay: zIndex.overlay,
  },
};

// Re-export tokens for convenience
export { 
  colors, 
  typography, 
  spacing, 
  borderRadius, 
  shadows, 
  animations 
} from '../design-tokens';

export default lightTheme;
