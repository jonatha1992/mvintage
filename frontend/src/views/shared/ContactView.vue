<template>
  <div class="min-h-screen py-8 bg-gray-50">
    <div class="max-w-4xl px-4 mx-auto sm:px-6 lg:px-8">
      <div class="p-6 bg-white rounded-lg shadow">
        <h1 class="mb-6 text-3xl font-bold text-gray-900 font-heading">Contacto</h1>
        
        <div class="grid grid-cols-1 gap-8 md:grid-cols-2">
          <!-- Información de contacto -->
          <div>
            <h2 class="mb-4 text-xl font-semibold text-gray-800 font-heading">Información de Contacto</h2>
            <div class="space-y-4">
              <div class="flex items-center">
                <svg class="w-5 h-5 mr-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
                <a href="mailto:Showroomisabella@gmail.com" class="transition-colors font-body text-body-text hover:text-gray-900">Showroomisabella@gmail.com</a>
              </div>
              <div class="flex items-center">
                <svg class="w-5 h-5 mr-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                </svg>
                <a href="tel:+5491176372876" class="transition-colors font-body text-body-text hover:text-gray-900">+54 9 11 7637-2876</a>
              </div>
              <div class="flex items-start">
                <svg class="w-5 h-5 mr-3 mt-0.5 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                <div>
                  <a :href="STORE_MAPS_URL" target="_blank" rel="noopener noreferrer" class="underline transition-colors font-body text-body-text hover:text-gray-900">
                    {{ STORE_PICKUP_ADDRESS }}
                  </a>
                  <p class="mt-1 text-sm text-gray-500 font-body">{{ STORE_PICKUP_HOURS }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Formulario de contacto -->
          <div>
            <h2 class="mb-4 text-xl font-semibold text-gray-800 font-heading">Envíanos un mensaje</h2>
            <p class="mb-4 text-sm text-gray-600">Todos los campos son obligatorios.</p>
            <form class="space-y-4" method="post" :aria-busy="sending" @submit.prevent="sendMessage">
              <div>
                <label for="name" class="block mb-1 text-sm font-medium font-body text-body-text">Nombre</label>
                <input type="text" id="name" name="name" v-model.trim="form.nombre" required minlength="2" maxlength="100" autocomplete="name"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Tu nombre">
              </div>
              <div>
                <label for="email" class="block mb-1 text-sm font-medium font-body text-body-text">Email</label>
                <input type="email" id="email" name="email" v-model.trim="form.email" required maxlength="254" autocomplete="email"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="tu@email.com">
              </div>
              <div>
                <label for="message" class="block mb-1 text-sm font-medium font-body text-body-text">Mensaje</label>
                <textarea id="message" name="message" rows="4" v-model.trim="form.mensaje" required minlength="10" maxlength="4000"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Tu mensaje..."></textarea>
              </div>
              <button type="submit" :disabled="sending"
                class="w-full min-h-12 px-4 py-2 text-white transition duration-200 bg-gray-500 rounded-md hover:bg-gray-700">
                <span class="text-white">{{ sending ? 'Enviando…' : 'Enviar mensaje' }}</span>
              </button>
            </form>
            <p v-if="success" role="status" class="mt-4 text-sm text-green-800">Recibimos tu mensaje. Te responderemos por email.</p>
            <p v-if="error" role="alert" class="mt-4 text-sm text-red-800">{{ error }}</p>
            <a :href="`https://wa.me/${WHATSAPP_NUMBER}`" target="_blank" rel="noopener noreferrer" class="inline-flex items-center min-h-12 mt-3 text-sm underline">O escribinos por WhatsApp</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { apiClient } from '../../config/index'
import { WHATSAPP_NUMBER } from '../../config/payments'
import { STORE_MAPS_URL, STORE_PICKUP_ADDRESS, STORE_PICKUP_HOURS } from '../../config/store'
const form = reactive({ nombre: '', email: '', mensaje: '' })
const sending = ref(false)
const success = ref(false)
const error = ref('')

const sendMessage = async () => {
  if (sending.value) return
  sending.value = true
  success.value = false
  error.value = ''
  try {
    await apiClient.post('/contact', { ...form })
    success.value = true
    Object.assign(form, { nombre: '', email: '', mensaje: '' })
  } catch {
    error.value = 'No pudimos enviar tu mensaje. Intentá de nuevo en unos minutos o escribinos por WhatsApp.'
  } finally {
    sending.value = false
  }
}
</script>

