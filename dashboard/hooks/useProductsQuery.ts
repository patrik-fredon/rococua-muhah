import { createCrudHooks } from "./useGenericQuery";
import {
  productsService,
  Product,
  ProductCreate,
  ProductUpdate,
} from "../services/productsApi";

// Create products CRUD hooks using the generic factory
const productHooks = createCrudHooks<Product, ProductCreate, ProductUpdate>(
  "Product",
  productsService
);

// Export all hooks with product-specific names
export const useProducts = productHooks.useGetAll;
export const useProduct = productHooks.useGetById;
export const useCreateProduct = productHooks.useCreate;
export const useUpdateProduct = productHooks.useUpdate;
export const useDeleteProduct = productHooks.useDelete;

// Export additional product-specific hooks
export const useProductSearch = productHooks.useSearch;
export const useProductCount = productHooks.useCount;
export const useInvalidateProducts = productHooks.useInvalidateAll;
export const useInvalidateProductLists = productHooks.useInvalidateLists;
export const usePrefetchProduct = productHooks.usePrefetchDetail;

// Export query keys for external use
export const productKeys = productHooks.queryKeys;

// Product-specific hooks for common queries
export function useProductsByCategory(
  category: string,
  skip: number = 0,
  limit: number = 100
) {
  return productHooks.useSearch({ category }, { skip, limit });
}

export function useProductsByBrand(
  brand: string,
  skip: number = 0,
  limit: number = 100
) {
  return productHooks.useSearch({ brand }, { skip, limit });
}

export function useFeaturedProducts(skip: number = 0, limit: number = 100) {
  return productHooks.useSearch({ is_featured: true }, { skip, limit });
}

export function useInStockProducts(skip: number = 0, limit: number = 100) {
  return productHooks.useSearch({ is_in_stock: true }, { skip, limit });
}

// Legacy wrapper functions for backward compatibility
export function useUpdateProductLegacy() {
  const updateProduct = useUpdateProduct();

  return {
    ...updateProduct,
    mutate: ({
      productId,
      productData,
    }: {
      productId: string;
      productData: ProductUpdate;
    }) => updateProduct.mutate({ id: productId, data: productData }),
    mutateAsync: ({
      productId,
      productData,
    }: {
      productId: string;
      productData: ProductUpdate;
    }) => updateProduct.mutateAsync({ id: productId, data: productData }),
  };
}
