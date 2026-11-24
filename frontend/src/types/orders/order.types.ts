import { PaymentMethod, PaymentStatus } from './payment';
import { TransferInfo, DeliveryInfo } from './delivery.types';

export interface Order {
  // Campos requeridos
  order_id: number;
  status: string;
  shipping_status: string;
  customer_name: string;
  customer_email: string;
  shipping_address: string;
  total: number;
  payment_method: string | PaymentMethod;
  
  // Campos opcionales
  shipping_method?: string | null;
  tracking_number?: string | null;
  shipping_provider?: string | null;
  estimated_delivery?: string | null;
  customer_phone?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at?: string | null;
  shipped_at?: string | null;
  delivery_method?: string | null;
  provider_name?: string | null;
  
  // Campos de pago
  payment_status?: PaymentStatus;
  mercadopago_payment_id?: string;
  mercadopago_preference_id?: string;
  mercadopago_checkout_url?: string;
  payment_expires_at?: string;
  stock_released?: boolean;
  
  // Campos de envío
  delivery_cost?: number;
  delivery_zone?: string;
  delivery_notes?: string;
  
  // Campos de verificación
  verification_required?: boolean;
  verified_by_admin?: boolean;
  admin_verification_date?: string;
  
  // Campos calculados
  can_add_tracking?: boolean;
  can_mark_shipped?: boolean;
  can_coordinate_pickup?: boolean;
  
  // Relaciones
  items?: OrderItem[];
  customer?: Customer;
  
  // Para propiedades adicionales
  [key: string]: any;
}

export interface OrderItem {
  id?: number;
  order_id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  price: number;
  variant_id?: number;
  color_id?: number;
  size_id?: number;
  color_name?: string;
  size_name?: string;
  image_url?: string;
  product?: {
    id: number;
    name: string;
    description: string;
    price: number;
    images: Array<{ id: number; image_url: string }>;
  };
}

// Tipo específico para crear OrderItems que coincide exactamente con el backend
export interface OrderItemCreate {
  order_id: number;
  product_id: number;
  variant_id?: number;
  quantity: number;
  price: number;
}

export interface OrderResponse {
  order: Order;
  payment_preference?: PaymentPreference;
  transfer_info?: TransferInfo;
  delivery_info?: DeliveryInfo;
  payment_error?: string;
}

export interface OrderFilters {
  status?: string;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
  page?: number;
  limit?: number;
}

export interface PaginatedOrders {
  data: Order[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface AdminOrderFilters {
  payment_method?: string;
  payment_status?: string;
  verification_required?: boolean | string;
  delivery_status?: string;
}

export interface AdminStats {
  pending_verification: number;
  pending_delivery: number;
  scheduled_delivery: number;
  total_pending_amount: number;
  orders_by_method: Record<PaymentMethod, number>;
  last_updated: string;
}

// Importaciones necesarias
import { PaymentPreference } from './payment.types';
import { Customer } from '../users/user.types';

export interface OrderStatistics {
  // Estadísticas generales
  total_orders: number;
  total_sales: number;
  average_order_value: number;
  
  // Estadísticas por estado
  pending_orders: number;
  processing_orders: number;
  completed_orders: number;
  cancelled_orders: number;
  pending_shipment: number;  // Añadido
  shipped_orders: number;    // Añadido
  
  // Métricas de rendimiento
  shipping_rate_percent: number;  // Añadido
  avg_processing_hours: number;   // Añadido
  
  // Datos agrupados
  orders_by_status: Record<string, number>;
  orders_by_month: Array<{
    month: string;
    count: number;
    total: number;
  }>;
  
  // Productos más vendidos
  top_products: Array<{
    product_id: number;
    product_name: string;
    quantity_sold: number;
    total_revenue: number;
  }>;
  
  // Metadatos
  last_updated: string;
}
