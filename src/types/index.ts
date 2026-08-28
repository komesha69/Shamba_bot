/**
 * Types for Shamba Authentication & User Management
 */

export interface Permission {
  id: number;
  name: string;
  description?: string;
  created_at?: string;
}

export interface User {
  id: number;
  name: string;
  email: string;
  username: string;
  status: 'active' | 'inactive' | 'suspended';
  role: string;
  role_id: number;
  permissions: string[];
  created_at?: string;
  last_login_at?: string;
}

export interface LoginResponseData {
  token: string;
  user: User;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (identifier: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}
