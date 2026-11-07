<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-3xl px-4 py-16 mx-auto sm:px-6 lg:px-8">
      <div class="p-8 text-center bg-white rounded-lg shadow">
        <!-- Error Icon -->
        <div class="flex items-center justify-center w-16 h-16 mx-auto mb-6 bg-red-100 rounded-full">
          <svg class="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        
        <!-- Error Message -->
        <h1 class="mb-4 text-3xl font-bold text-gray-900">Pago no procesado</h1>
        <p class="mb-8 text-lg text-gray-600">
          Hubo un problema al procesar tu pago. No te preocupes, no se realizó ningún cargo.
        </p>
        
        <!-- Order Details -->
        <div v-if="orderDetails" class="p-6 mb-8 rounded-lg bg-gray-50">
          <h2 class="mb-4 text-lg font-medium text-gray-900">Detalles del pedido</h2>
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
              <span class="font-medium text-red-600">{{ getPaymentStatusText(orderDetails.payment_status) }}</span>
            </div>
          </div>
        </div>
        
        <!-- Actions -->
        <div class="space-y-4 sm:space-y-0 sm:space-x-4 sm:flex sm:justify-center">
          <button
            @click="retryPayment"
            :disabled="!orderDetails"
            class="inline-flex items-center justify-center w-full px-6 py-3 text-base font-medium text-white transition-colors bg-gray-800 border border-transparent rounded-md sm:w-auto hover:bg-gray-900 disabled:bg-gray-400"
          >
            Intentar nuevamente
          </button>
          
          <router-link
            to="/cart"
            class="inline-flex items-center justify-center w-full px-6 py-3 text-base font-medium text-gray-700 transition-colors bg-white border border-gray-300 rounded-md sm:w-auto hover:bg-gray-50"
          >
            Volver al carrito
          </router-link>
          
          <router-link
            to="/"
            class="inline-flex items-center justify-center w-full px-6 py-3 text-base font-medium text-gray-700 transition-colors bg-white border border-gray-300 rounded-md sm:w-auto hover:bg-gray-50"
          >
            Volver al inicio
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { paymentsApi } from '../../config/api';
import { useToast } from 'vue-toastification';

const route = useRoute();
const toast = useToast();
const orderDetails = ref<any>(null);

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

const retryPayment = async () => {
  if (!orderDetails.value) return;
  
  try {
    const preference = await paymentsApi.createPreference(orderDetails.value.order_id);
    // Redirigir a MercadoPago
    window.location.href = preference.init_point;
  } catch (error) {
    toast.error('Error al reintentar el pago');
  }
};

onMounted(async () => {
  // Clean up stored order data (payment failed, so clean up)
  localStorage.removeItem('pending_order');
  
  // Note: Do NOT clear cart here - user might want to retry purchase
  
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

