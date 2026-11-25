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
        <h1 class="text-3xl font-light text-gray-900">Pedido recibido · Esperando tu transferencia</h1>
        <p class="mt-2 text-lg text-gray-600">
          Recibimos tu pedido #{{ orderData?.order_id || 'Cargando...' }}
        </p>
      </div>

      <div v-if="transferInfo" class="space-y-6">
        <router-link v-if="orderData?.order_id" :to="orderLink(Number(orderData.order_id))" class="inline-flex items-center min-h-11 px-3 underline">Ver mi pedido</router-link>
        <PendingTransferActions v-if="orderData?.order_id" :order-id="Number(orderData.order_id)" @updated="router.push(orderLink(Number(orderData.order_id)))" />
        <!-- Datos de Transferencia -->
        <div class="p-6 bg-white rounded-lg shadow">
          <h2 class="flex items-center mb-6 text-xl font-medium text-gray-900">
            <svg class="w-6 h-6 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            Datos para Transferencia
          </h2>
          
          <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div class="space-y-4">
              <div class="p-4 border border-gray-200 rounded">
                <h3 class="mb-3 font-medium text-gray-900">Información Bancaria</h3>
                <div class="space-y-3 text-sm">
                  <div class="flex flex-wrap items-center justify-between gap-2 p-3 rounded-md bg-gray-50">
                    <div>
                      <span class="block text-xs text-gray-600">Alias</span>
                      <span id="transfer-alias" class="font-mono text-lg font-semibold text-gray-900">{{ displayAlias }}</span>
                    </div>
                    <span class="copy-control">
                      <button
                        type="button"
                        class="copy-button inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-white transition-colors bg-gray-900 rounded-md hover:bg-gray-700"
                        command="--copy"
                        commandfor="transfer-alias"
                      >
                        <svg class="w-4 h-4 icon-copy" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                        <svg class="w-4 h-4 icon-check" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                        <span>Copiar alias</span>
                      </button>
                      <span class="copy-tip" role="status"></span>
                    </span>
                  </div>
                  <div v-if="hasValidBankInfo && transferInfo.bank_info.bank_name?.trim()" class="flex justify-between">
                    <span class="text-gray-600">Banco:</span>
                    <span class="font-medium">{{ transferInfo.bank_info.bank_name }}</span>
                  </div>
                  <div v-if="hasValidBankInfo && transferInfo.bank_info.account_type?.trim()" class="flex justify-between">
                    <span class="text-gray-600">Tipo de cuenta:</span>
                    <span class="font-medium">{{ transferInfo.bank_info.account_type }}</span>
                  </div>
                  <div v-if="hasValidBankInfo && transferInfo.bank_info.account_number?.trim()" class="flex justify-between">
                    <span class="text-gray-600">Número de cuenta:</span>
                    <span class="font-mono font-medium">{{ transferInfo.bank_info.account_number }}</span>
                  </div>
                  <div v-if="hasValidBankInfo && transferInfo.bank_info.cbu?.trim()" class="flex justify-between">
                    <span class="text-gray-600">CBU:</span>
                    <span class="font-mono font-medium">{{ transferInfo.bank_info.cbu }}</span>
                  </div>
                  <div v-if="hasValidBankInfo && transferInfo.bank_info.holder_name?.trim()" class="flex justify-between">
                    <span class="text-gray-600">Titular:</span>
                    <span class="font-medium">{{ transferInfo.bank_info.holder_name }}</span>
                  </div>
                  <div v-if="hasValidBankInfo && transferInfo.bank_info.cuit?.trim()" class="flex justify-between">
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

        <!-- Enviar comprobante por WhatsApp -->
        <div class="p-6 text-center bg-white rounded-lg shadow">
          <h2 class="mb-2 text-xl font-medium text-gray-900">Enviá el comprobante por WhatsApp</h2>
          <p class="mb-4 text-sm text-gray-600">
            Mandá el comprobante por WhatsApp e indicá el número de pedido #{{ orderData?.order_id }}. Te confirmamos el pago por mail y coordinamos el retiro en el local.
          </p>
          <a
            :href="whatsappTransferUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center justify-center px-6 py-3 font-medium text-white transition-colors bg-green-700 rounded-md hover:bg-green-800"
          >
            Enviar comprobante por WhatsApp
          </a>
        </div>

        <!-- Instrucciones -->
        <div class="p-6 bg-white rounded-lg shadow">
          <h2 class="flex items-center mb-4 text-xl font-medium text-gray-900">
            <svg class="w-6 h-6 mr-2 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Instrucciones Importantes
          </h2>
          
          <div class="space-y-3">
            <ol class="pl-5 space-y-3 text-gray-900 list-decimal">
              <li>Transferí <strong>{{ formatPrice(transferInfo.total_amount) }}</strong> al alias <strong>{{ displayAlias }}</strong>, a nombre de <strong>{{ transferInfo.bank_info?.holder_name || 'Priscila Moyano' }}</strong>.</li>
              <li>Mandá el comprobante por WhatsApp e indicá el número de pedido <strong>#{{ orderData?.order_id }}</strong>.</li>
              <li>Te confirmamos el pago por mail y coordinamos el retiro en el local.</li>
            </ol>
            <p class="mt-4 text-gray-700">Tu pedido queda pendiente de pago hasta que verifiquemos la transferencia. Crear el pedido no confirma el pago. La reserva vence a las 24 horas.</p>

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
              <div class="space-y-1 text-sm text-gray-700">
                <p>
                  <a :href="STORE_MAPS_URL" target="_blank" rel="noopener noreferrer" class="underline text-gray-900 hover:text-gray-600">
                    {{ STORE_PICKUP_ADDRESS }}
                  </a>
                </p>
                <p>{{ STORE_PICKUP_HOURS }}. Te avisamos por WhatsApp cuando tu pedido esté listo para retirar.</p>
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
              type="button"
              @click="copyTransferData"
              class="flex items-center justify-center flex-1 px-4 py-3 font-medium text-white transition-colors bg-gray-700 rounded-md hover:bg-gray-900"
            >
              <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copiar Datos
            </button>
            
            <button
              type="button"
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
import PendingTransferActions from '../../components/checkout/PendingTransferActions.vue'
import { orderLink } from '../../utils/orderAccess'
import { formatPrice } from '../../utils/price'
import { WHATSAPP_NUMBER } from '../../config/payments'
import { STORE_MAPS_URL, STORE_PICKUP_ADDRESS, STORE_PICKUP_HOURS, TRANSFER_ALIAS } from '../../config/store'
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import type { TransferInfo, Customer } from '../../types';

