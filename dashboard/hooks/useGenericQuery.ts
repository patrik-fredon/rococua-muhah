import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
  UseMutationOptions,
} from "@tanstack/react-query";
import toast from "react-hot-toast";
import { CrudApiService } from "../services/baseApi";

/**
 * Generic query keys factory
 */
export function createQueryKeys(entityName: string) {
  return {
    all: [entityName] as const,
    lists: () => [...createQueryKeys(entityName).all, "list"] as const,
    list: (filters: string) =>
      [...createQueryKeys(entityName).lists(), { filters }] as const,
    details: () => [...createQueryKeys(entityName).all, "detail"] as const,
    detail: (id: string) =>
      [...createQueryKeys(entityName).details(), id] as const,
  };
}

/**
 * Generic CRUD hooks factory
 */
export function createCrudHooks<T, TCreate = Partial<T>, TUpdate = Partial<T>>(
  entityName: string,
  service: CrudApiService<T, TCreate, TUpdate>
) {
  const queryKeys = createQueryKeys(entityName);

  return {
    // Query hooks
    useGetAll: (
      params: { skip?: number; limit?: number } = {},
      options?: Omit<UseQueryOptions<T[], Error>, "queryKey" | "queryFn">
    ) => {
      const filterString = `skip=${params.skip || 0}&limit=${
        params.limit || 100
      }`;
      return useQuery({
        queryKey: queryKeys.list(filterString),
        queryFn: () => service.getAll(params),
        staleTime: 5 * 60 * 1000, // 5 minutes
        ...options,
      });
    },

    useGetById: (
      id: string,
      options?: Omit<UseQueryOptions<T, Error>, "queryKey" | "queryFn">
    ) => {
      return useQuery({
        queryKey: queryKeys.detail(id),
        queryFn: () => service.getById(id),
        enabled: !!id,
        ...options,
      });
    },

    useSearch: (
      filters: Record<string, any>,
      params: { skip?: number; limit?: number } = {},
      options?: Omit<UseQueryOptions<T[], Error>, "queryKey" | "queryFn">
    ) => {
      const filterString = JSON.stringify({ ...filters, ...params });
      return useQuery({
        queryKey: queryKeys.list(filterString),
        queryFn: () => service.search(filters, params),
        staleTime: 5 * 60 * 1000,
        ...options,
      });
    },

    useCount: (
      filters?: Record<string, any>,
      options?: Omit<UseQueryOptions<number, Error>, "queryKey" | "queryFn">
    ) => {
      const filterString = JSON.stringify(filters || {});
      return useQuery({
        queryKey: [...queryKeys.all, "count", filterString],
        queryFn: () => service.count(filters),
        staleTime: 5 * 60 * 1000,
        ...options,
      });
    },

    // Mutation hooks
    useCreate: (
      options?: Omit<UseMutationOptions<T, Error, TCreate>, "mutationFn">
    ) => {
      const queryClient = useQueryClient();

      return useMutation({
        mutationFn: (data: TCreate) => service.create(data),
        onSuccess: (newItem: T) => {
          // Invalidate and refetch lists
          queryClient.invalidateQueries({ queryKey: queryKeys.lists() });
          toast.success(`${entityName} created successfully`);
        },
        onError: (error: any) => {
          const message =
            error.response?.data?.detail || `Failed to create ${entityName}`;
          toast.error(message);
        },
        ...options,
      });
    },

    useUpdate: (
      options?: Omit<
        UseMutationOptions<T, Error, { id: string; data: TUpdate }>,
        "mutationFn"
      >
    ) => {
      const queryClient = useQueryClient();

      return useMutation({
        mutationFn: ({ id, data }: { id: string; data: TUpdate }) =>
          service.update(id, data),
        onSuccess: (updatedItem: T, variables) => {
          // Update the item in the cache
          queryClient.setQueryData(queryKeys.detail(variables.id), updatedItem);
          // Invalidate lists to refresh
          queryClient.invalidateQueries({ queryKey: queryKeys.lists() });
          toast.success(`${entityName} updated successfully`);
        },
        onError: (error: any) => {
          const message =
            error.response?.data?.detail || `Failed to update ${entityName}`;
          toast.error(message);
        },
        ...options,
      });
    },

    useDelete: (
      options?: Omit<UseMutationOptions<void, Error, string>, "mutationFn">
    ) => {
      const queryClient = useQueryClient();

      return useMutation({
        mutationFn: (id: string) => service.delete(id),
        onSuccess: (_: void, id: string) => {
          // Remove the item from the cache
          queryClient.removeQueries({ queryKey: queryKeys.detail(id) });
          // Invalidate lists to refresh
          queryClient.invalidateQueries({ queryKey: queryKeys.lists() });
          toast.success(`${entityName} deleted successfully`);
        },
        onError: (error: any) => {
          const message =
            error.response?.data?.detail || `Failed to delete ${entityName}`;
          toast.error(message);
        },
        ...options,
      });
    },

    // Utility hooks
    useInvalidateAll: () => {
      const queryClient = useQueryClient();
      return () => queryClient.invalidateQueries({ queryKey: queryKeys.all });
    },

    useInvalidateLists: () => {
      const queryClient = useQueryClient();
      return () =>
        queryClient.invalidateQueries({ queryKey: queryKeys.lists() });
    },

    usePrefetchDetail: () => {
      const queryClient = useQueryClient();
      return (id: string) => {
        queryClient.prefetchQuery({
          queryKey: queryKeys.detail(id),
          queryFn: () => service.getById(id),
          staleTime: 5 * 60 * 1000,
        });
      };
    },

    // Query keys for external use
    queryKeys,
  };
}

/**
 * Hook for optimistic updates
 */
export function useOptimisticUpdate<T>(
  queryKeys: ReturnType<typeof createQueryKeys>,
  entityName: string
) {
  const queryClient = useQueryClient();

  const optimisticUpdate = (
    id: string,
    updateFn: (oldData: T) => T,
    onError?: (error: any, context: any) => void
  ) => {
    return {
      onMutate: async (variables: any) => {
        // Cancel outgoing refetches
        await queryClient.cancelQueries({ queryKey: queryKeys.detail(id) });

        // Snapshot the previous value
        const previousData = queryClient.getQueryData<T>(queryKeys.detail(id));

        // Optimistically update the cache
        if (previousData) {
          queryClient.setQueryData(
            queryKeys.detail(id),
            updateFn(previousData)
          );
        }

        return { previousData };
      },
      onError: (error: any, variables: any, context: any) => {
        // Rollback on error
        if (context?.previousData) {
          queryClient.setQueryData(queryKeys.detail(id), context.previousData);
        }

        const message =
          error.response?.data?.detail || `Failed to update ${entityName}`;
        toast.error(message);

        onError?.(error, context);
      },
      onSettled: () => {
        // Refetch to ensure consistency
        queryClient.invalidateQueries({ queryKey: queryKeys.detail(id) });
      },
    };
  };

  return { optimisticUpdate };
}
