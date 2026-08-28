/**
 * Shamba API Client & Authentication Services
 */
import axios, { AxiosError } from 'axios';
import { ApiResponse, LoginResponseData, User } from '../types';

const TOKEN_KEY = 'shamba_auth_token';

export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

export const setToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const clearToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
};

export const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Interceptor to inject JWT Bearer Token
apiClient.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor to handle global responses and errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiResponse>) => {
    if (!error.response) {
      // Network or server unreachable error
      return Promise.reject({
        code: 'NETWORK_ERROR',
        message: 'Unable to connect to Shamba. Please try again.',
      });
    }

    const data = error.response.data;
    if (data && data.error) {
      return Promise.reject(data.error);
    }

    // Default error fallback
    return Promise.reject({
      code: `HTTP_${error.response.status}`,
      message: error.response.statusText || 'An unexpected error occurred.',
    });
  }
);

export const authApi = {
  async login(identifier: string, password: string): Promise<LoginResponseData> {
    const response = await apiClient.post<ApiResponse<LoginResponseData>>('/auth/login', {
      username: identifier.trim(),
      password,
    });

    if (response.data.success && response.data.data) {
      const { token } = response.data.data;
      setToken(token);
      return response.data.data;
    }

    throw new Error(response.data.error?.message || 'Login failed.');
  },

  async getMe(): Promise<User> {
    const response = await apiClient.get<ApiResponse<{ user: User }>>('/auth/me');
    if (response.data.success && response.data.data) {
      return response.data.data.user;
    }
    throw new Error(response.data.error?.message || 'Failed to fetch authenticated user.');
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post<ApiResponse>('/auth/logout');
    } catch {
      // Ignore network errors on logout
    } finally {
      clearToken();
    }
  },
};
