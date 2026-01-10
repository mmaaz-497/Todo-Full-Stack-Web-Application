/**
 * Better Auth Client Integration
 *
 * Handles user authentication with Better Auth service:
 * - Signup
 * - Signin
 * - Signout
 * - Token management
 * - User state
 */

import axios from 'axios';
import {
  safeLocalStorageGetItem,
  safeLocalStorageSetItem,
  safeLocalStorageRemoveItem,
  safeRedirect,
  isBrowser,
} from '@/lib/utils';

// Auth service configuration
const AUTH_BASE_URL = process.env.NEXT_PUBLIC_AUTH_URL || 'http://localhost:3001';

// User interface
export interface User {
  id: string;
  email: string;
  name?: string;
  emailVerified: boolean;
  image?: string;
  createdAt: string;
  updatedAt: string;
}

// Auth response interface (Better Auth format)
export interface AuthResponse {
  user: User;
  token: string;
  redirect?: boolean;
}

// Signup data interface
export interface SignupData {
  email: string;
  password: string;
  name?: string;
}

// Signin data interface
export interface SigninData {
  email: string;
  password: string;
}

/**
 * Auth Service Class
 */
class AuthService {
  /**
   * Sign up a new user
   */
  async signup(data: SignupData): Promise<AuthResponse> {
    try {
      const response = await axios.post<AuthResponse>(
        `${AUTH_BASE_URL}/api/auth/sign-up/email`,
        data,
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      console.log('Sign-up response:', response.data);

      // Better Auth returns token directly in response body
      const token = response.data.token;
      const user = response.data.user;

      console.log('Extracted token:', token);
      console.log('Extracted user:', user);

      if (!token || !user) {
        console.error('Invalid auth response - missing token or user');
        console.error('Response data:', response.data);
        throw new Error('Registration failed - invalid response from server');
      }

      // Store token and user in localStorage
      safeLocalStorageSetItem('auth_token', token);
      safeLocalStorageSetItem('user', JSON.stringify(user));

      console.log('Auth data stored successfully');

      return { user, token };
    } catch (error: any) {
      console.error('Signup error:', error);
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.error || error.response?.data?.message || error.message;
        throw new Error(message || 'Signup failed');
      }
      throw error;
    }
  }

  /**
   * Sign in an existing user
   */
  async signin(data: SigninData): Promise<AuthResponse> {
    try {
      const response = await axios.post<AuthResponse>(
        `${AUTH_BASE_URL}/api/auth/sign-in/email`,
        data,
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      console.log('Sign-in response:', response.data);

      // Better Auth returns token directly in response body
      const token = response.data.token;
      const user = response.data.user;

      console.log('Extracted token:', token);
      console.log('Extracted user:', user);

      if (!token || !user) {
        console.error('Invalid auth response - missing token or user');
        console.error('Headers:', response.headers);
        console.error('Body:', response.data);
        throw new Error('Authentication failed - invalid response from server');
      }

      // Store token and user in localStorage
      safeLocalStorageSetItem('auth_token', token);
      safeLocalStorageSetItem('user', JSON.stringify(user));

      console.log('Auth data stored successfully');

      return { user, token };
    } catch (error: any) {
      console.error('Signin error:', error);
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.error || error.response?.data?.message || error.message;
        throw new Error(message || 'Signin failed');
      }
      throw error;
    }
  }

  /**
   * Sign out the current user
   */
  async signout(): Promise<void> {
    try {
      const token = safeLocalStorageGetItem('auth_token');

      if (token) {
        await axios.post(
          `${AUTH_BASE_URL}/api/auth/sign-out`,
          {},
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
      }
    } catch (error) {
      console.error('Signout error:', error);
    } finally {
      // Always clear local storage
      safeLocalStorageRemoveItem('auth_token');
      safeLocalStorageRemoveItem('user');
    }
  }

  /**
   * Get current user from localStorage
   */
  getCurrentUser(): User | null {
    if (!isBrowser()) {
      return null;
    }

    const userStr = safeLocalStorageGetItem('user');
    if (!userStr) {
      return null;
    }

    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }

  /**
   * Get current token from localStorage
   */
  getToken(): string | null {
    if (!isBrowser()) {
      return null;
    }

    return safeLocalStorageGetItem('auth_token');
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

// Export singleton instance
export const auth = new AuthService();
