import { useEffect, useRef, useState } from 'react';
import io, { Socket } from 'socket.io-client';
import { useAppDispatch } from '../store/store';
import { campaignsActions, notificationsActions, dashboardActions, trendingActions } from '../store/store';
import { WebSocketMessage } from '../types';

interface UseWebSocketOptions {
  url?: string;
  autoConnect?: boolean;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

interface WebSocketState {
  isConnected: boolean;
  error: string | null;
  lastMessage: WebSocketMessage | null;
}

export const useWebSocket = (options: UseWebSocketOptions = {}): WebSocketState => {
  const {
    url = import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
    autoConnect = true,
    reconnectAttempts = 5,
    reconnectInterval = 3000
  } = options;

  const dispatch = useAppDispatch();
  const socketRef = useRef<Socket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    error: null,
    lastMessage: null,
  });

  const connect = () => {
    if (socketRef.current?.connected) return;

    const token = localStorage.getItem('auth_token');
    if (!token) return;

    socketRef.current = io(url, {
      auth: { token },
      transports: ['websocket', 'polling'],
    });

    const socket = socketRef.current;

    socket.on('connect', () => {
      console.log('WebSocket connected');
      setState(prev => ({ ...prev, isConnected: true, error: null }));
      reconnectAttemptsRef.current = 0;
    });

    socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      setState(prev => ({ ...prev, isConnected: false }));
      
      if (reason === 'io server disconnect') {
        // Server disconnected, need to reconnect manually
        attemptReconnect();
      }
    });

    socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      setState(prev => ({ ...prev, error: error.message, isConnected: false }));
      attemptReconnect();
    });

    // Campaign updates
    socket.on('campaign_update', (data) => {
      dispatch(campaignsActions.updateCampaign(data.campaign));
      const message: WebSocketMessage = {
        type: 'campaign_update',
        payload: data,
        timestamp: new Date().toISOString(),
      };
      setState(prev => ({ ...prev, lastMessage: message }));
    });

    socket.on('campaign_created', (data) => {
      dispatch(campaignsActions.addCampaign(data.campaign));
    });

    socket.on('campaign_deleted', (data) => {
      dispatch(campaignsActions.removeCampaign(data.campaignId));
    });

    // Dashboard metrics updates
    socket.on('metrics_update', (data) => {
      dispatch(dashboardActions.updateMetrics(data.metrics));
      const message: WebSocketMessage = {
        type: 'metrics_update',
        payload: data,
        timestamp: new Date().toISOString(),
      };
      setState(prev => ({ ...prev, lastMessage: message }));
    });

    // Trending topics updates
    socket.on('trending_update', (data) => {
      if (data.newTopic) {
        dispatch(trendingActions.addTopic(data.newTopic));
      }
      if (data.updatedTopic) {
        dispatch(trendingActions.updateTopic(data.updatedTopic));
      }
      const message: WebSocketMessage = {
        type: 'trending_update',
        payload: data,
        timestamp: new Date().toISOString(),
      };
      setState(prev => ({ ...prev, lastMessage: message }));
    });

    // Notifications
    socket.on('notification', (data) => {
      dispatch(notificationsActions.addNotification(data.notification));
      const message: WebSocketMessage = {
        type: 'notification',
        payload: data,
        timestamp: new Date().toISOString(),
      };
      setState(prev => ({ ...prev, lastMessage: message }));
    });

    // Video generation updates
    socket.on('video_generation_update', (data) => {
      // Handle video generation status updates
      console.log('Video generation update:', data);
    });

    // Analytics updates
    socket.on('analytics_update', (data) => {
      // Handle real-time analytics updates
      console.log('Analytics update:', data);
    });
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }

    setState(prev => ({ ...prev, isConnected: false }));
  };

  const attemptReconnect = () => {
    if (reconnectAttemptsRef.current >= reconnectAttempts) {
      console.log('Max reconnection attempts reached');
      setState(prev => ({ ...prev, error: 'Connection failed after multiple attempts' }));
      return;
    }

    reconnectAttemptsRef.current++;
    console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${reconnectAttempts})...`);

    reconnectTimeoutRef.current = setTimeout(() => {
      disconnect();
      connect();
    }, reconnectInterval);
  };

  const sendMessage = (type: string, payload: any) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit(type, payload);
    } else {
      console.warn('Cannot send message: WebSocket not connected');
    }
  };

  // Subscribe to specific campaign updates
  const subscribeToCampaign = (campaignId: string) => {
    sendMessage('subscribe_campaign', { campaignId });
  };

  const unsubscribeFromCampaign = (campaignId: string) => {
    sendMessage('unsubscribe_campaign', { campaignId });
  };

  // Subscribe to trending updates for specific categories
  const subscribeToTrending = (categories: string[]) => {
    sendMessage('subscribe_trending', { categories });
  };

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, []);

  // Reconnect when token changes (user login/logout)
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token && !socketRef.current?.connected) {
      connect();
    } else if (!token && socketRef.current?.connected) {
      disconnect();
    }
  }, [localStorage.getItem('auth_token')]);

  return {
    ...state,
    connect,
    disconnect,
    sendMessage,
    subscribeToCampaign,
    unsubscribeFromCampaign,
    subscribeToTrending,
  } as WebSocketState & {
    connect: () => void;
    disconnect: () => void;
    sendMessage: (type: string, payload: any) => void;
    subscribeToCampaign: (campaignId: string) => void;
    unsubscribeFromCampaign: (campaignId: string) => void;
    subscribeToTrending: (categories: string[]) => void;
  };
};

export default useWebSocket;