<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-4xl px-4 py-8 mx-auto sm:py-12 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-light tracking-tight text-gray-900">Mis Pedidos</h1>
        <p class="mt-2 text-sm text-gray-600">
          Aquí puedes ver el historial de todos tus pedidos
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="py-12 text-center">
        <div class="inline-block w-8 h-8 border-b-2 border-gray-900 rounded-full animate-spin"></div>
        <p class="mt-2 text-gray-600">Cargando pedidos...</p>
      </div>

      <!-- Orders List -->
      <div v-else-if="orders.length > 0" class="space-y-6">
        <div 
          v-for="order in orders" 
          :key="order.id"
          class="transition-shadow bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md"
        >
          <div class="p-6">
            <!-- Order Header -->
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-lg font-medium text-gray-900">
                  Pedido #{{ order.id }}
                </h3>
                <p class="text-sm text-gray-500">
                  {{ order.created_at ? formatDate(order.created_at) : 'Fecha no disponible' }}
                </p>
              </div>
              <div class="text-right">
                <span 
                  class="inline-flex items-center px-3 py-1 text-sm font-medium rounded-full"
                  :class="getShippingStatusClass(order.shipping_status || order.status || '')"
                >
                  {{ getShippingStatusText(order.shipping_status || order.status || '') }}
                </span>
                <p class="mt-1 text-lg font-medium text-gray-900">
                  ${{ order.total.toLocaleString() }}
                </p>
              </div>
            </div>

            <!-- Order Items Preview -->
            <div class="pt-4 border-t border-gray-200">
              <div class="flex items-center space-x-4">
                <div 
                  v-for="item in order.items?.slice(0, 3)" 
                  :key="item.id"
                  class="flex-shrink-0"
                >
                  <img 
                    :src="item.product?.images?.[0]?.image_url || '/placeholder-image.jpg'"
                    :alt="item.product?.name || 'Producto'"
                    class="object-cover object-center w-16 h-16 rounded-md"
                  >
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-gray-900">
                    {{ order.items?.length || 0 }} {{ (order.items?.length || 0) === 1 ? 'producto' : 'productos' }}
                  </p>
                  <p class="text-sm text-gray-500 truncate">
                    {{ order.items?.map((item: OrderItem) => item.product?.name).filter(Boolean).join(', ') || 'Sin productos' }}
                  </p>
                </div>
                <div class="flex-shrink-0">
                  <router-link
                    :to="{ path: `/orders/${order.id}`, state: { order } }"
                    class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50"
                  >
                    Ver detalles
                  </router-link>
                </div>
              </div>
            </div>

            <!-- Shipping/Delivery Info -->
            <div class="pt-4 mt-4 border-t border-gray-200">
              <!-- Delivery Method -->
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center">
                  <svg class="w-5 h-5 mr-2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  </svg>
                  <span class="text-sm font-medium text-gray-700">Método de entrega:</span>
                </div>
                <span :class="getDeliveryMethodClass(order.delivery_method || '')" 
                  class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                  {{ getDeliveryMethodText(order.delivery_method || '') }}
                </span>
              </div>

              <!-- Tracking Info (for shipping orders) -->
              <div v-if="isShippingOrder(order.delivery_method || '')" class="space-y-3">
                <!-- Tracking Number -->
                <div v-if="order.tracking_number" class="flex items-center justify-between">
                  <div class="flex items-center">
                    <svg class="w-5 h-5 mr-2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span class="text-sm font-medium text-gray-700">Numero de seguimiento:</span>
                  </div>
                  <div class="text-right">
                    <div class="font-mono text-sm text-gray-900">{{ order.tracking_number }}</div>
                    <div v-if="order.shipping_provider" class="text-xs text-gray-500">{{ getShippingProviderName(order.shipping_provider) }}</div>
                  </div>
                </div>

                <!-- Track Shipment Button -->
                <div v-if="order.tracking_number" class="flex justify-end">
                  <button @click="trackShipment(order.tracking_number, order.shipping_provider || '')"
                    class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700">
                    <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-2M7 7l10 10M17 7l-4 4" />
                    </svg>
                    Seguir envio
                  </button>
                </div>

                <!-- No tracking yet -->
                <div v-else-if="order.status === 'approved'" class="py-3 text-center rounded-lg bg-blue-50">
                  <svg class="w-8 h-8 mx-auto mb-2 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p class="text-sm text-blue-700">Preparando envío</p>
                  <p class="mt-1 text-xs text-blue-600">Te notificaremos cuando el pedido sea enviado</p>
                </div>
              </div>

              <!-- Local Pickup Info -->
              <div v-else-if="order.delivery_method === 'retiro_local'" class="p-4 rounded-lg bg-purple-50">
                <div class="flex items-start">
                  <svg class="w-5 h-5 text-purple-600 mt-0.5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <div class="flex-1">
                    <h4 class="mb-2 text-sm font-medium text-purple-900">Retiro en Local</h4>
                    
                    <div v-if="order.status === 'approved'" class="space-y-2">
                      <p class="text-sm text-purple-700">
                        Tu pedido estÃ¡ listo para retirar. Coordina tu horario de retiro:
                      </p>
                      <div class="p-3 text-sm bg-white rounded">
                        <div class="mb-1 font-medium text-gray-900">Informacin de contacto:</div>
                        <div class="text-gray-700">ðŸ“± WhatsApp: +54 9 11 1234-5678</div>
                        <div class="text-gray-700">ðŸ“ Direccin: Av. Ejemplo 123, CABA</div>
                        <div class="text-gray-700">ðŸ• Horarios: Lun-Vie 9-18hs, SÃ¡b 9-13hs</div>
                      </div>
                      <button @click="contactForPickup(order)" 
                        class="flex items-center justify-center w-full px-4 py-2 text-sm font-medium text-white bg-purple-600 border border-transparent rounded-md hover:bg-purple-700">
                        <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        Contactar por WhatsApp
                      </button>
                    </div>
                    
                    <div v-else class="text-sm text-purple-700">
                      Una vez que tu pago sea confirmado, podrÃ¡s coordinar el retiro.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="hasError" class="py-12 text-center">
        <div class="w-24 h-24 mx-auto mb-4 text-red-400">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 class="mb-2 text-lg font-medium text-gray-900">Error al cargar pedidos</h3>
        <p class="mb-6 text-gray-600">Hubo un problema al cargar tus pedidos. Por favor, intenta nuevamente.</p>
        <button
          @click="loadOrders"
          :disabled="loading"
          class="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 disabled:bg-gray-400"
        >
          <span v-if="loading">Cargando...</span>
          <span v-else>Reintentar</span>
        </button>
      </div>

      <!-- Empty State -->
      <div v-else class="py-12 text-center">
        <div class="w-24 h-24 mx-auto mb-4 text-gray-400">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
        </div>
        <h3 class="mb-2 text-lg font-medium text-gray-900">No tienes pedidos aún</h3>
        <p class="mb-6 text-gray-600">Cuando realices tu primera compra, aparecerá aquí</p>
        <div class="space-x-4">
          <router-link
            to="/shop"
            class="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-black border border-transparent rounded-md hover:bg-gray-800"
          >
            Comenzar a comprar
          </router-link>
          <button
            @click="loadOrders"
            :disabled="loading"
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 disabled:bg-gray-100"
          >
            Actualizar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../store/auth';
