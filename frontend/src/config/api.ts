import axios, { type AxiosInstance } from 'axios';
import { auth } from './firebase';
import { config } from './app';

// Importar tipos de usuarios
import type {
  Role,
  RoleType
} from '../types/users/role.types';
import type {
  User,
  UserWithRoles,
  UserCreateData,
  UserUpdateData,
  Customer,
  CustomerCreate
} from '../types/users/user.types';

// Importar tipos de productos
import type {
  Color,
  Category,
  Size,
  Product,
  ProductImage,
  ProductVariant,
  ProductCreateData,
  ProductUpdateData
} from '../types/products/product.types';

// Importar tipos de stock
import type {
  StockCheckItem,
  StockCheckResponse
} from '../types/stock';

// Importar tipos de órdenes
import type {
  Order,
  OrderItem,
  OrderItemCreate
} from '../types/orders/order.types';

// User interfaces moved to types/users/user.types.ts
// Configuración base del cliente HTTP
const createApiClient = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: config.backendUrl,
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true,
    timeout: 30000, // 30 segundos de timeout
  });

  return instance;
};

const apiClient = createApiClient();

// Interceptor para manejar errores comunes
const setupResponseInterceptors = (client: AxiosInstance) => {
  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      // Si el error es 401 (no autorizado) y no es una solicitud de refresco
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          // Intentar refrescar el token
          const user = auth.currentUser;
          if (user) {
            const token = await user.getIdToken(true);
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          }
        } catch (refreshError) {
          // Si falla el refresh, redirigir al login
          if (window.location.pathname !== '/auth') {
            window.location.href = '/auth?session_expired=true';
          }
          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    }
  );
};

setupResponseInterceptors(apiClient);

// Interceptor para agregar el token de autenticación a cada petición
apiClient.interceptors.request.use(
  async (config) => {
    try {
      const user = auth.currentUser;
      if (user) {
        const token = await user.getIdToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
    } catch (error) {
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
// Interceptor para manejar errores de respuesta
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;

      // Manejar respuestas HTML inesperadas
      if (typeof data === 'string' && data.startsWith('<!DOCTYPE html>')) {

        const errorHtml = new Error(`El servidor devolvió una respuesta HTML. Verifica si el backend está en ejecución en ${config.backendUrl}`);
        (errorHtml as any).isHtmlResponse = true;
        return Promise.reject(errorHtml);
      }

      // Registrar errores (excepto 401 que ya se maneja en el interceptor de respuesta)
      if (status !== 401) {
      }
    } else if (error.request) {
      // No se recibió respuesta del servidor
    } else {
      // Error al configurar la petición
    }

    return Promise.reject(error);
  }
);

// API functions for authentication
export const authApi = {
  // Login with email and password
  async login(email: string, password: string): Promise<{ user: User; token: string }> {
    const response = await apiClient.post('/auth/login', { email, password });
    return response.data;
  },

  // Register new user
  async register(userData: UserCreateData): Promise<User> {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  // Get current user info
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('/users/me');
    return response.data;
  },

  // Update current user
  async updateCurrentUser(updates: Partial<UserUpdateData>): Promise<User> {
    const response = await apiClient.patch('/users/me', updates);
    return response.data;
  },

  // Request password reset
  async requestPasswordReset(email: string): Promise<void> {
    await apiClient.post('/auth/forgot-password', { email });
  },

  // Reset password with token
  async resetPassword(token: string, newPassword: string): Promise<void> {
    await apiClient.post('/auth/reset-password', { token, newPassword });
  },

  // Verify email with token
  async verifyEmail(token: string): Promise<void> {
    await apiClient.post('/auth/verify-email', { token });
  },

  // Logout
  async logout(): Promise<void> {
    // Clear any stored tokens or session data
    localStorage.removeItem('firebase_jwt_token');
    // Call backend logout if needed
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
    }
  },
};

