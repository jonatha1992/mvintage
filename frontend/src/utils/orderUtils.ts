import { Order } from '../types/orders';

/**
 * Creates a complete Order object with default values for optional fields
 * @param order The base order object
 * @returns A complete Order object with all fields properly initialized
 */
export function createCompleteOrder(order: Partial<Order>): Order {
  return {
    order_id: order.order_id || 0,
    status: order.status || 'pending',
    shipping_status: order.shipping_status || 'pending',
    // Payment status (important for admin modals)
    payment_status: order.payment_status || 'pending',
    customer_name: order.customer_name || '',
    customer_email: order.customer_email || '',
    shipping_address: order.shipping_address || '',
    total: order.total || 0,
    payment_method: order.payment_method || 'credit_card',
    created_at: order.created_at || new Date().toISOString(),

    // Optional fields with proper null handling
    ...(order.customer_phone !== undefined && { customer_phone: order.customer_phone }),
    ...(order.tracking_number !== undefined && { tracking_number: order.tracking_number }),
    ...(order.shipping_provider !== undefined && { shipping_provider: order.shipping_provider }),
    ...(order.provider_name !== undefined && { provider_name: order.provider_name }),
    ...(order.notes !== undefined && { notes: order.notes }),
    ...(order.shipping_method !== undefined && { shipping_method: order.shipping_method }),
    ...(order.estimated_delivery !== undefined && { estimated_delivery: order.estimated_delivery }),
    ...(order.updated_at !== undefined && { updated_at: order.updated_at }),
    ...(order.shipped_at !== undefined && { shipped_at: order.shipped_at }),
    ...(order.delivery_method !== undefined && { delivery_method: order.delivery_method }),

    // Computed properties with defaults
    can_add_tracking: order.can_add_tracking || false,
    can_mark_shipped: order.can_mark_shipped || false,
    can_coordinate_pickup: order.can_coordinate_pickup || false
  };
}

/**
 * Gets the CSS class for a delivery method
 */
export function getDeliveryMethodClass(method: string | null | undefined): string {
  if (!method) return 'bg-gray-100 text-gray-800';
  const methodClasses: Record<string, string> = {
    'standard': 'bg-blue-100 text-blue-800',
    'express': 'bg-purple-100 text-purple-800',
    'pickup': 'bg-green-100 text-green-800'
  };
  return methodClasses[method.toLowerCase()] || 'bg-gray-100 text-gray-800';
}

/**
 * Gets the display text for a delivery method
 */
export function getDeliveryMethodText(method: string | null | undefined): string {
  if (!method) return 'Retiro en el local';
  const methodText: Record<string, string> = {
    'retiro_local': 'Retiro en el local',
    'pickup': 'Retiro en el local',
    'standard': 'Retiro en el local',
    'express': 'Retiro en el local'
  };
  return methodText[method.toLowerCase()] || 'Retiro en el local';
}

/**
 * Gets the placeholder text for a tracking number input
 */
export function getTrackingPlaceholder(providerCode: string | undefined): string {
  return providerCode ? `Ej: ${providerCode.toUpperCase()}1234567890` : 'Número de seguimiento';
}

/**
 * Gets the hint text for a tracking number input
 */
export function getTrackingHint(providerCode: string | undefined): string {
  return providerCode ? `Formato: ${providerCode.toUpperCase()} + 10 dígitos` : 'Ingrese el número de seguimiento';
}

/**
 * Formats a date string to a more readable format
 */
export function formatDate(dateString: string | undefined): string {
  if (!dateString) return 'N/A';
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };
  return new Date(dateString).toLocaleDateString('es-ES', options);
}

/**
 * Safely converts a value to a string, returning undefined for null/undefined values
 */
export function safeString(value: any): string | undefined {
  return value != null ? String(value) : undefined;
}

/**
 * Converts a value to a string, null, or undefined
 */
export function toStringOrNull(value: any): string | null | undefined {
  if (value === null || value === undefined) return undefined;
  return String(value);
}