import { useToast } from 'vue-toastification';
import { ordersApi } from '../../config/api';
import type { Order, OrderItem } from '../../types';
import { 
  getShippingStatusClass, 
  getShippingStatusText,
  getDeliveryMethodClass,
  getDeliveryMethodText 
} from '../../utils/orderStatusUtils';

const authStore = useAuthStore();
const router = useRouter();
const toast = useToast();

const orders = ref<Order[]>([]);
const loading = ref(true);
const hasError = ref(false);

onMounted(async () => {
  // Check authentication
  if (!authStore.isAuthenticated) {
    toast.warning('Debes iniciar sesin para ver tus pedidos');
    router.push('/auth');
    return;
  }

  await loadOrders();
});

const loadOrders = async () => {
  try {
    loading.value = true;
    hasError.value = false; // Reset error state
    orders.value = await ordersApi.getMyOrders();

    // Si no hay pedidos pero no hubo error, mostrar info
    if (orders.value.length === 0) {
    }
    
  } catch (error: any) {
    // Manejo de errores específicos
    if (error?.response?.status === 401) {
      toast.error('Sesion expirada. Por favor, inicia sesión nuevamente.');
      authStore.logout();
      router.push('/auth');
    } else if (error?.response?.status === 400) {
      toast.error('Error en la solicitud. Intenta cerrar sesión y volver a iniciar.');
    } else if (error?.response?.status === 404) {
      toast.error('Error del servidor. El servicio no está disponible.');
    } else if (error?.response?.status >= 500) {
      toast.error('Error del servidor. Por favor, intenta más tarde.');
    } else if (error?.code === 'NETWORK_ERROR' || error?.message?.includes('Network Error')) {
      toast.error('Error de conexión. Verifica tu internet e intenta nuevamente.');
    } else {
      toast.error(`Error al cargar los pedidos: ${error?.response?.data?.detail || error?.message || 'Error desconocido'}`);
    }
    
    hasError.value = true; // Set error state
    orders.value = [];
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return 'Fecha no disponible';
  const date = new Date(dateString);
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

// Status functions now imported from centralized orderStatusUtils

// Delivery method functions now imported from centralized orderStatusUtils

const isShippingOrder = (deliveryMethod: string | undefined) => {
  return deliveryMethod === 'envio_andreani' || deliveryMethod === 'envio_correo';
};

const getShippingProviderName = (provider: string) => {
  switch (provider) {
    case 'andreani':
      return 'Andreani';
    case 'correo-argentino':
      return 'Correo Argentino';
    default:
      return provider || 'Proveedor';
  }
};

// Tracking functions
const trackShipment = (trackingNumber: string | undefined, provider: string | undefined) => {
  if (!trackingNumber || !provider) {
    toast.error('Información de tracking no disponible');
    return;
  }
  
  let trackingUrl = '';
  
  switch (provider) {
    case 'andreani':
      trackingUrl = `https://www.andreani.com/seguimiento?codigo=${trackingNumber}`;
      break;
    case 'correo-argentino':
      trackingUrl = `https://www.correoargentino.com.ar/formularios/e-commerce?codigo=${trackingNumber}`;
      break;
    default:
      toast.info('Número de tracking copiado al portapapeles');
      navigator.clipboard.writeText(trackingNumber);
      return;
  }
  
  window.open(trackingUrl, '_blank');
};

const contactForPickup = (order: any) => {
  const message = `Hola! Soy ${order.customer_name || 'un cliente'} y tengo el pedido #${order.id} listo para retirar.


¿Cuando puedo pasar a retirarlo?`;

  const encodedMessage = encodeURIComponent(message);
  const whatsappUrl = `https://wa.me/5491112345678?text=${encodedMessage}`;
  
  window.open(whatsappUrl, '_blank');
};
</script>

