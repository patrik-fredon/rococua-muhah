import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";
import Cookies from "js-cookie";
import toast from "react-hot-toast";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Generic API client with authentication and error handling
 */
class BaseApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config: any) => {
        const token = Cookies.get("access_token");
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error: any) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response: any) => response,
      (error: any) => {
        if (error.response?.status === 401) {
          Cookies.remove("access_token");
          window.location.href = "/login";
        }

        // Show error toast for API errors
        const message = error.response?.data?.detail || "An error occurred";
        toast.error(message);

        return Promise.reject(error);
      }
    );
  }

  /**
   * GET request
   */
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get(url, config);
    return response.data;
  }

  /**
   * POST request
   */
  async post<T, D = any>(
    url: string,
    data?: D,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(
      url,
      data,
      config
    );
    return response.data;
  }

  /**
   * PUT request
   */
  async put<T, D = any>(
    url: string,
    data?: D,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put(url, data, config);
    return response.data;
  }

  /**
   * PATCH request
   */
  async patch<T, D = any>(
    url: string,
    data?: D,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.client.patch(
      url,
      data,
      config
    );
    return response.data;
  }

  /**
   * DELETE request
   */
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.delete(url, config);
    return response.data;
  }

  /**
   * Get raw axios instance for custom operations
   */
  getClient(): AxiosInstance {
    return this.client;
  }
}

/**
 * Generic CRUD API service for any entity
 */
export class CrudApiService<T, TCreate = Partial<T>, TUpdate = Partial<T>> {
  constructor(private client: BaseApiClient, private endpoint: string) {}

  /**
   * Get all items with pagination
   */
  async getAll(params: { skip?: number; limit?: number } = {}): Promise<T[]> {
    const queryParams = new URLSearchParams();
    if (params.skip !== undefined)
      queryParams.set("skip", params.skip.toString());
    if (params.limit !== undefined)
      queryParams.set("limit", params.limit.toString());

    const url = queryParams.toString()
      ? `${this.endpoint}?${queryParams}`
      : this.endpoint;
    return this.client.get<T[]>(url);
  }

  /**
   * Get single item by ID
   */
  async getById(id: string): Promise<T> {
    return this.client.get<T>(`${this.endpoint}/${id}`);
  }

  /**
   * Create new item
   */
  async create(data: TCreate): Promise<T> {
    return this.client.post<T, TCreate>(this.endpoint, data);
  }

  /**
   * Update existing item
   */
  async update(id: string, data: TUpdate): Promise<T> {
    return this.client.patch<T, TUpdate>(`${this.endpoint}/${id}`, data);
  }

  /**
   * Delete item
   */
  async delete(id: string): Promise<void> {
    return this.client.delete<void>(`${this.endpoint}/${id}`);
  }

  /**
   * Get count of items
   */
  async count(filters?: Record<string, any>): Promise<number> {
    const queryParams = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.set(key, value.toString());
        }
      });
    }

    const url = queryParams.toString()
      ? `${this.endpoint}/count?${queryParams}`
      : `${this.endpoint}/count`;
    return this.client.get<number>(url);
  }

  /**
   * Search items with filters
   */
  async search(
    filters: Record<string, any>,
    params: { skip?: number; limit?: number } = {}
  ): Promise<T[]> {
    const queryParams = new URLSearchParams();

    // Add pagination params
    if (params.skip !== undefined)
      queryParams.set("skip", params.skip.toString());
    if (params.limit !== undefined)
      queryParams.set("limit", params.limit.toString());

    // Add filter params
    Object.entries(filters).forEach(([key, value]: [string, any]) => {
      if (value !== undefined && value !== null) {
        queryParams.set(key, value.toString());
      }
    });

    const url = `${this.endpoint}/search?${queryParams}`;
    return this.client.get<T[]>(url);
  }
}

// Export singleton instance
export const apiClient = new BaseApiClient();

// Helper function to create CRUD service for any entity
export function createCrudService<
  T,
  TCreate = Partial<T>,
  TUpdate = Partial<T>
>(endpoint: string): CrudApiService<T, TCreate, TUpdate> {
  return new CrudApiService<T, TCreate, TUpdate>(apiClient, endpoint);
}

export default apiClient;
