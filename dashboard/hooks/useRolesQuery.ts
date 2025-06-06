import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { rolesApi, Role, RoleCreate, RoleUpdate } from "../services/rolesApi";
import toast from "react-hot-toast";

// Query keys
export const roleKeys = {
  all: ["roles"] as const,
  lists: () => [...roleKeys.all, "list"] as const,
  list: (filters: string) => [...roleKeys.lists(), { filters }] as const,
  details: () => [...roleKeys.all, "detail"] as const,
  detail: (id: string) => [...roleKeys.details(), id] as const,
};

// Get all roles
export function useRoles(skip: number = 0, limit: number = 100) {
  return useQuery({
    queryKey: roleKeys.list(`skip=${skip}&limit=${limit}`),
    queryFn: () => rolesApi.getRoles(skip, limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Get role by ID
export function useRole(roleId: string) {
  return useQuery({
    queryKey: roleKeys.detail(roleId),
    queryFn: () => rolesApi.getRole(roleId),
    enabled: !!roleId,
  });
}

// Create role mutation
export function useCreateRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (roleData: RoleCreate) => rolesApi.createRole(roleData),
    onSuccess: (newRole: Role) => {
      // Invalidate and refetch roles list
      queryClient.invalidateQueries({ queryKey: roleKeys.lists() });
      toast.success("Role created successfully");
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || "Failed to create role";
      toast.error(message);
    },
  });
}

// Update role mutation
export function useUpdateRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      roleId,
      roleData,
    }: {
      roleId: string;
      roleData: RoleUpdate;
    }) => rolesApi.updateRole(roleId, roleData),
    onSuccess: (updatedRole: Role) => {
      // Update the role in the cache
      queryClient.setQueryData(roleKeys.detail(updatedRole.id), updatedRole);
      // Invalidate roles list to refresh
      queryClient.invalidateQueries({ queryKey: roleKeys.lists() });
      toast.success("Role updated successfully");
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || "Failed to update role";
      toast.error(message);
    },
  });
}

// Delete role mutation
export function useDeleteRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (roleId: string) => rolesApi.deleteRole(roleId),
    onSuccess: (_: void, roleId: string) => {
      // Remove the role from the cache
      queryClient.removeQueries({ queryKey: roleKeys.detail(roleId) });
      // Invalidate roles list to refresh
      queryClient.invalidateQueries({ queryKey: roleKeys.lists() });
      toast.success("Role deleted successfully");
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || "Failed to delete role";
      toast.error(message);
    },
  });
}
