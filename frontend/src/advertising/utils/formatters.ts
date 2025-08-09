import { format, formatDistance, formatRelative, parseISO } from 'date-fns';

// Currency formatting
export const formatCurrency = (
  amount: number,
  currency: string = 'USD',
  minimumFractionDigits: number = 0,
  maximumFractionDigits: number = 2
): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits,
    maximumFractionDigits,
  }).format(amount);
};

// Number formatting with locale
export const formatNumber = (
  value: number,
  options: Intl.NumberFormatOptions = {}
): string => {
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 2,
    ...options,
  }).format(value);
};

// Compact number formatting (1.2K, 1.5M, etc.)
export const formatCompactNumber = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value);
};

// Percentage formatting
export const formatPercentage = (
  value: number,
  decimals: number = 1
): string => {
  return `${value.toFixed(decimals)}%`;
};

// Duration formatting (seconds to MM:SS or HH:MM:SS)
export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

// File size formatting
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

// Date formatting utilities
export const formatDate = (date: string | Date, formatString: string = 'PPP'): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, formatString);
};

export const formatDateTime = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, 'PPP p');
};

export const formatRelativeTime = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return formatDistance(dateObj, new Date(), { addSuffix: true });
};

export const formatRelativeDate = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return formatRelative(dateObj, new Date());
};

// Campaign status formatting
export const formatCampaignStatus = (status: string): string => {
  return status.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
};

// Platform name formatting
export const formatPlatformName = (platform: string): string => {
  const platformMap: Record<string, string> = {
    youtube: 'YouTube',
    tiktok: 'TikTok',
    instagram: 'Instagram',
    facebook: 'Facebook',
    twitter: 'Twitter/X',
    linkedin: 'LinkedIn',
    snapchat: 'Snapchat',
    pinterest: 'Pinterest',
  };
  
  return platformMap[platform.toLowerCase()] || platform;
};

// Metric value formatting with appropriate units
export const formatMetricValue = (
  value: number,
  type: 'currency' | 'percentage' | 'number' | 'compact' | 'duration'
): string => {
  switch (type) {
    case 'currency':
      return formatCurrency(value);
    case 'percentage':
      return formatPercentage(value);
    case 'compact':
      return formatCompactNumber(value);
    case 'duration':
      return formatDuration(value);
    default:
      return formatNumber(value);
  }
};

// Age range formatting
export const formatAgeRange = (min: number, max: number): string => {
  if (max >= 65) {
    return `${min}+`;
  }
  return `${min}-${max}`;
};

// Gender formatting
export const formatGender = (gender: string): string => {
  const genderMap: Record<string, string> = {
    all: 'All Genders',
    male: 'Male',
    female: 'Female',
    other: 'Other',
  };
  
  return genderMap[gender] || gender;
};

// Competition level formatting
export const formatCompetitionLevel = (level: string): string => {
  const levelMap: Record<string, string> = {
    low: 'Low Competition',
    medium: 'Medium Competition',
    high: 'High Competition',
  };
  
  return levelMap[level] || level;
};

// URL formatting for display
export const formatUrl = (url: string, maxLength: number = 50): string => {
  try {
    const urlObj = new URL(url);
    const domain = urlObj.hostname.replace('www.', '');
    const path = urlObj.pathname;
    
    const displayUrl = domain + path;
    
    if (displayUrl.length > maxLength) {
      return displayUrl.substring(0, maxLength - 3) + '...';
    }
    
    return displayUrl;
  } catch {
    return url.length > maxLength ? url.substring(0, maxLength - 3) + '...' : url;
  }
};

// Performance change formatting with color indicators
export const formatPerformanceChange = (change: number): {
  formatted: string;
  color: 'success' | 'error' | 'info';
  trend: 'up' | 'down' | 'neutral';
} => {
  const abs = Math.abs(change);
  const formatted = `${change >= 0 ? '+' : ''}${formatPercentage(change)}`;
  
  if (abs < 0.1) {
    return { formatted: '0.0%', color: 'info', trend: 'neutral' };
  }
  
  return {
    formatted,
    color: change > 0 ? 'success' : 'error',
    trend: change > 0 ? 'up' : 'down',
  };
};

// Search volume formatting
export const formatSearchVolume = (volume: number): string => {
  if (volume >= 1000000) {
    return `${(volume / 1000000).toFixed(1)}M searches`;
  } else if (volume >= 1000) {
    return `${(volume / 1000).toFixed(1)}K searches`;
  }
  return `${volume} searches`;
};

// Trending score formatting with labels
export const formatTrendingScore = (score: number): {
  score: string;
  label: string;
  color: string;
} => {
  const scoreStr = score.toFixed(0);
  
  if (score >= 80) {
    return { score: scoreStr, label: 'HOT', color: '#FF5722' };
  } else if (score >= 60) {
    return { score: scoreStr, label: 'TRENDING', color: '#FF9800' };
  } else if (score >= 40) {
    return { score: scoreStr, label: 'WARM', color: '#FFC107' };
  } else {
    return { score: scoreStr, label: 'EMERGING', color: '#4CAF50' };
  }
};

// Error message formatting
export const formatErrorMessage = (error: any): string => {
  if (typeof error === 'string') return error;
  
  if (error?.message) return error.message;
  if (error?.detail) return error.detail;
  if (error?.error) return error.error;
  
  return 'An unexpected error occurred';
};

// Time remaining formatting
export const formatTimeRemaining = (endDate: string | Date): string => {
  const end = typeof endDate === 'string' ? parseISO(endDate) : endDate;
  const now = new Date();
  
  if (end <= now) {
    return 'Ended';
  }
  
  const diffMs = end.getTime() - now.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  
  if (diffDays > 0) {
    return `${diffDays} day${diffDays !== 1 ? 's' : ''} remaining`;
  } else if (diffHours > 0) {
    return `${diffHours} hour${diffHours !== 1 ? 's' : ''} remaining`;
  } else if (diffMinutes > 0) {
    return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} remaining`;
  } else {
    return 'Less than a minute remaining';
  }
};

export default {
  formatCurrency,
  formatNumber,
  formatCompactNumber,
  formatPercentage,
  formatDuration,
  formatFileSize,
  formatDate,
  formatDateTime,
  formatRelativeTime,
  formatRelativeDate,
  formatCampaignStatus,
  formatPlatformName,
  formatMetricValue,
  formatAgeRange,
  formatGender,
  formatCompetitionLevel,
  formatUrl,
  formatPerformanceChange,
  formatSearchVolume,
  formatTrendingScore,
  formatErrorMessage,
  formatTimeRemaining,
};