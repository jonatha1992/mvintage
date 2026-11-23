<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-3xl px-4 py-8 mx-auto sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8 text-center">
        <div class="w-16 h-16 mx-auto mb-4 text-green-600">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h1 class="text-3xl font-light text-gray-900">¡Pedido Confirmado!</h1>
        <p class="mt-2 text-lg text-gray-600">
          Orden #{{ orderData?.order_id || 'Cargando...' }}
        </p>
      </div>

      <div v-if="transferInfo" class="space-y-6">
        <!-- Datos de Transferencia -->
        <div v-if="hasValidBankInfo" class="p-6 bg-white rounded-lg shadow">
          <h2 class="flex items-center mb-6 text-xl font-medium text-gray-900">
            <svg class="w-6 h-6 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            Datos para Transferencia
          </h2>
          
          <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div class="space-y-4">
              <div class="p-4 border border-gray-200 rounded">
                <h3 class="mb-3 font-medium text-gray-900">Información Bancaria</h3>
                <div class="space-y-2 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-600">Banco:</span>
                    <span class="font-medium">{{ transferInfo.bank_info.bank_name }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Tipo de cuenta:</span>
                    <span class="font-medium">{{ transferInfo.bank_info.account_type }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Número de cuenta:</span>
                    <span class="font-mono font-medium">{{ transferInfo.bank_info.account_number }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">CBU:</span>
                    <span class="font-mono font-medium">{{ transferInfo.bank_info.cbu }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Alias:</span>
                    <span class="font-medium">{{ transferInfo.bank_info.alias }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Titular:</span>
                    <span class="font-medium">{{ transferInfo.bank_info.holder_name }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">CUIT:</span>
                    <span class="font-medium">{{ transferInfo.bank_info.cuit }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="space-y-4">
              <div class="p-4 border border-gray-200 rounded">
                <h3 class="mb-3 font-medium text-gray-900">Monto a Transferir</h3>
                <div class="text-center">
                  <div class="text-3xl font-bold text-green-600">
                    {{ formatPrice(transferInfo.total_amount) }}
                  </div>
                  <p class="mt-1 text-sm text-gray-600">Monto exacto</p>
                </div>
              </div>
              
              <div class="p-4 border border-gray-200 rounded">
                <h3 class="mb-3 font-medium text-gray-900">Referencia</h3>
                <div class="text-center">
                  <div class="p-2 font-mono text-lg font-medium bg-gray-100 rounded">
                    {{ transferInfo.reference }}
                  </div>
                  <p class="mt-1 text-xs text-gray-600">Incluir en el detalle de transferencia</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Datos por WhatsApp si falta información bancaria real -->
        <div v-if="!hasValidBankInfo" class="p-6 text-center bg-white rounded-lg shadow">
          <h2 class="mb-3 text-xl font-medium text-gray-900">Te enviamos los datos para transferir por WhatsApp</h2>
          <p class="mb-4 text-sm text-gray-600">
            Monto a transferir: <strong class="text-gray-900">{{ formatPrice(transferInfo.total_amount) }}</strong>
          </p>
          <a
            :href="whatsappTransferUrl"
            target="_blank"
            rel="noopener"
            class="inline-flex items-center justify-center px-6 py-3 font-medium text-white transition-colors bg-green-600 rounded-md hover:bg-green-700"
          >
            Pedir datos por WhatsApp
          </a>
        </div>

        <!-- Instrucciones -->
        <div v-if="hasValidBankInfo" class="p-6 bg-white rounded-lg shadow">
          <h2 class="flex items-center mb-4 text-xl font-medium text-gray-900">
            <svg class="w-6 h-6 mr-2 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Instrucciones Importantes
          </h2>
          
          <div class="space-y-3">
            <div v-for="(instruction, index) in transferInfo.instructions" :key="index" class="flex items-start">
              <div class="flex-shrink-0 h-6 w-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
                {{ index + 1 }}
              </div>
              <p class="text-gray-700">{{ instruction }}</p>
            </div>
          </div>
        </div>

        <!-- Información del Cliente -->
        <div class="p-6 bg-white rounded-lg shadow">
          <h2 class="mb-4 text-xl font-medium text-gray-900">Información de Retiro</h2>
          <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div>
              <h3 class="mb-2 font-medium text-gray-900">Datos de Contacto</h3>
              <div class="space-y-1 text-sm">
                <p><span class="text-gray-600">Nombre:</span> {{ customerInfo.name }}</p>
                <p><span class="text-gray-600">Email:</span> {{ customerInfo.email }}</p>
                <p><span class="text-gray-600">Teléfono:</span> {{ customerInfo.phone }}</p>
              </div>
            </div>
            <div>
              <h3 class="mb-2 font-medium text-gray-900">Retiro en el local</h3>
              <div class="text-sm text-gray-700">
                <p>Te avisamos por WhatsApp cuando tu pedido esté listo para retirar.</p>
                <p v-if="customerInfo.delivery_notes" class="mt-1 text-gray-600">
                  Notas: {{ customerInfo.delivery_notes }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Acciones -->
        <div class="p-6 bg-white rounded-lg shadow">
          <div class="flex flex-col gap-4 sm:flex-row">
            <button
              v-if="hasValidBankInfo"
              @click="copyTransferData"
              class="flex items-center justify-center flex-1 px-4 py-3 font-medium text-white transition-colors bg-gray-500 rounded-md hover:bg-gray-700"
            >
              <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copiar Datos
            </button>
            
            <button
              @click="goHome"
              class="flex-1 px-4 py-3 font-medium text-gray-700 transition-colors border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Volver al Inicio
            </button>
          </div>
          
          <p class="mt-4 text-xs text-center text-gray-500">
            Recibirás un email de confirmación con estos datos. Tu pedido será procesado una vez que verifiquemos la transferencia.
          </p>
        </div>
      </div>

      <!-- Loading state -->
      <div v-else class="py-12 text-center">
        <div class="w-12 h-12 mx-auto mb-4 border-b-2 border-blue-600 rounded-full animate-spin"></div>
        <p class="text-gray-600">Cargando información de transferencia...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatPrice } from '../../utils/price'
import { WHATSAPP_NUMBER } from '../../config/payments'
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import type { TransferInfo, Customer } from '../../types';

const router = useRouter();
const toast = useToast();

const orderData = ref<any>(null);
const transferInfo = ref<TransferInfo | null>(null);
const customerInfo = ref<Customer | any>({});

onMounted(() => {
  const storedData = localStorage.getItem('transfer_order');
  if (storedData) {
    try {
      const data = JSON.parse(storedData);
      orderData.value = data;
      transferInfo.value = data.transfer_info;
      customerInfo.value = data.customer;
      
      // Clear stored data to prevent reuse
      localStorage.removeItem('transfer_order');
    } catch (error) {
      toast.error('Error cargando datos de transferencia');
      router.push('/');
    }
  } else {
    toast.warning('No se encontraron datos de transferencia');
    router.push('/');
  }
});

const hasValidBankInfo = computed(() => {
  const bank = transferInfo.value?.bank_info;
  if (!bank?.cbu?.trim()) return false;
  if (bank.alias?.trim().toLowerCase() === 'mvintage') return false;
  if (bank.holder_name?.toLowerCase().includes('m-vintage')) return false;
  return true;
});

const whatsappTransferUrl = computed(() => {
  const orderId = orderData.value?.order_id ?? '';
  const message = `Hola! Realicé el pedido #${orderId} y necesito los datos para transferir.`;
  return `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(message)}`;
});

const copyTransferData = () => {
  if (!transferInfo.value) return;
  
  const data = `
Datos de Transferencia - Orden #${orderData.value.order_id}

Banco: ${transferInfo.value.bank_info.bank_name}
CBU: ${transferInfo.value.bank_info.cbu}
Alias: ${transferInfo.value.bank_info.alias}
Titular: ${transferInfo.value.bank_info.holder_name}
Monto: ${formatPrice(transferInfo.value.total_amount)}
Referencia: ${transferInfo.value.reference}
  `.trim();
  
  navigator.clipboard.writeText(data).then(() => {
    toast.success('Datos copiados al portapapeles');
  }).catch(() => {
    toast.error('Error copiando los datos');
  });
};

const goHome = () => {
  router.push('/');
};
</script>
