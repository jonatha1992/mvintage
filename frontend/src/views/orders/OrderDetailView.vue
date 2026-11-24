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
            <div class="flex items-center space-x-3">
              <button
                v-if="canPayNow(order)"
                type="button"
                :disabled="payingNow"
                @click="payOrderNow"
                class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-black border border-transparent rounded-md shadow-sm hover:bg-gray-800 disabled:opacity-60"
              >
                {{ payingNow ? 'Redirigiendo...' : 'Pagar ahora' }}
              </button>
              <span class="inline-flex items-center px-3 py-1 text-sm font-medium rounded-full"
                :class="getOrderPickupStatusConfig(order).class">
                {{ getOrderPickupStatusConfig(order).text }}
              </span>
            </div>
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
                  <p class="mt-1 text-xs text-gray-400">Tu pedido ha sido recibido y está siendo procesado</p>
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

              <!-- Step 3: Ready for Pickup -->
              <li class="relative flex items-start">
                <div class="relative flex items-center justify-center flex-none w-8 h-8">
                  <div class="h-1.5 w-1.5 rounded-full ring-4 ring-white border-2"
                    :class="getReadyForPickupClass(order)"></div>
                </div>
                <div class="flex-1 min-w-0 ml-4">
                  <div class="flex items-center">
                    <p class="text-sm font-medium text-gray-900">Listo para retirar</p>
                    <div class="flex ml-auto">
                      <svg v-if="isReadyOrPickedUp(order)" class="w-5 h-5 text-green-600" viewBox="0 0 20 20"
                        fill="currentColor">
                        <path fill-rule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clip-rule="evenodd" />
                      </svg>
                      <svg v-else-if="order.status === 'approved' || order.payment_status === 'approved'"
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
                  <p class="mt-1 text-xs text-gray-400">{{ getPreparationDescription(order) }}</p>
                </div>
              </li>

              <!-- Step 4: Picked up -->
              <li v-if="order.shipping_status === 'delivered' || order.status === 'delivered'" class="relative flex items-start">
                <div class="relative flex items-center justify-center flex-none w-8 h-8">
                  <div class="h-1.5 w-1.5 rounded-full bg-green-600 ring-4 ring-white border-2 border-green-600"></div>
                </div>
                <div class="flex-1 min-w-0 ml-4">
                  <div class="flex items-center">
                    <p class="text-sm font-medium text-gray-900">Retirado</p>
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
                  <p class="mt-1 text-xs text-gray-400">Tu pedido fue retirado en el local</p>
                </div>
              </li>
            </ul>
          </div>

          <!-- Additional Pickup Notes -->
          <div v-if="order.delivery_notes_shipping" class="p-4 mt-6 rounded-md bg-gray-50">
            <h3 class="mb-2 text-sm font-medium text-gray-900">Notas del retiro</h3>
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
                  <div class="text-right">
                    <p class="text-sm font-medium text-gray-900">
                      {{ formatPrice((item.price * item.quantity)) }}
                    </p>
                    <p v-if="item.quantity > 1" class="text-xs text-gray-500">
                      {{ formatPrice(item.price) }} c/u
                    </p>
                  </div>
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
              <dd class="text-sm font-medium text-gray-900">{{ formatPrice(order.subtotal) }}</dd>
            </div>
            <div v-if="order.discount && order.discount > 0" class="flex justify-between">
              <dt class="text-sm text-gray-600">Descuento</dt>
              <dd class="text-sm font-medium text-green-600">-{{ formatPrice(order.discount) }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-sm text-gray-600">Retiro en el local</dt>
              <dd class="text-sm font-medium text-green-700">Gratis</dd>
            </div>
            <div class="flex justify-between pt-3 border-t">
              <dt class="text-base font-medium text-gray-900">Total</dt>
              <dd class="text-base font-medium text-gray-900">{{ formatPrice(order.total) }}</dd>
            </div>
          </dl>
        </div>

        <!-- Pickup Information -->
        <div class="p-6 bg-white rounded-lg shadow">
          <h2 class="mb-4 text-lg font-medium text-gray-900">Información de retiro</h2>
          <div class="space-y-1 text-sm text-gray-600">
            <p class="font-medium text-gray-900">{{ order.customer_name }}</p>
            <p>
              Retiro en el local:
              <a :href="STORE_MAPS_URL" target="_blank" rel="noopener noreferrer" class="underline text-gray-900 hover:text-gray-600">{{ STORE_PICKUP_ADDRESS }}</a>.
              {{ STORE_PICKUP_HOURS }} cuando tu pedido esté listo para retirar.
            </p>
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
        <p class="mb-6 text-gray-600">No se pudo cargar la información del pedido</p>
        <router-link to="/orders"
          class="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-black border border-transparent rounded-md hover:bg-gray-800">
          Volver a mis pedidos
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatPrice } from '../../utils/price'
import { orderAccessToken } from '../../utils/orderAccess'
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../../store/auth';
import { useToast } from 'vue-toastification';
import { ordersApi, paymentsApi } from '../../config/api';
import { MERCADOPAGO_HABILITADO } from '../../config/payments';
import { STORE_MAPS_URL, STORE_PICKUP_ADDRESS, STORE_PICKUP_HOURS } from '../../config/store';
import { 
  getOrderPickupStatusConfig,
  getPaymentStatusText 
} from '../../utils/orderStatusUtils';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

