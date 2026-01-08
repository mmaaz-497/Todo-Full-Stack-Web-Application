/**
 * WebSocket Hook for Real-Time Task Synchronization
 *
 * Implements Phase V WebSocket Integration (T203-T208):
 * - T203: Create useWebSocket hook with Socket.IO client
 * - T204: Connection to WebSocket Sync Service
 * - T205: JWT token authentication
 * - T206: task.sync event listener
 * - T207: Update task list state on sync event
 * - T208: Auto-reconnect on disconnect
 */

import { useEffect, useState, useCallback, useRef } from 'react';

// WebSocket message types
export interface TaskSyncMessage {
  type: 'task_update';
  operation: 'create' | 'update' | 'delete';
  task_id: number;
  task: {
    id: number;
    title: string;
    description?: string;
    status: string;
    priority?: string;
    tags?: string[];
    due_date?: string;
    created_at: string;
    updated_at: string;
  };
  timestamp: string;
}

export interface WebSocketMessage {
  type: 'connected' | 'pong' | 'task_update';
  user_id?: number;
  message?: string;
  [key: string]: any;
}

export interface UseWebSocketOptions {
  url: string;
  token: string | null;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  onMessage?: (message: WebSocketMessage) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export interface UseWebSocketReturn {
  isConnected: boolean;
  error: string | null;
  sendMessage: (message: any) => void;
  reconnect: () => void;
}

/**
 * Custom React hook for WebSocket real-time synchronization.
 *
 * Features:
 * - Automatic connection with JWT authentication
 * - Auto-reconnection with exponential backoff
 * - Ping/pong keep-alive mechanism
 * - Type-safe message handling
 * - Connection state management
 *
 * @param options - WebSocket configuration options
 * @returns WebSocket connection state and controls
 *
 * @example
 * ```typescript
 * const { isConnected, sendMessage } = useWebSocket({
 *   url: 'ws://localhost:8004/ws',
 *   token: localStorage.getItem('jwt_token'),
 *   onMessage: (message) => {
 *     if (message.type === 'task_update') {
 *       // Update task list
 *     }
 *   }
 * });
 * ```
 */
export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  const {
    url,
    token,
    onConnect,
    onDisconnect,
    onError,
    onMessage,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * T204: Connect to WebSocket Sync Service with JWT authentication
   */
  const connect = useCallback(() => {
    if (!token) {
      setError('No authentication token available');
      return;
    }

    try {
      // T205: Add JWT token to connection query parameter
      const wsUrl = `${url}?token=${encodeURIComponent(token)}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('[WebSocket] Connected to sync service');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;

        // T206: Start ping/pong keep-alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000); // Ping every 30 seconds

        if (onConnect) {
          onConnect();
        }
      };

      // T206: Listen for task.sync events
      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          // Handle pong response
          if (message.type === 'pong') {
            console.log('[WebSocket] Pong received');
            return;
          }

          // Handle connected message
          if (message.type === 'connected') {
            console.log(`[WebSocket] Connected as user ${message.user_id}`);
            return;
          }

          // T207: Forward task updates to parent component
          if (onMessage) {
            onMessage(message);
          }
        } catch (err) {
          console.error('[WebSocket] Failed to parse message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('[WebSocket] Error:', event);
        setError('WebSocket connection error');

        if (onError) {
          onError(event);
        }
      };

      // T208: Auto-reconnect on disconnect
      ws.onclose = () => {
        console.log('[WebSocket] Disconnected from sync service');
        setIsConnected(false);

        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        if (onDisconnect) {
          onDisconnect();
        }

        // Attempt reconnection with exponential backoff
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = reconnectInterval * Math.pow(2, reconnectAttemptsRef.current);
          console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`);

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            connect();
          }, delay);
        } else {
          setError('Maximum reconnection attempts reached');
        }
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('[WebSocket] Connection failed:', err);
      setError('Failed to establish WebSocket connection');
    }
  }, [url, token, onConnect, onDisconnect, onError, onMessage, reconnectInterval, maxReconnectAttempts]);

  /**
   * Send message to WebSocket server
   */
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('[WebSocket] Cannot send message: connection not open');
    }
  }, []);

  /**
   * Manual reconnection
   */
  const reconnect = useCallback(() => {
    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Clear reconnection timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Reset reconnection attempts
    reconnectAttemptsRef.current = 0;

    // Reconnect
    connect();
  }, [connect]);

  /**
   * Establish connection on mount
   */
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      // Close WebSocket connection
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }

      // Clear timeouts/intervals
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
    };
  }, [connect]);

  return {
    isConnected,
    error,
    sendMessage,
    reconnect,
  };
}

export default useWebSocket;
