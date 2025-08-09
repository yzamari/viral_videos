/**
 * Modern Clean Theme - Professional, Clean Design
 * Inspired by modern corporate websites with excellent UX
 */

import { createTheme, alpha } from '@mui/material/styles';

// Modern color palette
const colors = {
  primary: {
    main: '#FF6B35',      // Vibrant orange
    light: '#FF8F65',
    dark: '#E55100',
    contrastText: '#FFFFFF',
  },
  
  secondary: {
    main: '#004E89',      // Deep blue
    light: '#1A73B5',
    dark: '#003764',
    contrastText: '#FFFFFF',
  },
  
  accent: {
    purple: '#7B2CBF',
    green: '#00BF63',
    yellow: '#FFD23F',
    red: '#DC2F02',
  },
  
  neutral: {
    50: '#FAFAFA',
    100: '#F5F5F5',
    200: '#EEEEEE',
    300: '#E0E0E0',
    400: '#BDBDBD',
    500: '#9E9E9E',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
  },
  
  background: {
    default: '#FFFFFF',
    paper: '#FFFFFF',
    section: '#FAFAFA',
    card: '#FFFFFF',
  },
  
  text: {
    primary: '#212121',
    secondary: '#616161',
    disabled: '#9E9E9E',
  },
};

export const modernCleanTheme = createTheme({
  palette: {
    mode: 'light',
    primary: colors.primary,
    secondary: colors.secondary,
    background: colors.background,
    text: colors.text,
    divider: colors.neutral[200],
  },
  
  typography: {
    fontFamily: '"Inter", "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
    
    h1: {
      fontSize: '3rem',
      fontWeight: 900,
      lineHeight: 1.2,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontSize: '2.25rem',
      fontWeight: 800,
      lineHeight: 1.3,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontSize: '1.875rem',
      fontWeight: 800,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 700,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 700,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 700,
      lineHeight: 1.5,
    },
    body1: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.7,
    },
    body2: {
      fontSize: '0.875rem',
      fontWeight: 500,
      lineHeight: 1.6,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
      letterSpacing: '0.02em',
    },
  },
  
  shape: {
    borderRadius: 16,
  },
  
  shadows: [
    'none',
    '0 2px 4px rgba(0,0,0,0.05)',
    '0 4px 8px rgba(0,0,0,0.08)',
    '0 8px 16px rgba(0,0,0,0.1)',
    '0 12px 24px rgba(0,0,0,0.12)',
    '0 16px 32px rgba(0,0,0,0.14)',
    '0 20px 40px rgba(0,0,0,0.16)',
    ...Array(18).fill('0 24px 48px rgba(0,0,0,0.18)'),
  ],
  
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollBehavior: 'smooth',
        },
      },
    },
    
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 50,
          padding: '12px 32px',
          fontSize: '1rem',
          fontWeight: 600,
          boxShadow: 'none',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 16px rgba(0,0,0,0.15)',
          },
        },
        contained: {
          background: `linear-gradient(135deg, ${colors.primary.main} 0%, ${colors.primary.dark} 100%)`,
          '&:hover': {
            background: `linear-gradient(135deg, ${colors.primary.light} 0%, ${colors.primary.main} 100%)`,
          },
        },
        outlined: {
          borderWidth: 2,
          '&:hover': {
            borderWidth: 2,
            backgroundColor: alpha(colors.primary.main, 0.08),
          },
        },
      },
    },
    
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
          border: 'none',
          overflow: 'hidden',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 32px rgba(0,0,0,0.1)',
          },
        },
      },
    },
    
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 2px 12px rgba(0,0,0,0.04)',
        },
        elevation1: {
          boxShadow: '0 2px 12px rgba(0,0,0,0.04)',
        },
        elevation2: {
          boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
        },
        elevation3: {
          boxShadow: '0 8px 28px rgba(0,0,0,0.08)',
        },
      },
    },
    
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
            backgroundColor: colors.neutral[50],
            transition: 'all 0.3s ease',
            '& fieldset': {
              borderColor: colors.neutral[200],
              borderWidth: 1,
              transition: 'all 0.3s ease',
            },
            '&:hover': {
              backgroundColor: '#FFFFFF',
              '& fieldset': {
                borderColor: colors.primary.main,
                borderWidth: 2,
              },
            },
            '&.Mui-focused': {
              backgroundColor: '#FFFFFF',
              boxShadow: `0 0 0 4px ${alpha(colors.primary.main, 0.1)}`,
              '& fieldset': {
                borderColor: colors.primary.main,
                borderWidth: 2,
              },
            },
          },
          '& .MuiInputLabel-root': {
            fontWeight: 500,
          },
        },
      },
    },
    
    MuiSelect: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          '& .MuiOutlinedInput-notchedOutline': {
            borderColor: colors.neutral[200],
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: colors.primary.main,
            borderWidth: 2,
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: colors.primary.main,
            borderWidth: 2,
          },
        },
      },
    },
    
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          fontWeight: 500,
          height: 32,
        },
        filled: {
          backgroundColor: alpha(colors.primary.main, 0.1),
          color: colors.primary.main,
          '&:hover': {
            backgroundColor: alpha(colors.primary.main, 0.2),
          },
        },
      },
    },
    
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF',
          color: colors.text.primary,
          boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
        },
      },
    },
    
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRadius: '0 20px 20px 0',
          boxShadow: '4px 0 24px rgba(0,0,0,0.08)',
        },
      },
    },
    
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          margin: '4px 8px',
          transition: 'all 0.3s ease',
          '&:hover': {
            backgroundColor: alpha(colors.primary.main, 0.08),
          },
          '&.Mui-selected': {
            backgroundColor: alpha(colors.primary.main, 0.12),
            borderLeft: `4px solid ${colors.primary.main}`,
            '&:hover': {
              backgroundColor: alpha(colors.primary.main, 0.16),
            },
          },
        },
      },
    },
    
    MuiToggleButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          border: `2px solid ${colors.neutral[200]}`,
          margin: '0 4px',
          '&.Mui-selected': {
            backgroundColor: colors.primary.main,
            color: '#FFFFFF',
            border: `2px solid ${colors.primary.main}`,
            '&:hover': {
              backgroundColor: colors.primary.dark,
            },
          },
        },
      },
    },
    
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          height: 8,
          backgroundColor: colors.neutral[200],
        },
        bar: {
          borderRadius: 10,
          background: `linear-gradient(90deg, ${colors.primary.main} 0%, ${colors.primary.light} 100%)`,
        },
      },
    },
    
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          fontSize: '0.95rem',
        },
      },
    },
    
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: colors.neutral[900],
          borderRadius: 8,
          fontSize: '0.875rem',
          padding: '8px 12px',
        },
      },
    },
  },
});

// Dark theme variant with better contrast
export const modernDarkTheme = createTheme({
  ...modernCleanTheme,
  palette: {
    mode: 'dark',
    primary: {
      main: '#FF8F65',
      light: '#FFAB91',
      dark: '#FF6B35',
      contrastText: '#000000',
    },
    secondary: {
      main: '#4FC3F7',
      light: '#81D4FA',
      dark: '#29B6F6',
      contrastText: '#000000',
    },
    background: {
      default: '#0A0A0A',  // Much darker background
      paper: '#1A1A1A',     // Darker paper for better contrast
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#E0E0E0',  // Lighter secondary text
    },
    divider: '#333333',
  },
  components: {
    ...modernCleanTheme.components,
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#1A1A1A',
          borderRadius: 16,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#1A1A1A',
          border: '1px solid #333333',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            backgroundColor: '#2A2A2A',
            '& fieldset': {
              borderColor: '#444444',
            },
          },
        },
      },
    },
  },
});

export default modernCleanTheme;