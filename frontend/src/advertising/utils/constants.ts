// Platform definitions
export const PLATFORMS = {
  YOUTUBE: {
    id: 'youtube',
    name: 'YouTube',
    color: '#FF0000',
    icon: '📺',
    maxVideoLength: 3600, // seconds
    recommendedAspectRatio: '16:9',
    supportedFormats: ['mp4', 'mov', 'avi'],
  },
  TIKTOK: {
    id: 'tiktok',
    name: 'TikTok',
    color: '#000000',
    icon: '🎵',
    maxVideoLength: 180, // seconds
    recommendedAspectRatio: '9:16',
    supportedFormats: ['mp4', 'mov'],
  },
  INSTAGRAM: {
    id: 'instagram',
    name: 'Instagram',
    color: '#E4405F',
    icon: '📸',
    maxVideoLength: 60, // seconds for reels
    recommendedAspectRatio: '9:16',
    supportedFormats: ['mp4', 'mov'],
  },
  FACEBOOK: {
    id: 'facebook',
    name: 'Facebook',
    color: '#4267B2',
    icon: '👥',
    maxVideoLength: 240, // seconds
    recommendedAspectRatio: '16:9',
    supportedFormats: ['mp4', 'mov', 'avi'],
  },
  TWITTER: {
    id: 'twitter',
    name: 'Twitter/X',
    color: '#1DA1F2',
    icon: '🐦',
    maxVideoLength: 140, // seconds
    recommendedAspectRatio: '16:9',
    supportedFormats: ['mp4', 'mov'],
  },
} as const;

// Campaign objectives
export const CAMPAIGN_OBJECTIVES = {
  BRAND_AWARENESS: {
    id: 'brand_awareness',
    name: 'Brand Awareness',
    description: 'Increase recognition and recall of your brand',
    icon: '🎯',
    metrics: ['impressions', 'reach', 'frequency'],
  },
  ENGAGEMENT: {
    id: 'engagement',
    name: 'Engagement',
    description: 'Get more likes, shares, comments, and interactions',
    icon: '❤️',
    metrics: ['engagements', 'engagement_rate', 'shares', 'comments'],
  },
  CONVERSIONS: {
    id: 'conversions',
    name: 'Conversions',
    description: 'Drive actions like purchases, signups, or downloads',
    icon: '🛒',
    metrics: ['conversions', 'conversion_rate', 'roas', 'revenue'],
  },
  TRAFFIC: {
    id: 'traffic',
    name: 'Website Traffic',
    description: 'Bring visitors to your website or landing page',
    icon: '🌐',
    metrics: ['clicks', 'ctr', 'website_visits', 'page_views'],
  },
  REACH: {
    id: 'reach',
    name: 'Reach',
    description: 'Show your ads to the maximum number of people',
    icon: '📢',
    metrics: ['reach', 'unique_users', 'frequency', 'impressions'],
  },
  VIDEO_VIEWS: {
    id: 'video_views',
    name: 'Video Views',
    description: 'Maximize views and watch time for your video content',
    icon: '▶️',
    metrics: ['video_views', 'view_rate', 'watch_time', 'completion_rate'],
  },
} as const;

// Campaign statuses
export const CAMPAIGN_STATUS = {
  DRAFT: {
    id: 'draft',
    name: 'Draft',
    color: '#9E9E9E',
    icon: '📝',
    description: 'Campaign is being prepared',
    canEdit: true,
    canDelete: true,
    canLaunch: true,
  },
  ACTIVE: {
    id: 'active',
    name: 'Active',
    color: '#4CAF50',
    icon: '▶️',
    description: 'Campaign is currently running',
    canEdit: false,
    canDelete: false,
    canPause: true,
  },
  PAUSED: {
    id: 'paused',
    name: 'Paused',
    color: '#FF9800',
    icon: '⏸️',
    description: 'Campaign is temporarily stopped',
    canEdit: true,
    canDelete: true,
    canResume: true,
  },
  COMPLETED: {
    id: 'completed',
    name: 'Completed',
    color: '#2196F3',
    icon: '✅',
    description: 'Campaign has finished successfully',
    canEdit: false,
    canDelete: true,
    canDuplicate: true,
  },
  CANCELLED: {
    id: 'cancelled',
    name: 'Cancelled',
    color: '#F44336',
    icon: '❌',
    description: 'Campaign was cancelled before completion',
    canEdit: false,
    canDelete: true,
    canDuplicate: true,
  },
} as const;

