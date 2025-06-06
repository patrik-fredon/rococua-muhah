import apiClient from "./authApi";

export interface Role {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RoleCreate {
  name: string;
  display_name: string;
  description?: string;
  is_active?: boolean;
}

export interface RoleUpdate {
  name?: string;
  display_name?: string;
  description?: string;
  is_active?: boolean;
}

export const rolesApi = {
  // Get all roles (admin only)
  getRoles: async (skip: number = 0, limit: number = 100): Promise<Role[]> => {
    const response = await apiClient.get(
      `/api/v1/roles?skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  // Get role by ID (admin only)
  getRole: async (roleId: string): Promise<Role> => {
    const response = await apiClient.get(`/api/v1/roles/${roleId}`);
    return response.data;
  },

  // Create new role (admin only)
  createRole: async (roleData: RoleCreate): Promise<Role> => {
    const response = await apiClient.post("/api/v1/roles", roleData);
    return response.data;
  },

  // Update role (admin only)
  updateRole: async (roleId: string, roleData: RoleUpdate): Promise<Role> => {
    const response = await apiClient.patch(`/api/v1/roles/${roleId}`, roleData);
    return response.data;
  },

  // Delete role (admin only)
  deleteRole: async (roleId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/roles/${roleId}`);
  },
};