const router = useRouter();
const toast = useToast();

const orderData = ref<any>(null);
const transferInfo = ref<TransferInfo | null>(null);
const customerInfo = ref<Customer | any>({});

const copyTimers = new WeakMap<HTMLElement, number>();
let lastCopyMessage = '';

const reportCopy = (button: HTMLElement, ok: boolean) => {
  const tip = button.nextElementSibling as HTMLElement | null;
  const existing = copyTimers.get(button);
  if (existing) clearTimeout(existing);
  button.removeAttribute('data-copied');
  button.removeAttribute('data-failed');
  let message = ok ? 'Copiado' : 'No se pudo copiar';
  if (message === lastCopyMessage) message += '\u00A0';
  lastCopyMessage = message;
  if (tip) tip.textContent = '';
  void button.offsetWidth;
  button.setAttribute(ok ? 'data-copied' : 'data-failed', '');
  requestAnimationFrame(() => {
    if (tip) tip.textContent = message;
  });
  copyTimers.set(button, window.setTimeout(() => {
    button.removeAttribute('data-copied');
    button.removeAttribute('data-failed');
    if (tip) tip.textContent = '';
  }, 2000));
};

const copyFromTarget = async (button: HTMLElement, target: HTMLElement) => {
  const text = target.innerText.trim();
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    reportCopy(button, true);
  } catch {
    reportCopy(button, false);
  }
};

const handleCommandCopy = (event: Event) => {
  const cmdEvent = event as Event & { command?: string; source?: HTMLElement | null; target?: EventTarget | null };
  if (cmdEvent.command === '--copy' && cmdEvent.source && cmdEvent.target instanceof HTMLElement) {
    copyFromTarget(cmdEvent.source, cmdEvent.target);
  }
};

