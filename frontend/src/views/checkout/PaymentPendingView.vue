<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-3xl px-4 py-16 mx-auto sm:px-6 lg:px-8">
      <div class="p-8 text-center bg-white rounded-lg shadow">
        <!-- Pending Icon -->
        <div class="flex items-center justify-center w-16 h-16 mx-auto mb-6 bg-yellow-100 rounded-full">
          <svg class="w-8 h-8 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        
        <!-- Pending Message -->
        <h1 class="mb-4 text-3xl font-bold text-gray-900">Pago pendiente</h1>
        <p class="mb-8 text-lg text-gray-600">
          Tu pago estÃ¡ siendo procesado. Te notificaremos cuando se complete la transaccin.
        </p>
        
        <!-- Order Details -->
        <div v-if="orderDetails" class="p-6 mb-8 rounded-lg bg-gray-50">
          <h2 class="mb-4 text-lg font-medium text-gray-900">Detalles de tu pedido</h2>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Número de orden:</span>
              <span class="font-medium">#{{ orderDetails.order_id }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Total:</span>
              <span class="font-medium">${{ orderDetails.total?.toLocaleString() }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Estado del pago:</span>
              <span class="font-medium text-yellow-600">{{ getPaymentStatusText(orderDetails.payment_status) }}</span>
            </div>
          </div>
        </div>
        
        <!-- Status Check -->
        <div class="mb-8">
          <button
            @click="checkPaymentStatus"
            :disabled="checking"
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 transition-colors bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:bg-gray-100"
          >
            <svg v-if="checking" class="w-4 h-4 mr-2 -ml-1 text-gray-500 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ checking ? 'Verificando...' : 'Verificar estado del pago' }}
          </button>
        </div>
        
        <!-- Actions -->
        <div class="space-y-4 sm:space-y-0 sm:space-x-4 sm:flex sm:justify-center">
          <router-link
            to="/"
            class="inline-flex items-center justify-center w-full px-6 py-3 text-base font-medium text-white transition-colors bg-gray-800 border border-transparent rounded-md sm:w-auto hover:bg-gray-900"
          >
            Volver al inicio
          </router-link>
          
          <router-link
            to="/shop"
            class="inline-flex items-center justify-center w-full px-6 py-3 text-base font-medium text-gray-700 transition-colors bg-white border border-gray-300 rounded-md sm:w-auto hover:bg-gray-50"
          >
            Seguir comprando
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { paymentsApi } from '../../config/api';
import { useToast } from 'vue-toastification';
import { useCartStore } from '../../store/cart';

const route = useRoute();
const router = useRouter();
const toast = useToast();
const cartStore = useCartStore();
const orderDetails = ref<any>(null);
const checking = ref(false);

const getPaymentStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'approved': 'Aprobado',
    'pending': 'Pendiente',
    'pending_payment': 'Pendiente de pago',
    'rejected': 'Rechazado',
    'cancelled': 'Cancelado'
  };
  return statusMap[status] || status;
};

const checkPaymentStatus = async () => {
  if (!orderDetails.value) return;
  
  checking.value = true;
  try {
    const updatedDetails = await paymentsApi.getPaymentStatus(orderDetails.value.order_id);
    orderDetails.value = updatedDetails;
    
    // Redirigir segun el nuevo estado
    if (updatedDetails.payment_status === 'approved') {
      toast.success('¡Pago aprobado!');
      router.push(`/payment/success?order_id=${updatedDetails.order_id}`);
    } else if (updatedDetails.payment_status === 'rejected') {
      toast.error('Pago rechazado');
      router.push(`/payment/failure?order_id=${updatedDetails.order_id}`);
    } else {
      toast.info('El pago sigue pendiente');
    }
  } catch (error) {
    toast.error('Error al verificar el estado del pago');
  } finally {
    checking.value = false;
  }
};

onMounted(async () => {
  // Clear cart since order was created successfully (even if payment is pending)
  cartStore.clearCart();
  
  // Clean up any stored order data
  localStorage.removeItem('pending_order');
  
  // Obtener order_id de los query params
  const orderId = route.query.external_reference || route.query.order_id;
  
  if (orderId) {
    try {
      orderDetails.value = await paymentsApi.getPaymentStatus(Number(orderId));
    } catch (error) {
      toast.error('Error obteniendo detalles del pedido');
    }
  }
});
</script>

