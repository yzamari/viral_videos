import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  Toolbar,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Badge,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useTheme,
  useMediaQuery,
  Chip,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Campaign,
  Analytics,
  TrendingUp,
  VideoLibrary,
  Settings,
  Logout,
  Notifications,
  AccountCircle,
  Brightness4,
  Brightness7,
  Close,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useAppDispatch, useAppSelector } from '../store/store';
import { uiActions, notificationsActions } from '../store/store';
import io, { Socket } from 'socket.io-client';

const DRAWER_WIDTH = 280;

interface LayoutProps {
  children: React.ReactNode;
}

interface NavigationItem {
  title: string;
  icon: React.ReactElement;
  path: string;
  badge?: string | number;
  disabled?: boolean;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const dispatch = useAppDispatch();
  
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const { 
    theme: currentTheme, 
    sidebarOpen, 
    mobileMenuOpen 
  } = useAppSelector(state => state.ui);
  
  const { 
    notifications, 
    unreadCount 
  } = useAppSelector(state => state.notifications);

  const [anchorElUser, setAnchorElUser] = useState<null | HTMLElement>(null);
  const [anchorElNotifications, setAnchorElNotifications] = useState<null | HTMLElement>(null);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'warning' | 'info'>('info');

  // Initialize WebSocket connection
  useEffect(() => {
    const socketUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const newSocket = io(socketUrl, {
      auth: {
        token: localStorage.getItem('auth_token'),
      },
    });

    newSocket.on('connect', () => {
      console.log('WebSocket connected');
    });

    newSocket.on('campaign_update', (data) => {
      showSnackbar(`Campaign "${data.name}" has been updated`, 'info');
    });

    newSocket.on('trending_update', () => {
      showSnackbar('New trending topics available', 'info');
    });

    newSocket.on('notification', (notification) => {
      dispatch(notificationsActions.addNotification(notification));
      showSnackbar(notification.title, notification.type);
    });

    newSocket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [dispatch]);

  const navigationItems: NavigationItem[] = [
    {
      title: 'Dashboard',
      icon: <Dashboard />,
      path: '/dashboard',
    },
    {
      title: 'Campaigns',
      icon: <Campaign />,
      path: '/campaigns',
    },
    {
      title: 'Create Campaign',
      icon: <Campaign />,
      path: '/create-campaign',
    },
    {
      title: 'Analytics',
      icon: <Analytics />,
      path: '/analytics',
    },
    {
      title: 'Trending',
      icon: <TrendingUp />,
      path: '/trending',
      badge: 'HOT',
    },
    {
      title: 'Video Library',
      icon: <VideoLibrary />,
      path: '/videos',
    },
  ];

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'warning' | 'info') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleDrawerToggle = () => {
    if (isMobile) {
      dispatch(uiActions.toggleMobileMenu());
    } else {
      dispatch(uiActions.toggleSidebar());
    }
  };

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorElUser(null);
  };

  const handleNotificationsOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorElNotifications(event.currentTarget);
  };

  const handleNotificationsClose = () => {
    setAnchorElNotifications(null);
  };

  const handleThemeToggle = () => {
    dispatch(uiActions.toggleTheme());
  };

  const handleLogout = async () => {
    handleUserMenuClose();
    try {
      await logout();
    } catch (error) {
      showSnackbar('Logout failed. Please try again.', 'error');
    }
  };

  const handleNavigate = (path: string) => {
    navigate(path);
    if (isMobile) {
      dispatch(uiActions.setMobileMenuOpen(false));
    }
  };

  const handleNotificationClick = (notificationId: string) => {
    dispatch(notificationsActions.markAsRead(notificationId));
  };

  const isActiveRoute = (path: string) => {
    return location.pathname === path;
  };

  const drawer = (
    <Box>
      <Toolbar sx={{ px: 3, py: 2 }}>
        <Typography variant="h6" noWrap component="div" color="primary" fontWeight="bold">
          ViralAI Ads
        </Typography>
      </Toolbar>
      <Divider />
      <List sx={{ px: 2 }}>
        {navigationItems.map((item) => (
          <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              selected={isActiveRoute(item.path)}
              onClick={() => handleNavigate(item.path)}
              disabled={item.disabled}
              sx={{
                borderRadius: 2,
                '&.Mui-selected': {
                  backgroundColor: theme.palette.primary.main,
                  color: 'white',
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                  },
                },
                '&.Mui-selected:hover': {
                  backgroundColor: theme.palette.primary.dark,
                },
              }}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.title} />
              {item.badge && (
                <Chip
                  label={item.badge}
                  size="small"
                  color="error"
                  sx={{ ml: 1, fontSize: '0.7rem', height: 20 }}
                />
              )}
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider sx={{ my: 2 }} />
      <List sx={{ px: 2 }}>
        <ListItem disablePadding sx={{ mb: 0.5 }}>
          <ListItemButton
            onClick={() => handleNavigate('/settings')}
            selected={isActiveRoute('/settings')}
            sx={{ borderRadius: 2 }}
          >
            <ListItemIcon>
              <Settings />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${sidebarOpen ? DRAWER_WIDTH : 0}px)` },
          ml: { md: `${sidebarOpen ? DRAWER_WIDTH : 0}px` },
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="toggle drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {navigationItems.find(item => isActiveRoute(item.path))?.title || 'ViralAI Advertising'}
          </Typography>

          {/* Theme Toggle */}
          <IconButton color="inherit" onClick={handleThemeToggle} sx={{ mr: 1 }}>
            {currentTheme === 'light' ? <Brightness4 /> : <Brightness7 />}
          </IconButton>

          {/* Notifications */}
          <IconButton
            color="inherit"
            onClick={handleNotificationsOpen}
            sx={{ mr: 1 }}
          >
            <Badge badgeContent={unreadCount} color="error">
              <Notifications />
            </Badge>
          </IconButton>

          {/* User Menu */}
          <IconButton
            size="large"
            aria-label="user account"
            aria-controls="user-menu"
            aria-haspopup="true"
            onClick={handleUserMenuOpen}
            color="inherit"
          >
            <Avatar
              sx={{ width: 32, height: 32 }}
              alt={user?.name}
              src={user?.avatar}
            >
              {user?.name?.[0]?.toUpperCase()}
            </Avatar>
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* User Menu */}
      <Menu
        id="user-menu"
        anchorEl={anchorElUser}
        open={Boolean(anchorElUser)}
        onClose={handleUserMenuClose}
        keepMounted
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={() => { handleUserMenuClose(); handleNavigate('/profile'); }}>
          <ListItemIcon>
            <AccountCircle fontSize="small" />
          </ListItemIcon>
          Profile
        </MenuItem>
        <MenuItem onClick={() => { handleUserMenuClose(); handleNavigate('/settings'); }}>
          <ListItemIcon>
            <Settings fontSize="small" />
          </ListItemIcon>
          Settings
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <Logout fontSize="small" />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>

      {/* Notifications Menu */}
      <Menu
        anchorEl={anchorElNotifications}
        open={Boolean(anchorElNotifications)}
        onClose={handleNotificationsClose}
        keepMounted
        PaperProps={{
          sx: {
            width: 350,
            maxHeight: 400,
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">Notifications</Typography>
        </Box>
        {notifications.length === 0 ? (
          <MenuItem disabled>
            <Typography variant="body2" color="textSecondary">
              No notifications
            </Typography>
          </MenuItem>
        ) : (
          notifications.slice(0, 5).map((notification) => (
            <MenuItem
              key={notification.id}
              onClick={() => handleNotificationClick(notification.id)}
              sx={{
                backgroundColor: notification.read ? 'transparent' : 'action.hover',
                borderLeft: notification.read ? 'none' : '3px solid',
                borderLeftColor: 'primary.main',
              }}
            >
              <Box>
                <Typography variant="subtitle2" fontWeight="bold">
                  {notification.title}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {notification.message}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {new Date(notification.timestamp).toLocaleString()}
                </Typography>
              </Box>
            </MenuItem>
          ))
        )}
        {notifications.length > 5 && (
          <MenuItem onClick={() => { handleNotificationsClose(); handleNavigate('/notifications'); }}>
            <Typography variant="body2" color="primary">
              View all notifications
            </Typography>
          </MenuItem>
        )}
      </Menu>

      {/* Sidebar */}
      <Box
        component="nav"
        sx={{ width: { md: sidebarOpen ? DRAWER_WIDTH : 0 }, flexShrink: { md: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileMenuOpen}
          onClose={() => dispatch(uiActions.setMobileMenuOpen(false))}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
            },
          }}
        >
          {drawer}
        </Drawer>
        
        {/* Desktop drawer */}
        <Drawer
          variant="persistent"
          open={sidebarOpen}
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${sidebarOpen ? DRAWER_WIDTH : 0}px)` },
          minHeight: '100vh',
          backgroundColor: theme.palette.background.default,
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        }}
      >
        <Toolbar /> {/* Spacer for fixed app bar */}
        {children}
      </Box>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbarOpen(false)}
          severity={snackbarSeverity}
          sx={{ width: '100%' }}
          action={
            <IconButton
              size="small"
              aria-label="close"
              color="inherit"
              onClick={() => setSnackbarOpen(false)}
            >
              <Close fontSize="small" />
            </IconButton>
          }
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Layout;