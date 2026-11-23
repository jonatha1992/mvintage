/**
 * Centralized order status utilities
 * Single source of truth for all status mappings across the application
 */

// Configuration for payment status display
export const PAYMENT_STATUS_CONFIG = {
  'pending': { text: 'Pendiente de pago', class: 'bg-orange-100 text-orange-800' },
  'pending_payment': { text: 'Pendiente de pago', class: 'bg-orange-100 text-orange-800' },
  'approved': { text: 'Pago confirmado', class: 'bg-green-100 text-green-800' },
  'paid': { text: 'Pago confirmado', class: 'bg-green-100 text-green-800' },
  'rejected': { text: 'Cancelado', class: 'bg-red-100 text-red-800' },
  'cancelled': { text: 'Cancelado', class: 'bg-red-100 text-red-800' }
} as const;

// Configuration for pickup/order status display
export const SHIPPING_STATUS_CONFIG = {
  'pending': { text: 'Pendiente de pago', class: 'bg-yellow-100 text-yellow-800' },
  'pending_payment': { text: 'Pendiente de pago', class: 'bg-yellow-100 text-yellow-800' },
  'approved': { text: 'Pago confirmado', class: 'bg-green-100 text-green-800' },
  'paid': { text: 'Pago confirmado', class: 'bg-green-100 text-green-800' },
  'prepared': { text: 'Listo para retirar', class: 'bg-indigo-100 text-indigo-800' },
  'ready_to_ship': { text: 'Listo para retirar', class: 'bg-indigo-100 text-indigo-800' },
  'ready_for_pickup': { text: 'Listo para retirar', class: 'bg-indigo-100 text-indigo-800' },
  'shipped': { text: 'Listo para retirar', class: 'bg-indigo-100 text-indigo-800' },
  'in_transit': { text: 'Listo para retirar', class: 'bg-indigo-100 text-indigo-800' },
  'out_for_delivery': { text: 'Listo para retirar', class: 'bg-indigo-100 text-indigo-800' },
  'delivered': { text: 'Retirado', class: 'bg-green-100 text-green-800' },
  'cancelled': { text: 'Cancelado', class: 'bg-red-100 text-red-800' },
  'rejected': { text: 'Cancelado', class: 'bg-red-100 text-red-800' },
  'failed': { text: 'Cancelado', class: 'bg-red-100 text-red-800' }
} as const;

// Configuration for delivery method display
export const DELIVERY_METHOD_CONFIG = {
  'retiro_local': { text: 'Retiro en el local', class: 'bg-green-100 text-green-800' },
  'pickup': { text: 'Retiro en el local', class: 'bg-green-100 text-green-800' },
  'standard': { text: 'Retiro en el local', class: 'bg-green-100 text-green-800' },
  'express': { text: 'Retiro en el local', class: 'bg-green-100 text-green-800' }
} as const;

/**
 * Gets payment status configuration (text and CSS class)
 */
export function getPaymentStatusConfig(status: string | undefined) {
  if (!status) return { text: 'Pendiente', class: 'bg-gray-100 text-gray-800' };
  return PAYMENT_STATUS_CONFIG[status.toLowerCase() as keyof typeof PAYMENT_STATUS_CONFIG] 
    || { text: status, class: 'bg-gray-100 text-gray-800' };
}

/**
 * Gets shipping status configuration (text and CSS class)
 */
export function getShippingStatusConfig(status: string | undefined) {
  if (!status) return { text: 'Pendiente', class: 'bg-gray-100 text-gray-800' };
  return SHIPPING_STATUS_CONFIG[status.toLowerCase() as keyof typeof SHIPPING_STATUS_CONFIG] 
    || { text: status, class: 'bg-gray-100 text-gray-800' };
}

/**
 * Gets delivery method configuration (text and CSS class)
 */
export function getDeliveryMethodConfig(method: string | null | undefined) {
  if (!method) return { text: 'Retiro en el local', class: 'bg-green-100 text-green-800' };
  return DELIVERY_METHOD_CONFIG[method.toLowerCase() as keyof typeof DELIVERY_METHOD_CONFIG] 
    || { text: 'Retiro en el local', class: 'bg-green-100 text-green-800' };
}

export function getOrderPickupStatusConfig(order: {
  status?: string;
  payment_status?: string;
  shipping_status?: string;
} | null | undefined) {
  if (!order) return SHIPPING_STATUS_CONFIG.pending;
  const status = (order.status || '').toLowerCase();
  const paymentStatus = (order.payment_status || '').toLowerCase();
  const shippingStatus = (order.shipping_status || '').toLowerCase();

  if (status === 'cancelled' || status === 'rejected' || paymentStatus === 'cancelled' || paymentStatus === 'rejected' || shippingStatus === 'cancelled' || shippingStatus === 'failed') {
    return SHIPPING_STATUS_CONFIG.cancelled;
  }
  if (shippingStatus === 'delivered' || status === 'delivered') {
    return SHIPPING_STATUS_CONFIG.delivered;
  }
  if (['prepared', 'ready_for_pickup', 'ready_to_ship', 'shipped', 'in_transit', 'out_for_delivery'].includes(shippingStatus)) {
    return SHIPPING_STATUS_CONFIG.ready_for_pickup;
  }
  if (paymentStatus === 'approved' || paymentStatus === 'paid' || status === 'approved' || status === 'paid') {
    return SHIPPING_STATUS_CONFIG.approved;
  }
  return SHIPPING_STATUS_CONFIG.pending;
}

/**
 * Gets payment status text only
 */
export function getPaymentStatusText(status: string | undefined): string {
  return getPaymentStatusConfig(status).text;
}

/**
 * Gets payment status CSS class only
 */
export function getPaymentStatusClass(status: string | undefined): string {
  return getPaymentStatusConfig(status).class;
}

/**
 * Gets shipping status text only
 */
export function getShippingStatusText(status: string | undefined): string {
  return getShippingStatusConfig(status).text;
}

/**
 * Gets shipping status CSS class only
 */
export function getShippingStatusClass(status: string | undefined): string {
  return getShippingStatusConfig(status).class;
}

/**
 * Gets delivery method text only
 */
export function getDeliveryMethodText(method: string | null | undefined): string {
  return getDeliveryMethodConfig(method).text;
}

/**
 * Gets delivery method CSS class only
 */
export function getDeliveryMethodClass(method: string | null | undefined): string {
  return getDeliveryMethodConfig(method).class;
}

/**
 * Legacy compatibility - maps general status to appropriate shipping status
 * Used for backward compatibility when shipping_status is not available
 */
export function mapLegacyStatusToShipping(status: string | undefined): string {
  const mapping: Record<string, string> = {
    'pending': 'pending',
    'pending_payment': 'pending',
    'approved': 'prepared',
    'shipped': 'shipped',
    'delivered': 'delivered',
    'cancelled': 'failed'
  };
  
  return status ? (mapping[status.toLowerCase()] || status) : 'pending';
}