const handleFallbackClickCopy = (event: MouseEvent) => {
  if (event.defaultPrevented) return;
  const el = event.target instanceof Element ? event.target.closest<HTMLElement>('button[command="--copy"]') : null;
  if (!el) return;
  const targetId = el.getAttribute('commandfor');
  const target = targetId ? document.getElementById(targetId) : null;
  if (target) copyFromTarget(el, target);
};

const supportsCommandEvent = typeof window !== 'undefined' && 'CommandEvent' in window;

onMounted(() => {
  if (supportsCommandEvent) {
    document.addEventListener('command', handleCommandCopy, true);
  } else {
    document.addEventListener('click', handleFallbackClickCopy);
  }

  const storedData = localStorage.getItem('transfer_order');
  if (storedData) {
    try {
      const data = JSON.parse(storedData);
      orderData.value = data;
      transferInfo.value = data.transfer_info;
      customerInfo.value = data.customer;
      
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

onUnmounted(() => {
  if (supportsCommandEvent) {
    document.removeEventListener('command', handleCommandCopy, true);
  } else {
    document.removeEventListener('click', handleFallbackClickCopy);
  }
});

const hasValidBankInfo = computed(() => {
  const bank = transferInfo.value?.bank_info;
  const alias = bank?.alias?.trim() || '';
  const cbu = bank?.cbu?.trim() || '';
  if (!alias && !cbu) return false;
  const lowerAlias = alias.toLowerCase();
  if (lowerAlias === 'mvintage' || lowerAlias.includes('matilda')) return false;
  const lowerHolder = (bank?.holder_name || '').toLowerCase();
  if (lowerHolder.includes('m-vintage') || lowerHolder.includes('matilda')) return false;
  return true;
});

const displayAlias = computed(() => {
  const alias = hasValidBankInfo.value ? transferInfo.value?.bank_info?.alias?.trim() : '';
  return alias || TRANSFER_ALIAS;
});

const whatsappTransferUrl = computed(() => {
  const orderId = orderData.value?.order_id ?? '';
  const total = transferInfo.value?.total_amount ? ` por ${formatPrice(transferInfo.value.total_amount)}` : '';
  const message = `Hola! Hice el pedido #${orderId}${total} y realicé la transferencia al alias ${displayAlias.value}. Te envío el comprobante.`;
  return `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(message)}`;
});

const copyTransferData = () => {
  if (!transferInfo.value) return;
  const bank = hasValidBankInfo.value ? transferInfo.value.bank_info : null;
  const lines = [
    `Datos de Transferencia - Orden #${orderData.value.order_id}`,
    '',
    `Alias: ${displayAlias.value}`,
    bank?.bank_name?.trim() ? `Banco: ${bank.bank_name.trim()}` : '',
    bank?.cbu?.trim() ? `CBU: ${bank.cbu.trim()}` : '',
    bank?.holder_name?.trim() ? `Titular: ${bank.holder_name.trim()}` : '',
    bank?.cuit?.trim() ? `CUIT: ${bank.cuit.trim()}` : '',
    `Monto: ${formatPrice(transferInfo.value.total_amount)}`,
    `Referencia: ${transferInfo.value.reference}`,
  ].filter((line, idx) => idx === 1 || Boolean(line));

  navigator.clipboard.writeText(lines.join('\n')).then(() => {
    toast.success('Datos copiados al portapapeles');
  }).catch(() => {
    toast.error('Error copiando los datos');
  });
};

const goHome = () => {
  router.push('/');
};
</script>

<style scoped>
.copy-control {
  position: relative;
  display: inline-flex;
  align-items: center;
}
.copy-button {
  min-inline-size: 24px;
  min-block-size: 36px;
}
.copy-button .icon-check {
  display: none;
}
.copy-button[data-copied] .icon-copy {
  display: none;
}
.copy-button[data-copied] .icon-check {
  display: block;
}
.copy-tip {
  position: absolute;
  inset-block-end: calc(100% + 6px);
  inset-inline-end: 0;
  padding: 2px 8px;
  border-radius: 4px;
  background: #111827;
  color: #fff;
  font-size: 12px;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 150ms ease;
}
.copy-button[data-copied] + .copy-tip,
.copy-button[data-failed] + .copy-tip {
  opacity: 1;
}
@media (prefers-reduced-motion: reduce) {
  .copy-tip {
    transition: opacity 150ms linear;
  }
}
</style>