// API functions for users
export const usersApi = {
  // Get all users (admin only)
  async getAllUsers(): Promise<UserWithRoles[]> {
    const response = await apiClient.get('/users/');
    return response.data;
  },

  // Get user by ID
  async getUserById(id: number): Promise<UserWithRoles> {
    const response = await apiClient.get(`/users/${id}`);
    return response.data;
  },

  // Create new user (admin only)
  async createUser(userData: UserCreateData): Promise<User> {
    const response = await apiClient.post('/users', userData);
    return response.data;
  },

  // Update user (admin only)
  async updateUser(id: number, updates: Partial<UserUpdateData>): Promise<User> {
    const response = await apiClient.patch(`/users/${id}`, updates);
    return response.data;
  },

  // Delete user (admin only)
  async deleteUser(id: number): Promise<void> {
    await apiClient.delete(`/users/${id}`);
  },

  // Get current user roles
  async getMyRoles(): Promise<Role[]> {
    const response = await apiClient.get('/me/roles');
    return response.data;
  },

  // Assign role to user (admin only)
  async assignRole(userId: number, roleId: number): Promise<void> {
    await apiClient.post(`/users/${userId}/roles`, { roleId });
  },

  // Remove role from user (admin only)
  async removeRole(userId: number, roleId: number): Promise<void> {
    await apiClient.delete(`/users/${userId}/roles/${roleId}`);
  },

  // Debug endpoint to check user authentication and permissions
  async getUserDebugInfo(): Promise<any> {
    const response = await apiClient.get('/users/debug');
    return response.data;
  },
};

// API functions for roles
export const rolesApi = {
  // Get all roles
  async getAllRoles(): Promise<Role[]> {
    const response = await apiClient.get('/roles/');
    return response.data;
  },

  // Get role by ID
  async getRole(id: number): Promise<Role> {
    const response = await apiClient.get(`/roles/${id}`);
    return response.data;
  },

  // Create role
  async createRole(roleData: { name: RoleType; description?: string }): Promise<Role> {
    const response = await apiClient.post('/roles', roleData);
    return response.data;
  },

  // Update role
  async updateRole(id: number, updates: Partial<Role>): Promise<Role> {
    const response = await apiClient.patch(`/roles/${id}`, updates);
    return response.data;
  },

  // Delete role
  async deleteRole(id: number): Promise<void> {
    await apiClient.delete(`/roles/${id}`);
  },

  // Get roles for current user
  async getMyRoles(): Promise<Role[]> {
    const response = await apiClient.get('/roles/me/roles');
    return response.data;
  },

  // Get users with specific role
  async getUsersWithRole(roleId: number): Promise<User[]> {
    const response = await apiClient.get(`/roles/${roleId}/users`);
    return response.data;
  },

  // Assign role to user (admin only)
  async assignRole(userId: number, roleId: number): Promise<void> {
    await apiClient.post(`/users/${userId}/roles`, { roleId });
  },

  // Remove role from user (admin only)  
  async removeRole(userId: number, roleId: number): Promise<void> {
    await apiClient.delete(`/users/${userId}/roles/${roleId}`);
  },

  // Get specific user's roles (for role management)
  async getUserRoles(userId: number): Promise<Role[]> {
    const response = await apiClient.get(`/users/${userId}/roles`);
    return response.data;
  }
};

// API functions for master data (colors, categories, sizes)
export const masterDataApi = {
  // Get all colors
  async getColors(): Promise<Color[]> {
    const response = await apiClient.get('/colors');
    return response.data;
  },

  // Get all categories
  async getCategories(): Promise<Category[]> {
    const response = await apiClient.get('/categories');
    return response.data;
  },

  // Get categories that have products with stock (for navbar)
  async getCategoriesWithStock(): Promise<Category[]> {
    const response = await apiClient.get('/categories/with-stock');
    return response.data;
  },

  // Get all sizes
  async getSizes(): Promise<Size[]> {
    const response = await apiClient.get('/sizes');
    return response.data;
  }
};

// API functions for payments
export const paymentsApi = {
  // Create MercadoPago preference for an order
  async createPreference(orderId: number): Promise<any> {
    const response = await apiClient.post('/payments/create-preference', null, {
      params: { order_id: orderId }
    });
    return response.data;
  },

  // Get payment status for an order
  async getPaymentStatus(orderId: number): Promise<any> {
    const response = await apiClient.get(`/payments/status/${orderId}`);
    return response.data;
  }
};

