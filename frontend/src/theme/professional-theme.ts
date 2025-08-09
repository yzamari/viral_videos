/**
 * Professional Theme - Clean, Authentic Design
 * No AI-generated look, just clean professional aesthetics
 */

import { createTheme, alpha } from '@mui/material/styles';

// Professional color palette - clean and minimal
const colors = {
  // Primary - Deep blue (trustworthy, professional)
  primary: {
    main: '#1e40af', // Deep blue
    light: '#3b82f6', // Bright blue
    dark: '#1e3a8a', // Navy blue
    contrast: '#ffffff',
  },
  
  // Secondary - Warm gray (neutral, sophisticated)
  secondary: {
    main: '#64748b', // Slate
    light: '#94a3b8', 
    dark: '#475569',
    contrast: '#ffffff',
  },
  
  // Accent - Emerald (growth, success)
  accent: {
    main: '#10b981',
    light: '#34d399',
    dark: '#059669',
    contrast: '#ffffff',
  },
  
  // Error, Warning, Info, Success - Standard
  error: {
    main: '#dc2626',
    light: '#ef4444',
    dark: '#b91c1c',
  },
  
  warning: {
    main: '#f59e0b',
    light: '#fbbf24',
    dark: '#d97706',
  },
  
  info: {
    main: '#3b82f6',
    light: '#60a5fa',
    dark: '#2563eb',
  },
  
  success: {
    main: '#10b981',
    light: '#34d399',
    dark: '#059669',
  },
  
  // Backgrounds - Clean whites and grays
  background: {
    default: '#ffffff',
    paper: '#ffffff',
    subtle: '#f8fafc',
    gray: '#f1f5f9',
  },
  
  // Text - High contrast, readable
  text: {
    primary: '#0f172a', // Almost black
    secondary: '#475569', // Dark gray
    disabled: '#94a3b8', // Light gray
    hint: '#64748b',
  },
  
  // Borders and dividers
  divider: '#e2e8f0',
  border: '#cbd5e1',
};

// Create professional theme
export const professionalTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: colors.primary.main,
      light: colors.primary.light,
      dark: colors.primary.dark,
      contrastText: colors.primary.contrast,
    },
    secondary: {
      main: colors.secondary.main,
      light: colors.secondary.light,
      dark: colors.secondary.dark,
      contrastText: colors.secondary.contrast,
    },
    error: colors.error,
    warning: colors.warning,
    info: colors.info,
    success: colors.success,
    background: {
      default: colors.background.default,
      paper: colors.background.paper,
    },
    text: colors.text,
    divider: colors.divider,
  },
  
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      lineHeight: 1.2,
      letterSpacing: '-0.02em',
      color: colors.text.primary,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '-0.01em',
      color: colors.text.primary,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      lineHeight: 1.4,
      color: colors.text.primary,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
      color: colors.text.primary,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.5,
      color: colors.text.primary,
    },
    h6: {
      fontSize: '1.125rem',
      fontWeight: 600,
      lineHeight: 1.5,
      color: colors.text.primary,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
      color: colors.text.primary,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.6,
      color: colors.text.secondary,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
      letterSpacing: '0.02em',
    },
    caption: {
      fontSize: '0.75rem',
      color: colors.text.secondary,
    },
  },
  
  shape: {
    borderRadius: 8, // Subtle, professional radius
  },
  
  shadows: [
    'none',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    // ... rest are similar subtle shadows
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  ],
  
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          padding: '8px 16px',
          fontWeight: 500,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
        contained: {
          backgroundColor: colors.primary.main,
          color: '#ffffff',
          '&:hover': {
            backgroundColor: colors.primary.dark,
          },
        },
        outlined: {
          borderColor: colors.border,
          color: colors.text.primary,
          '&:hover': {
            backgroundColor: colors.background.subtle,
            borderColor: colors.primary.main,
          },
        },
        text: {
          color: colors.primary.main,
          '&:hover': {
            backgroundColor: alpha(colors.primary.main, 0.04),
          },
        },
      },
    },
    
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          border: `1px solid ${colors.divider}`,
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
          backgroundColor: colors.background.paper,
        },
      },
    },
    
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: colors.background.paper,
        },
        rounded: {
          borderRadius: 12,
        },
        elevation1: {
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        },
      },
    },
    
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: colors.background.paper,
          color: colors.text.primary,
          borderBottom: `1px solid ${colors.divider}`,
          boxShadow: 'none',
        },
      },
    },
    
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: colors.background.paper,
          borderRight: `1px solid ${colors.divider}`,
        },
      },
    },
    
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            backgroundColor: colors.background.paper,
            '& fieldset': {
              borderColor: colors.border,
            },
            '&:hover fieldset': {
              borderColor: colors.primary.light,
            },
            '&.Mui-focused fieldset': {
              borderColor: colors.primary.main,
              borderWidth: 2,
            },
          },
        },
      },
    },
    
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          fontWeight: 500,
        },
        filled: {
          backgroundColor: colors.background.gray,
          color: colors.text.primary,
        },
        outlined: {
          borderColor: colors.border,
          color: colors.text.primary,
        },
      },
    },
    
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          marginBottom: 4,
          '&:hover': {
            backgroundColor: colors.background.subtle,
          },
          '&.Mui-selected': {
            backgroundColor: alpha(colors.primary.main, 0.08),
            borderLeft: `3px solid ${colors.primary.main}`,
            '&:hover': {
              backgroundColor: alpha(colors.primary.main, 0.12),
            },
          },
        },
      },
    },
    
    MuiIconButton: {
      styleOverrides: {
        root: {
          color: colors.text.secondary,
          '&:hover': {
            backgroundColor: colors.background.subtle,
          },
        },
      },
    },
    
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: colors.text.primary,
          color: colors.background.paper,
          fontSize: '0.75rem',
          borderRadius: 4,
        },
      },
    },
    
    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: colors.divider,
        },
      },
    },
    
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          backgroundColor: colors.background.gray,
          borderRadius: 4,
        },
        bar: {
          borderRadius: 4,
        },
      },
    },
    
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

// Dark theme variant with better contrast
export const professionalDarkTheme = createTheme({
  ...professionalTheme,
  palette: {
    mode: 'dark',
    primary: {
      main: '#60a5fa', // Bright blue for dark mode
      light: '#93c5fd',
      dark: '#3b82f6',
      contrastText: '#000000', // Black text on blue buttons
    },
    secondary: {
      main: '#a5b4c7',
      light: '#cbd5e1',
      dark: '#64748b',
      contrastText: '#000000',
    },
    error: {
      main: '#ef4444',
      light: '#f87171',
      dark: '#dc2626',
    },
    warning: {
      main: '#f59e0b',
      light: '#fbbf24',
      dark: '#d97706',
    },
    info: {
      main: '#60a5fa',
      light: '#93c5fd',
      dark: '#3b82f6',
    },
    success: {
      main: '#10b981',
      light: '#34d399',
      dark: '#059669',
    },
    background: {
      default: '#0f172a', // Dark navy
      paper: '#1e293b', // Slightly lighter
    },
    text: {
      primary: '#ffffff', // Pure white for better contrast
      secondary: '#cbd5e1', // Lighter gray for better readability
      disabled: '#64748b',
    },
    divider: '#475569', // Lighter divider for visibility
  },
});

export default professionalTheme;