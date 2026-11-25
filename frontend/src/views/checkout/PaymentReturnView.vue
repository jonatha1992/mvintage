<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-6 shadow sm:rounded-lg text-center">
        <div v-if="viewState === 'checking'" class="space-y-4">
          <div class="mx-auto w-12 h-12 border-b-2 border-gray-900 rounded-full animate-spin"></div>
          <h1 class="text-2xl font-light text-gray-900">Estamos confirmando tu pago</h1>
          <p class="text-sm text-gray-600">
            Estamos confirmando el estado de tu pedido <span v-if="orderId">#{{ orderId }}</span> con Mercado Pago.
          </p>
        </div>

        <div v-else-if="viewState === 'paid'" class="space-y-4">
          <div class="mx-auto flex items-center justify-center h-14 w-14 rounded-full bg-green-100">
            <svg class="h-7 w-7 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 class="text-2xl font-light text-gray-900">¡Pago confirmado!</h1>
          <p class="text-sm text-gray-600">
            Tu pedido #{{ orderId }} fue pagado correctamente.
          </p>
          <p v-if="totalAmount !== null" class="text-lg font-medium text-gray-900">
            Total: {{ formatPrice(totalAmount) }}
          </p>
          <div class="pt-4 space-y-3">
            <router-link
              v-if="orderId"
              :to="orderLink(orderId)"
              class="w-full inline-flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800"
            >
              Ver mi pedido
            </router-link>
            <router-link
              :to="orderId ? orderLink(orderId) : '/shop'"
              class="w-full inline-flex justify-center py-2.5 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-800 bg-white hover:bg-gray-50"
            >
              Volver a la tienda
            </router-link>
          </div>
        </div>

        <div v-else-if="viewState === 'expired'" class="space-y-4">
          <div class="mx-auto flex items-center justify-center h-14 w-14 rounded-full bg-red-100">
            <svg class="h-7 w-7 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h1 class="text-2xl font-light text-gray-900">Pago vencido o cancelado</h1>
          <p class="text-sm text-gray-600">
            El tiempo para completar el pago del pedido #{{ orderId }} venció o el pago fue cancelado. El stock fue liberado.
          </p>
          <div class="pt-4 space-y-3">
            <router-link
              to="/shop"
              class="w-full inline-flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800"
            >
              Volver a la tienda
            </router-link>
            <router-link
              :to="orderId ? orderLink(orderId) : '/shop'"
              class="w-full inline-flex justify-center py-2.5 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-800 bg-white hover:bg-gray-50"
            >
              Ver mi pedido
            </router-link>
          </div>
        </div>

        <div v-else class="space-y-4">
          <div class="mx-auto flex items-center justify-center h-14 w-14 rounded-full bg-yellow-100">
            <svg class="h-7 w-7 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1 class="text-2xl font-light text-gray-900">Pago pendiente</h1>
          <p class="text-sm text-gray-600">
            {{ statusMessage || 'Todavía estamos esperando la confirmación de Mercado Pago. Podés verificar de nuevo o revisar tus pedidos.' }}
          </p>
          <div class="pt-4 space-y-3">
            <button
              type="button"
              @click="startPolling"
              class="w-full inline-flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800"
            >
              Volver a verificar
            </button>
            <router-link
              :to="orderId ? orderLink(orderId) : '/shop'"
              class="w-full inline-flex justify-center py-2.5 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-800 bg-white hover:bg-gray-50"
            >
              Ver mi pedido
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { paymentsApi } from '../../config/api';
import { useCartStore } from '../../store/cart';
import { orderAccessToken, orderLink } from '../../utils/orderAccess';
import { formatPrice } from '../../utils/price';

const POLL_INTERVAL_MS = 5000;
const MAX_POLL_DURATION_MS = 120000;

const route = useRoute();
const cartStore = useCartStore();

const orderId = ref<number | null>(null);
const totalAmount = ref<number | null>(null);
const viewState = ref<'checking' | 'paid' | 'pending' | 'expired'>('checking');
const statusMessage = ref('');

let pollTimer: ReturnType<typeof setTimeout> | null = null;
let startedAt = 0;

const clearTimer = () => {
  if (pollTimer !== null) {
    clearTimeout(pollTimer);
    pollTimer = null;
  }
};

const resolveOrderId = (): number | null => {
  const raw = route.query.order_id || route.query.external_reference;
  const parsed = Number(Array.isArray(raw) ? raw[0] : raw);
  if (Number.isInteger(parsed) && parsed > 0) return parsed;

  const stored = localStorage.getItem('pending_order');
  if (stored) {
    try {
      const data = JSON.parse(stored);
      const storedId = Number(data?.order_id);
      if (Number.isInteger(storedId) && storedId > 0) return storedId;
    } catch {
      return null;
    }
  }
  return null;
};

const pollOnce = async () => {
  if (!orderId.value) {
    viewState.value = 'pending';
    statusMessage.value = 'No pudimos identificar el pedido. Revisá tu historial en Mis Pedidos.';
    return;
  }

  try {
    const data = await paymentsApi.getPaymentStatus(orderId.value);
    if (typeof data?.total === 'number') {
      totalAmount.value = data.total;
    }

    const status = String(data?.payment_status || '').toLowerCase();
    if (status === 'approved' || status === 'paid') {
      viewState.value = 'paid';
      cartStore.clearCart();
      localStorage.removeItem('pending_order');
      return;
    }

    if (status === 'expired' || status === 'cancelled' || status === 'rejected' || status === 'needs_refund') {
      viewState.value = 'expired';
      localStorage.removeItem('pending_order');
      return;
    }
  } catch {
    // Reintentar hasta agotar el tiempo máximo
  }

  if (Date.now() - startedAt >= MAX_POLL_DURATION_MS) {
    viewState.value = 'pending';
    return;
  }

  pollTimer = setTimeout(pollOnce, POLL_INTERVAL_MS);
};

const startPolling = () => {
  clearTimer();
  startedAt = Date.now();
  viewState.value = 'checking';
  statusMessage.value = '';
  pollOnce();
};

onMounted(() => {
  orderId.value = resolveOrderId();
  if (orderId.value) orderAccessToken(orderId.value, route.query.access_token);
  startPolling();
});

onUnmounted(() => {
  clearTimer();
});
</script>