// API functions for orders
export const ordersApi = {
  // Create new order
  async createOrder(orderData: any): Promise<any> {
    const response = await apiClient.post('/orders/', orderData);
    return response.data;
  },

  // Get all orders
  async getOrders(): Promise<any[]> {
    const response = await apiClient.get('/orders/');
    return response.data;
  },

  // Get all orders with customer info (for admin)
  async getOrdersWithCustomerInfo(): Promise<any[]> {
    const response = await apiClient.get('/orders/admin');
    return response.data;
  },

  // Get order by ID
  async getOrder(id: number): Promise<any> {
    const response = await apiClient.get(`/orders/${id}`);
    return response.data;
  },

  // Update order
  async updateOrder(id: number, updates: any): Promise<any> {
    const response = await apiClient.put(`/orders/${id}`, updates);
    return response.data;
  },

  // Delete order
  async deleteOrder(id: number): Promise<void> {
    await apiClient.delete(`/orders/${id}`);
  },

  // Get orders for a specific customer
  async getCustomerOrders(customerId: number): Promise<any[]> {
    const response = await apiClient.get(`/orders/customer/${customerId}`);
    return response.data;
  },

  // Get orders for the authenticated user
  async getMyOrders(): Promise<any[]> {
    const response = await apiClient.get('/orders/my-orders');
    return response.data;
  },

  // Admin functions
  // Get orders with filters for admin panel
  async getOrdersWithFilters(filters: any): Promise<any[]> {
    const response = await apiClient.get('/orders/admin/filtered', { params: filters });
    return response.data;
  },

  // Get admin statistics
  async getAdminStats(): Promise<any> {
    const response = await apiClient.get('/orders/admin/stats');
    return response.data;
  },

  // Verify bank transfer
  async verifyTransfer(orderId: number, verified: boolean, adminNotes: string): Promise<any> {
    const response = await apiClient.post(`/admin/verify-transfer/${orderId}`, {
      verified,
      admin_notes: adminNotes
    });
    return response.data;
  },

  // Schedule delivery for cash orders
  async scheduleDelivery(orderId: number, scheduledDate: Date, timeSlot: string, notes: string): Promise<any> {
    const response = await apiClient.post(`/orders/${orderId}/schedule-delivery`, {
      scheduled_date: scheduledDate.toISOString(),
      time_slot: timeSlot,
      notes
    });
    return response.data;
  },

  // Mark order as delivered
  async markAsDelivered(orderId: number, deliveryNotes: string): Promise<any> {
    const response = await apiClient.post(`/orders/${orderId}/mark-delivered`, {
      delivery_notes: deliveryNotes
    });
    return response.data;
  },

  // Update order PAYMENT status only (admin)
  async updateOrderPaymentStatus(orderId: number, statusData: { status: string; adminNotes?: string }): Promise<any> {
    const response = await apiClient.put(`/orders/${orderId}/status`, statusData);
    return response.data;
  },

  // Update order shipping status manually (admin)
  async updateOrderShippingStatus(orderId: number, shippingStatus: string): Promise<any> {
    const response = await apiClient.put(`/orders/${orderId}/shipping-status`, {
      shipping_status: shippingStatus
    });

    return response.data;
  },

  // Update order shipping (admin)
  async updateOrderShipping(orderId: number, shippingData: {
    trackingNumber: string;
    shippingProvider: string;
    estimatedDelivery?: string;
    shippingNotes?: string;
  }): Promise<any> {
    const response = await apiClient.put(`/orders/${orderId}/shipping`, shippingData);
    return response.data;
  },

  // Bulk mark orders as shipped
  async bulkMarkAsShipped(orderIds: number[]): Promise<any> {
    const response = await apiClient.post('/admin/shipping/bulk-actions/mark-shipped', orderIds);
    return response.data;
  },

  // Admin shipping functions
  // Get shipping statistics
  async getShippingStatistics(): Promise<any> {
    const response = await apiClient.get('/admin/shipping/statistics');
    return response.data;
  },

  // Get shipping providers
  async getShippingProviders(): Promise<any[]> {
    const response = await apiClient.get('/admin/shipping/providers');
    return response.data.providers;
  },

  // Update shipping info for order
  async updateShippingInfo(orderId: number, shippingData: any): Promise<any> {
    const response = await apiClient.put(`/admin/shipping/orders/${orderId}/shipping-info`, shippingData);
    return response.data;
  },

  // Mark order as shipped
  async markOrderAsShipped(orderId: number): Promise<any> {
    const response = await apiClient.post(`/admin/shipping/orders/${orderId}/mark-shipped`, {
      send_notification: true
    });
    return response.data;
  }
  ,
  // Update order status (general purpose) — kept for compatibility with components
  async updateOrderStatus(orderId: number, updates: any): Promise<any> {
    const response = await apiClient.put(`/orders/${orderId}`, updates);
    return response.data;
  }
};

