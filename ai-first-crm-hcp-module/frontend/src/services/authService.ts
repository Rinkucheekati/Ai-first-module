import axios, { AxiosInstance } from 'axios';
import { API_BASE_URL } from './apiClient';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

class AuthService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Login user with email and password
   * @param email - User email
   * @param password - User password
   * @returns Authentication response with token and user data
   */
  async login(email: string, password: string): Promise<AuthResponse> {
    try {
      const response = await this.api.post<AuthResponse>('/auth/login', {
        email,
        password,
      });

      // Store token in localStorage
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Login failed');
      }
      throw error;
    }
  }

  /**
   * Verify a JWT token
   * @param token - JWT token to verify
   * @returns Token verification status
   */
  async verifyToken(token: string): Promise<{ valid: boolean; email?: string; exp?: number }> {
    try {
      const response = await this.api.get('/auth/verify', {
        params: { token },
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Token verification failed');
      }
      throw error;
    }
  }

  /**
   * Get stored token from localStorage
   * @returns JWT token or null
   */
  getToken(): string | null {
    return localStorage.getItem('token');
  }

  /**
   * Get stored user data from localStorage
   * @returns User object or null
   */
  getUser(): User | null {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  /**
   * Logout user by removing token and user data
   */
  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  /**
   * Check if user is authenticated
   * @returns True if token exists and is valid
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  /**
   * Setup axios interceptor to include token in requests
   */
  setupInterceptors(): void {
    this.api.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        // Handle 401 Unauthorized
        if (error.response?.status === 401) {
          this.logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }
}

export const authService = new AuthService();
