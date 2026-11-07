<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-4xl px-4 py-8 mx-auto sm:py-12 sm:px-6 lg:px-8">
      <!-- Breadcrumb -->
      <nav class="flex mb-8" aria-label="Breadcrumb">
        <ol class="flex items-center space-x-4">
          <li>
            <router-link to="/orders" class="flex items-center text-gray-400 hover:text-gray-500">
              <svg class="flex-shrink-0 w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd"
                  d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                  clip-rule="evenodd" />
              </svg>
              <span class="ml-1">Mis Pedidos</span>
            </router-link>
          </li>
          <li>
            <div class="flex items-center">
              <svg class="flex-shrink-0 w-5 h-5 text-gray-300" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd"
                  d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                  clip-rule="evenodd" />
              </svg>
              <span class="ml-4 text-sm font-medium text-gray-500">Pedido #{{ orderId }}</span>
            </div>
          </li>
        </ol>
      </nav>

      <!-- Loading State -->
      <div v-if="loading" class="py-12 text-center">
        <div class="inline-block w-8 h-8 border-b-2 border-gray-900 rounded-full animate-spin"></div>
        <p class="mt-2 text-gray-600">Cargando detalles del pedido...</p>
      </div>

      <!-- Order Details -->
      <div v-else-if="order" class="space-y-6">
        <!-- Order Header -->
        <div class="p-6 bg-white rounded-lg shadow">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h1 class="text-2xl font-light text-gray-900">Pedido #{{ order.id }}</h1>
              <p class="text-sm text-gray-500">
                Realizado el {{ formatDate(order.created_at) }}
              </p>
            </div>
            <span class="inline-flex items-center px-3 py-1 text-sm font-medium rounded-full"
              :class="getShippingStatusClass(order.shipping_status || order.status)">
              {{ getShippingStatusText(order.shipping_status || order.status) }}
            </span>
          </div>
        </div>

        <!-- Order Status Timeline -->
        <div class="p-6 bg-white rounded-lg shadow">
          <h2 class="mb-6 text-lg font-medium text-gray-900">Estado del Pedido</h2>

          <!-- Timeline -->
          <div class="relative">
            <!-- Timeline line -->
            <div class="absolute left-4 top-0 h-full w-0.5 bg-gray-200" aria-hidden="true"></div>

            <ul class="space-y-6">
              <!-- Step 1: Order Created -->
              <li class="relative flex items-start">
                <div class="relative flex items-center justify-center flex-none w-8 h-8">
                  <div class="h-1.5 w-1.5 rounded-full bg-green-600 ring-4 ring-white border-2 border-green-600"></div>
                </div>
                <div class="flex-1 min-w-0 ml-4">
                  <div class="flex items-center">
                    <p class="text-sm font-medium text-gray-900">Pedido Realizado</p>
                    <div class="flex ml-auto">
                      <svg class="w-5 h-5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clip-rule="evenodd" />
                      </svg>
                    </div>
                  </div>
                  <p class="text-sm text-gray-500">{{ formatDateTime(order.created_at) }}</p>
                  <p class="mt-1 text-xs text-gray-400">Tu pedido ha sido recibido y estÃ¡ siendo procesado</p>
                </div>
              </li>

              <!-- Step 2: Payment Status -->
              <li class="relative flex items-start">
                <div class="relative flex items-center justify-center flex-none w-8 h-8">
                  <div class="h-1.5 w-1.5 rounded-full ring-4 ring-white border-2"
                    :class="getPaymentTimelineClass(order.payment_status)"></div>
                </div>
                <div class="flex-1 min-w-0 ml-4">
                  <div class="flex items-center">
                    <p class="text-sm font-medium text-gray-900">{{ getPaymentStatusText(order.payment_status) }}</p>
                    <div class="flex ml-auto">
                      <svg v-if="order.payment_status === 'approved'" class="w-5 h-5 text-green-600" viewBox="0 0 20 20"
                        fill="currentColor">
                        <path fill-rule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clip-rule="evenodd" />
                      </svg>
                      <svg v-else-if="order.payment_status === 'pending' || order.payment_status === 'pending_payment'"
                        class="w-5 h-5 text-yellow-500 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                        </circle>
                        <path class="opacity-75" fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                        </path>
                      </svg>
                      <svg v-else class="w-5 h-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </div>
                  </div>
                  <p v-if="order.approved_at" class="text-sm text-gray-500">{{ formatDateTime(order.approved_at) }}</p>
                  <p class="mt-1 text-xs text-gray-400">{{ getPaymentDescription(order.payment_method,
                    order.payment_status) }}</p>
                </div>
              </li>

              <!-- Step 3: Shipping Preparation -->
              <li class="relative flex items-start">
                <div class="relative flex items-center justify-center flex-none w-8 h-8">
                  <div class="h-1.5 w-1.5 rounded-full ring-4 ring-white border-2"
                    :class="getShippingPreparationClass(order)"></div>
                </div>
                <div class="flex-1 min-w-0 ml-4">
                  <div class="flex items-center">
                    <p class="text-sm font-medium text-gray-900">Preparación del Envío</p>
                    <div class="flex ml-auto">
                      <svg v-if="order.tracking_number" class="w-5 h-5 text-green-600" viewBox="0 0 20 20"
                        fill="currentColor">
                        <path fill-rule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clip-rule="evenodd" />
                      </svg>
                      <svg v-else-if="order.status === 'approved' && order.payment_status === 'approved'"
                        class="w-5 h-5 text-yellow-500 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                        </circle>
                        <path class="opacity-75" fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                        </path>
                      </svg>
                      <div v-else class="w-5 h-5 bg-gray-300 rounded-full"></div>
                    </div>
                  </div>
                  <p v-if="order.tracking_updated_at" class="text-sm text-gray-500">{{
                    formatDateTime(order.tracking_updated_at) }}</p>
                  <p class="mt-1 text-xs text-gray-400">{{ getPreparationDescription(order) }}</p>
                </div>
              </li>

              <!-- Step 4: Shipped -->
              <li class="relative flex items-start">
                <div class="relative flex items-center justify-center flex-none w-8 h-8">
                  <div class="h-1.5 w-1.5 rounded-full ring-4 ring-white border-2"
                    :class="getShippedTimelineClass(order)"></div>
                </div>
                <div class="flex-1 min-w-0 ml-4">
                  <div class="flex items-center">
                    <p class="text-sm font-medium text-gray-900">Enviado</p>
                    <div class="flex ml-auto">
                      <svg v-if="order.shipped_at" class="w-5 h-5 text-green-600" viewBox="0 0 20 20"
                        fill="currentColor">
                        <path fill-rule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clip-rule="evenodd" />
                      </svg>
                      <div v-else class="w-5 h-5 bg-gray-300 rounded-full"></div>
                    </div>
                  </div>
                  <p v-if="order.shipped_at" class="text-sm text-gray-500">{{ formatDateTime(order.shipped_at) }}</p>
                  <div v-if="order.tracking_number" class="p-3 mt-2 rounded-md bg-blue-50">
                    <div class="flex items-center justify-between">
                      <div>
                        <p class="text-sm font-medium text-blue-900">Número de Seguimiento</p>
                        <p class="font-mono text-sm text-blue-700">{{ order.tracking_number }}</p>
                        <p v-if="order.shipping_provider" class="mt-1 text-xs text-blue-600">
                          Proveedor: {{ getProviderName(order.shipping_provider) }}
                        </p>
                      </div>
                      <a v-if="getTrackingUrl(order.tracking_number, order.shipping_provider)"
                        :href="getTrackingUrl(order.tracking_number, order.shipping_provider) || undefined"
                        target="_blank"
                        class="inline-flex items-center px-3 py-1 text-xs font-medium text-white bg-blue-600 border border-transparent rounded hover:bg-blue-700">
                        Rastrear
                        <svg class="w-3 h-3 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </a>
                    </div>
                  </div>
                  <p v-if="order.estimated_delivery" class="mt-1 text-xs text-gray-400">
                    Entrega estimada: {{ formatDate(order.estimated_delivery) }}
                  </p>
                </div>
              </li>

              <!-- Step 5: Delivered -->
              <li v-if="order.status === 'delivered'" class="relative flex items-start">
                <div class="relative flex items-center justify-center flex-none w-8 h-8">
                  <div class="h-1.5 w-1.5 rounded-full bg-green-600 ring-4 ring-white border-2 border-green-600"></div>
                </div>
                <div class="flex-1 min-w-0 ml-4">
                  <div class="flex items-center">
                    <p class="text-sm font-medium text-gray-900">Entregado</p>
                    <div class="flex ml-auto">
                      <svg class="w-5 h-5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clip-rule="evenodd" />
                      </svg>
                    </div>
                  </div>
                  <p v-if="order.delivered_at" class="text-sm text-gray-500">{{ formatDateTime(order.delivered_at) }}
                  </p>
                  <p class="mt-1 text-xs text-gray-400">Tu pedido ha sido entregado exitosamente</p>
                </div>
              </li>
            </ul>
          </div>

          <!-- Additional Shipping Notes -->
          <div v-if="order.delivery_notes_shipping" class="p-4 mt-6 rounded-md bg-gray-50">
            <h3 class="mb-2 text-sm font-medium text-gray-900">Notas del Envío</h3>
            <p class="text-sm text-gray-600">{{ order.delivery_notes_shipping }}</p>
          </div>
        </div>

        <!-- Order Items -->
        <div class="p-6 bg-white rounded-lg shadow">
          <h2 class="mb-4 text-lg font-medium text-gray-900">Productos</h2>
          <ul class="divide-y divide-gray-200">
            <li v-for="item in order.items" :key="item.id" class="flex py-4">
              <img :src="item.product.images[0]?.image_url || '/placeholder-image.jpg'" :alt="item.product.name"
                class="object-cover object-center w-16 h-16 rounded-md">
              <div class="flex-1 ml-4">
                <div class="flex justify-between">
                  <div>
                    <h3 class="text-sm font-medium text-gray-900">{{ item.product.name }}</h3>
                    <p class="text-sm text-gray-500">Cantidad: {{ item.quantity }}</p>
                  </div>
                  <p class="text-sm font-medium text-gray-900">
                    ${{ (item.price * item.quantity).toLocaleString() }}
                  </p>
                </div>
              </div>
            </li>
          </ul>
        </div>

        <!-- Order Summary -->
        <div class="p-6 bg-white rounded-lg shadow">
          <h2 class="mb-4 text-lg font-medium text-gray-900">Resumen del Pedido</h2>
          <dl class="space-y-3">
            <div class="flex justify-between">
              <dt class="text-sm text-gray-600">Subtotal</dt>
              <dd class="text-sm font-medium text-gray-900">${{ order.subtotal?.toLocaleString() }}</dd>
            </div>
            <div v-if="order.discount && order.discount > 0" class="flex justify-between">
              <dt class="text-sm text-gray-600">Descuento</dt>
              <dd class="text-sm font-medium text-green-600">-${{ order.discount.toLocaleString() }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-sm text-gray-600">Envío</dt>
              <dd class="text-sm font-medium text-gray-900">${{ order.shipping_cost?.toLocaleString() }}</dd>
            </div>
            <div class="flex justify-between pt-3 border-t">
              <dt class="text-base font-medium text-gray-900">Total</dt>
              <dd class="text-base font-medium text-gray-900">${{ order.total.toLocaleString() }}</dd>
            </div>
          </dl>
        </div>

        <!-- Shipping Information -->
        <div class="p-6 bg-white rounded-lg shadow">
          <h2 class="mb-4 text-lg font-medium text-gray-900">Informacin de Envio</h2>
          <div class="text-sm text-gray-600">
            <p class="font-medium text-gray-900">{{ order.customer_name }}</p>
            <p>{{ order.shipping_address }}</p>
            <p>{{ order.shipping_city }}, {{ order.shipping_postal_code }}</p>
            <p v-if="order.delivery_notes" class="mt-2">
              <span class="font-medium">Notas:</span> {{ order.delivery_notes }}
            </p>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div v-else class="py-12 text-center">
        <div class="w-24 h-24 mx-auto mb-4 text-gray-400">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 class="mb-2 text-lg font-medium text-gray-900">Pedido no encontrado</h3>
        <p class="mb-6 text-gray-600">No se pudo cargar la informacin del pedido</p>
        <router-link to="/orders"
          class="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-black border border-transparent rounded-md hover:bg-gray-800">
          Volver a mis pedidos
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../../store/auth';
import { useToast } from 'vue-toastification';
import { ordersApi } from '../../config/api';
import { 
  getShippingStatusClass, 
  getShippingStatusText,
  getPaymentStatusClass,
  getPaymentStatusText 
} from '../../utils/orderStatusUtils';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

const loading = ref(true);
const order = ref<any>(null);

const orderId = computed(() => route.params.id as string);

onMounted(async () => {
  // Check authentication
  if (!authStore.isAuthenticated) {
    toast.warning('Debes iniciar sesin para ver tus pedidos');
    router.push('/auth');
    return;
  }

  await loadOrderDetails();
});

const loadOrderDetails = async () => {
  try {
    loading.value = true;

    // First, check if the OrdersView passed the order via history.state
    const passedOrder = (window.history && (window.history.state as any)?.order) ? (window.history.state as any).order : null;
    if (passedOrder) {
      // Normalize minimal fields in the passed object
      if (passedOrder.order_id && !passedOrder.id) passedOrder.id = passedOrder.order_id;
      // Flatten customer if exists
      if (passedOrder.customer) {
        passedOrder.customer_name = passedOrder.customer.name || passedOrder.customer_name || '';
        passedOrder.customer_email = passedOrder.customer.email || passedOrder.customer_email || '';
        passedOrder.shipping_address = passedOrder.shipping_address || passedOrder.customer.address || '';
        passedOrder.shipping_city = passedOrder.shipping_city || passedOrder.customer.city || '';
        passedOrder.shipping_postal_code = passedOrder.shipping_postal_code || passedOrder.customer.postal_code || '';
      }

      // Use the passed order as the starting point
      let enrichedOrder: any = passedOrder;

      // If passed order already includes items and customer, skip network calls
      const hasItems = enrichedOrder.items && enrichedOrder.items.length > 0;
      const hasCustomer = enrichedOrder.customer || enrichedOrder.customer_name || enrichedOrder.customer_email;

      if (!hasItems || !hasCustomer) {
        // Fallback to fetching enriched data if necessary (admin/my-orders)
        try {

          if (authStore.hasAdminAccess) {
            const adminOrders: any[] = await ordersApi.getOrdersWithCustomerInfo();
            const found = adminOrders.find(o => Number(o.id || o.order_id) === Number(passedOrder.id || passedOrder.order_id || orderId.value));
            if (found) {
              enrichedOrder = found;
            }
          } else {
            const myOrders: any[] = await ordersApi.getMyOrders();
            const found = myOrders.find(o => Number(o.id || o.order_id) === Number(passedOrder.id || passedOrder.order_id || orderId.value));
            if (found) {
              enrichedOrder = found;
            }
          }
        } catch (err) {
        }
      }

      // Final normalization
      if (enrichedOrder && enrichedOrder.order_id && !enrichedOrder.id) {
        enrichedOrder.id = enrichedOrder.order_id;
      }

      if (enrichedOrder && enrichedOrder.customer) {
        enrichedOrder.customer_name = enrichedOrder.customer.name || enrichedOrder.customer_name || '';
        enrichedOrder.customer_email = enrichedOrder.customer.email || enrichedOrder.customer_email || '';
        enrichedOrder.shipping_address = enrichedOrder.shipping_address || enrichedOrder.customer.address || '';
        enrichedOrder.shipping_city = enrichedOrder.shipping_city || enrichedOrder.customer.city || '';
        enrichedOrder.shipping_postal_code = enrichedOrder.shipping_postal_code || enrichedOrder.customer.postal_code || '';
      }

      order.value = enrichedOrder;

      return;
    }

    // No passed order: First attempt: basic order endpoint
    const basicOrder: any = await ordersApi.getOrder(parseInt(orderId.value));

    let enrichedOrder: any = basicOrder;

    // If the basic order is missing items or customer info, try to fetch an enriched version.
    const missingItems = !basicOrder || !basicOrder.items || basicOrder.items.length === 0;
    const missingCustomer = !basicOrder || (!basicOrder.customer && !basicOrder.customer_name && !basicOrder.customer_email);

    if (missingItems || missingCustomer) {
      try {

        // Prefer admin endpoint when user has admin access (returns customer + items)
        if (authStore.hasAdminAccess) {
          const adminOrders: any[] = await ordersApi.getOrdersWithCustomerInfo();
          const found = adminOrders.find(o => Number(o.id || o.order_id) === Number(basicOrder.id || basicOrder.order_id || orderId.value));
          if (found) {
            enrichedOrder = found;
          }
        } else {
          // For regular users, try the my-orders endpoint (which includes items)
          const myOrders: any[] = await ordersApi.getMyOrders();
          const found = myOrders.find(o => Number(o.id || o.order_id) === Number(basicOrder.id || basicOrder.order_id || orderId.value));
          if (found) {
            enrichedOrder = found;
          }
        }
      } catch (err) {
      }
    }

    // Final normalization: ensure template fields exist (backwards compatible)
    // Some endpoints use `id`, some admin logic may include `order_id` — normalize to `id`.
    if (enrichedOrder && enrichedOrder.order_id && !enrichedOrder.id) {
      enrichedOrder.id = enrichedOrder.order_id;
    }

    // Flatten simple customer fields for compatibility with template
    if (enrichedOrder && enrichedOrder.customer) {
      enrichedOrder.customer_name = enrichedOrder.customer.name || enrichedOrder.customer_name || '';
      enrichedOrder.customer_email = enrichedOrder.customer.email || enrichedOrder.customer_email || '';
      enrichedOrder.shipping_address = enrichedOrder.shipping_address || enrichedOrder.customer.address || '';
      enrichedOrder.shipping_city = enrichedOrder.shipping_city || enrichedOrder.customer.city || '';
      enrichedOrder.shipping_postal_code = enrichedOrder.shipping_postal_code || enrichedOrder.customer.postal_code || '';
    }

    order.value = enrichedOrder;
  } catch (error) {
    toast.error('Error al cargar los detalles del pedido');
    order.value = null;
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

// Status functions now imported from centralized orderStatusUtils

const formatDateTime = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Payment status text function now imported from centralized orderStatusUtils

const getPaymentTimelineClass = (paymentStatus: string) => {
  switch (paymentStatus) {
    case 'approved':
      return 'bg-green-600 border-green-600';
    case 'pending':
    case 'pending_payment':
      return 'bg-yellow-500 border-yellow-500';
    case 'rejected':
    case 'cancelled':
      return 'bg-red-500 border-red-500';
    default:
      return 'bg-gray-300 border-gray-300';
  }
};

const getPaymentDescription = (paymentMethod: string, paymentStatus: string) => {
  if (paymentStatus === 'approved') {
    return 'Tu pago ha sido confirmado y procesado';
  } else if (paymentStatus === 'pending_payment') {
    switch (paymentMethod) {
      case 'mercadopago':
        return 'Completa el pago en MercadoPago para continuar';
      case 'transfer':
        return 'Realiza la transferencia para confirmar tu pedido';
      case 'cash':
        return 'TendrÃ¡s que pagar en efectivo al recibir';
      default:
        return 'Pago pendiente de confirmacin';
    }
  } else if (paymentStatus === 'pending') {
    return 'Estamos verificando tu pago';
  }
  return 'Verifica el estado de tu pago';
};

const getShippingPreparationClass = (order: any) => {
  if (order.tracking_number) {
    return 'bg-green-600 border-green-600';
  } else if (order.status === 'approved' && order.payment_status === 'approved') {
    return 'bg-yellow-500 border-yellow-500';
  }
  return 'bg-gray-300 border-gray-300';
};

const getPreparationDescription = (order: any) => {
  if (order.tracking_number) {
    return 'Tu pedido está listo y tiene número de seguimiento asignado';
  } else if (order.status === 'approved' && order.payment_status === 'approved') {
    return 'Estamos preparando tu pedido para el envío';
  }
  return 'Esperando confirmación de pago para preparar envío';
};

const getShippedTimelineClass = (order: any) => {
  if (order.shipped_at) {
    return 'bg-green-600 border-green-600';
  }
  return 'bg-gray-300 border-gray-300';
};

const getProviderName = (provider: string) => {
  const providers = {
    'correo-argentino': 'Correo Argentino',
    'oca': 'OCA',
    'andreani': 'Andreani'
  };
  return providers[provider as keyof typeof providers] || provider;
};

const getTrackingUrl = (trackingNumber: string, provider: string) => {
  if (!trackingNumber || !provider) return null;

  const trackingUrls = {
    'correo-argentino': `https://www.correoargentino.com.ar/formularios/e-commerce?id=${trackingNumber}`,
    'oca': `https://www1.oca.com.ar/OcaEpakNet/Tracking.aspx?numeroenvio=${trackingNumber}`,
    'andreani': `https://www.andreani.com/seguimiento?codigo=${trackingNumber}`
  };

  return trackingUrls[provider as keyof typeof trackingUrls] || null;
};
</script>
