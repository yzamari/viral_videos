/**
 * Material Design 3 (Material You) Theme Configuration
 * Following Google's M3 design principles
 */

import { createTheme, alpha } from '@mui/material/styles';

// M3 Color Tokens - Dynamic color scheme
const m3Colors = {
  // Primary colors - vibrant purple/blue gradient
  primary: {
    0: '#000000',
    10: '#21005D',
    20: '#381E72',
    30: '#4F378B',
    40: '#6750A4',
    50: '#7F67BE',
    60: '#9A82DB',
    70: '#B69DF8',
    80: '#D0BCFF',
    90: '#EADDFF',
    95: '#F6EDFF',
    99: '#FFFBFE',
    100: '#FFFFFF',
  },
  
  // Secondary colors - teal accent
  secondary: {
    0: '#000000',
    10: '#051F20',
    20: '#0A3537',
    30: '#0F4A4C',
    40: '#146063',
    50: '#19777A',
    60: '#1E8E92',
    70: '#23A6AA',
    80: '#4FC3C7',
    90: '#7BE0E5',
    95: '#A3F0F4',
    99: '#F2FEFF',
    100: '#FFFFFF',
  },
  
  // Tertiary colors - coral accent
  tertiary: {
    0: '#000000',
    10: '#31111D',
    20: '#492532',
    30: '#633B48',
    40: '#7D5260',
    50: '#986977',
    60: '#B38290',
    70: '#CF9BA9',
    80: '#EBB5C3',
    90: '#FFD9E2',
    95: '#FFECF0',
    99: '#FFFBFA',
    100: '#FFFFFF',
  },
  
  // Error colors
  error: {
    0: '#000000',
    10: '#410E0B',
    20: '#601410',
    30: '#8C1D18',
    40: '#B3261E',
    50: '#DC362E',
    60: '#E46962',
    70: '#EC928E',
    80: '#F2B8B5',
    90: '#F9DEDC',
    95: '#FCEEEE',
    99: '#FFFBF9',
    100: '#FFFFFF',
  },
  
  // Neutral colors
  neutral: {
    0: '#000000',
    10: '#1C1B1F',
    20: '#313033',
    30: '#484649',
    40: '#605D62',
    50: '#79747E',
    60: '#938F99',
    70: '#AEA9B4',
    80: '#CAC4D0',
    90: '#E7E0EC',
    95: '#F5EFF7',
    99: '#FFFBFE',
    100: '#FFFFFF',
  },
  
  // Surface colors with elevation
  surface: {
    dim: '#DED8E0',
    default: '#FDF7FF',
    bright: '#FDF7FF',
    containerLowest: '#FFFFFF',
    containerLow: '#F7F2FA',
    container: '#F1ECF4',
    containerHigh: '#ECE6EE',
    containerHighest: '#E6E0E9',
  }
};

