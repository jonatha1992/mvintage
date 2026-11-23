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
              Cambiar Estado del Pedido #{{ order?.order_id }}
            </h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Order Info -->
          <div v-if="order" class="p-4 mb-6 rounded-lg bg-gray-50">
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="font-medium text-gray-700">Cliente:</span>
                <div class="text-gray-900">{{ order.customer_name }}</div>
                <div class="text-gray-600">{{ order.customer_email }}</div>
              </div>
              <div>
                <span class="font-medium text-gray-700">Total:</span>
                <div class="font-medium text-gray-900">${{ order.total?.toLocaleString() }}</div>
                <span class="block mt-1 font-medium text-gray-700">Método de pago:</span>
                <div class="text-gray-600">{{ getPaymentMethodText(order.payment_method) }}</div>
              </div>
            </div>
          </div>

          <!-- Status Selection -->
          <form @submit.prevent="updateStatus">
            <div class="mb-4">
              <label for="newStatus" class="block mb-2 text-sm font-medium text-gray-700">
                Nuevo Estado de Pago
              </label>
              <select
                v-model="selectedStatus"
                id="newStatus"
                required
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Seleccionar estado...</option>
                <option value="pending">Pendiente de pago</option>
                <option value="approved">Pago confirmado</option>
                <option value="rejected">Cancelado</option>
              </select>
            </div>

            <!-- Admin Notes -->
            <div class="mb-6">
              <label for="adminNotes" class="block mb-2 text-sm font-medium text-gray-700">
                Notas del Administrador (opcional)
              </label>
              <textarea
                v-model="adminNotes"
                id="adminNotes"
                rows="3"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                placeholder="Agregar comentarios sobre la verificación del pago..."
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
                :disabled="!selectedStatus || loading"
                class="px-4 py-2 text-sm text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                <span class="text-white" v-if="loading">Actualizando...</span>
                <span class="text-white" v-else>Actualizar Estado</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

interface Order {
  order_id: number;
  customer_name: string;
  customer_email: string;
  total: number;
  payment_method: string;
  status: string;
}

interface Props {
  isOpen: boolean;
  order: Order | null;
}

interface Emits {
  (e: 'close'): void;
  (e: 'update-status', orderId: number, status: string, notes: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const selectedStatus = ref('');
const adminNotes = ref('');
const loading = ref(false);

// Reset form when modal opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen && props.order) {
    selectedStatus.value = props.order.status || '';
    adminNotes.value = '';
  }
});

const closeModal = () => {
  emit('close');
};

const updateStatus = async () => {
  if (!props.order || !selectedStatus.value) return;

  loading.value = true;
  try {
    emit('update-status', props.order.order_id, selectedStatus.value, adminNotes.value);
  } finally {
    loading.value = false;
  }
};

const getPaymentMethodText = (method: string): string => {
  const methods: Record<string, string> = {
    'transfer': 'Transferencia bancaria',
    'mercadopago': 'Mercado Pago',
    'cash': 'Efectivo'
  };
  return methods[method] || method;
};
</script>