// Competition levels
export const COMPETITION_LEVELS = {
  LOW: {
    id: 'low',
    name: 'Low Competition',
    color: '#4CAF50',
    description: 'Easy to compete, lower costs',
    score: 1,
  },
  MEDIUM: {
    id: 'medium',
    name: 'Medium Competition',
    color: '#FF9800',
    description: 'Moderate competition, average costs',
    score: 2,
  },
  HIGH: {
    id: 'high',
    name: 'High Competition',
    color: '#F44336',
    description: 'Very competitive, higher costs',
    score: 3,
  },
} as const;

// Content categories
export const CONTENT_CATEGORIES = {
  TECHNOLOGY: {
    id: 'technology',
    name: 'Technology',
    icon: '💻',
    trending: true,
  },
  ENTERTAINMENT: {
    id: 'entertainment',
    name: 'Entertainment',
    icon: '🎬',
    trending: true,
  },
  SPORTS: {
    id: 'sports',
    name: 'Sports',
    icon: '⚽',
    trending: true,
  },
  LIFESTYLE: {
    id: 'lifestyle',
    name: 'Lifestyle',
    icon: '✨',
    trending: false,
  },
  BUSINESS: {
    id: 'business',
    name: 'Business',
    icon: '💼',
    trending: false,
  },
  HEALTH: {
    id: 'health',
    name: 'Health & Fitness',
    icon: '💪',
    trending: true,
  },
  FOOD: {
    id: 'food',
    name: 'Food & Cooking',
    icon: '🍳',
    trending: false,
  },
  TRAVEL: {
    id: 'travel',
    name: 'Travel',
    icon: '✈️',
    trending: false,
  },
  FASHION: {
    id: 'fashion',
    name: 'Fashion & Beauty',
    icon: '👗',
    trending: true,
  },
  EDUCATION: {
    id: 'education',
    name: 'Education',
    icon: '📚',
    trending: false,
  },
} as const;

// Demographics
export const AGE_GROUPS = [
  { min: 13, max: 17, label: '13-17' },
  { min: 18, max: 24, label: '18-24' },
  { min: 25, max: 34, label: '25-34' },
  { min: 35, max: 44, label: '35-44' },
  { min: 45, max: 54, label: '45-54' },
  { min: 55, max: 64, label: '55-64' },
  { min: 65, max: 100, label: '65+' },
] as const;

export const GENDERS = {
  ALL: { id: 'all', name: 'All Genders' },
  MALE: { id: 'male', name: 'Male' },
  FEMALE: { id: 'female', name: 'Female' },
  OTHER: { id: 'other', name: 'Other' },
} as const;

