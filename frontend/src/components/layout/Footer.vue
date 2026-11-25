<template>
  <footer class="text-white bg-gray-900">
    <div class="px-4 py-12 mx-auto max-w-7xl sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 gap-8 md:grid-cols-4 lg:gap-12">
        <!-- Company Info -->
        <div class="col-span-1 md:col-span-2 footer-section fade-in-up">
          <div class="flex items-center mb-6 space-x-3">
            <img src="/logo_redondo.jpg" alt="Showroom Isabella" class="object-cover w-8 h-8 rounded-full" />
            <h3 class="text-2xl font-light tracking-wider text-white font-heading">SHOWROOM ISABELLA</h3>
          </div>
          <p class="max-w-md mb-4 font-light leading-relaxed text-gray-300 font-body">
            Prendas pensadas para acompañarte todos los días, con la calidad y el estilo que nos representa.
          </p>
          
          <!-- Contact Info -->
          <div class="mb-6 space-y-2">
            <div class="flex items-center space-x-3">
              <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
              </svg>
              <a href="mailto:Showroomisabella@gmail.com" class="text-sm text-gray-300 transition-colors font-body hover:text-white">
                Showroomisabella@gmail.com
              </a>
            </div>
            <div class="flex items-center space-x-3">
              <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
              </svg>
              <a href="tel:+5491176372876" class="text-sm text-gray-300 transition-colors font-body hover:text-white">
                +54 9 11 7637-2876
              </a>
            </div>
            <div class="flex items-start space-x-3">
              <svg class="w-4 h-4 mt-0.5 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              <div class="text-sm text-gray-300 font-body">
                <a :href="STORE_MAPS_URL" target="_blank" rel="noopener noreferrer" class="underline transition-colors underline-offset-2 hover:text-white">
                  {{ STORE_PICKUP_ADDRESS }}
                </a>
                <p class="text-xs text-gray-400">{{ STORE_PICKUP_HOURS }}</p>
              </div>
            </div>
          </div>
          
          <!-- Social Media -->
          <div class="mb-6">
            <h4 class="mb-4 text-sm font-medium tracking-wide text-white uppercase font-body">Síguenos</h4>
            <div class="flex space-x-4">
              <a href="https://www.instagram.com/showroomisabella_/" target="_blank" rel="noopener noreferrer"
                 class="p-2 transition-colors duration-200 bg-gray-800 rounded-full group hover:bg-gray-700">
                <svg class="w-5 h-5 text-gray-300 group-hover:text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
                <span class="sr-only">Instagram</span>
              </a>
              
              <a href="https://wa.me/5491176372876" target="_blank" rel="noopener noreferrer"
                 class="p-2 transition-colors duration-200 bg-gray-800 rounded-full group hover:bg-gray-700">
                <svg class="w-5 h-5 text-gray-300 group-hover:text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.51 3.487"/>
                </svg>
                <span class="sr-only">WhatsApp</span>
              </a>
            </div>
          </div>
        </div>

        <!-- Shop Links -->
        <div class="footer-section fade-in-up stagger-1">
          <h4 class="mb-4 text-sm font-medium tracking-wide text-white uppercase font-body">Tienda</h4>
          <ul class="space-y-3">
            <li><router-link to="/shop" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Nueva Colección</router-link></li>
            <li v-for="category in categories" :key="category"><router-link :to="`/shop?category=${category.toLowerCase()}`" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">{{ categoryLabel(category) }}</router-link></li>
            <li><router-link to="/shop?sort=newest" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Nuevos Arribos</router-link></li>
          </ul>
        </div>

        <!-- Customer Service -->
        <div class="footer-section fade-in-up stagger-2">
          <h4 class="mb-4 text-sm font-medium tracking-wide text-white uppercase font-body">Ayuda</h4>
          <ul class="space-y-3">
            <li><router-link to="/contact" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Contacto</router-link></li>
            <li><router-link to="/shipping" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Retiro en el local</router-link></li>
            <li><router-link to="/how-to-shop" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Guía de Compra</router-link></li>
            <li><router-link to="/size-guide" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Guía de Talles</router-link></li>
          </ul>
        </div>
      </div>

      <!-- Payment Methods -->
      <p class="pt-6 mt-8 text-sm text-center text-gray-400 border-t border-gray-800 font-body">
        {{ MERCADOPAGO_HABILITADO ? 'Medios de pago: Mercado Pago y transferencia bancaria. Retiro en el local.' : 'Medios de pago: transferencia bancaria. Retiro en el local.' }}
      </p>

      <!-- Bottom Section -->
      <div class="pt-6 mt-6 border-t border-gray-800">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <div class="flex flex-wrap items-center gap-6 text-sm text-gray-400">
            <p class="font-body">&copy; 2026 Showroom Isabella. Todos los derechos reservados.</p>
            <router-link to="/terms" class="transition-colors font-body hover:text-white">Términos y Condiciones</router-link>
            <router-link to="/privacy" class="transition-colors font-body hover:text-white">Política de Privacidad</router-link>
          </div>
          <div class="mt-4 lg:mt-0">
            <p class="text-xs text-gray-400 font-body">
              Desarrollado por
              <a href="https://tecnofusion.dev" target="_blank" rel="noopener" class="font-semibold text-white underline-offset-2 hover:underline">
                TecnoFusion
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { categoryLabel } from '../../utils/category'
import { MERCADOPAGO_HABILITADO } from '../../config/payments'
import { STORE_MAPS_URL, STORE_PICKUP_ADDRESS, STORE_PICKUP_HOURS } from '../../config/store'

const categories = ['BLUSA', 'BODY', 'CONJUNTO', 'PANTALON', 'REMERA', 'TOP', 'VESTIDO']
</script>

<style scoped>
a {
  display: inline-flex;
  align-items: center;
  min-block-size: 44px;
  min-inline-size: 44px;
}
</style>
