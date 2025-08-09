import type { WebSocketMessage, GenerationSession, AgentDiscussion, VideoClip, AudioSegment, Script, Overlay, Subtitle, GenerationProgress } from '../types';

export class WebSocketService {
  private socket: WebSocket | null = null;
  private sessionId: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  // Event callbacks
  private onProgressUpdateCallback?: (progress: GenerationProgress) => void;
  private onAgentDiscussionCallback?: (discussion: AgentDiscussion) => void;
  private onVideoClipUpdateCallback?: (clip: VideoClip) => void;
  private onAudioUpdateCallback?: (audio: AudioSegment) => void;
  private onScriptUpdateCallback?: (script: Script) => void;
  private onOverlayUpdateCallback?: (overlays: Overlay[]) => void;
  private onSubtitleUpdateCallback?: (subtitles: Subtitle[]) => void;
  private onGenerationCompleteCallback?: (session: GenerationSession) => void;
  private onConnectionChangeCallback?: (connected: boolean) => void;
  private onErrorCallback?: (error: string) => void;

  constructor(private wsUrl = 'ws://localhost:8770/ws') {}

  connect(sessionId?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.sessionId = sessionId || null;
        
        this.socket = new WebSocket(this.wsUrl);

        this.socket.onopen = () => {
          console.log('✅ WebSocket connected');
          this.reconnectAttempts = 0;
          this.onConnectionChangeCallback?.(true);
          
          if (this.sessionId) {
            this.sendMessage({
              type: 'join_session',
              sessionId: this.sessionId
            });
          }
          
          resolve();
        };

        this.socket.onclose = (event) => {
          console.log('❌ WebSocket disconnected:', event.reason);
          this.onConnectionChangeCallback?.(false);
          
          // Try to reconnect unless it was a clean close
          if (!event.wasClean) {
            this.handleReconnect();
          }
        };

        this.socket.onerror = (error) => {
          console.error('❌ WebSocket connection error:', error);
          this.onConnectionChangeCallback?.(false);
          this.onErrorCallback?.('Connection failed');
          reject(error);
        };

        this.socket.onmessage = (event) => {
          this.handleMessage(event.data);
        };

      } catch (error) {
        console.error('❌ Failed to initialize WebSocket:', error);
        reject(error);
      }
    });
  }

  private handleMessage(data: string): void {
    try {
      const message = JSON.parse(data);
      
      switch (message.type) {
        case 'progress_update':
          console.log('📊 Progress update:', message.data);
          this.onProgressUpdateCallback?.(message.data);
          break;
          
        case 'discussion_update':
          console.log('💬 Discussion update:', message.data);
          this.onAgentDiscussionCallback?.(message.data);
          break;
          
        case 'clip_update':
          console.log('🎬 Video clip update:', message.data);
          this.onVideoClipUpdateCallback?.(message.data);
          break;
          
        case 'audio_update':
          console.log('🎵 Audio update:', message.data);
          this.onAudioUpdateCallback?.(message.data);
          break;
          
        case 'script_update':
          console.log('📝 Script update:', message.data);
          this.onScriptUpdateCallback?.(message.data);
          break;
          
        case 'overlay_update':
          console.log('🎨 Overlay update:', message.data);
          this.onOverlayUpdateCallback?.(message.data);
          break;
          
        case 'subtitle_update':
          console.log('📖 Subtitle update:', message.data);
          this.onSubtitleUpdateCallback?.(message.data);
          break;
          
        case 'generation_complete':
          console.log('✅ Generation complete:', message.data);
          this.onGenerationCompleteCallback?.(message.data);
          break;
          
        case 'error':
          console.error('❌ WebSocket error:', message.data);
          this.onErrorCallback?.(message.data);
          break;
          
        case 'session_joined':
          console.log('🔗 Joined session:', message.sessionId);
          this.sessionId = message.sessionId;
          break;
          
        case 'session_not_found':
          console.warn('⚠️ Session not found:', message.sessionId);
          this.onErrorCallback?.(`Session ${message.sessionId} not found`);
          break;
          
        case 'pong':
          // Handle pong response (for connection health)
          break;
          
        default:
          console.log('📨 Unknown message type:', message.type);
      }
    } catch (error) {
      console.error('❌ Failed to parse WebSocket message:', error);
    }
  }

  private sendMessage(message: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Max reconnection attempts reached');
      this.onErrorCallback?.('Connection lost. Please refresh the page.');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms...`);
    
    setTimeout(() => {
      if (this.socket?.readyState === WebSocket.OPEN) return;
      
      this.connect(this.sessionId || undefined);
    }, delay);
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.sessionId = null;
    this.reconnectAttempts = 0;
  }

  // Join a specific session
  joinSession(sessionId: string): void {
    this.sessionId = sessionId;
    this.sendMessage({
      type: 'join_session',
      sessionId: sessionId
    });
  }

  // Leave current session
  leaveSession(): void {
    if (this.sessionId) {
      this.sendMessage({
        type: 'leave_session',
        sessionId: this.sessionId
      });
      this.sessionId = null;
    }
  }

  // Send messages to server
  startGeneration(config: any): void {
    this.sendMessage({
      type: 'start_generation',
      data: config
    });
  }

  stopGeneration(): void {
    this.sendMessage({
      type: 'stop_generation'
    });
  }

  updateScript(script: Script): void {
    this.sendMessage({
      type: 'update_script',
      data: script
    });
  }

  updateOverlays(overlays: Overlay[]): void {
    this.sendMessage({
      type: 'update_overlays',
      data: overlays
    });
  }

  updateSubtitles(subtitles: Subtitle[]): void {
    this.sendMessage({
      type: 'update_subtitles',
      data: subtitles
    });
  }

  requestSessionStatus(): void {
    this.sendMessage({
      type: 'get_session_status'
    });
  }

  // Ping/Pong for connection health
  ping(): Promise<number> {
    return new Promise((resolve) => {
      const startTime = Date.now();
      this.sendMessage({
        type: 'ping',
        timestamp: startTime
      });
      
      // Set up one-time listener for pong response
      const originalHandler = this.socket?.onmessage;
      this.socket!.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'pong') {
            const latency = Date.now() - message.timestamp;
            resolve(latency);
            // Restore original handler
            this.socket!.onmessage = originalHandler;
          }
        } catch (error) {
          // Restore original handler on error
          this.socket!.onmessage = originalHandler;
        }
      };
    });
  }

  // Event listeners
  onProgressUpdate(callback: (progress: GenerationProgress) => void): void {
    this.onProgressUpdateCallback = callback;
  }

  onAgentDiscussion(callback: (discussion: AgentDiscussion) => void): void {
    this.onAgentDiscussionCallback = callback;
  }

  onVideoClipUpdate(callback: (clip: VideoClip) => void): void {
    this.onVideoClipUpdateCallback = callback;
  }

  onAudioUpdate(callback: (audio: AudioSegment) => void): void {
    this.onAudioUpdateCallback = callback;
  }

  onScriptUpdate(callback: (script: Script) => void): void {
    this.onScriptUpdateCallback = callback;
  }

  onOverlayUpdate(callback: (overlays: Overlay[]) => void): void {
    this.onOverlayUpdateCallback = callback;
  }

  onSubtitleUpdate(callback: (subtitles: Subtitle[]) => void): void {
    this.onSubtitleUpdateCallback = callback;
  }

  onGenerationComplete(callback: (session: GenerationSession) => void): void {
    this.onGenerationCompleteCallback = callback;
  }

  onConnectionChange(callback: (connected: boolean) => void): void {
    this.onConnectionChangeCallback = callback;
  }

  onError(callback: (error: string) => void): void {
    this.onErrorCallback = callback;
  }

  // Getters
  get isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }

  get currentSessionId(): string | null {
    return this.sessionId;
  }

  get connectionState(): string {
    if (!this.socket) return 'disconnected';
    
    switch (this.socket.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'unknown';
    }
  }
}

// Singleton instance
export const websocketService = new WebSocketService();

// Helper functions for connection management
export const connectWebSocket = (sessionId?: string): Promise<void> => {
  return websocketService.connect(sessionId);
};

export const disconnectWebSocket = (): void => {
  websocketService.disconnect();
};

export const joinSession = (sessionId: string): void => {
  websocketService.joinSession(sessionId);
};

export const isWebSocketConnected = (): boolean => {
  return websocketService.isConnected;
};