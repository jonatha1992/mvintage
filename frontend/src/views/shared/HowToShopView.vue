<template>
  <div class="min-h-screen py-8 bg-gray-50">
    <div class="max-w-4xl px-4 mx-auto sm:px-6 lg:px-8">
      <div class="p-6 bg-white rounded-lg shadow">
        <h1 class="mb-6 text-3xl font-bold text-gray-900 font-heading">Cómo Comprar</h1>
        
        <div v-if="!COMPRAS_HABILITADAS" class="p-5 mb-8 space-y-3 rounded-md bg-gray-50">
          <h2 class="text-xl font-semibold">Comprá por WhatsApp</h2>
          <p>Elegí tu prenda en la colección y abrí su botón de WhatsApp. Mandanos el talle y color que querés; te confirmamos disponibilidad, forma de pago y retiro en el local.</p>
          <a :href="`https://wa.me/${WHATSAPP_NUMBER}`" target="_blank" rel="noopener noreferrer" class="inline-flex items-center min-h-12 underline">Consultar por WhatsApp</a>
        </div>
        <div class="space-y-8">
          <!-- Paso 1 -->
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0">
              <div class="flex items-center justify-center w-8 h-8 font-bold text-white bg-gray-500 rounded-full">
                <span class="text-white" >1</span>
              </div>
            </div>
            <div> 
              <h2 class="mb-2 text-xl font-semibold text-gray-800 font-heading">Navega nuestra colección</h2>
              <p class="font-body text-body-text">
                Explorá nuestras blusas, remeras, vestidos, conjuntos y más.
                Usa los filtros para encontrar exactamente lo que buscas.
              </p>
            </div>
          </div>

          <!-- Paso 2 -->
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0">
              <div class="flex items-center justify-center w-8 h-8 font-bold text-white bg-gray-500 rounded-full">
                <span class="text-white" >2</span>
              </div>
            </div>
            <div>
              <h2 class="mb-2 text-xl font-semibold text-gray-800 font-heading">Selecciona tu talla y color</h2>
              <p class="font-body text-body-text">
                Revisa nuestras guías de tallas para encontrar el ajuste perfecto. 
                Elige entre nuestra variedad de colores disponibles.
              </p>
            </div>
          </div>

          <!-- Paso 3 -->
                    <div v-if="COMPRAS_HABILITADAS" class="flex items-start space-x-4">
            <div class="flex-shrink-0">
              <div class="flex items-center justify-center w-8 h-8 font-bold text-white bg-gray-500 rounded-full">
                <span class="text-white">3</span>
              </div>
            </div>
            <div>
              <h2 class="mb-2 text-xl font-semibold text-gray-800 font-heading">Agrega al carrito</h2>
              <p class="font-body text-body-text">
                Una vez que hayas seleccionado tus productos, agrégalos al carrito de compras. 
                Puedes seguir comprando o finalizar tu compra.
              </p>
            </div>
          </div>

          <!-- Paso 4 -->
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0">
              <div class="flex items-center justify-center w-8 h-8 font-bold text-white bg-gray-500 rounded-full">
                <span class="text-white" >4</span>
              </div>
            </div>
            <div>
              <h2 class="mb-2 text-xl font-semibold text-gray-800 font-heading">Completa tus datos para el retiro</h2>
              <p class="font-body text-body-text">
                Completá tus datos de contacto. Todas las compras se retiran sin costo en
                <a :href="STORE_MAPS_URL" target="_blank" rel="noopener noreferrer" class="underline text-gray-900 hover:text-gray-600">{{ STORE_PICKUP_ADDRESS }}</a>.
                {{ STORE_PICKUP_HOURS }} cuando tu pedido esté listo para retirar.
              </p>
            </div>
          </div>

          <!-- Paso 5 -->
                    <div v-if="COMPRAS_HABILITADAS" class="flex items-start space-x-4">
            <div class="flex-shrink-0">
              <div class="flex items-center justify-center w-8 h-8 font-bold text-white bg-gray-500 rounded-full">
                <span class="text-white" >5</span>
              </div>
            </div>
            <div>
              <h2 class="mb-2 text-xl font-semibold text-gray-800 font-heading">Elige tu método de pago y confirma</h2>
              <p class="font-body text-body-text">
                Pagá por transferencia bancaria<span v-if="MERCADOPAGO_HABILITADO"> o Mercado Pago (tarjetas de crédito y débito)</span>.
                El pago se completa online antes de retirar el pedido.
              </p>
            </div>
          </div>

          <!-- Métodos de pago -->
          <div v-if="COMPRAS_HABILITADAS" class="p-6 mt-8 rounded-lg bg-gray-50">
            <h3 class="mb-4 text-lg font-semibold text-gray-800 font-heading">Métodos de Pago Aceptados</h3>
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div class="flex items-center p-4 bg-white rounded-lg shadow">
                <div class="p-2 mr-3 bg-blue-100 rounded-full">
                  <svg class="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900 font-heading">Transferencia Bancaria</h4>
                  <p class="text-sm text-gray-600 font-body">Pago directo a cuenta bancaria</p>
                </div>
              </div>
              
              <div v-if="MERCADOPAGO_HABILITADO" class="flex items-center p-4 bg-white rounded-lg shadow">
                <div class="p-2 mr-3 bg-purple-100 rounded-full">
                  <svg class="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900 font-heading">Mercado Pago</h4>
                  <p class="text-sm text-gray-600 font-body">Tarjetas de crédito, débito y más</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Contacto -->
          <div class="p-6 rounded-lg bg-indigo-50">
            <h3 class="mb-2 text-lg font-semibold text-gray-800 font-heading">¿Necesitas ayuda?</h3>
            <p class="mb-3 font-body text-body-text">
              Si tienes alguna pregunta sobre el proceso de compra, no dudes en contactarnos.
            </p>
            <router-link to="/contact" 
              class="inline-flex items-center min-h-12 px-4 py-2 text-white transition duration-200 bg-gray-500 rounded-md gray-600 hover:bg-gray-800">
              <span  class="text-white">Contactar</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { STORE_MAPS_URL, STORE_PICKUP_ADDRESS, STORE_PICKUP_HOURS } from '../../config/store'
import { COMPRAS_HABILITADAS, MERCADOPAGO_HABILITADO, WHATSAPP_NUMBER } from '../../config/payments'
</script>

