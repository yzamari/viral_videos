import { io, Socket } from 'socket.io-client';
import type { WebSocketMessage, GenerationSession, AgentDiscussion, VideoClip, AudioSegment, Script, Overlay, Subtitle, GenerationProgress } from '../types';

export class WebSocketService {
  private socket: Socket | null = null;
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

  constructor(private wsUrl = 'ws://localhost:8000') {}

  connect(sessionId?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.sessionId = sessionId || null;
        
        this.socket = io(this.wsUrl, {
          transports: ['websocket'],
          upgrade: false,
          query: sessionId ? { sessionId } : {},
        });

        this.socket.on('connect', () => {
          console.log('✅ WebSocket connected');
          this.reconnectAttempts = 0;
          this.onConnectionChangeCallback?.(true);
          
          if (this.sessionId) {
            this.socket?.emit('join_session', this.sessionId);
          }
          
          resolve();
        });

        this.socket.on('disconnect', (reason) => {
          console.log('❌ WebSocket disconnected:', reason);
          this.onConnectionChangeCallback?.(false);
          
          if (reason === 'io server disconnect') {
            // Server disconnected, try to reconnect
            this.handleReconnect();
          }
        });

        this.socket.on('connect_error', (error) => {
          console.error('❌ WebSocket connection error:', error);
          this.onConnectionChangeCallback?.(false);
          this.onErrorCallback?.(`Connection failed: ${error.message}`);
          this.handleReconnect();
          reject(error);
        });

        // Register message handlers
        this.setupMessageHandlers();

      } catch (error) {
        console.error('❌ Failed to initialize WebSocket:', error);
        reject(error);
      }
    });
  }

  private setupMessageHandlers(): void {
    if (!this.socket) return;

    // Progress updates
    this.socket.on('progress_update', (data: GenerationProgress) => {
      console.log('📊 Progress update:', data);
      this.onProgressUpdateCallback?.(data);
    });

    // Agent discussions
    this.socket.on('discussion_update', (data: AgentDiscussion) => {
      console.log('💬 Discussion update:', data);
      this.onAgentDiscussionCallback?.(data);
    });

    // Video clip updates
    this.socket.on('clip_update', (data: VideoClip) => {
      console.log('🎬 Video clip update:', data);
      this.onVideoClipUpdateCallback?.(data);
    });

    // Audio updates
    this.socket.on('audio_update', (data: AudioSegment) => {
      console.log('🎵 Audio update:', data);
      this.onAudioUpdateCallback?.(data);
    });

    // Script updates
    this.socket.on('script_update', (data: Script) => {
      console.log('📝 Script update:', data);
      this.onScriptUpdateCallback?.(data);
    });

    // Overlay updates
    this.socket.on('overlay_update', (data: Overlay[]) => {
      console.log('🎨 Overlay update:', data);
      this.onOverlayUpdateCallback?.(data);
    });

    // Subtitle updates
    this.socket.on('subtitle_update', (data: Subtitle[]) => {
      console.log('📖 Subtitle update:', data);
      this.onSubtitleUpdateCallback?.(data);
    });

    // Generation completion
    this.socket.on('generation_complete', (data: GenerationSession) => {
      console.log('✅ Generation complete:', data);
      this.onGenerationCompleteCallback?.(data);
    });

    // Error handling
    this.socket.on('error', (error: string) => {
      console.error('❌ WebSocket error:', error);
      this.onErrorCallback?.(error);
    });

    // Session events
    this.socket.on('session_joined', (sessionId: string) => {
      console.log('🔗 Joined session:', sessionId);
      this.sessionId = sessionId;
    });

    this.socket.on('session_not_found', (sessionId: string) => {
      console.warn('⚠️ Session not found:', sessionId);
      this.onErrorCallback?.(`Session ${sessionId} not found`);
    });
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
      if (this.socket?.connected) return;
      
      this.socket?.connect();
    }, delay);
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.sessionId = null;
    this.reconnectAttempts = 0;
  }

  // Join a specific session
  joinSession(sessionId: string): void {
    this.sessionId = sessionId;
    this.socket?.emit('join_session', sessionId);
  }

  // Leave current session
  leaveSession(): void {
    if (this.sessionId) {
      this.socket?.emit('leave_session', this.sessionId);
      this.sessionId = null;
    }
  }

  // Send messages to server
  startGeneration(config: any): void {
    this.socket?.emit('start_generation', config);
  }

  stopGeneration(): void {
    this.socket?.emit('stop_generation');
  }

  updateScript(script: Script): void {
    this.socket?.emit('update_script', script);
  }

  updateOverlays(overlays: Overlay[]): void {
    this.socket?.emit('update_overlays', overlays);
  }

  updateSubtitles(subtitles: Subtitle[]): void {
    this.socket?.emit('update_subtitles', subtitles);
  }

  requestSessionStatus(): void {
    this.socket?.emit('get_session_status');
  }

  // Ping/Pong for connection health
  ping(): Promise<number> {
    return new Promise((resolve) => {
      const startTime = Date.now();
      this.socket?.emit('ping', startTime);
      this.socket?.once('pong', (timestamp: number) => {
        const latency = Date.now() - timestamp;
        resolve(latency);
      });
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
    return this.socket?.connected || false;
  }

  get currentSessionId(): string | null {
    return this.sessionId;
  }

  get connectionState(): string {
    if (!this.socket) return 'disconnected';
    return this.socket.connected ? 'connected' : 'disconnected';
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