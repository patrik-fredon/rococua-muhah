import apiClient from "./authApi";

export interface User {
  id: string;
  email: string;
  username: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  address?: string;
  is_active: boolean;
  is_verified: boolean;
  roles: Role[];
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface Role {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  is_active: boolean;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  address?: string;
  is_active?: boolean;
  is_verified?: boolean;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  address?: string;
  is_active?: boolean;
  is_verified?: boolean;
}

export interface UserStatusUpdate {
  is_active?: boolean;
  is_verified?: boolean;
}

export const usersApi = {
  // Get all users (admin only)
  getUsers: async (skip: number = 0, limit: number = 100): Promise<User[]> => {
    const response = await apiClient.get(
      `/api/v1/users?skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  // Get user by ID (admin only)
  getUser: async (userId: string): Promise<User> => {
    const response = await apiClient.get(`/api/v1/users/${userId}`);
    return response.data;
  },

  // Create new user (admin only)
  createUser: async (userData: UserCreate): Promise<User> => {
    const response = await apiClient.post("/api/v1/users/register", userData);
    return response.data.user;
  },

  // Update user (admin only)
  updateUser: async (userId: string, userData: UserUpdate): Promise<User> => {
    const response = await apiClient.patch(`/api/v1/users/${userId}`, userData);
    return response.data;
  },

  // Update user status (admin only)
  updateUserStatus: async (
    userId: string,
    statusData: UserStatusUpdate
  ): Promise<void> => {
    await apiClient.post(`/api/v1/users/${userId}/status`, statusData);
  },

  // Update current user profile
  updateProfile: async (userData: UserUpdate): Promise<User> => {
    const response = await apiClient.patch("/api/v1/users/me", userData);
    return response.data;
  },
};