// Create M3 theme
export const m3Theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: m3Colors.primary[40],
      light: m3Colors.primary[80],
      dark: m3Colors.primary[20],
      contrastText: m3Colors.primary[100],
    },
    secondary: {
      main: m3Colors.secondary[40],
      light: m3Colors.secondary[80],
      dark: m3Colors.secondary[20],
      contrastText: m3Colors.secondary[100],
    },
    error: {
      main: m3Colors.error[40],
      light: m3Colors.error[80],
      dark: m3Colors.error[20],
      contrastText: m3Colors.error[100],
    },
    warning: {
      main: '#F9A825',
      light: '#FFD54F',
      dark: '#F57C00',
      contrastText: '#000000',
    },
    info: {
      main: m3Colors.secondary[50],
      light: m3Colors.secondary[70],
      dark: m3Colors.secondary[30],
      contrastText: m3Colors.secondary[100],
    },
    success: {
      main: '#2E7D32',
      light: '#66BB6A',
      dark: '#1B5E20',
      contrastText: '#FFFFFF',
    },
    background: {
      default: m3Colors.surface.default,
      paper: m3Colors.surface.container,
    },
    text: {
      primary: m3Colors.neutral[10],
      secondary: m3Colors.neutral[40],
      disabled: m3Colors.neutral[60],
    },
    divider: alpha(m3Colors.neutral[40], 0.12),
  },
  
  typography: {
    fontFamily: '"Google Sans", "Roboto", "Helvetica", "Arial", sans-serif',
    
    // Display styles
    h1: {
      fontSize: '57px',
      lineHeight: '64px',
      letterSpacing: '-0.25px',
      fontWeight: 400,
    },
    h2: {
      fontSize: '45px',
      lineHeight: '52px',
      letterSpacing: '0px',
      fontWeight: 400,
    },
    h3: {
      fontSize: '36px',
      lineHeight: '44px',
      letterSpacing: '0px',
      fontWeight: 400,
    },
    
    // Headline styles
    h4: {
      fontSize: '32px',
      lineHeight: '40px',
      letterSpacing: '0px',
      fontWeight: 400,
    },
    h5: {
      fontSize: '28px',
      lineHeight: '36px',
      letterSpacing: '0px',
      fontWeight: 400,
    },
    h6: {
      fontSize: '24px',
      lineHeight: '32px',
      letterSpacing: '0px',
      fontWeight: 400,
    },
    
    // Body styles
    body1: {
      fontSize: '16px',
      lineHeight: '24px',
      letterSpacing: '0.5px',
      fontWeight: 400,
    },
    body2: {
      fontSize: '14px',
      lineHeight: '20px',
      letterSpacing: '0.25px',
      fontWeight: 400,
    },
    
    // Label styles
    button: {
      fontSize: '14px',
      lineHeight: '20px',
      letterSpacing: '0.1px',
      fontWeight: 500,
      textTransform: 'none',
    },
    caption: {
      fontSize: '12px',
      lineHeight: '16px',
      letterSpacing: '0.4px',
      fontWeight: 400,
    },
    overline: {
      fontSize: '11px',
      lineHeight: '16px',
      letterSpacing: '0.5px',
      fontWeight: 500,
      textTransform: 'uppercase',
    },
  },
  
  shape: {
    borderRadius: 28, // M3 uses larger border radius
  },
  
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          padding: '10px 24px',
          fontSize: '14px',
          fontWeight: 500,
          letterSpacing: '0.1px',
          lineHeight: '20px',
          textTransform: 'none',
          boxShadow: 'none',
          transition: 'all 0.2s cubic-bezier(0.2, 0, 0, 1)',
          '&:hover': {
            boxShadow: '0px 1px 2px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15)',
          },
        },
        contained: {
          '&:hover': {
            boxShadow: '0px 1px 2px rgba(0, 0, 0, 0.3), 0px 2px 6px 2px rgba(0, 0, 0, 0.15)',
          },
        },
        outlined: {
          borderWidth: 1,
          '&:hover': {
            borderWidth: 1,
            backgroundColor: alpha(m3Colors.primary[40], 0.08),
          },
        },
        text: {
          '&:hover': {
            backgroundColor: alpha(m3Colors.primary[40], 0.08),
          },
        },
        // FAB styles
        fab: {
          borderRadius: 16,
          boxShadow: '0px 3px 3px rgba(0, 0, 0, 0.2), 0px 3px 4px rgba(0, 0, 0, 0.14), 0px 1px 8px rgba(0, 0, 0, 0.12)',
          '&:hover': {
            boxShadow: '0px 4px 4px rgba(0, 0, 0, 0.25), 0px 4px 5px rgba(0, 0, 0, 0.18), 0px 1px 10px rgba(0, 0, 0, 0.14)',
          },
        },
      },
    },
    
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 28,
          boxShadow: '0px 1px 2px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15)',
          backgroundImage: 'none',
          backgroundColor: m3Colors.surface.container,
          transition: 'all 0.2s cubic-bezier(0.2, 0, 0, 1)',
          '&:hover': {
            boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.3), 0px 4px 5px rgba(0, 0, 0, 0.15)',
          },
        },
      },
    },
    
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
        rounded: {
          borderRadius: 28,
        },
        elevation1: {
          boxShadow: '0px 1px 2px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15)',
        },
        elevation2: {
          boxShadow: '0px 1px 2px rgba(0, 0, 0, 0.3), 0px 2px 6px 2px rgba(0, 0, 0, 0.15)',
        },
        elevation3: {
          boxShadow: '0px 4px 8px 3px rgba(0, 0, 0, 0.15), 0px 1px 3px rgba(0, 0, 0, 0.3)',
        },
      },
    },
    
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 16,
            '& fieldset': {
              borderWidth: 1,
            },
            '&:hover fieldset': {
              borderWidth: 1,
            },
            '&.Mui-focused fieldset': {
              borderWidth: 2,
            },
          },
          '& .MuiFilledInput-root': {
            borderRadius: '16px 16px 0 0',
            backgroundColor: m3Colors.surface.containerHighest,
            '&:hover': {
              backgroundColor: alpha(m3Colors.surface.containerHighest, 0.9),
            },
            '&.Mui-focused': {
              backgroundColor: m3Colors.surface.containerHighest,
            },
          },
        },
      },
    },
    
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          height: 32,
          fontWeight: 500,
          fontSize: '14px',
          letterSpacing: '0.1px',
        },
        filled: {
          backgroundColor: m3Colors.surface.containerHigh,
          '&:hover': {
            backgroundColor: alpha(m3Colors.surface.containerHigh, 0.8),
          },
        },
        outlined: {
          borderColor: m3Colors.neutral[50],
          '&:hover': {
            backgroundColor: alpha(m3Colors.primary[40], 0.08),
          },
        },
      },
    },
    
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: m3Colors.surface.container,
          color: m3Colors.neutral[10],
          boxShadow: 'none',
          borderBottom: `1px solid ${alpha(m3Colors.neutral[40], 0.12)}`,
        },
      },
    },
    
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundImage: 'none',
          backgroundColor: m3Colors.surface.containerLow,
          borderRadius: '0 28px 28px 0',
        },
      },
    },
    
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 28,
          backgroundImage: 'none',
          backgroundColor: m3Colors.surface.container,
        },
      },
    },
    
    MuiSnackbar: {
      styleOverrides: {
        root: {
          '& .MuiSnackbarContent-root': {
            borderRadius: 16,
            backgroundColor: m3Colors.neutral[90],
            color: m3Colors.neutral[10],
          },
        },
      },
    },
    
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          borderRadius: 8,
          backgroundColor: m3Colors.neutral[90],
          color: m3Colors.neutral[10],
          fontSize: '12px',
          padding: '8px 12px',
        },
      },
    },
    
    MuiSwitch: {
      styleOverrides: {
        root: {
          width: 52,
          height: 32,
          padding: 0,
          '& .MuiSwitch-switchBase': {
            padding: 0,
            margin: 4,
            transitionDuration: '200ms',
            '&.Mui-checked': {
              transform: 'translateX(20px)',
              color: '#fff',
              '& + .MuiSwitch-track': {
                backgroundColor: m3Colors.primary[40],
                opacity: 1,
                border: 0,
              },
            },
          },
          '& .MuiSwitch-thumb': {
            boxSizing: 'border-box',
            width: 24,
            height: 24,
          },
          '& .MuiSwitch-track': {
            borderRadius: 16,
            backgroundColor: m3Colors.surface.containerHighest,
            opacity: 1,
          },
        },
      },
    },
    
    MuiFab: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0px 3px 3px rgba(0, 0, 0, 0.2), 0px 3px 4px rgba(0, 0, 0, 0.14), 0px 1px 8px rgba(0, 0, 0, 0.12)',
          '&:hover': {
            boxShadow: '0px 4px 4px rgba(0, 0, 0, 0.25), 0px 4px 5px rgba(0, 0, 0, 0.18), 0px 1px 10px rgba(0, 0, 0, 0.14)',
          },
        },
        primary: {
          backgroundColor: m3Colors.primary[40],
          color: m3Colors.primary[100],
          '&:hover': {
            backgroundColor: m3Colors.primary[30],
          },
        },
        secondary: {
          backgroundColor: m3Colors.secondary[40],
          color: m3Colors.secondary[100],
          '&:hover': {
            backgroundColor: m3Colors.secondary[30],
          },
        },
        extended: {
          borderRadius: 16,
          padding: '16px 24px',
          minWidth: 80,
        },
      },
    },
    
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 28,
          margin: '4px 8px',
          '&:hover': {
            backgroundColor: alpha(m3Colors.primary[40], 0.08),
          },
          '&.Mui-selected': {
            backgroundColor: alpha(m3Colors.primary[40], 0.12),
            '&:hover': {
              backgroundColor: alpha(m3Colors.primary[40], 0.16),
            },
          },
        },
      },
    },
    
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          fontSize: '14px',
          letterSpacing: '0.1px',
          minHeight: 48,
          padding: '12px 16px',
          '&:hover': {
            backgroundColor: alpha(m3Colors.primary[40], 0.08),
          },
          '&.Mui-selected': {
            color: m3Colors.primary[40],
          },
        },
      },
    },
    
    MuiTabs: {
      styleOverrides: {
        indicator: {
          height: 3,
          borderRadius: '3px 3px 0 0',
        },
      },
    },
  },
});

// Dark theme variant
export const m3DarkTheme = createTheme({
  ...m3Theme,
  palette: {
    mode: 'dark',
    primary: {
      main: m3Colors.primary[80],
      light: m3Colors.primary[90],
      dark: m3Colors.primary[60],
      contrastText: m3Colors.primary[20],
    },
    secondary: {
      main: m3Colors.secondary[80],
      light: m3Colors.secondary[90],
      dark: m3Colors.secondary[60],
      contrastText: m3Colors.secondary[20],
    },
    error: {
      main: m3Colors.error[80],
      light: m3Colors.error[90],
      dark: m3Colors.error[60],
      contrastText: m3Colors.error[20],
    },
    background: {
      default: m3Colors.neutral[10],
      paper: m3Colors.neutral[20],
    },
    text: {
      primary: m3Colors.neutral[90],
      secondary: m3Colors.neutral[70],
      disabled: m3Colors.neutral[50],
    },
    divider: alpha(m3Colors.neutral[60], 0.12),
  },
});

export default m3Theme;