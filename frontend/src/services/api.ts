import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  VideoGenerationConfig, 
  GenerationSession, 
  Script, 
  Overlay, 
  Subtitle, 
  FinalVideo 
} from '../types';

export interface ApiConfig {
  baseURL: string;
  timeout: number;
}

export class ApiService {
  private client: AxiosInstance;

  constructor(config: ApiConfig = { baseURL: 'http://localhost:8770', timeout: 30000 }) {
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('❌ API Response Error:', error.response?.status, error.response?.data);
        return Promise.reject(this.handleError(error));
      }
    );
  }

  private handleError(error: any): Error {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.message || error.response.statusText || 'Server Error';
      return new Error(`Server Error (${error.response.status}): ${message}`);
    } else if (error.request) {
      // Request was made but no response received
      return new Error('Network Error: Unable to connect to server');
    } else {
      // Something else happened
      return new Error(`Request Error: ${error.message}`);
    }
  }

  // Authentication and health checks
  async checkHealth(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  async testAuth(): Promise<{ authenticated: boolean; details: any }> {
    const response = await this.client.get('/auth/test');
    return response.data;
  }

  // Session management
  async createSession(config: VideoGenerationConfig): Promise<GenerationSession> {
    const response = await this.client.post('/sessions', config);
    return response.data;
  }

  async getSession(sessionId: string): Promise<GenerationSession> {
    const response = await this.client.get(`/sessions/${sessionId}`);
    return response.data;
  }

  async getSessions(): Promise<GenerationSession[]> {
    const response = await this.client.get('/sessions');
    return response.data;
  }

  async deleteSession(sessionId: string): Promise<void> {
    await this.client.delete(`/sessions/${sessionId}`);
  }

  // Video generation
  async startGeneration(sessionId: string, config: VideoGenerationConfig): Promise<{ success: boolean; message: string }> {
    const response = await this.client.post(`/sessions/${sessionId}/generate`, config);
    return response.data;
  }

  async stopGeneration(sessionId: string): Promise<{ success: boolean; message: string }> {
    const response = await this.client.post(`/sessions/${sessionId}/stop`);
    return response.data;
  }

  async getGenerationStatus(sessionId: string): Promise<{ status: string; progress: number; message: string }> {
    const response = await this.client.get(`/sessions/${sessionId}/status`);
    return response.data;
  }

  // Script management
  async getScript(sessionId: string): Promise<Script | null> {
    try {
      const response = await this.client.get(`/sessions/${sessionId}/script`);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async updateScript(sessionId: string, script: Script): Promise<Script> {
    const response = await this.client.put(`/sessions/${sessionId}/script`, script);
    return response.data;
  }

  // Overlay management
  async getOverlays(sessionId: string): Promise<Overlay[]> {
    const response = await this.client.get(`/sessions/${sessionId}/overlays`);
    return response.data;
  }

  async updateOverlays(sessionId: string, overlays: Overlay[]): Promise<Overlay[]> {
    const response = await this.client.put(`/sessions/${sessionId}/overlays`, overlays);
    return response.data;
  }

  // Subtitle management
  async getSubtitles(sessionId: string): Promise<Subtitle[]> {
    const response = await this.client.get(`/sessions/${sessionId}/subtitles`);
    return response.data;
  }

  async updateSubtitles(sessionId: string, subtitles: Subtitle[]): Promise<Subtitle[]> {
    const response = await this.client.put(`/sessions/${sessionId}/subtitles`, subtitles);
    return response.data;
  }

  async exportSubtitles(sessionId: string, format: 'srt' | 'vtt'): Promise<Blob> {
    const response = await this.client.get(`/sessions/${sessionId}/subtitles/export`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  }

  // File management
  async getVideoClips(sessionId: string): Promise<any[]> {
    const response = await this.client.get(`/sessions/${sessionId}/clips`);
    return response.data;
  }

  async getAudioSegments(sessionId: string): Promise<any[]> {
    const response = await this.client.get(`/sessions/${sessionId}/audio`);
    return response.data;
  }

  async getFinalVideo(sessionId: string): Promise<FinalVideo | null> {
    try {
      const response = await this.client.get(`/sessions/${sessionId}/final-video`);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  // File downloads
  async downloadFile(url: string, filename?: string): Promise<void> {
    const response = await this.client.get(url, {
      responseType: 'blob',
    });

    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }

  async downloadVideo(sessionId: string, filename?: string): Promise<void> {
    await this.downloadFile(`/sessions/${sessionId}/download`, filename || 'video.mp4');
  }

  async downloadScript(sessionId: string, format: 'txt' | 'json' = 'txt'): Promise<void> {
    await this.downloadFile(`/sessions/${sessionId}/script/export?format=${format}`, `script.${format}`);
  }

  // Agent discussions
  async getDiscussions(sessionId: string): Promise<any[]> {
    const response = await this.client.get(`/sessions/${sessionId}/discussions`);
    return response.data;
  }

  async getAgentStatus(sessionId: string): Promise<any[]> {
    const response = await this.client.get(`/sessions/${sessionId}/agents`);
    return response.data;
  }

  // Analytics and metrics
  async getSessionMetrics(sessionId: string): Promise<any> {
    const response = await this.client.get(`/sessions/${sessionId}/metrics`);
    return response.data;
  }

  async getSystemMetrics(): Promise<any> {
    const response = await this.client.get('/metrics/system');
    return response.data;
  }

  // File uploads
  async uploadSubtitleFile(sessionId: string, file: File): Promise<Subtitle[]> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post(`/sessions/${sessionId}/subtitles/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async uploadScriptFile(sessionId: string, file: File): Promise<Script> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post(`/sessions/${sessionId}/script/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Utility methods
  getFileUrl(path: string): string {
    return `${this.client.defaults.baseURL}${path}`;
  }

  async getServerTime(): Promise<Date> {
    const response = await this.client.get('/time');
    return new Date(response.data.timestamp);
  }

  // Configuration
  updateConfig(config: Partial<ApiConfig>): void {
    if (config.baseURL) {
      this.client.defaults.baseURL = config.baseURL;
    }
    if (config.timeout) {
      this.client.defaults.timeout = config.timeout;
    }
  }
}

// Singleton instance
export const apiService = new ApiService();

// Convenience functions
export const checkServerHealth = () => apiService.checkHealth();
export const testAuthentication = () => apiService.testAuth();
export const createSession = (config: VideoGenerationConfig) => apiService.createSession(config);
export const getSession = (sessionId: string) => apiService.getSession(sessionId);
export const startGeneration = (sessionId: string, config: VideoGenerationConfig) => 
  apiService.startGeneration(sessionId, config);
export const stopGeneration = (sessionId: string) => apiService.stopGeneration(sessionId);

// Error handling utility
export const isApiError = (error: any): boolean => {
  return error?.response?.status !== undefined;
};

export const getApiErrorMessage = (error: any): string => {
  if (isApiError(error)) {
    return error.response?.data?.message || error.response?.statusText || 'API Error';
  }
  return error.message || 'Unknown error';
};

export const isNetworkError = (error: any): boolean => {
  return !error.response && error.request;
};

export const isServerError = (error: any): boolean => {
  return isApiError(error) && error.response.status >= 500;
};

export const isClientError = (error: any): boolean => {
  return isApiError(error) && error.response.status >= 400 && error.response.status < 500;
};