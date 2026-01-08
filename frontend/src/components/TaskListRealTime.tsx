/**
 * Real-Time Task List Component
 *
 * Demonstrates integration of useWebSocket hook for real-time task synchronization.
 * Implements T207: Update task list state on sync event
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useWebSocket, TaskSyncMessage, WebSocketMessage } from '../hooks/useWebSocket';

interface Task {
  id: number;
  title: string;
  description?: string;
  status: string;
  priority?: string;
  tags?: string[];
  due_date?: string;
  created_at: string;
  updated_at: string;
}

export const TaskListRealTime: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<string>('Connecting...');

  // Get WebSocket URL and token from environment or localStorage
  const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8004/ws';
  const token = localStorage.getItem('jwt_token');

  /**
   * T207: Handle task updates from WebSocket
   */
  const handleTaskUpdate = useCallback((message: WebSocketMessage) => {
    if (message.type === 'task_update') {
      const update = message as TaskSyncMessage;

      setTasks((prevTasks) => {
        switch (update.operation) {
          case 'create':
            // Add new task to list
            return [...prevTasks, update.task];

          case 'update':
            // Update existing task
            return prevTasks.map((task) =>
              task.id === update.task_id ? update.task : task
            );

          case 'delete':
            // Remove task from list
            return prevTasks.filter((task) => task.id !== update.task_id);

          default:
            return prevTasks;
        }
      });

      // Show notification
      console.log(`[Task Update] ${update.operation} - Task ID: ${update.task_id}`);
    }
  }, []);

  /**
   * Initialize WebSocket connection
   */
  const { isConnected, error, reconnect } = useWebSocket({
    url: wsUrl,
    token,
    onConnect: () => {
      setConnectionStatus('Connected');
      console.log('[TaskListRealTime] WebSocket connected');
    },
    onDisconnect: () => {
      setConnectionStatus('Disconnected');
      console.log('[TaskListRealTime] WebSocket disconnected');
    },
    onError: (err) => {
      setConnectionStatus('Error');
      console.error('[TaskListRealTime] WebSocket error:', err);
    },
    onMessage: handleTaskUpdate,
  });

  /**
   * Load initial tasks from API
   */
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await fetch(`/api/tasks`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setTasks(data);
        }
      } catch (err) {
        console.error('[TaskListRealTime] Failed to fetch tasks:', err);
      }
    };

    fetchTasks();
  }, [token]);

  return (
    <div className="task-list-realtime">
      <div className="header">
        <h1>My Tasks (Real-Time)</h1>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></span>
          <span className="status-text">{connectionStatus}</span>
          {!isConnected && (
            <button onClick={reconnect} className="reconnect-button">
              Reconnect
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <strong>Connection Error:</strong> {error}
        </div>
      )}

      <div className="task-list">
        {tasks.length === 0 ? (
          <p className="empty-state">No tasks yet. Create one to get started!</p>
        ) : (
          tasks.map((task) => (
            <div key={task.id} className="task-item">
              <div className="task-header">
                <h3>{task.title}</h3>
                {task.priority && (
                  <span className={`priority priority-${task.priority.toLowerCase()}`}>
                    {task.priority}
                  </span>
                )}
              </div>
              {task.description && <p className="task-description">{task.description}</p>}
              <div className="task-meta">
                <span className={`status status-${task.status}`}>{task.status}</span>
                {task.tags && task.tags.length > 0 && (
                  <div className="tags">
                    {task.tags.map((tag, idx) => (
                      <span key={idx} className="tag">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
                {task.due_date && (
                  <span className="due-date">
                    Due: {new Date(task.due_date).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      <style>{`
        .task-list-realtime {
          padding: 20px;
          max-width: 800px;
          margin: 0 auto;
        }

        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .connection-status {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .status-indicator {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background-color: #ccc;
        }

        .status-indicator.connected {
          background-color: #4caf50;
          animation: pulse 2s infinite;
        }

        .status-indicator.disconnected {
          background-color: #f44336;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        .reconnect-button {
          padding: 4px 12px;
          background: #2196f3;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .error-banner {
          padding: 12px;
          background: #ffebee;
          border-left: 4px solid #f44336;
          margin-bottom: 20px;
        }

        .task-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .task-item {
          padding: 16px;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          background: white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .task-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .priority {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: bold;
        }

        .priority-urgent { background: #f44336; color: white; }
        .priority-high { background: #ff9800; color: white; }
        .priority-medium { background: #ffc107; color: black; }
        .priority-low { background: #4caf50; color: white; }

        .task-meta {
          display: flex;
          gap: 12px;
          align-items: center;
          margin-top: 8px;
        }

        .status {
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 12px;
        }

        .status-pending { background: #e3f2fd; color: #1976d2; }
        .status-completed { background: #e8f5e9; color: #388e3c; }

        .tags {
          display: flex;
          gap: 4px;
        }

        .tag {
          padding: 2px 8px;
          background: #f5f5f5;
          border-radius: 12px;
          font-size: 12px;
        }

        .empty-state {
          text-align: center;
          padding: 40px;
          color: #999;
        }
      `}</style>
    </div>
  );
};

export default TaskListRealTime;
