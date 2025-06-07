import { createCrudService } from "./baseApi";

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

// Create products CRUD service using the generic base
const productsService = createCrudService<
  Product,
  ProductCreate,
  ProductUpdate
>("/api/v1/products");

export const productsApi = {
  // Get all products (public)
  getProducts: async (
    skip: number = 0,
    limit: number = 100
  ): Promise<Product[]> => {
    return productsService.getAll({ skip, limit });
  },

  // Get product by ID (public)
  getProduct: async (productId: string): Promise<Product> => {
    return productsService.getById(productId);
  },

  // Create new product (admin only)
  createProduct: async (productData: ProductCreate): Promise<Product> => {
    return productsService.create(productData);
  },

  // Update product (admin only)
  updateProduct: async (
    productId: string,
    productData: ProductUpdate
  ): Promise<Product> => {
    return productsService.update(productId, productData);
  },

  // Delete product (admin only)
  deleteProduct: async (productId: string): Promise<void> => {
    return productsService.delete(productId);
  },

  // Additional product-specific methods
  getProductsByCategory: async (
    category: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<Product[]> => {
    return productsService.search({ category }, { skip, limit });
  },

  getProductsByBrand: async (
    brand: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<Product[]> => {
    return productsService.search({ brand }, { skip, limit });
  },

  getFeaturedProducts: async (
    skip: number = 0,
    limit: number = 100
  ): Promise<Product[]> => {
    return productsService.search({ is_featured: true }, { skip, limit });
  },

  getInStockProducts: async (
    skip: number = 0,
    limit: number = 100
  ): Promise<Product[]> => {
    return productsService.search({ is_in_stock: true }, { skip, limit });
  },
};

// Export the service for direct access if needed
export { productsService };
