/**
 * Enhanced Theme - High Contrast Professional Design
 * Optimized for maximum readability in both light and dark modes
 */

import { createTheme, alpha } from '@mui/material/styles';

// Enhanced color palette with better contrast
const lightColors = {
  primary: {
    main: '#0052CC', // Strong blue
    light: '#2684FF',
    dark: '#00357A',
    contrastText: '#FFFFFF',
  },
  
  secondary: {
    main: '#5E376D', // Deep purple
    light: '#7A4E8C',
    dark: '#42254B',
    contrastText: '#FFFFFF',
  },
  
  accent: {
    main: '#00875A', // Forest green
    light: '#36B37E',
    dark: '#006644',
    contrastText: '#FFFFFF',
  },
  
  error: {
    main: '#DE350B',
    light: '#FF5630',
    dark: '#BF2600',
  },
  
  warning: {
    main: '#FF8B00',
    light: '#FFAB00',
    dark: '#FF6B00',
  },
  
  info: {
    main: '#0065FF',
    light: '#4C9AFF',
    dark: '#0052CC',
  },
  
  success: {
    main: '#00875A',
    light: '#36B37E',
    dark: '#006644',
  },
  
  background: {
    default: '#F8F9FA',
    paper: '#FFFFFF',
    subtle: '#F3F4F6',
    elevated: '#FFFFFF',
    input: '#FFFFFF',
  },
  
  text: {
    primary: '#172B4D', // Very dark blue-gray
    secondary: '#5E6C84', // Medium gray
    disabled: '#A5ADBA',
    hint: '#7A869A',
  },
  
  divider: '#DFE1E6',
  border: '#C1C7D0',
};

const darkColors = {
  primary: {
    main: '#579DFF', // Bright blue
    light: '#85B8FF',
    dark: '#388BFF',
    contrastText: '#000000',
  },
  
  secondary: {
    main: '#B794F6', // Bright purple
    light: '#D6B7FF',
    dark: '#9F7AEA',
    contrastText: '#000000',
  },
  
  accent: {
    main: '#57D9A3', // Bright teal
    light: '#79F2C0',
    dark: '#00C781',
    contrastText: '#000000',
  },
  
  error: {
    main: '#FF5630',
    light: '#FF7452',
    dark: '#DE350B',
  },
  
  warning: {
    main: '#FFAB00',
    light: '#FFC400',
    dark: '#FF8B00',
  },
  
  info: {
    main: '#4C9AFF',
    light: '#79B8FF',
    dark: '#2684FF',
  },
  
  success: {
    main: '#36B37E',
    light: '#57D9A3',
    dark: '#00875A',
  },
  
  background: {
    default: '#0D1117', // Very dark
    paper: '#161B22', // Slightly lighter
    subtle: '#21262D',
    elevated: '#1C2128',
  },
  
  text: {
    primary: '#F0F6FC', // Almost white
    secondary: '#8B949E', // Light gray
    disabled: '#484F58',
    hint: '#6E7681',
  },
  
  divider: '#30363D',
  border: '#30363D',
};

