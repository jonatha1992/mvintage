<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="closeModal"></div>

      <!-- Modal panel -->
      <div class="inline-block px-4 pt-5 pb-4 overflow-hidden text-left align-bottom transition-all transform bg-white rounded-lg shadow-xl sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
        <div>
          <!-- Header -->
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium leading-6 text-gray-900 font-heading">
              Gestionar Envío - Pedido #{{ order?.order_id }}
            </h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Order Info -->
          <div v-if="order" class="mb-6 p-4 bg-gray-50 rounded-lg">
            <div class="grid grid-cols-1 gap-2 text-sm">
              <div>
                <span class="font-medium text-gray-700">Cliente:</span>
                <span class="text-gray-900">{{ order.customer_name }}</span>
              </div>
              <div>
                <span class="font-medium text-gray-700">Total:</span>
                <span class="text-gray-900 font-medium">${{ order.total?.toLocaleString() }}</span>
              </div>
              <div v-if="order.customer_phone">
                <span class="font-medium text-gray-700">Teléfono:</span>
                <span class="text-gray-900">{{ order.customer_phone }}</span>
              </div>
            </div>
          </div>

          <!-- Shipping Form -->
          <form @submit.prevent="updateShipping">
            <!-- Tracking Number (only for shipping orders) -->
            <div v-if="isShippingOrder" class="mb-4">
              <label for="trackingNumber" class="block text-sm font-medium text-gray-700 mb-2">
                Número de Seguimiento *
              </label>
              <input
                v-model="trackingNumber"
                type="text"
                id="trackingNumber"
                :required="isShippingOrder"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                :placeholder="getTrackingPlaceholder()"
              />
              <p v-if="shippingProvider" class="mt-1 text-xs text-gray-500">
                {{ getTrackingHint() }}
              </p>
            </div>

            <!-- Shipping Provider (only for shipping orders) -->
            <div v-if="isShippingOrder" class="mb-4">
              <label for="shippingProvider" class="block text-sm font-medium text-gray-700 mb-2">
                Empresa de Envío *
              </label>
              <select
                v-model="shippingProvider"
                id="shippingProvider"
                :required="isShippingOrder"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Seleccionar empresa...</option>
                <option value="andreani">Andreani</option>
                <option value="correo-argentino">Correo Argentino</option>
              </select>
            </div>

            <!-- Estimated Delivery Date (only for shipping orders) -->
            <div v-if="isShippingOrder" class="mb-4">
              <label for="estimatedDelivery" class="block text-sm font-medium text-gray-700 mb-2">
                Fecha Estimada de Entrega (opcional)
              </label>
              <input
                v-model="estimatedDelivery"
                type="date"
                id="estimatedDelivery"
                :min="today"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <!-- Local Pickup Coordination (only for pickup orders) -->
            <div v-if="!isShippingOrder" class="mb-6">
              <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <div class="flex items-start">
                  <svg class="w-5 h-5 text-purple-600 mt-0.5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <div class="flex-1">
                    <h4 class="text-sm font-medium text-purple-900 mb-2">Coordinar Retiro por WhatsApp</h4>
                    <p class="text-sm text-purple-700 mb-3">
                      Este pedido es para retiro en local. Haz clic en el botón para contactar al cliente por WhatsApp.
                    </p>
                    <button type="button" @click="contactCustomerForPickup" 
                      class="w-full flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700">
                      <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                      Contactar por WhatsApp
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Shipping Notes -->
            <div class="mb-6">
              <label for="shippingNotes" class="block text-sm font-medium text-gray-700 mb-2">
                Notas del Envío (opcional)
              </label>
              <textarea
                v-model="shippingNotes"
                id="shippingNotes"
                rows="3"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                placeholder="Instrucciones especiales, horarios de entrega, etc..."
              ></textarea>
            </div>

            <!-- Action Buttons -->
            <div class="flex justify-end space-x-3">
              <button
                type="button"
                @click="closeModal"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancelar
              </button>
              <button
                type="submit"
                :disabled="(isShippingOrder && (!trackingNumber || !shippingProvider)) || loading"
                class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                <span v-if="loading">Guardando...</span>
                <span v-else-if="isShippingOrder">Guardar Envío</span>
                <span v-else>Marcar como Entregado</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { Order } from '../../types/orders/order.types';

