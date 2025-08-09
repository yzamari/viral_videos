import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import {
  ApiResponse,
  PaginatedResponse,
  Campaign,
  CreateCampaignRequest,
  UpdateCampaignRequest,
  DashboardMetrics,
  TrendingTopic,
  Video,
  User,
  CampaignFilters,
  SortOption
} from '../types';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          this.clearToken();
          window.location.href = '/login';
        }
        return Promise.reject(this.formatError(error));
      }
    );

    // Initialize token from localStorage
    this.token = localStorage.getItem('auth_token');
  }

  private formatError(error: AxiosError): Error {
    if (error.response?.data) {
      const data = error.response.data as any;
      return new Error(data.message || data.detail || 'An error occurred');
    }
    return new Error(error.message || 'Network error');
  }

  // Authentication methods
  setToken(token: string): void {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken(): void {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  getToken(): string | null {
    return this.token;
  }

  // Authentication endpoints
  async login(email: string, password: string): Promise<ApiResponse<{ user: User; token: string }>> {
    const response = await this.client.post('/auth/login', { email, password });
    const { token } = response.data.data;
    this.setToken(token);
    return response.data;
  }

  async register(userData: {
    email: string;
    password: string;
    name: string;
  }): Promise<ApiResponse<{ user: User; token: string }>> {
    const response = await this.client.post('/auth/register', userData);
    const { token } = response.data.data;
    this.setToken(token);
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/auth/logout');
    } finally {
      this.clearToken();
    }
  }

  async refreshToken(): Promise<ApiResponse<{ token: string }>> {
    const response = await this.client.post('/auth/refresh');
    const { token } = response.data.data;
    this.setToken(token);
    return response.data;
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Dashboard endpoints
  async getDashboardMetrics(timeframe?: string): Promise<ApiResponse<DashboardMetrics>> {
    const params = timeframe ? { timeframe } : {};
    const response = await this.client.get('/dashboard/metrics', { params });
    return response.data;
  }

  // Campaign endpoints
  async getCampaigns(
    page: number = 1,
    pageSize: number = 10,
    filters?: CampaignFilters,
    sort?: SortOption
  ): Promise<PaginatedResponse<Campaign>> {
    const params = {
      page,
      page_size: pageSize,
      ...filters,
      sort_field: sort?.field,
      sort_direction: sort?.direction,
    };
    const response = await this.client.get('/campaigns', { params });
    return response.data;
  }

  async getCampaign(id: string): Promise<ApiResponse<Campaign>> {
    const response = await this.client.get(`/campaigns/${id}`);
    return response.data;
  }

  async createCampaign(campaignData: CreateCampaignRequest): Promise<ApiResponse<Campaign>> {
    const response = await this.client.post('/campaigns', campaignData);
    return response.data;
  }

  async updateCampaign(id: string, updates: UpdateCampaignRequest): Promise<ApiResponse<Campaign>> {
    const response = await this.client.patch(`/campaigns/${id}`, updates);
    return response.data;
  }

  async deleteCampaign(id: string): Promise<ApiResponse<void>> {
    const response = await this.client.delete(`/campaigns/${id}`);
    return response.data;
  }

  async pauseCampaign(id: string): Promise<ApiResponse<Campaign>> {
    const response = await this.client.post(`/campaigns/${id}/pause`);
    return response.data;
  }

  async resumeCampaign(id: string): Promise<ApiResponse<Campaign>> {
    const response = await this.client.post(`/campaigns/${id}/resume`);
    return response.data;
  }

  async duplicateCampaign(id: string): Promise<ApiResponse<Campaign>> {
    const response = await this.client.post(`/campaigns/${id}/duplicate`);
    return response.data;
  }

  // Analytics endpoints
  async getCampaignAnalytics(
    campaignId: string,
    startDate: string,
    endDate: string
  ): Promise<ApiResponse<any>> {
    const params = { start_date: startDate, end_date: endDate };
    const response = await this.client.get(`/campaigns/${campaignId}/analytics`, { params });
    return response.data;
  }

  async getAnalyticsOverview(
    startDate: string,
    endDate: string,
    metrics?: string[]
  ): Promise<ApiResponse<any>> {
    const params = {
      start_date: startDate,
      end_date: endDate,
      metrics: metrics?.join(','),
    };
    const response = await this.client.get('/analytics/overview', { params });
    return response.data;
  }

  async getPerformanceComparison(
    campaignIds: string[],
    startDate: string,
    endDate: string
  ): Promise<ApiResponse<any>> {
    const params = {
      campaign_ids: campaignIds.join(','),
      start_date: startDate,
      end_date: endDate,
    };
    const response = await this.client.get('/analytics/comparison', { params });
    return response.data;
  }

  // Trending topics endpoints
  async getTrendingTopics(
    page: number = 1,
    pageSize: number = 20,
    category?: string,
    platform?: string
  ): Promise<PaginatedResponse<TrendingTopic>> {
    const params = {
      page,
      page_size: pageSize,
      category,
      platform,
    };
    const response = await this.client.get('/trending/topics', { params });
    return response.data;
  }

  async getTrendingTopic(id: string): Promise<ApiResponse<TrendingTopic>> {
    const response = await this.client.get(`/trending/topics/${id}`);
    return response.data;
  }

  async searchTrendingTopics(query: string): Promise<ApiResponse<TrendingTopic[]>> {
    const params = { q: query };
    const response = await this.client.get('/trending/search', { params });
    return response.data;
  }

  async getViralOpportunities(): Promise<ApiResponse<TrendingTopic[]>> {
    const response = await this.client.get('/trending/viral-opportunities');
    return response.data;
  }

  // Video endpoints
  async getVideos(
    page: number = 1,
    pageSize: number = 20,
    status?: string
  ): Promise<PaginatedResponse<Video>> {
    const params = { page, page_size: pageSize, status };
    const response = await this.client.get('/videos', { params });
    return response.data;
  }

  async getVideo(id: string): Promise<ApiResponse<Video>> {
    const response = await this.client.get(`/videos/${id}`);
    return response.data;
  }

  async uploadVideo(file: File, metadata: {
    title: string;
    description: string;
    tags: string[];
    category: string;
  }): Promise<ApiResponse<Video>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));

    const response = await this.client.post('/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async deleteVideo(id: string): Promise<ApiResponse<void>> {
    const response = await this.client.delete(`/videos/${id}`);
    return response.data;
  }

  async generateVideo(prompt: string, options?: {
    duration?: number;
    style?: string;
    format?: string;
  }): Promise<ApiResponse<{ taskId: string }>> {
    const response = await this.client.post('/videos/generate', {
      prompt,
      options,
    });
    return response.data;
  }

  async getVideoGenerationStatus(taskId: string): Promise<ApiResponse<{
    status: 'pending' | 'processing' | 'completed' | 'failed';
    progress?: number;
    videoId?: string;
    error?: string;
  }>> {
    const response = await this.client.get(`/videos/generation/${taskId}`);
    return response.data;
  }

  // User management endpoints
  async getUsers(
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResponse<User>> {
    const params = { page, page_size: pageSize };
    const response = await this.client.get('/users', { params });
    return response.data;
  }

  async updateUserProfile(userData: Partial<User>): Promise<ApiResponse<User>> {
    const response = await this.client.patch('/users/profile', userData);
    return response.data;
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<ApiResponse<void>> {
    const response = await this.client.post('/users/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  }

  // Notification endpoints
  async getNotifications(): Promise<ApiResponse<any[]>> {
    const response = await this.client.get('/notifications');
    return response.data;
  }

  async markNotificationRead(id: string): Promise<ApiResponse<void>> {
    const response = await this.client.patch(`/notifications/${id}/read`);
    return response.data;
  }

  async markAllNotificationsRead(): Promise<ApiResponse<void>> {
    const response = await this.client.post('/notifications/mark-all-read');
    return response.data;
  }

  // File upload helper
  async uploadFile(file: File, path?: string): Promise<ApiResponse<{ url: string; id: string }>> {
    const formData = new FormData();
    formData.append('file', file);
    if (path) {
      formData.append('path', path);
    }

    const response = await this.client.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{ status: string; timestamp: string }>> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export individual service objects for better organization
export const authService = {
  login: apiClient.login.bind(apiClient),
  register: apiClient.register.bind(apiClient),
  logout: apiClient.logout.bind(apiClient),
  refreshToken: apiClient.refreshToken.bind(apiClient),
  getCurrentUser: apiClient.getCurrentUser.bind(apiClient),
};

export const campaignService = {
  getCampaigns: apiClient.getCampaigns.bind(apiClient),
  getCampaign: apiClient.getCampaign.bind(apiClient),
  createCampaign: apiClient.createCampaign.bind(apiClient),
  updateCampaign: apiClient.updateCampaign.bind(apiClient),
  deleteCampaign: apiClient.deleteCampaign.bind(apiClient),
  pauseCampaign: apiClient.pauseCampaign.bind(apiClient),
  resumeCampaign: apiClient.resumeCampaign.bind(apiClient),
  duplicateCampaign: apiClient.duplicateCampaign.bind(apiClient),
};

export const analyticsService = {
  getCampaignAnalytics: apiClient.getCampaignAnalytics.bind(apiClient),
  getAnalyticsOverview: apiClient.getAnalyticsOverview.bind(apiClient),
  getPerformanceComparison: apiClient.getPerformanceComparison.bind(apiClient),
};

export const trendingService = {
  getTrendingTopics: apiClient.getTrendingTopics.bind(apiClient),
  getTrendingTopic: apiClient.getTrendingTopic.bind(apiClient),
  searchTrendingTopics: apiClient.searchTrendingTopics.bind(apiClient),
  getViralOpportunities: apiClient.getViralOpportunities.bind(apiClient),
};

export const videoService = {
  getVideos: apiClient.getVideos.bind(apiClient),
  getVideo: apiClient.getVideo.bind(apiClient),
  uploadVideo: apiClient.uploadVideo.bind(apiClient),
  deleteVideo: apiClient.deleteVideo.bind(apiClient),
  generateVideo: apiClient.generateVideo.bind(apiClient),
  getVideoGenerationStatus: apiClient.getVideoGenerationStatus.bind(apiClient),
};

export default apiClient;