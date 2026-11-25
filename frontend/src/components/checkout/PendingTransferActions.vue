<template>
  <section v-if="canChange" class="p-5 space-y-3 bg-white border border-gray-200 rounded-lg" aria-label="Cambiar o cancelar el pago pendiente">
    <p class="text-sm text-gray-700">Si todavía no transferiste, podés elegir otra forma de pago o cancelar tu pedido.</p>
    <button type="button" :disabled="busy" class="w-full min-h-11 px-4 py-3 text-white bg-gray-900 rounded-md transition-colors hover:bg-gray-700 disabled:opacity-60 motion-safe:active:scale-[0.98]" @click="payWithMercadoPago">Prefiero pagar con Mercado Pago</button>
    <button type="button" :disabled="busy" class="w-full min-h-11 px-4 py-3 text-red-800 border border-red-300 rounded-md transition-colors hover:bg-red-50 disabled:opacity-60" @click="cancelOrder">Cancelar pedido</button>
    <p role="status" aria-live="polite" class="text-sm text-gray-700">{{ message }}</p>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ordersApi } from '../../config/api'
import type { Order } from '../../types'

const props = defineProps<{ orderId: number }>()
const emit = defineEmits<{ updated: [] }>()
const order = ref<Order | null>(null)
const busy = ref(false)
const message = ref('')
const canChange = computed(() => order.value?.payment_method === 'bank_transfer'
  && order.value.payment_status === 'pending_payment'
  && !order.value.transfer_verified && !order.value.verified_by_admin && !order.value.stock_released)

const load = async () => {
  try { order.value = await ordersApi.getOrder(props.orderId) }
  catch { order.value = null }
}
onMounted(load)

const payWithMercadoPago = async () => {
  busy.value = true
  message.value = 'Preparando el pago con Mercado Pago…'
  try {
    const result = await ordersApi.payWithMercadoPago(props.orderId)
    window.location.assign(result.checkout_url)
  } catch {
    message.value = 'No pudimos cambiar el pago. Revisá el estado del pedido e intentá de nuevo.'
    await load()
  } finally { busy.value = false }
}

const cancelOrder = async () => {
  if (!window.confirm('¿Cancelar este pedido? Se devolverán las prendas al stock. Hacelo solo si todavía no pagaste.')) return
  busy.value = true
  try {
    await ordersApi.cancelPendingOrder(props.orderId)
    await load()
    emit('updated')
  } catch {
    message.value = 'No pudimos cancelar. El pedido puede haber sido pagado o verificado; revisá su estado.'
    await load()
  } finally { busy.value = false }
}
</script>