const loading = ref(true);
const order = ref<any>(null);
const payingNow = ref(false);

const canPayNow = (o: any) => {
  if (!MERCADOPAGO_HABILITADO || !o) return false;
  if (o.payment_method !== 'mercadopago' || o.payment_status !== 'pending_payment') return false;
  if (o.payment_expires_at && new Date(o.payment_expires_at).getTime() <= Date.now()) return false;
  return true;
};

const payOrderNow = async () => {
  if (!order.value || !canPayNow(order.value)) return;
  if (order.value.mercadopago_checkout_url) {
    window.location.href = order.value.mercadopago_checkout_url;
    return;
  }
  payingNow.value = true;
  try {
    const pref = await paymentsApi.createPreference(order.value.id);
    const url = pref?.checkoutUrl || pref?.checkout_url || pref?.init_point;
    if (!url) {
      toast.error('No se pudo generar el enlace de pago.');
      return;
    }
    window.location.href = url;
  } catch (error: any) {
    toast.error(error?.response?.data?.detail || 'No se pudo iniciar el pago con Mercado Pago.');
  } finally {
    payingNow.value = false;
  }
};

const orderId = computed(() => route.params.id as string);

onMounted(async () => {
  // Check authentication
  const token = orderAccessToken(Number(orderId.value), route.query.access_token);
  if (!authStore.isAuthenticated && !token) {
    toast.warning('Debes iniciar sesión para ver tus pedidos');
    router.push('/auth');
    return;
  }

  await loadOrderDetails();
});

const loadOrderDetails = async () => {
  try {
    loading.value = true;

    if (!authStore.isAuthenticated) {
      order.value = await ordersApi.getOrder(Number(orderId.value));
      return;
    }

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
  if (paymentStatus === 'approved' || paymentStatus === 'paid') {
    return 'Tu pago fue confirmado';
  } else if (paymentStatus === 'pending_payment') {
    switch (paymentMethod) {
      case 'mercadopago':
        return 'Completá el pago en Mercado Pago para continuar';
      case 'transfer':
        return 'Realizá la transferencia para confirmar tu pedido';
      default:
        return 'Pago pendiente de confirmación';
    }
  } else if (paymentStatus === 'pending') {
    return 'Estamos verificando tu pago';
  }
  return 'Verificá el estado de tu pago';
};

const isReadyOrPickedUp = (order: any) => {
  const s = (order?.shipping_status || '').toLowerCase();
  return ['prepared', 'ready_for_pickup', 'ready_to_ship', 'shipped', 'in_transit', 'out_for_delivery', 'delivered'].includes(s) || order?.status === 'delivered';
};

const getReadyForPickupClass = (order: any) => {
  if (isReadyOrPickedUp(order)) {
    return 'bg-green-600 border-green-600';
  } else if (order.status === 'approved' || order.payment_status === 'approved') {
    return 'bg-yellow-500 border-yellow-500';
  }
  return 'bg-gray-300 border-gray-300';
};

const getPreparationDescription = (order: any) => {
  if (order.shipping_status === 'delivered' || order.status === 'delivered') {
    return 'Pedido retirado en el local';
  } else if (isReadyOrPickedUp(order)) {
    return 'Tu pedido está listo para retirar en el local';
  } else if (order.status === 'approved' || order.payment_status === 'approved') {
    return 'Te avisamos por WhatsApp cuando tu pedido esté listo para retirar.';
  }
  return 'Esperando confirmación de pago';
};
</script>
