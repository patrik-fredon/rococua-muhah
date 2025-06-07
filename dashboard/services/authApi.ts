import { apiClient } from "./baseApi";

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    username: string;
    first_name?: string;
    last_name?: string;
    is_active: boolean;
    roles: string[];
  };
}

export interface User {
  id: string;
  email: string;
  username: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  roles: string[];
}

export const authApi = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    return apiClient.post<LoginResponse>("/api/v1/users/login", {
      username,
      password,
    });
  },

  getCurrentUser: async (): Promise<User> => {
    return apiClient.get<User>("/api/v1/users/me");
  },

  logout: async (): Promise<void> => {
    return apiClient.post<void>("/api/v1/users/logout");
  },

  changePassword: async (
    currentPassword: string,
    newPassword: string
  ): Promise<void> => {
    return apiClient.post<void>("/api/v1/users/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },
};

export { apiClient };