// Languages
export const LANGUAGES = [
  { code: 'en', name: 'English', native: 'English' },
  { code: 'es', name: 'Spanish', native: 'Español' },
  { code: 'fr', name: 'French', native: 'Français' },
  { code: 'de', name: 'German', native: 'Deutsch' },
  { code: 'it', name: 'Italian', native: 'Italiano' },
  { code: 'pt', name: 'Portuguese', native: 'Português' },
  { code: 'ru', name: 'Russian', native: 'Русский' },
  { code: 'zh', name: 'Chinese', native: '中文' },
  { code: 'ja', name: 'Japanese', native: '日本語' },
  { code: 'ko', name: 'Korean', native: '한국어' },
  { code: 'ar', name: 'Arabic', native: 'العربية' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
] as const;

// Countries
export const TOP_COUNTRIES = [
  { code: 'US', name: 'United States', flag: '🇺🇸' },
  { code: 'CA', name: 'Canada', flag: '🇨🇦' },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧' },
  { code: 'AU', name: 'Australia', flag: '🇦🇺' },
  { code: 'DE', name: 'Germany', flag: '🇩🇪' },
  { code: 'FR', name: 'France', flag: '🇫🇷' },
  { code: 'IT', name: 'Italy', flag: '🇮🇹' },
  { code: 'ES', name: 'Spain', flag: '🇪🇸' },
  { code: 'NL', name: 'Netherlands', flag: '🇳🇱' },
  { code: 'SE', name: 'Sweden', flag: '🇸🇪' },
  { code: 'BR', name: 'Brazil', flag: '🇧🇷' },
  { code: 'MX', name: 'Mexico', flag: '🇲🇽' },
  { code: 'JP', name: 'Japan', flag: '🇯🇵' },
  { code: 'KR', name: 'South Korea', flag: '🇰🇷' },
  { code: 'IN', name: 'India', flag: '🇮🇳' },
  { code: 'CN', name: 'China', flag: '🇨🇳' },
] as const;

// Budget ranges
export const BUDGET_RANGES = [
  { min: 100, max: 500, label: '$100 - $500' },
  { min: 500, max: 1000, label: '$500 - $1,000' },
  { min: 1000, max: 5000, label: '$1,000 - $5,000' },
  { min: 5000, max: 10000, label: '$5,000 - $10,000' },
  { min: 10000, max: 50000, label: '$10,000 - $50,000' },
  { min: 50000, max: 100000, label: '$50,000 - $100,000' },
  { min: 100000, max: Infinity, label: '$100,000+' },
] as const;

// Timeframes for analytics
export const ANALYTICS_TIMEFRAMES = {
  LAST_7_DAYS: { id: '7d', name: 'Last 7 days', days: 7 },
  LAST_30_DAYS: { id: '30d', name: 'Last 30 days', days: 30 },
  LAST_90_DAYS: { id: '90d', name: 'Last 90 days', days: 90 },
  LAST_6_MONTHS: { id: '6m', name: 'Last 6 months', days: 180 },
  LAST_YEAR: { id: '1y', name: 'Last year', days: 365 },
  CUSTOM: { id: 'custom', name: 'Custom range', days: null },
} as const;

// Chart colors
export const CHART_COLORS = [
  '#2196F3', // Blue
  '#FF9800', // Orange
  '#4CAF50', // Green
  '#F44336', // Red
  '#9C27B0', // Purple
  '#FF5722', // Deep Orange
  '#795548', // Brown
  '#607D8B', // Blue Grey
  '#E91E63', // Pink
  '#00BCD4', // Cyan
] as const;

// Video resolutions and formats
export const VIDEO_SPECS = {
  RESOLUTIONS: {
    '720p': { width: 1280, height: 720, name: 'HD (720p)' },
    '1080p': { width: 1920, height: 1080, name: 'Full HD (1080p)' },
    '1440p': { width: 2560, height: 1440, name: '2K (1440p)' },
    '2160p': { width: 3840, height: 2160, name: '4K (2160p)' },
  },
  ASPECT_RATIOS: {
    '16:9': { ratio: 16/9, name: 'Landscape (16:9)' },
    '9:16': { ratio: 9/16, name: 'Portrait (9:16)' },
    '1:1': { ratio: 1, name: 'Square (1:1)' },
    '4:3': { ratio: 4/3, name: 'Traditional (4:3)' },
  },
  FORMATS: ['mp4', 'mov', 'avi', 'mkv', 'webm'],
} as const;

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    ME: '/auth/me',
  },
  CAMPAIGNS: {
    LIST: '/campaigns',
    CREATE: '/campaigns',
    GET: (id: string) => `/campaigns/${id}`,
    UPDATE: (id: string) => `/campaigns/${id}`,
    DELETE: (id: string) => `/campaigns/${id}`,
    PAUSE: (id: string) => `/campaigns/${id}/pause`,
    RESUME: (id: string) => `/campaigns/${id}/resume`,
    DUPLICATE: (id: string) => `/campaigns/${id}/duplicate`,
    ANALYTICS: (id: string) => `/campaigns/${id}/analytics`,
  },
  ANALYTICS: {
    OVERVIEW: '/analytics/overview',
    COMPARISON: '/analytics/comparison',
    EXPORT: '/analytics/export',
  },
  TRENDING: {
    TOPICS: '/trending/topics',
    SEARCH: '/trending/search',
    VIRAL_OPPORTUNITIES: '/trending/viral-opportunities',
  },
  VIDEOS: {
    LIST: '/videos',
    UPLOAD: '/videos/upload',
    GENERATE: '/videos/generate',
    STATUS: (taskId: string) => `/videos/generation/${taskId}`,
  },
} as const;

