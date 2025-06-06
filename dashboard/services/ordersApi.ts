import apiClient from "./authApi";

export interface OrderItem {
  id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  product_name: string;
  product_sku: string;
  product_description?: string;
}

export interface Order {
  id: string;
  order_number: string;
  user_id: string;
  status: string;
  payment_status: string;
  subtotal: number;
  tax_amount: number;
  shipping_amount: number;
  discount_amount: number;
  total_amount: number;
  customer_email: string;
  customer_phone?: string;
  shipping_first_name: string;
  shipping_last_name: string;
  shipping_company?: string;
  shipping_address_line1: string;
  shipping_address_line2?: string;
  shipping_city: string;
  shipping_state?: string;
  shipping_postal_code: string;
  shipping_country: string;
  billing_first_name: string;
  billing_last_name: string;
  billing_company?: string;
  billing_address_line1: string;
  billing_address_line2?: string;
  billing_city: string;
  billing_state?: string;
  billing_postal_code: string;
  billing_country: string;
  notes?: string;
  internal_notes?: string;
  created_at: string;
  updated_at: string;
  shipped_at?: string;
  delivered_at?: string;
  order_items: OrderItem[];
  user?: {
    id: string;
    email: string;
    username: string;
    first_name?: string;
    last_name?: string;
  };
}

export interface OrderSummary {
  id: string;
  order_number: string;
  status: string;
  payment_status: string;
  total_amount: number;
  created_at: string;
  order_items: {
    id: string;
    product_name: string;
    quantity: number;
  }[];
}

export interface OrderItemCreate {
  product_id: string;
  quantity: number;
  unit_price?: number;
  product_name: string;
  product_sku: string;
  product_description?: string;
}

export interface OrderCreate {
  customer_email: string;
  customer_phone?: string;
  shipping_first_name: string;
  shipping_last_name: string;
  shipping_company?: string;
  shipping_address_line1: string;
  shipping_address_line2?: string;
  shipping_city: string;
  shipping_state?: string;
  shipping_postal_code: string;
  shipping_country: string;
  billing_first_name: string;
  billing_last_name: string;
  billing_company?: string;
  billing_address_line1: string;
  billing_address_line2?: string;
  billing_city: string;
  billing_state?: string;
  billing_postal_code: string;
  billing_country: string;
  notes?: string;
  order_items: OrderItemCreate[];
}

export interface OrderUpdate {
  status?: string;
  payment_status?: string;
  customer_email?: string;
  customer_phone?: string;
  shipping_first_name?: string;
  shipping_last_name?: string;
  shipping_company?: string;
  shipping_address_line1?: string;
  shipping_address_line2?: string;
  shipping_city?: string;
  shipping_state?: string;
  shipping_postal_code?: string;
  shipping_country?: string;
  billing_first_name?: string;
  billing_last_name?: string;
  billing_company?: string;
  billing_address_line1?: string;
  billing_address_line2?: string;
  billing_city?: string;
  billing_state?: string;
  billing_postal_code?: string;
  billing_country?: string;
  notes?: string;
  internal_notes?: string;
}

export const ordersApi = {
  // Get user's orders
  getUserOrders: async (
    skip: number = 0,
    limit: number = 100
  ): Promise<OrderSummary[]> => {
    const response = await apiClient.get(
      `/api/v1/orders?skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  // Get all orders (admin only)
  getAllOrders: async (
    skip: number = 0,
    limit: number = 100
  ): Promise<OrderSummary[]> => {
    const response = await apiClient.get(
      `/api/v1/orders/all?skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  // Get order by ID (user's own order)
  getOrder: async (orderId: string): Promise<Order> => {
    const response = await apiClient.get(`/api/v1/orders/${orderId}`);
    return response.data;
  },

  // Get any order by ID (admin only)
  getAnyOrder: async (orderId: string): Promise<Order> => {
    const response = await apiClient.get(`/api/v1/orders/admin/${orderId}`);
    return response.data;
  },

  // Create new order
  createOrder: async (orderData: OrderCreate): Promise<Order> => {
    const response = await apiClient.post("/api/v1/orders", orderData);
    return response.data;
  },

  // Update order (user's own order)
  updateOrder: async (
    orderId: string,
    orderData: OrderUpdate
  ): Promise<Order> => {
    const response = await apiClient.patch(
      `/api/v1/orders/${orderId}`,
      orderData
    );
    return response.data;
  },

  // Update any order (admin only)
  updateAnyOrder: async (
    orderId: string,
    orderData: OrderUpdate
  ): Promise<Order> => {
    const response = await apiClient.patch(
      `/api/v1/orders/admin/${orderId}`,
      orderData
    );
    return response.data;
  },

  // Add item to order
  addOrderItem: async (
    orderId: string,
    itemData: OrderItemCreate
  ): Promise<OrderItem> => {
    const response = await apiClient.post(
      `/api/v1/orders/${orderId}/items`,
      itemData
    );
    return response.data;
  },

  // Update order item
  updateOrderItem: async (
    orderId: string,
    itemId: string,
    itemData: Partial<OrderItemCreate>
  ): Promise<OrderItem> => {
    const response = await apiClient.patch(
      `/api/v1/orders/${orderId}/items/${itemId}`,
      itemData
    );
    return response.data;
  },

  // Remove order item
  removeOrderItem: async (orderId: string, itemId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/orders/${orderId}/items/${itemId}`);
  },
};