// API functions for customers
export const customersApi = {
  // Create new customer
  async createCustomer(customerData: any): Promise<any> {
    const response = await apiClient.post('/customers/', customerData);
    return response.data;
  },

  // Get all customers
  async getCustomers(): Promise<any[]> {
    const response = await apiClient.get('/customers/');
    return response.data;
  },

  // Get customer by ID
  async getCustomer(id: number): Promise<any> {
    const response = await apiClient.get(`/customers/${id}`);
    return response.data;
  },

  // Update customer
  async updateCustomer(id: number, updates: any): Promise<any> {
    const response = await apiClient.put(`/customers/${id}`, updates);
    return response.data;
  },

  // Delete customer
  async deleteCustomer(id: number): Promise<void> {
    await apiClient.delete(`/customers/${id}`);
  },

  // Get customer data for authenticated user
  async getMyCustomerData(): Promise<any> {
    const response = await apiClient.get('/customers/my-data');
    return response.data;
  }
};

// API functions for order items
export const orderItemsApi = {
  // Create new order item
  async createOrderItem(orderItemData: OrderItemCreate): Promise<OrderItem> {
    const response = await apiClient.post('/order-items/', orderItemData);
    return response.data;
  },

  // Get all order items
  async getOrderItems(): Promise<any[]> {
    const response = await apiClient.get('/order-items/');
    return response.data;
  },

  // Get order item by ID
  async getOrderItem(id: number): Promise<any> {
    const response = await apiClient.get(`/order-items/${id}`);
    return response.data;
  },

  // Update order item
  async updateOrderItem(id: number, updates: any): Promise<any> {
    const response = await apiClient.put(`/order-items/${id}`, updates);
    return response.data;
  },

  // Delete order item
  async deleteOrderItem(id: number): Promise<void> {
    await apiClient.delete(`/order-items/${id}`);
  }
};

// Product interfaces moved to types/products/product.types.ts

// API functions for shipping quotes
export const shippingQuotesApi = {
  // Get shipping quotes for a destination and weight
  async getShippingQuotes(data: {
    postal_code: string;
    city?: string;
    province?: string;
    total_weight_kg: number;
    include_fallback?: boolean;
  }): Promise<any> {
    const response = await apiClient.post('/shipping/quote', data);
    return response.data;
  },

  // Get available carriers
  async getAvailableCarriers(): Promise<any> {
    const response = await apiClient.get('/shipping/carriers');
    return response.data;
  },

  // Test shipping API connection
  async testShippingApi(): Promise<any> {
    const response = await apiClient.get('/shipping/test-api');
    return response.data;
  }
};

