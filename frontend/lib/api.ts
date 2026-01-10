/**
 * API Client for Todo Backend
 *
 * Centralized HTTP client for all backend API calls.
 * Handles token attachment, error handling, and type-safe responses.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  safeLocalStorageGetItem,
  safeLocalStorageRemoveItem,
  safeRedirect,
  isBrowser,
} from '@/lib/utils';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Task Priority Enum (Intermediate Feature)
export type TaskPriority = 'HIGH' | 'MEDIUM' | 'LOW';

// Recurrence Pattern Enum (Advanced Feature)
export type RecurrencePattern = 'none' | 'daily' | 'weekly' | 'monthly';

// Task TypeScript interfaces
export interface Task {
  // Basic Level Fields
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;

  // Intermediate Level Fields
  priority: TaskPriority;
  tags: string[];

  // Advanced Level Fields
  due_date: string | null;
  reminder_time: string | null;
  recurrence_pattern: RecurrencePattern;
  last_completed_at: string | null;

  // Computed Fields
  is_overdue: boolean;
}

export interface TaskCreate {
  // Basic Level
  title: string;
  description?: string;

  // Intermediate Level
  priority?: TaskPriority;
  tags?: string[];

  // Advanced Level
  due_date?: string;
  reminder_time?: string;
  recurrence_pattern?: RecurrencePattern;
}

export interface TaskUpdate {
  // Basic Level
  title?: string;
  description?: string;

  // Intermediate Level
  priority?: TaskPriority;
  tags?: string[];

  // Advanced Level
  due_date?: string;
  reminder_time?: string;
  recurrence_pattern?: RecurrencePattern;
}

// Create axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds (increased for database latency)
});

// Request interceptor to attach JWT token
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = safeLocalStorageGetItem('auth_token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear and redirect to signin
      safeLocalStorageRemoveItem('auth_token');
      safeLocalStorageRemoveItem('user');
      if (isBrowser()) {
        safeRedirect('/signin');
      }
    }
    return Promise.reject(error);
  }
);

// Filter and Sort Params (Intermediate Feature)
export interface TaskFilters {
  priority?: TaskPriority | 'all';
  tags?: string[];
  status?: 'all' | 'pending' | 'completed';
  sort?: 'created_date' | 'due_date' | 'priority' | 'title';
}

// Toggle Complete Response (Advanced Feature - recurring tasks)
export interface ToggleCompleteResponse {
  task: Task;
  next_occurrence: Task | null;
}

/**
 * API Service Class
 */
class ApiService {
  /**
   * Get all tasks for a user with optional filters and sorting
   */
  async getTasks(userId: string, filters?: TaskFilters): Promise<Task[]> {
    const params = new URLSearchParams();

    if (filters?.priority && filters.priority !== 'all') {
      params.append('priority', filters.priority);
    }

    if (filters?.tags && filters.tags.length > 0) {
      filters.tags.forEach(tag => params.append('tags', tag));
    }

    if (filters?.status) {
      params.append('status', filters.status);
    }

    if (filters?.sort) {
      params.append('sort', filters.sort);
    }

    const response = await apiClient.get<Task[]>(
      `/api/${userId}/tasks${params.toString() ? `?${params.toString()}` : ''}`
    );
    return response.data;
  }

  /**
   * Create a new task
   */
  async createTask(userId: string, taskData: TaskCreate): Promise<Task> {
    const response = await apiClient.post<Task>(`/api/${userId}/tasks`, taskData);
    return response.data;
  }

  /**
   * Get a single task by ID
   */
  async getTask(userId: string, taskId: number): Promise<Task> {
    const response = await apiClient.get<Task>(`/api/${userId}/tasks/${taskId}`);
    return response.data;
  }

  /**
   * Update an existing task
   */
  async updateTask(userId: string, taskId: number, taskData: TaskUpdate): Promise<Task> {
    const response = await apiClient.put<Task>(`/api/${userId}/tasks/${taskId}`, taskData);
    return response.data;
  }

  /**
   * Delete a task
   */
  async deleteTask(userId: string, taskId: number): Promise<void> {
    await apiClient.delete(`/api/${userId}/tasks/${taskId}`);
  }

  /**
   * Toggle task completion status
   * Returns task and potentially a next_occurrence for recurring tasks
   */
  async toggleComplete(userId: string, taskId: number): Promise<ToggleCompleteResponse> {
    const response = await apiClient.patch<ToggleCompleteResponse>(
      `/api/${userId}/tasks/${taskId}/complete`
    );
    return response.data;
  }

  /**
   * Search tasks by keyword (Intermediate Feature)
   */
  async searchTasks(userId: string, query: string): Promise<Task[]> {
    const response = await apiClient.get<Task[]>(
      `/api/${userId}/tasks/search?q=${encodeURIComponent(query)}`
    );
    return response.data;
  }

  /**
   * Get all unique tags for autocomplete (Intermediate Feature)
   */
  async getUserTags(userId: string): Promise<string[]> {
    const response = await apiClient.get<string[]>(`/api/${userId}/tags`);
    return response.data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; message: string }> {
    const response = await apiClient.get('/health');
    return response.data;
  }
}

// Export singleton instance
export const api = new ApiService();

// Export axios instance for custom requests
export { apiClient };
