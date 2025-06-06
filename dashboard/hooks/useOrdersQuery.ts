import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ordersApi,
  Order,
  OrderSummary,
  OrderCreate,
  OrderUpdate,
  OrderItemCreate,
} from "../services/ordersApi";
import toast from "react-hot-toast";

// Query keys
export const orderKeys = {
  all: ["orders"] as const,
  lists: () => [...orderKeys.all, "list"] as const,
  list: (filters: string) => [...orderKeys.lists(), { filters }] as const,
  details: () => [...orderKeys.all, "detail"] as const,
  detail: (id: string) => [...orderKeys.details(), id] as const,
  userOrders: (userId: string) => [...orderKeys.all, "user", userId] as const,
};

// Get user's orders
export function useUserOrders(skip: number = 0, limit: number = 100) {
  return useQuery({
    queryKey: orderKeys.list(`user-skip=${skip}&limit=${limit}`),
    queryFn: () => ordersApi.getUserOrders(skip, limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Get all orders (admin only)
export function useAllOrders(skip: number = 0, limit: number = 100) {
  return useQuery({
    queryKey: orderKeys.list(`all-skip=${skip}&limit=${limit}`),
    queryFn: () => ordersApi.getAllOrders(skip, limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Get order by ID
export function useOrder(orderId: string, isAdmin: boolean = false) {
  return useQuery({
    queryKey: orderKeys.detail(orderId),
    queryFn: () =>
      isAdmin ? ordersApi.getAnyOrder(orderId) : ordersApi.getOrder(orderId),
    enabled: !!orderId,
  });
}

// Create order mutation
export function useCreateOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (orderData: OrderCreate) => ordersApi.createOrder(orderData),
    onSuccess: (newOrder: Order) => {
      // Invalidate and refetch orders list
      queryClient.invalidateQueries({ queryKey: orderKeys.lists() });
      toast.success("Order created successfully");
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || "Failed to create order";
      toast.error(message);
    },
  });
}

// Update order mutation
export function useUpdateOrder(isAdmin: boolean = false) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      orderId,
      orderData,
    }: {
      orderId: string;
      orderData: OrderUpdate;
    }) =>
      isAdmin
        ? ordersApi.updateAnyOrder(orderId, orderData)
        : ordersApi.updateOrder(orderId, orderData),
    onSuccess: (updatedOrder: Order) => {
      // Update the order in the cache
      queryClient.setQueryData(orderKeys.detail(updatedOrder.id), updatedOrder);
      // Invalidate orders list to refresh
      queryClient.invalidateQueries({ queryKey: orderKeys.lists() });
      toast.success("Order updated successfully");
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || "Failed to update order";
      toast.error(message);
    },
  });
}

// Add order item mutation
export function useAddOrderItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      orderId,
      itemData,
    }: {
      orderId: string;
      itemData: OrderItemCreate;
    }) => ordersApi.addOrderItem(orderId, itemData),
    onSuccess: (_, { orderId }) => {
      // Invalidate order detail to refresh with new item
      queryClient.invalidateQueries({ queryKey: orderKeys.detail(orderId) });
      toast.success("Item added to order");
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.detail || "Failed to add item to order";
      toast.error(message);
    },
  });
}

// Update order item mutation
export function useUpdateOrderItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      orderId,
      itemId,
      itemData,
    }: {
      orderId: string;
      itemId: string;
      itemData: Partial<OrderItemCreate>;
    }) => ordersApi.updateOrderItem(orderId, itemId, itemData),
    onSuccess: (_, { orderId }) => {
      // Invalidate order detail to refresh with updated item
      queryClient.invalidateQueries({ queryKey: orderKeys.detail(orderId) });
      toast.success("Order item updated");
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.detail || "Failed to update order item";
      toast.error(message);
    },
  });
}

// Remove order item mutation
export function useRemoveOrderItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ orderId, itemId }: { orderId: string; itemId: string }) =>
      ordersApi.removeOrderItem(orderId, itemId),
    onSuccess: (_, { orderId }) => {
      // Invalidate order detail to refresh without removed item
      queryClient.invalidateQueries({ queryKey: orderKeys.detail(orderId) });
      toast.success("Item removed from order");
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.detail || "Failed to remove item from order";
      toast.error(message);
    },
  });
}