interface Props {
  isOpen: boolean;
  order: Order | null;
}

interface Emits {
  (e: 'close'): void;
  (e: 'update-shipping', orderId: number, shippingData: {
    trackingNumber: string;
    shippingProvider: string;
    estimatedDelivery?: string;
    shippingNotes?: string;
  }): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const trackingNumber = ref('');
const shippingProvider = ref('');
const estimatedDelivery = ref('');
const shippingNotes = ref('');
const loading = ref(false);

// Today's date for min date validation
const today = computed(() => {
  return new Date().toISOString().split('T')[0];
});

// Check if this is a shipping order (not pickup)
const isShippingOrder = computed(() => {
  return props.order?.delivery_method === 'envio_andreani' || props.order?.delivery_method === 'envio_correo';
});

// Helper functions for tracking
const getTrackingPlaceholder = () => {
  if (shippingProvider.value === 'andreani') return 'Ej: ABC12345678';
  if (shippingProvider.value === 'correo-argentino') return 'Ej: CC123456789AR';
  return 'Número de seguimiento';
};

const getTrackingHint = () => {
  if (shippingProvider.value === 'andreani') return 'Formato: 8-15 caracteres alfanuméricos';
  if (shippingProvider.value === 'correo-argentino') return 'Formato: 2 letras + 9 números + 2 letras';
  return '';
};

// Reset form when modal opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen && props.order) {
    trackingNumber.value = props.order.tracking_number || '';
    shippingProvider.value = props.order.shipping_provider || '';
    estimatedDelivery.value = props.order.estimated_delivery ? 
      new Date(props.order.estimated_delivery).toISOString().split('T')[0] : '';
    shippingNotes.value = '';
  }
});

const closeModal = () => {
  emit('close');
};

const contactCustomerForPickup = () => {
  if (!props.order) return;
  
  const message = `Hola ${props.order.customer_name}, tu pedido #${props.order.order_id} está listo para retirar. 

📦 Total: $${props.order.total.toLocaleString()}

📍 Dirección: Av. Ejemplo 123, CABA
🕐 Horarios: Lun-Vie 9-18hs, Sáb 9-13hs

¿Cuándo te conviene pasar a retirarlo?`;

  const encodedMessage = encodeURIComponent(message);
  const phoneNumber = props.order.customer_phone?.replace(/[^\d]/g, '') || '5491112345678';
  const whatsappUrl = `https://wa.me/${phoneNumber}?text=${encodedMessage}`;
  
  window.open(whatsappUrl, '_blank');
};

const updateShipping = async () => {
  if (!props.order) return;
  
  // Different validation based on delivery method
  if (isShippingOrder.value && (!trackingNumber.value || !shippingProvider.value)) {
    return;
  }

  loading.value = true;
  try {
    let shippingData;
    
    if (isShippingOrder.value) {
      // For shipping orders, include tracking info
      shippingData = {
        trackingNumber: trackingNumber.value.trim(),
        shippingProvider: shippingProvider.value,
        estimatedDelivery: estimatedDelivery.value || undefined,
        shippingNotes: shippingNotes.value.trim() || undefined
      };
    } else {
      // For pickup orders, just mark as completed
      shippingData = {
        trackingNumber: 'PICKUP_' + Date.now(), // Generate pickup reference
        shippingProvider: 'retiro_local',
        shippingNotes: shippingNotes.value.trim() || 'Pedido retirado en local'
      };
    }

    emit('update-shipping', props.order.order_id, shippingData);
  } finally {
    loading.value = false;
  }
};
</script>
