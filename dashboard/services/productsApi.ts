import apiClient from "./authApi";

export interface Product {
  id: string;
  name: string;
  description?: string;
  short_description?: string;
  sku: string;
  price: number;
  cost_price?: number;
  compare_at_price?: number;
  stock_quantity: number;
  track_inventory: boolean;
  allow_backorders: boolean;
  weight?: number;
  dimensions?: string;
  category?: string;
  brand?: string;
  is_active: boolean;
  is_featured: boolean;
  is_digital: boolean;
  slug?: string;
  meta_title?: string;
  meta_description?: string;
  is_in_stock: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductCreate {
  name: string;
  description?: string;
  short_description?: string;
  sku: string;
  price: number;
  cost_price?: number;
  compare_at_price?: number;
  stock_quantity?: number;
  track_inventory?: boolean;
  allow_backorders?: boolean;
  weight?: number;
  dimensions?: string;
  category?: string;
  brand?: string;
  is_active?: boolean;
  is_featured?: boolean;
  is_digital?: boolean;
  slug?: string;
  meta_title?: string;
  meta_description?: string;
}

export interface ProductUpdate {
  name?: string;
  description?: string;
  short_description?: string;
  sku?: string;
  price?: number;
  cost_price?: number;
  compare_at_price?: number;
  stock_quantity?: number;
  track_inventory?: boolean;
  allow_backorders?: boolean;
  weight?: number;
  dimensions?: string;
  category?: string;
  brand?: string;
  is_active?: boolean;
  is_featured?: boolean;
  is_digital?: boolean;
  slug?: string;
  meta_title?: string;
  meta_description?: string;
}

export const productsApi = {
  // Get all products (public)
  getProducts: async (
    skip: number = 0,
    limit: number = 100
  ): Promise<Product[]> => {
    const response = await apiClient.get(
      `/api/v1/products?skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  // Get product by ID (public)
  getProduct: async (productId: string): Promise<Product> => {
    const response = await apiClient.get(`/api/v1/products/${productId}`);
    return response.data;
  },

  // Create new product (admin only)
  createProduct: async (productData: ProductCreate): Promise<Product> => {
    const response = await apiClient.post("/api/v1/products", productData);
    return response.data;
  },

  // Update product (admin only)
  updateProduct: async (
    productId: string,
    productData: ProductUpdate
  ): Promise<Product> => {
    const response = await apiClient.patch(
      `/api/v1/products/${productId}`,
      productData
    );
    return response.data;
  },

  // Delete product (admin only)
  deleteProduct: async (productId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/products/${productId}`);
  },
};