// Error codes
export const ERROR_CODES = {
  AUTHENTICATION: {
    INVALID_CREDENTIALS: 'invalid_credentials',
    TOKEN_EXPIRED: 'token_expired',
    UNAUTHORIZED: 'unauthorized',
  },
  VALIDATION: {
    REQUIRED_FIELD: 'required_field',
    INVALID_FORMAT: 'invalid_format',
    OUT_OF_RANGE: 'out_of_range',
  },
  CAMPAIGN: {
    BUDGET_EXCEEDED: 'budget_exceeded',
    INVALID_DATES: 'invalid_dates',
    NO_CONTENT: 'no_content',
  },
} as const;

// Success messages
export const SUCCESS_MESSAGES = {
  CAMPAIGN_CREATED: 'Campaign created successfully!',
  CAMPAIGN_UPDATED: 'Campaign updated successfully!',
  CAMPAIGN_DELETED: 'Campaign deleted successfully!',
  CAMPAIGN_PAUSED: 'Campaign paused successfully!',
  CAMPAIGN_RESUMED: 'Campaign resumed successfully!',
  VIDEO_UPLOADED: 'Video uploaded successfully!',
  PROFILE_UPDATED: 'Profile updated successfully!',
  SETTINGS_SAVED: 'Settings saved successfully!',
} as const;

// Local storage keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_PREFERENCES: 'user_preferences',
  THEME: 'theme',
  LANGUAGE: 'language',
  RECENT_SEARCHES: 'recent_searches',
  BOOKMARKED_TOPICS: 'bookmarked_topics',
  CAMPAIGN_DRAFTS: 'campaign_drafts',
} as const;

// Feature flags
export const FEATURES = {
  DARK_MODE: true,
  REAL_TIME_UPDATES: true,
  ADVANCED_ANALYTICS: true,
  AI_RECOMMENDATIONS: true,
  VIDEO_GENERATION: true,
  MULTI_LANGUAGE: true,
  CAMPAIGN_TEMPLATES: true,
  A_B_TESTING: false, // Coming soon
  AUTOMATED_BIDDING: false, // Coming soon
} as const;

export default {
  PLATFORMS,
  CAMPAIGN_OBJECTIVES,
  CAMPAIGN_STATUS,
  COMPETITION_LEVELS,
  CONTENT_CATEGORIES,
  AGE_GROUPS,
  GENDERS,
  LANGUAGES,
  TOP_COUNTRIES,
  BUDGET_RANGES,
  ANALYTICS_TIMEFRAMES,
  CHART_COLORS,
  VIDEO_SPECS,
  API_ENDPOINTS,
  ERROR_CODES,
  SUCCESS_MESSAGES,
  STORAGE_KEYS,
  FEATURES,
};