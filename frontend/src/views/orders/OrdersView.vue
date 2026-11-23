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
                  :class="getOrderPickupStatusConfig(order).class"
                >
                  {{ getOrderPickupStatusConfig(order).text }}
                </span>
                <p class="mt-1 text-lg font-medium text-gray-900">
                  {{ formatPrice(order.total) }}
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

            <!-- Local Pickup Info -->
            <div class="pt-4 mt-4 border-t border-gray-200">
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center">
                  <svg class="w-5 h-5 mr-2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span class="text-sm font-medium text-gray-700">Modalidad:</span>
                </div>
                <span :class="getDeliveryMethodClass(order.delivery_method || 'retiro_local')" 
                  class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                  {{ getDeliveryMethodText(order.delivery_method || 'retiro_local') }}
                </span>
              </div>

              <div class="p-4 rounded-lg bg-gray-50">
                <p class="text-sm text-gray-700">
                  Te avisamos por WhatsApp cuando tu pedido esté listo para retirar.
                </p>
                <button
                  v-if="order.payment_status === 'approved' || order.status === 'approved'"
                  @click="contactForPickup(order)"
                  class="inline-flex items-center justify-center mt-3 px-4 py-2 text-sm font-medium text-white bg-black border border-transparent rounded-md hover:bg-gray-800"
                >
                  Consultar retiro por WhatsApp
                </button>
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
import { formatPrice } from '../../utils/price'
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../store/auth';
import { useToast } from 'vue-toastification';
import { ordersApi } from '../../config/api';
import type { Order, OrderItem } from '../../types';
import { WHATSAPP_NUMBER } from '../../config/payments';
import { 
  getOrderPickupStatusConfig,
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
    toast.warning('Debes iniciar sesión para ver tus pedidos');
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
      toast.error('Sesión expirada. Por favor, inicia sesión nuevamente.');
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

const contactForPickup = (order: any) => {
  const message = `Hola! Soy ${order.customer_name || 'un cliente'} y quiero coordinar el retiro de mi pedido #${order.id}.`;
  const encodedMessage = encodeURIComponent(message);
  const whatsappUrl = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodedMessage}`;
  
  window.open(whatsappUrl, '_blank');
};
</script>