// API functions for products
export const productsApi = {
  // Get all products
  async getProducts(params?: {
    categoryId?: number;
    colorId?: number;
    sizeId?: number;
    search?: string;
    minPrice?: number;
    maxPrice?: number;
    inStock?: boolean;
    sortBy?: 'name' | 'price' | 'created_at';
    sortOrder?: 'asc' | 'desc';
    page?: number;
    limit?: number;
  }): Promise<{ products: Product[]; total: number }> {
    const response = await apiClient.get('/products/', { params });
    // Backend returns array directly, not wrapped in object
    const products = Array.isArray(response.data) ? response.data : [];
    return { products, total: products.length };
  },

  // Get product by ID
  async getProduct(id: number): Promise<Product> {
    const response = await apiClient.get(`/products/${id}`);
    return response.data;
  },

  // Create new product (admin only)
  async createProduct(productData: ProductCreateData): Promise<Product> {
    const response = await apiClient.post('/products/', productData);
    return response.data;
  },

  // Update product (admin only)
  async updateProduct(id: number, updates: ProductUpdateData): Promise<Product> {
    const response = await apiClient.put(`/products/${id}`, updates);
    return response.data;
  },

  // Delete product (admin only)
  async deleteProduct(id: number): Promise<void> {
    await apiClient.delete(`/products/${id}`);
  },

  // Upload product image (admin only)
  async uploadProductImage(productId: number, file: File): Promise<{ imageUrl: string }> {
    const formData = new FormData();
    formData.append('image', file);

    const response = await apiClient.post(`/products/${productId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  // Delete product image (admin only)
  async deleteProductImage(productId: number, imageId: number): Promise<void> {
    await apiClient.delete(`/products/${productId}/images/${imageId}`);
  },

  // Check product stock
  async checkStock(items: StockCheckItem[]): Promise<StockCheckResponse> {
    const response = await apiClient.post('/products/check-stock/', items);
    return response.data;
  },

  // Get featured products
  async getFeaturedProducts(limit: number = 8): Promise<Product[]> {
    const response = await apiClient.get('/products/featured', {
      params: { limit },
    });
    return response.data;
  },

  // Get related products
  async getRelatedProducts(productId: number, limit: number = 4): Promise<Product[]> {
    const response = await apiClient.get(`/products/${productId}/related`, {
      params: { limit },
    });
    return response.data;
  },

  // Get products by category
  async getProductsByCategory(categoryId: number, params?: {
    colorId?: number;
    sizeId?: number;
    minPrice?: number;
    maxPrice?: number;
    sortBy?: 'name' | 'price' | 'created_at';
    sortOrder?: 'asc' | 'desc';
    page?: number;
    limit?: number;
  }): Promise<{ products: Product[]; total: number }> {
    const response = await apiClient.get(`/categories/${categoryId}/products`, { params });
    return response.data;
  },
};

// API functions for categories
export const categoriesApi = {
  // Get all categories
  async getCategories(params?: { includeInactive?: boolean }): Promise<Category[]> {
    const response = await apiClient.get('/categories', { params });
    return response.data;
  },

  // Get category by ID
  async getCategory(id: number): Promise<Category> {
    const response = await apiClient.get(`/categories/${id}`);
    return response.data;
  },

  // Create category (admin only)
  async createCategory(categoryData: Omit<Category, 'id'>): Promise<Category> {
    const response = await apiClient.post('/categories', categoryData);
    return response.data;
  },

  // Update category (admin only)
  async updateCategory(id: number, updates: Partial<Category>): Promise<Category> {
    const response = await apiClient.patch(`/categories/${id}`, updates);
    return response.data;
  },

  // Delete category (admin only)
  async deleteCategory(id: number): Promise<void> {
    await apiClient.delete(`/categories/${id}`);
  },

  // Get category tree
  async getCategoryTree(includeInactive: boolean = false): Promise<Category[]> {
    const response = await apiClient.get('/categories/tree', {
      params: { includeInactive },
    });
    return response.data;
  },
};

// API functions for colors
export const colorsApi = {
  // Get all colors
  async getColors(includeInactive: boolean = false): Promise<Color[]> {
    const response = await apiClient.get('/colors', {
      params: { includeInactive },
    });
    return response.data;
  },

  // Create color (admin only)
  async createColor(colorData: Omit<Color, 'id'>): Promise<Color> {
    const response = await apiClient.post('/colors', colorData);
    return response.data;
  },

  // Update color (admin only)
  async updateColor(id: number, updates: Partial<Color>): Promise<Color> {
    const response = await apiClient.patch(`/colors/${id}`, updates);
    return response.data;
  },

  // Delete color (admin only)
  async deleteColor(id: number): Promise<void> {
    await apiClient.delete(`/colors/${id}`);
  },
};

// API functions for sizes
export const sizesApi = {
  // Get all sizes
  async getSizes(includeInactive: boolean = false): Promise<Size[]> {
    const response = await apiClient.get('/sizes', {
      params: { includeInactive },
    });
    return response.data;
  },

  // Create size (admin only)
  async createSize(sizeData: Omit<Size, 'id'>): Promise<Size> {
    const response = await apiClient.post('/sizes', sizeData);
    return response.data;
  },

  // Update size (admin only)
  async updateSize(id: number, updates: Partial<Size>): Promise<Size> {
    const response = await apiClient.patch(`/sizes/${id}`, updates);
    return response.data;
  },

  // Delete size (admin only)
  async deleteSize(id: number): Promise<void> {
    await apiClient.delete(`/sizes/${id}`);
  },
};

export default apiClient;