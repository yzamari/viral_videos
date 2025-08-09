export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'manager';
  avatar?: string;
  createdAt: string;
  lastLogin?: string;
}

export interface Campaign {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'active' | 'paused' | 'completed' | 'cancelled';
  budget: number;
  spent: number;
  startDate: string;
  endDate?: string;
  targetAudience: {
    demographics: {
      ageMin: number;
      ageMax: number;
      gender: 'all' | 'male' | 'female';
    };
    interests: string[];
    locations: string[];
    languages: string[];
  };
  platforms: Array<'youtube' | 'tiktok' | 'instagram' | 'facebook' | 'twitter'>;
  objectives: Array<'brand_awareness' | 'engagement' | 'conversions' | 'traffic' | 'reach'>;
  content: {
    videoIds: string[];
    creativeAssets: string[];
    callToAction: string;
  };
  performance: CampaignPerformance;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

export interface CampaignPerformance {
  impressions: number;
  clicks: number;
  views: number;
  engagements: number;
  conversions: number;
  ctr: number; // Click-through rate
  cpm: number; // Cost per mille
  cpc: number; // Cost per click
  roas: number; // Return on ad spend
  reach: number;
  frequency: number;
}

export interface Video {
  id: string;
  title: string;
  description: string;
  duration: number; // in seconds
  thumbnailUrl: string;
  videoUrl: string;
  status: 'processing' | 'ready' | 'failed' | 'archived';
  metadata: {
    format: string;
    resolution: string;
    fileSize: number;
    uploadedAt: string;
  };
  analytics: VideoAnalytics;
  tags: string[];
  category: string;
  viralScore?: number;
  trendingScore?: number;
}

export interface VideoAnalytics {
  views: number;
  likes: number;
  shares: number;
  comments: number;
  watchTime: number;
  clickThroughRate: number;
  engagementRate: number;
  retentionRate: number;
  demographics: {
    ageGroups: Record<string, number>;
    genderSplit: Record<string, number>;
    locations: Record<string, number>;
  };
}

export interface TrendingTopic {
  id: string;
  keyword: string;
  category: string;
  trending_score: number;
  search_volume: number;
  competition_level: 'low' | 'medium' | 'high';
  platforms: string[];
  demographics: {
    primary_age_group: string;
    primary_gender: string;
    top_locations: string[];
  };
  sentiment: 'positive' | 'negative' | 'neutral';
  related_keywords: string[];
  content_suggestions: string[];
  optimal_timing: {
    best_days: string[];
    best_hours: number[];
    timezone: string;
  };
  historical_data: {
    date: string;
    score: number;
  }[];
  createdAt: string;
  expiresAt: string;
}

export interface DashboardMetrics {
  totalCampaigns: number;
  activeCampaigns: number;
  totalBudget: number;
  totalSpent: number;
  totalImpressions: number;
  totalClicks: number;
  totalViews: number;
  averageCTR: number;
  averageCPM: number;
  averageROAS: number;
  topPerformingCampaigns: Campaign[];
  recentActivity: ActivityItem[];
}

export interface ActivityItem {
  id: string;
  type: 'campaign_created' | 'campaign_updated' | 'campaign_paused' | 'campaign_completed' | 'video_uploaded' | 'trend_detected';
  title: string;
  description: string;
  timestamp: string;
  userId: string;
  metadata?: Record<string, any>;
}

export interface AnalyticsTimeframe {
  start: string;
  end: string;
  label: string;
}

export interface ChartDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}

export interface CreateCampaignRequest {
  name: string;
  description: string;
  budget: number;
  startDate: string;
  endDate?: string;
  targetAudience: Campaign['targetAudience'];
  platforms: Campaign['platforms'];
  objectives: Campaign['objectives'];
  content: {
    videoIds: string[];
    callToAction: string;
  };
}

export interface UpdateCampaignRequest extends Partial<CreateCampaignRequest> {
  status?: Campaign['status'];
}

export interface WebSocketMessage {
  type: 'campaign_update' | 'metrics_update' | 'trending_update' | 'notification';
  payload: any;
  timestamp: string;
}

// Filter and sorting interfaces
export interface CampaignFilters {
  status?: Campaign['status'][];
  platforms?: Campaign['platforms'];
  dateRange?: {
    start: string;
    end: string;
  };
  budgetRange?: {
    min: number;
    max: number;
  };
}

export interface SortOption {
  field: string;
  direction: 'asc' | 'desc';
}

// Form validation schemas
export interface ValidationError {
  field: string;
  message: string;
}

export interface FormState<T> {
  values: T;
  errors: Record<keyof T, string>;
  touched: Record<keyof T, boolean>;
  isSubmitting: boolean;
  isValid: boolean;
}

// Notification types
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actionUrl?: string;
}

// Theme and UI types
export interface ThemeMode {
  palette: {
    mode: 'light' | 'dark';
  };
}

export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  code?: string;
}