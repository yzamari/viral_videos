import { configureStore, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import {
  User,
  Campaign,
  DashboardMetrics,
  TrendingTopic,
  Video,
  Notification,
  LoadingState,
  ErrorState,
} from '../types';

// Auth Slice
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: LoadingState;
  error: ErrorState;
}

const initialAuthState: AuthState = {
  user: null,
  token: localStorage.getItem('auth_token'),
  isAuthenticated: !!localStorage.getItem('auth_token'),
  loading: { isLoading: false },
  error: { hasError: false },
};

const authSlice = createSlice({
  name: 'auth',
  initialState: initialAuthState,
  reducers: {
    setLoading: (state, action: PayloadAction<LoadingState>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<ErrorState>) => {
      state.error = action.payload;
      state.loading = { isLoading: false };
    },
    loginStart: (state) => {
      state.loading = { isLoading: true, message: 'Signing in...' };
      state.error = { hasError: false };
    },
    loginSuccess: (state, action: PayloadAction<{ user: User; token: string }>) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.isAuthenticated = true;
      state.loading = { isLoading: false };
      state.error = { hasError: false };
    },
    loginFailure: (state, action: PayloadAction<string>) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.loading = { isLoading: false };
      state.error = { hasError: true, message: action.payload };
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.loading = { isLoading: false };
      state.error = { hasError: false };
    },
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
    clearError: (state) => {
      state.error = { hasError: false };
    },
  },
});

// Dashboard Slice
interface DashboardState {
  metrics: DashboardMetrics | null;
  loading: LoadingState;
  error: ErrorState;
  lastUpdated: string | null;
}

const initialDashboardState: DashboardState = {
  metrics: null,
  loading: { isLoading: false },
  error: { hasError: false },
  lastUpdated: null,
};

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState: initialDashboardState,
  reducers: {
    setLoading: (state, action: PayloadAction<LoadingState>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<ErrorState>) => {
      state.error = action.payload;
      state.loading = { isLoading: false };
    },
    setMetrics: (state, action: PayloadAction<DashboardMetrics>) => {
      state.metrics = action.payload;
      state.loading = { isLoading: false };
      state.error = { hasError: false };
      state.lastUpdated = new Date().toISOString();
    },
    updateMetrics: (state, action: PayloadAction<Partial<DashboardMetrics>>) => {
      if (state.metrics) {
        state.metrics = { ...state.metrics, ...action.payload };
        state.lastUpdated = new Date().toISOString();
      }
    },
    clearError: (state) => {
      state.error = { hasError: false };
    },
  },
});

// Campaigns Slice
interface CampaignsState {
  campaigns: Campaign[];
  selectedCampaign: Campaign | null;
  totalCount: number;
  currentPage: number;
  pageSize: number;
  loading: LoadingState;
  error: ErrorState;
  filters: {
    status?: string[];
    platforms?: string[];
    dateRange?: { start: string; end: string };
  };
}

const initialCampaignsState: CampaignsState = {
  campaigns: [],
  selectedCampaign: null,
  totalCount: 0,
  currentPage: 1,
  pageSize: 10,
  loading: { isLoading: false },
  error: { hasError: false },
  filters: {},
};

const campaignsSlice = createSlice({
  name: 'campaigns',
  initialState: initialCampaignsState,
  reducers: {
    setLoading: (state, action: PayloadAction<LoadingState>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<ErrorState>) => {
      state.error = action.payload;
      state.loading = { isLoading: false };
    },
    setCampaigns: (state, action: PayloadAction<{ campaigns: Campaign[]; totalCount: number }>) => {
      state.campaigns = action.payload.campaigns;
      state.totalCount = action.payload.totalCount;
      state.loading = { isLoading: false };
      state.error = { hasError: false };
    },
    addCampaign: (state, action: PayloadAction<Campaign>) => {
      state.campaigns.unshift(action.payload);
      state.totalCount += 1;
    },
    updateCampaign: (state, action: PayloadAction<Campaign>) => {
      const index = state.campaigns.findIndex(c => c.id === action.payload.id);
      if (index !== -1) {
        state.campaigns[index] = action.payload;
      }
      if (state.selectedCampaign?.id === action.payload.id) {
        state.selectedCampaign = action.payload;
      }
    },
    removeCampaign: (state, action: PayloadAction<string>) => {
      state.campaigns = state.campaigns.filter(c => c.id !== action.payload);
      state.totalCount -= 1;
      if (state.selectedCampaign?.id === action.payload) {
        state.selectedCampaign = null;
      }
    },
    setSelectedCampaign: (state, action: PayloadAction<Campaign | null>) => {
      state.selectedCampaign = action.payload;
    },
    setPage: (state, action: PayloadAction<number>) => {
      state.currentPage = action.payload;
    },
    setPageSize: (state, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
    },
    setFilters: (state, action: PayloadAction<CampaignsState['filters']>) => {
      state.filters = action.payload;
      state.currentPage = 1; // Reset to first page when filters change
    },
    clearError: (state) => {
      state.error = { hasError: false };
    },
  },
});