// Create enhanced light theme
export const enhancedLightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: lightColors.primary,
    secondary: lightColors.secondary,
    error: lightColors.error,
    warning: lightColors.warning,
    info: lightColors.info,
    success: lightColors.success,
    background: lightColors.background,
    text: lightColors.text,
    divider: lightColors.divider,
  },
  
  typography: {
    fontFamily: '"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      lineHeight: 1.2,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '1.125rem',
      fontWeight: 600,
      lineHeight: 1.5,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.6,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
      letterSpacing: '0.01em',
    },
    caption: {
      fontSize: '0.75rem',
    },
  },
  
  shape: {
    borderRadius: 6,
  },
  
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          padding: '10px 20px',
          fontWeight: 600,
          fontSize: '0.95rem',
          boxShadow: 'none',
          textTransform: 'none',
          '&:hover': {
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          },
        },
        contained: {
          backgroundColor: lightColors.primary.main,
          color: '#FFFFFF',
          '&:hover': {
            backgroundColor: lightColors.primary.dark,
            transform: 'translateY(-1px)',
          },
        },
        outlined: {
          borderWidth: 2,
          borderColor: lightColors.primary.main,
          color: lightColors.primary.main,
          '&:hover': {
            borderWidth: 2,
            backgroundColor: lightColors.primary.main,
            color: '#FFFFFF',
          },
        },
      },
    },
    
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          border: `2px solid ${lightColors.divider}`,
          boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
          backgroundColor: '#FFFFFF',
        },
      },
    },
    
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#FFFFFF',
        },
        rounded: {
          borderRadius: 8,
        },
        outlined: {
          border: '2px solid #E5E7EB',
        },
      },
    },
    
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            backgroundColor: '#FFFFFF',
            '& input': {
              color: lightColors.text.primary,
              '&::placeholder': {
                color: lightColors.text.secondary,
                opacity: 0.7,
              },
            },
            '& fieldset': {
              borderColor: '#D1D5DB',
              borderWidth: 2,
            },
            '&:hover fieldset': {
              borderColor: lightColors.primary.main,
              backgroundColor: '#F9FAFB',
            },
            '&.Mui-focused': {
              backgroundColor: '#FFFFFF',
              '& fieldset': {
                borderColor: lightColors.primary.main,
                borderWidth: 2.5,
              },
            },
          },
          '& .MuiInputLabel-root': {
            color: lightColors.text.secondary,
            fontWeight: 500,
            '&.Mui-focused': {
              color: lightColors.primary.main,
              fontWeight: 600,
            },
          },
        },
      },
    },
    
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          fontWeight: 500,
          fontSize: '0.875rem',
        },
        filled: {
          backgroundColor: '#EBF5FF',
          color: lightColors.primary.main,
        },
        outlined: {
          borderWidth: 2,
        },
      },
    },
    
    MuiSelect: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-notchedOutline': {
            borderWidth: 2,
            borderColor: '#D1D5DB',
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: lightColors.primary.main,
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: lightColors.primary.main,
            borderWidth: 2.5,
          },
        },
        select: {
          backgroundColor: '#FFFFFF',
          color: lightColors.text.primary,
        },
      },
    },
    
    MuiInputBase: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF',
          '& input': {
            color: lightColors.text.primary,
            fontWeight: 500,
          },
        },
      },
    },
    
    MuiFormLabel: {
      styleOverrides: {
        root: {
          color: lightColors.text.secondary,
          fontWeight: 500,
          '&.Mui-focused': {
            color: lightColors.primary.main,
            fontWeight: 600,
          },
        },
      },
    },
    
    MuiToggleButton: {
      styleOverrides: {
        root: {
          borderWidth: 2,
          color: lightColors.text.primary,
          '&.Mui-selected': {
            backgroundColor: lightColors.primary.main,
            color: '#FFFFFF',
            '&:hover': {
              backgroundColor: lightColors.primary.dark,
            },
          },
        },
      },
    },
  },
});

// Create enhanced dark theme
export const enhancedDarkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: darkColors.primary,
    secondary: darkColors.secondary,
    error: darkColors.error,
    warning: darkColors.warning,
    info: darkColors.info,
    success: darkColors.success,
    background: darkColors.background,
    text: darkColors.text,
    divider: darkColors.divider,
  },
  
  typography: enhancedLightTheme.typography,
  shape: enhancedLightTheme.shape,
  
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          padding: '8px 16px',
          fontWeight: 500,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
          },
        },
        contained: {
          '&:hover': {
            transform: 'translateY(-1px)',
          },
        },
      },
    },
    
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          border: `1px solid ${darkColors.divider}`,
          boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
          backgroundColor: darkColors.background.paper,
        },
      },
    },
    
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: darkColors.background.paper,
        },
        rounded: {
          borderRadius: 8,
        },
      },
    },
    
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: darkColors.background.elevated,
          borderBottom: `1px solid ${darkColors.divider}`,
        },
      },
    },
    
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: darkColors.background.paper,
          borderRight: `1px solid ${darkColors.divider}`,
        },
      },
    },
    
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            backgroundColor: darkColors.background.subtle,
            '& fieldset': {
              borderColor: darkColors.border,
              borderWidth: 1.5,
            },
            '&:hover fieldset': {
              borderColor: darkColors.primary.main,
            },
            '&.Mui-focused fieldset': {
              borderColor: darkColors.primary.main,
              borderWidth: 2,
            },
          },
          '& .MuiInputLabel-root': {
            color: darkColors.text.secondary,
          },
        },
      },
    },
    
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          fontWeight: 500,
        },
      },
    },
    
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          marginBottom: 2,
          '&:hover': {
            backgroundColor: alpha(darkColors.primary.main, 0.08),
          },
          '&.Mui-selected': {
            backgroundColor: alpha(darkColors.primary.main, 0.12),
            borderLeft: `3px solid ${darkColors.primary.main}`,
            '&:hover': {
              backgroundColor: alpha(darkColors.primary.main, 0.16),
            },
          },
        },
      },
    },
    
    MuiIconButton: {
      styleOverrides: {
        root: {
          color: darkColors.text.secondary,
          '&:hover': {
            backgroundColor: alpha(darkColors.primary.main, 0.08),
          },
        },
      },
    },
  },
});

export default enhancedLightTheme;