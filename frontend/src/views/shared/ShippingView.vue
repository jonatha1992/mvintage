<template>
  <main class="min-h-screen px-4 py-12 bg-gray-50 sm:px-6">
    <section class="max-w-3xl p-6 mx-auto bg-white rounded-lg shadow sm:p-8" aria-labelledby="pickup-heading">
      <h1 id="pickup-heading" class="text-3xl font-light text-gray-900 font-heading">
        Retiro en el local
      </h1>
      <p class="mt-4 text-base leading-7 text-gray-700 font-body">
        Todas las compras en Showroom Isabella son únicamente con retiro en el local, sin costo adicional. El pago se completa online antes del retiro.
      </p>

      <div class="pt-6 mt-6 border-t border-gray-200">
        <h2 class="text-lg font-medium text-gray-900 font-heading">Dónde retirás</h2>
        <p class="mt-2 text-sm leading-6 text-gray-700 font-body">
          <strong>Dirección:</strong>
          <a :href="STORE_MAPS_URL" target="_blank" rel="noopener noreferrer" class="ml-1 text-gray-900 underline hover:text-gray-600">
            {{ STORE_PICKUP_ADDRESS }}
          </a>
        </p>
        <p class="mt-1 text-sm leading-6 text-gray-700 font-body">
          <strong>Horarios:</strong> {{ STORE_PICKUP_HOURS }}.
        </p>
      </div>

      <div class="pt-6 mt-6 border-t border-gray-200">
        <h2 class="text-lg font-medium text-gray-900 font-heading">Cómo funciona</h2>
        <ol class="mt-3 space-y-3 text-sm leading-6 text-gray-700 list-decimal list-inside font-body">
          <li v-if="COMPRAS_HABILITADAS">Completá la compra y pagá por transferencia bancaria<span v-if="MERCADOPAGO_HABILITADO"> o Mercado Pago</span>.</li>
          <li v-else>Elegí tu prenda y escribinos por WhatsApp para confirmar disponibilidad, pago y retiro.</li>
          <li>Te avisamos por WhatsApp cuando tu pedido esté listo para retirar.</li>
          <li>{{ STORE_PICKUP_HOURS }} y pasá con tu número de pedido.</li>
        </ol>
      </div>

      <div class="p-4 mt-6 border border-gray-200 rounded-md bg-gray-50">
        <p class="text-sm text-gray-700 font-body">
          Tené a mano el número de pedido al coordinar. Realizamos cambios dentro de los 7 días hábiles posteriores al retiro.
        </p>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { STORE_MAPS_URL, STORE_PICKUP_ADDRESS, STORE_PICKUP_HOURS } from '../../config/store'
import { COMPRAS_HABILITADAS, MERCADOPAGO_HABILITADO } from '../../config/payments'
</script>