// Trending Slice
interface TrendingState {
  topics: TrendingTopic[];
  viralOpportunities: TrendingTopic[];
  selectedTopic: TrendingTopic | null;
  totalCount: number;
  currentPage: number;
  pageSize: number;
  loading: LoadingState;
  error: ErrorState;
  lastUpdated: string | null;
}

const initialTrendingState: TrendingState = {
  topics: [],
  viralOpportunities: [],
  selectedTopic: null,
  totalCount: 0,
  currentPage: 1,
  pageSize: 20,
  loading: { isLoading: false },
  error: { hasError: false },
  lastUpdated: null,
};

const trendingSlice = createSlice({
  name: 'trending',
  initialState: initialTrendingState,
  reducers: {
    setLoading: (state, action: PayloadAction<LoadingState>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<ErrorState>) => {
      state.error = action.payload;
      state.loading = { isLoading: false };
    },
    setTopics: (state, action: PayloadAction<{ topics: TrendingTopic[]; totalCount: number }>) => {
      state.topics = action.payload.topics;
      state.totalCount = action.payload.totalCount;
      state.loading = { isLoading: false };
      state.error = { hasError: false };
      state.lastUpdated = new Date().toISOString();
    },
    setViralOpportunities: (state, action: PayloadAction<TrendingTopic[]>) => {
      state.viralOpportunities = action.payload;
    },
    addTopic: (state, action: PayloadAction<TrendingTopic>) => {
      state.topics.unshift(action.payload);
      state.totalCount += 1;
    },
    updateTopic: (state, action: PayloadAction<TrendingTopic>) => {
      const index = state.topics.findIndex(t => t.id === action.payload.id);
      if (index !== -1) {
        state.topics[index] = action.payload;
      }
      if (state.selectedTopic?.id === action.payload.id) {
        state.selectedTopic = action.payload;
      }
    },
    setSelectedTopic: (state, action: PayloadAction<TrendingTopic | null>) => {
      state.selectedTopic = action.payload;
    },
    setPage: (state, action: PayloadAction<number>) => {
      state.currentPage = action.payload;
    },
    clearError: (state) => {
      state.error = { hasError: false };
    },
  },
});

// Videos Slice
interface VideosState {
  videos: Video[];
  selectedVideo: Video | null;
  totalCount: number;
  currentPage: number;
  pageSize: number;
  loading: LoadingState;
  error: ErrorState;
  uploadProgress: Record<string, number>;
}

const initialVideosState: VideosState = {
  videos: [],
  selectedVideo: null,
  totalCount: 0,
  currentPage: 1,
  pageSize: 20,
  loading: { isLoading: false },
  error: { hasError: false },
  uploadProgress: {},
};

