<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-6 font-heading">
          Prueba de Integración - API de Logística
        </h1>

        <!-- Test API Status -->
        <div class="mb-8">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Estado de la API</h2>
          <button
            @click="testApiConnection"
            :disabled="testingApi"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
          >
            <svg v-if="testingApi" class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ testingApi ? 'Probando...' : 'Probar Conexión API' }}
          </button>

          <div v-if="apiTestResult" class="mt-4 p-4 rounded-md" :class="apiTestResult.working ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
            <div class="flex">
              <svg class="w-5 h-5 mt-0.5 mr-2" :class="apiTestResult.working ? 'text-green-600' : 'text-red-600'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path v-if="apiTestResult.working" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p class="text-sm font-medium" :class="apiTestResult.working ? 'text-green-800' : 'text-red-800'">
                  {{ apiTestResult.working ? 'API Funcionando' : 'API con Problemas' }}
                </p>
                <p class="text-sm mt-1" :class="apiTestResult.working ? 'text-green-700' : 'text-red-700'">
                  {{ apiTestResult.message }}
                </p>
                <p class="text-xs mt-1 text-gray-600">
                  URL: {{ apiTestResult.url }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Shipping Calculator Test -->
        <div class="mb-8">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Calculadora de Envío</h2>
          <ShippingQuoteCalculator
            :total-weight="2.5"
            v-model="selectedQuote"
            @quote-selected="onQuoteSelected"
          />
        </div>

        <!-- Selected Quote Display -->
        <div v-if="selectedQuote" class="mb-8">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Cotización Seleccionada</h2>
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p class="text-sm font-medium text-blue-900">Transportista</p>
                <p class="text-lg text-blue-800">{{ selectedQuote.name }}</p>
              </div>
              <div>
                <p class="text-sm font-medium text-blue-900">Precio</p>
                <p class="text-lg font-semibold text-blue-800">${{ selectedQuote.price.toLocaleString() }} {{ selectedQuote.currency }}</p>
              </div>
              <div>
                <p class="text-sm font-medium text-blue-900">Tiempo de Entrega</p>
                <p class="text-sm text-blue-800">{{ selectedQuote.estimated_delivery_text }}</p>
              </div>
              <div>
                <p class="text-sm font-medium text-blue-900">Estado</p>
                <p class="text-sm" :class="selectedQuote.has_error ? 'text-orange-600' : 'text-green-600'">
                  {{ selectedQuote.has_error ? 'Con advertencias' : 'Disponible' }}
                </p>
              </div>
            </div>
            <div v-if="selectedQuote.error_message" class="mt-3 p-2 bg-orange-100 rounded">
              <p class="text-sm text-orange-800">{{ selectedQuote.error_message }}</p>
            </div>
          </div>
        </div>

        <!-- Available Carriers -->
        <div class="mb-8">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Transportistas Disponibles</h2>
          <button
            @click="loadCarriers"
            :disabled="loadingCarriers"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:bg-gray-400"
          >
            <svg v-if="loadingCarriers" class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loadingCarriers ? 'Cargando...' : 'Cargar Transportistas' }}
          </button>

          <div v-if="carriers.length > 0" class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div
              v-for="carrier in carriers"
              :key="carrier.code"
              class="border border-gray-200 rounded-lg p-4"
            >
              <h3 class="font-medium text-gray-900">{{ carrier.name }}</h3>
              <p class="text-sm text-gray-600 mt-1">{{ carrier.description }}</p>
              <p class="text-xs text-gray-500 mt-2">
                Entrega estimada: {{ carrier.estimated_days }} días
              </p>
            </div>
          </div>
        </div>

        <!-- Raw API Response -->
        <div v-if="lastApiResponse" class="mb-8">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Última Respuesta de la API</h2>
          <div class="bg-gray-100 rounded-lg p-4">
            <pre class="text-xs text-gray-800 whitespace-pre-wrap">{{ JSON.stringify(lastApiResponse, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ShippingQuoteCalculator from '../../components/checkout/ShippingQuoteCalculator.vue'
import { shippingQuotesApi } from '../../config/api'
import type { ShippingQuoteOption, CarrierInfo } from '../../types/orders/shipping.types'

// State
const testingApi = ref(false)
const apiTestResult = ref<any>(null)
const selectedQuote = ref<ShippingQuoteOption | null>(null)
const loadingCarriers = ref(false)
const carriers = ref<CarrierInfo[]>([])
const lastApiResponse = ref<any>(null)

// Methods
const testApiConnection = async () => {
  testingApi.value = true
  try {
    const response = await shippingQuotesApi.testShippingApi()
    apiTestResult.value = {
      working: response.api_working,
      message: response.message,
      url: response.api_url
    }
    lastApiResponse.value = response
  } catch (error: any) {
    apiTestResult.value = {
      working: false,
      message: error.response?.data?.detail || 'Error de conexión',
      url: 'N/A'
    }
    lastApiResponse.value = error.response?.data || { error: error.message }
  } finally {
    testingApi.value = false
  }
}

const loadCarriers = async () => {
  loadingCarriers.value = true
  try {
    const response = await shippingQuotesApi.getAvailableCarriers()
    carriers.value = response.carriers || []
    lastApiResponse.value = response
  } catch (error: any) {
    lastApiResponse.value = error.response?.data || { error: error.message }
  } finally {
    loadingCarriers.value = false
  }
}

const onQuoteSelected = (quote: ShippingQuoteOption) => {
}

// Auto-test API on mount
testApiConnection()
</script>
