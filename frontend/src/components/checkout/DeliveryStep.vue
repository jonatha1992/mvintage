<template>
  <section class="p-6 bg-white rounded-lg shadow" aria-labelledby="pickup-title">
    <div class="flex items-start gap-3">
      <MapPinIcon class="w-6 h-6 mt-0.5 text-gray-700 shrink-0" aria-hidden="true" />
      <div>
        <h3 id="pickup-title" class="text-lg font-medium text-gray-900 font-heading">
          Retiro en el showroom
        </h3>
        <p class="mt-1 text-sm text-gray-600 font-body">
          Tu compra se retira sin costo. Cuando esté lista, te contactaremos para coordinar día y horario.
        </p>
      </div>
    </div>

    <div class="pt-4 mt-5 border-t border-gray-200">
      <button
        type="button"
        :disabled="!contactComplete"
        class="inline-flex items-center justify-center w-full px-6 py-3 text-base font-medium text-white transition-colors bg-black rounded-md sm:w-auto hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed"
        @click="$emit('continue')"
      >
        Continuar al pago
      </button>
      <p v-if="!contactComplete" class="mt-2 text-sm text-gray-600 font-body" role="status">
        Completá tus datos de contacto para continuar.
      </p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { MapPinIcon } from '@heroicons/vue/24/outline'

defineProps<{
  contactComplete: boolean
}>()

const emit = defineEmits<{
  'delivery-method-changed': [data: { method: 'retiro_local'; cost: 0 }]
  'continue': []
}>()

onMounted(() => {
  emit('delivery-method-changed', { method: 'retiro_local', cost: 0 })
})
</script>
