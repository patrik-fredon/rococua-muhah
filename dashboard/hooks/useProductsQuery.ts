import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  productsApi,
  Product,
  ProductCreate,
  ProductUpdate,
} from "../services/productsApi";
import toast from "react-hot-toast";

// Query keys
export const productKeys = {
  all: ["products"] as const,
  lists: () => [...productKeys.all, "list"] as const,
  list: (filters: string) => [...productKeys.lists(), { filters }] as const,
  details: () => [...productKeys.all, "detail"] as const,
  detail: (id: string) => [...productKeys.details(), id] as const,
};

// Get all products
export function useProducts(skip: number = 0, limit: number = 100) {
  return useQuery({
    queryKey: productKeys.list(`skip=${skip}&limit=${limit}`),
    queryFn: () => productsApi.getProducts(skip, limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Get product by ID
export function useProduct(productId: string) {
  return useQuery({
    queryKey: productKeys.detail(productId),
    queryFn: () => productsApi.getProduct(productId),
    enabled: !!productId,
  });
}

// Create product mutation
export function useCreateProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (productData: ProductCreate) =>
      productsApi.createProduct(productData),
    onSuccess: (newProduct: Product) => {
      // Invalidate and refetch products list
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
      toast.success("Product created successfully");
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.detail || "Failed to create product";
      toast.error(message);
    },
  });
}

// Update product mutation
export function useUpdateProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      productId,
      productData,
    }: {
      productId: string;
      productData: ProductUpdate;
    }) => productsApi.updateProduct(productId, productData),
    onSuccess: (updatedProduct: Product) => {
      // Update the product in the cache
      queryClient.setQueryData(
        productKeys.detail(updatedProduct.id),
        updatedProduct
      );
      // Invalidate products list to refresh
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
      toast.success("Product updated successfully");
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.detail || "Failed to update product";
      toast.error(message);
    },
  });
}

// Delete product mutation
export function useDeleteProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (productId: string) => productsApi.deleteProduct(productId),
    onSuccess: (_: void, productId: string) => {
      // Remove the product from the cache
      queryClient.removeQueries({ queryKey: productKeys.detail(productId) });
      // Invalidate products list to refresh
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
      toast.success("Product deleted successfully");
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.detail || "Failed to delete product";
      toast.error(message);
    },
  });
}