const videosSlice = createSlice({
  name: 'videos',
  initialState: initialVideosState,
  reducers: {
    setLoading: (state, action: PayloadAction<LoadingState>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<ErrorState>) => {
      state.error = action.payload;
      state.loading = { isLoading: false };
    },
    setVideos: (state, action: PayloadAction<{ videos: Video[]; totalCount: number }>) => {
      state.videos = action.payload.videos;
      state.totalCount = action.payload.totalCount;
      state.loading = { isLoading: false };
      state.error = { hasError: false };
    },
    addVideo: (state, action: PayloadAction<Video>) => {
      state.videos.unshift(action.payload);
      state.totalCount += 1;
    },
    updateVideo: (state, action: PayloadAction<Video>) => {
      const index = state.videos.findIndex(v => v.id === action.payload.id);
      if (index !== -1) {
        state.videos[index] = action.payload;
      }
      if (state.selectedVideo?.id === action.payload.id) {
        state.selectedVideo = action.payload;
      }
    },
    removeVideo: (state, action: PayloadAction<string>) => {
      state.videos = state.videos.filter(v => v.id !== action.payload);
      state.totalCount -= 1;
      if (state.selectedVideo?.id === action.payload) {
        state.selectedVideo = null;
      }
    },
    setSelectedVideo: (state, action: PayloadAction<Video | null>) => {
      state.selectedVideo = action.payload;
    },
    setUploadProgress: (state, action: PayloadAction<{ videoId: string; progress: number }>) => {
      state.uploadProgress[action.payload.videoId] = action.payload.progress;
    },
    clearUploadProgress: (state, action: PayloadAction<string>) => {
      delete state.uploadProgress[action.payload];
    },
    setPage: (state, action: PayloadAction<number>) => {
      state.currentPage = action.payload;
    },
    clearError: (state) => {
      state.error = { hasError: false };
    },
  },
});

// Notifications Slice
interface NotificationsState {
  notifications: Notification[];
  unreadCount: number;
  loading: LoadingState;
  error: ErrorState;
}

const initialNotificationsState: NotificationsState = {
  notifications: [],
  unreadCount: 0,
  loading: { isLoading: false },
  error: { hasError: false },
};

const notificationsSlice = createSlice({
  name: 'notifications',
  initialState: initialNotificationsState,
  reducers: {
    setLoading: (state, action: PayloadAction<LoadingState>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<ErrorState>) => {
      state.error = action.payload;
      state.loading = { isLoading: false };
    },
    setNotifications: (state, action: PayloadAction<Notification[]>) => {
      state.notifications = action.payload;
      state.unreadCount = action.payload.filter(n => !n.read).length;
      state.loading = { isLoading: false };
      state.error = { hasError: false };
    },
    addNotification: (state, action: PayloadAction<Notification>) => {
      state.notifications.unshift(action.payload);
      if (!action.payload.read) {
        state.unreadCount += 1;
      }
    },
    markAsRead: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification && !notification.read) {
        notification.read = true;
        state.unreadCount -= 1;
      }
    },
    markAllAsRead: (state) => {
      state.notifications.forEach(n => n.read = true);
      state.unreadCount = 0;
    },
    clearError: (state) => {
      state.error = { hasError: false };
    },
  },
});

// UI Slice for global UI state
interface UIState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  mobileMenuOpen: boolean;
  activeModal: string | null;
  globalLoading: boolean;
}

const initialUIState: UIState = {
  theme: (localStorage.getItem('theme') as 'light' | 'dark') || 'light',
  sidebarOpen: true,
  mobileMenuOpen: false,
  activeModal: null,
  globalLoading: false,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState: initialUIState,
  reducers: {
    toggleTheme: (state) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', state.theme);
    },
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
      localStorage.setItem('theme', state.theme);
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    toggleMobileMenu: (state) => {
      state.mobileMenuOpen = !state.mobileMenuOpen;
    },
    setMobileMenuOpen: (state, action: PayloadAction<boolean>) => {
      state.mobileMenuOpen = action.payload;
    },
    openModal: (state, action: PayloadAction<string>) => {
      state.activeModal = action.payload;
    },
    closeModal: (state) => {
      state.activeModal = null;
    },
    setGlobalLoading: (state, action: PayloadAction<boolean>) => {
      state.globalLoading = action.payload;
    },
  },
});

// Configure store
export const store = configureStore({
  reducer: {
    auth: authSlice.reducer,
    dashboard: dashboardSlice.reducer,
    campaigns: campaignsSlice.reducer,
    trending: trendingSlice.reducer,
    videos: videosSlice.reducer,
    notifications: notificationsSlice.reducer,
    ui: uiSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Export typed hooks
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// Export action creators
export const authActions = authSlice.actions;
export const dashboardActions = dashboardSlice.actions;
export const campaignsActions = campaignsSlice.actions;
export const trendingActions = trendingSlice.actions;
export const videosActions = videosSlice.actions;
export const notificationsActions = notificationsSlice.actions;
export const uiActions = uiSlice.actions;

export default store;