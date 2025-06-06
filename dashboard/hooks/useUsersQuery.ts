import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  usersApi,
  User,
  UserCreate,
  UserUpdate,
  UserStatusUpdate,
} from "@/services/usersApi";
import toast from "react-hot-toast";

// Query keys
export const userKeys = {
  all: ["users"] as const,
  lists: () => [...userKeys.all, "list"] as const,
  list: (filters: string) => [...userKeys.lists(), { filters }] as const,
  details: () => [...userKeys.all, "detail"] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
};

// Get all users
export function useUsers(skip: number = 0, limit: number = 100) {
  return useQuery({
    queryKey: userKeys.list(`skip=${skip}&limit=${limit}`),
    queryFn: () => usersApi.getUsers(skip, limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Get user by ID
export function useUser(userId: string) {
  return useQuery({
    queryKey: userKeys.detail(userId),
    queryFn: () => usersApi.getUser(userId),
    enabled: !!userId,
  });
}

// Create user mutation
export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userData: UserCreate) => usersApi.createUser(userData),
    onSuccess: (newUser: User) => {
      // Invalidate and refetch users list
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
      toast.success("User created successfully");
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || "Failed to create user";
      toast.error(message);
    },
  });
}

// Update user mutation
export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      userId,
      userData,
    }: {
      userId: string;
      userData: UserUpdate;
    }) => usersApi.updateUser(userId, userData),
    onSuccess: (updatedUser: User) => {
      // Update the user in the cache
      queryClient.setQueryData(userKeys.detail(updatedUser.id), updatedUser);
      // Invalidate users list to refresh
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
      toast.success("User updated successfully");
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || "Failed to update user";
      toast.error(message);
    },
  });
}

// Update user status mutation
export function useUpdateUserStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      userId,
      statusData,
    }: {
      userId: string;
      statusData: UserStatusUpdate;
    }) => usersApi.updateUserStatus(userId, statusData),
    onSuccess: (
      _: void,
      { userId }: { userId: string; statusData: UserStatusUpdate }
    ) => {
      // Invalidate user detail and list queries
      queryClient.invalidateQueries({ queryKey: userKeys.detail(userId) });
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
      toast.success("User status updated successfully");
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.detail || "Failed to update user status";
      toast.error(message);
    },
  });
}

// Update profile mutation (for current user)
export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userData: UserUpdate) => usersApi.updateProfile(userData),
    onSuccess: (updatedUser: User) => {
      // Update current user data in auth context if needed
      toast.success("Profile updated successfully");
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.detail || "Failed to update profile";
      toast.error(message);
    },
  });
}
