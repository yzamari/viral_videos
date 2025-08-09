import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/store';
import { authActions } from '../store/store';
import { authService } from '../services/api';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: { email: string; password: string; name: string }) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  updateProfile: (userData: Partial<User>) => void;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { user, token, isAuthenticated, loading, error } = useAppSelector(state => state.auth);
  
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize authentication state
  useEffect(() => {
    const initializeAuth = async () => {
      const savedToken = localStorage.getItem('auth_token');
      
      if (savedToken) {
        try {
          dispatch(authActions.setLoading({ isLoading: true, message: 'Verifying authentication...' }));
          
          // Verify token and get user info
          const response = await authService.getCurrentUser();
          dispatch(authActions.loginSuccess({ 
            user: response.data, 
            token: savedToken 
          }));
        } catch (error) {
          console.error('Token verification failed:', error);
          // Clear invalid token
          localStorage.removeItem('auth_token');
          dispatch(authActions.logout());
        }
      }
      
      setIsInitialized(true);
      dispatch(authActions.setLoading({ isLoading: false }));
    };

    initializeAuth();
  }, [dispatch]);

  // Auto-refresh token before expiration
  useEffect(() => {
    if (!token || !isAuthenticated) return;

    const tokenPayload = parseJWT(token);
    if (!tokenPayload) return;

    const expirationTime = tokenPayload.exp * 1000; // Convert to milliseconds
    const currentTime = Date.now();
    const timeUntilExpiration = expirationTime - currentTime;
    const refreshThreshold = 5 * 60 * 1000; // 5 minutes before expiration

    if (timeUntilExpiration > refreshThreshold) {
      // Set timeout to refresh token
      const timeoutId = setTimeout(async () => {
        try {
          await refreshToken();
        } catch (error) {
          console.error('Auto token refresh failed:', error);
          await logout();
        }
      }, timeUntilExpiration - refreshThreshold);

      return () => clearTimeout(timeoutId);
    } else if (timeUntilExpiration <= 0) {
      // Token already expired
      logout();
    }
  }, [token, isAuthenticated]);

  const login = async (email: string, password: string): Promise<void> => {
    try {
      dispatch(authActions.loginStart());
      
      const response = await authService.login(email, password);
      
      dispatch(authActions.loginSuccess({
        user: response.data.user,
        token: response.data.token,
      }));

      // Navigate to dashboard after successful login
      navigate('/dashboard');
    } catch (error: any) {
      const message = error.message || 'Login failed. Please try again.';
      dispatch(authActions.loginFailure(message));
      throw error;
    }
  };

  const register = async (userData: { 
    email: string; 
    password: string; 
    name: string; 
  }): Promise<void> => {
    try {
      dispatch(authActions.setLoading({ isLoading: true, message: 'Creating account...' }));
      
      const response = await authService.register(userData);
      
      dispatch(authActions.loginSuccess({
        user: response.data.user,
        token: response.data.token,
      }));

      // Navigate to dashboard after successful registration
      navigate('/dashboard');
    } catch (error: any) {
      const message = error.message || 'Registration failed. Please try again.';
      dispatch(authActions.setError({ hasError: true, message }));
      throw error;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      // Call logout endpoint to invalidate token on server
      await authService.logout();
    } catch (error) {
      // Continue with logout even if server call fails
      console.error('Server logout failed:', error);
    } finally {
      // Clear local state and redirect
      dispatch(authActions.logout());
      localStorage.removeItem('auth_token');
      navigate('/login');
    }
  };

  const refreshToken = async (): Promise<void> => {
    try {
      const response = await authService.refreshToken();
      
      dispatch(authActions.loginSuccess({
        user: user!, // Keep existing user data
        token: response.data.token,
      }));
    } catch (error) {
      console.error('Token refresh failed:', error);
      await logout();
      throw error;
    }
  };

  const updateProfile = (userData: Partial<User>): void => {
    dispatch(authActions.updateUser(userData));
  };

  const clearError = (): void => {
    dispatch(authActions.clearError());
  };

  // Helper function to parse JWT token
  const parseJWT = (token: string) => {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('Failed to parse JWT:', error);
      return null;
    }
  };

  // Show loading spinner during initialization
  if (!isInitialized) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#f5f5f5'
      }}>
        <div style={{
          padding: '2rem',
          textAlign: 'center'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '4px solid #e0e0e0',
            borderLeft: '4px solid #1976d2',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 1rem'
          }} />
          <p style={{ color: '#666', margin: 0 }}>Loading...</p>
        </div>
      </div>
    );
  }

  const contextValue: AuthContextType = {
    user,
    token,
    isAuthenticated,
    isLoading: loading.isLoading,
    login,
    register,
    logout,
    refreshToken,
    updateProfile,
    error: error.hasError ? error.message || null : null,
    clearError,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Higher-order component for protecting routes
interface ProtectedRouteProps {
  children: ReactNode;
  requiredRole?: User['role'];
  fallback?: ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole,
  fallback 
}) => {
  const { isAuthenticated, user, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, isLoading, navigate]);

  // Show loading state
  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh'
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  // Not authenticated
  if (!isAuthenticated) {
    return fallback || null;
  }

  // Check role requirement
  if (requiredRole && user?.role !== requiredRole) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        textAlign: 'center',
        padding: '2rem'
      }}>
        <h2>Access Denied</h2>
        <p>You don't have permission to access this page.</p>
        <p>Required role: <strong>{requiredRole}</strong></p>
        <p>Your role: <strong>{user?.role}</strong></p>
        <button 
          onClick={() => navigate('/dashboard')}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#1976d2',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            marginTop: '1rem'
          }}
        >
          Go to Dashboard
        </button>
      </div>
    );
  }

  return <>{children}</>;
};

// Component for public routes (redirect if authenticated)
interface PublicRouteProps {
  children: ReactNode;
  redirectTo?: string;
}

export const PublicRoute: React.FC<PublicRouteProps> = ({ 
  children, 
  redirectTo = '/dashboard' 
}) => {
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      navigate(redirectTo);
    }
  }, [isAuthenticated, isLoading, navigate, redirectTo]);

  // Show loading state
  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh'
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  // Already authenticated, don't render
  if (isAuthenticated) {
    return null;
  }

  return <>{children}</>;
};

export default AuthContext;