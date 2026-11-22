<template>
  <main class="min-h-screen px-4 py-12 bg-gray-50 sm:px-6">
    <section class="max-w-2xl p-6 mx-auto bg-white rounded-lg shadow sm:p-8">
      <h1 class="text-2xl font-light text-gray-900 font-heading">Pedido confirmado</h1>

      <div v-if="pickupInfo" class="mt-6">
        <p class="text-base text-gray-700 font-body">
          Te contactaremos cuando el pedido esté listo para coordinar el retiro en Showroom Isabella.
        </p>
        <dl class="p-4 mt-5 space-y-2 rounded-md bg-gray-50">
          <div class="flex justify-between gap-4">
            <dt class="text-sm text-gray-600">Pedido</dt>
            <dd class="text-sm font-medium text-gray-900">#{{ pickupInfo.order_id }}</dd>
          </div>
          <div class="flex justify-between gap-4">
            <dt class="text-sm text-gray-600">Total a pagar al retirar</dt>
            <dd class="text-sm font-medium text-gray-900">{{ formatPrice(pickupInfo.final_total) }}</dd>
          </div>
        </dl>
        <ul class="mt-5 space-y-2 text-sm text-gray-700 list-disc list-inside font-body">
          <li v-for="instruction in pickupInfo.instructions" :key="instruction">{{ instruction }}</li>
        </ul>
      </div>

      <div v-else class="p-4 mt-6 text-sm text-red-800 border border-red-200 rounded-md bg-red-50" role="alert">
        No encontramos los datos del pedido. Revisá tus pedidos o contactanos para recibir ayuda.
      </div>

      <router-link to="/orders" class="inline-flex mt-6 text-sm font-medium text-gray-900 underline underline-offset-4">
        Ver mis pedidos
      </router-link>
    </section>
  </main>
</template>

<script setup lang="ts">
import { formatPrice } from '../../utils/price'
import { onMounted, ref } from 'vue'

interface PickupInfo {
  order_id: number
  final_total: number
  instructions: string[]
}

const pickupInfo = ref<PickupInfo | null>(null)

onMounted(() => {
  const storedOrder = localStorage.getItem('cash_order')
  if (!storedOrder) return

  try {
    const parsed = JSON.parse(storedOrder) as { delivery_info?: PickupInfo }
    pickupInfo.value = parsed.delivery_info ?? null
  } catch (error) {
    console.error('No se pudieron leer los datos locales del pedido', error)
  }
})
</script>
