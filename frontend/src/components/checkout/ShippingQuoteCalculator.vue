<template>
  <div class="bg-white rounded-lg border border-gray-200 p-6">
    <h3 class="text-lg font-medium text-gray-900 mb-4 font-heading">
      Calcular Costo de Envío
    </h3>

    <!-- Formulario de dirección -->
    <div class="space-y-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label for="postalCode" class="block text-sm font-medium text-gray-700 mb-1">
            Código Postal *
          </label>
          <input
            v-model="postalCode"
            type="text"
            id="postalCode"
            placeholder="Ej: 1000"
            maxlength="8"
            class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            @input="clearQuotes"
          />
        </div>
        <div>
          <label for="city" class="block text-sm font-medium text-gray-700 mb-1">
            Ciudad
          </label>
          <input
            v-model="city"
            type="text"
            id="city"
            placeholder="Ej: Buenos Aires"
            class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            @input="clearQuotes"
          />
        </div>
      </div>
      
      <div>
        <label for="province" class="block text-sm font-medium text-gray-700 mb-1">
          Provincia
        </label>
        <select
          v-model="province"
          id="province"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          @change="clearQuotes"
        >
          <option value="">Seleccionar provincia...</option>
          <option value="Buenos Aires">Buenos Aires</option>
          <option value="CABA">Ciudad Autónoma de Buenos Aires</option>
          <option value="Catamarca">Catamarca</option>
          <option value="Chaco">Chaco</option>
          <option value="Chubut">Chubut</option>
          <option value="Córdoba">Córdoba</option>
          <option value="Corrientes">Corrientes</option>
          <option value="Entre Ríos">Entre Ríos</option>
          <option value="Formosa">Formosa</option>
          <option value="Jujuy">Jujuy</option>
          <option value="La Pampa">La Pampa</option>
          <option value="La Rioja">La Rioja</option>
          <option value="Mendoza">Mendoza</option>
          <option value="Misiones">Misiones</option>
          <option value="Neuquén">Neuquén</option>
          <option value="Río Negro">Río Negro</option>
          <option value="Salta">Salta</option>
          <option value="San Juan">San Juan</option>
          <option value="San Luis">San Luis</option>
          <option value="Santa Cruz">Santa Cruz</option>
          <option value="Santa Fe">Santa Fe</option>
          <option value="Santiago del Estero">Santiago del Estero</option>
          <option value="Tierra del Fuego">Tierra del Fuego</option>
          <option value="Tucumán">Tucumán</option>
        </select>
      </div>
    </div>

    <!-- Botón para calcular -->
    <button
      @click="calculateShipping"
      :disabled="!postalCode || loading"
      class="w-full flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
    >
      <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      {{ loading ? 'Calculando...' : 'Calcular Envío' }}
    </button>

    <!-- Resultados de cotización -->
    <div v-if="quotes.length > 0" class="mt-6">
      <h4 class="text-md font-medium text-gray-900 mb-3">Opciones de Envío</h4>
      
      <!-- Mensaje de estado de la API -->
      <div v-if="quoteResponse?.message" class="mb-4 p-3 rounded-md" :class="quoteResponse.api_available ? 'bg-yellow-50 border border-yellow-200' : 'bg-red-50 border border-red-200'">
        <div class="flex">
          <svg class="w-5 h-5 mt-0.5 mr-2" :class="quoteResponse.api_available ? 'text-yellow-600' : 'text-red-600'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 15.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <p class="text-sm" :class="quoteResponse.api_available ? 'text-yellow-800' : 'text-red-800'">
            {{ quoteResponse.message }}
          </p>
        </div>
      </div>

      <div class="space-y-3">
        <div
          v-for="quote in quotes"
          :key="quote.carrier"
          class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors cursor-pointer"
          :class="{ 'border-blue-500 bg-blue-50': selectedQuote?.carrier === quote.carrier }"
          @click="selectQuote(quote)"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                type="radio"
                :id="`quote-${quote.carrier}`"
                :value="quote.carrier"
                v-model="selectedCarrier"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <div class="ml-3">
                <label :for="`quote-${quote.carrier}`" class="block text-sm font-medium text-gray-900 cursor-pointer">
                  {{ quote.name }}
                </label>
                <p class="text-sm text-gray-500">{{ quote.estimated_delivery_text }}</p>
                <p v-if="quote.has_error" class="text-xs text-orange-600 mt-1">
                  ⚠️ {{ quote.error_message }}
                </p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-lg font-semibold text-gray-900">
                ${{ quote.price.toLocaleString() }}
              </p>
              <p class="text-sm text-gray-500">{{ quote.currency }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error message -->
    <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
      <div class="flex">
        <svg class="w-5 h-5 text-red-600 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-sm text-red-800">{{ error }}</p>
      </div>
    </div>

    <!-- Información del peso -->
    <div v-if="totalWeight > 0" class="mt-4 p-3 bg-gray-50 rounded-md">
      <p class="text-sm text-gray-600">
        <span class="font-medium">Peso total del pedido:</span> {{ totalWeight.toFixed(1) }} kg
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { shippingQuotesApi } from '../../config/api'
import type { ShippingQuoteOption, ShippingQuoteResponse } from '../../types/orders/shipping.types'

interface Props {
  totalWeight?: number
  modelValue?: ShippingQuoteOption | null
}

interface Emits {
  (e: 'update:modelValue', value: ShippingQuoteOption | null): void
  (e: 'quote-selected', quote: ShippingQuoteOption): void
}

const props = withDefaults(defineProps<Props>(), {
  totalWeight: 1.0
})

const emit = defineEmits<Emits>()

// Form data
const postalCode = ref('')
const city = ref('')
const province = ref('')

// State
const loading = ref(false)
const error = ref('')
const quotes = ref<ShippingQuoteOption[]>([])
const quoteResponse = ref<ShippingQuoteResponse | null>(null)
const selectedCarrier = ref('')

// Computed
const selectedQuote = computed(() => {
  return quotes.value.find(q => q.carrier === selectedCarrier.value) || null
})

// Watch for selected quote changes
watch(selectedQuote, (newQuote) => {
  emit('update:modelValue', newQuote)
  if (newQuote) {
    emit('quote-selected', newQuote)
  }
})

// Methods
const clearQuotes = () => {
  quotes.value = []
  quoteResponse.value = null
  selectedCarrier.value = ''
  error.value = ''
}

const selectQuote = (quote: ShippingQuoteOption) => {
  selectedCarrier.value = quote.carrier
}

const calculateShipping = async () => {
  if (!postalCode.value.trim()) {
    error.value = 'Por favor ingresa un código postal'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    const response = await shippingQuotesApi.getShippingQuotes({
      postal_code: postalCode.value.trim(),
      city: city.value.trim() || undefined,
      province: province.value || undefined,
      total_weight_kg: props.totalWeight,
      include_fallback: true
    })

    quoteResponse.value = response
    quotes.value = response.options || []
    
    if (quotes.value.length === 0) {
      error.value = 'No se encontraron opciones de envío para esta dirección'
    } else {
      // Auto-select the first available option
      const firstAvailableQuote = quotes.value.find(q => !q.has_error) || quotes.value[0]
      if (firstAvailableQuote) {
        selectedCarrier.value = firstAvailableQuote.carrier
      }
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Error al calcular el envío. Por favor intenta nuevamente.'
  } finally {
    loading.value = false
  }
}

// Expose methods for parent component
defineExpose({
  calculateShipping,
  clearQuotes
})
</script>
