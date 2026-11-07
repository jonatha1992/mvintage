<template>
  <footer class="text-white bg-gray-900">
    <div class="px-4 py-16 mx-auto max-w-7xl sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 gap-8 md:grid-cols-4 lg:gap-12">
        <!-- Company Info -->
        <div class="col-span-1 md:col-span-2 footer-section fade-in-up">
          <div class="flex items-center mb-6 space-x-3">
            <img src="/imagen-portada.svg" alt="M-VINTAGE Logo" class="w-8 h-8" />
            <h3 class="text-2xl font-light tracking-wider text-white font-heading">MATILDA VINTAGE</h3>
          </div>
          <p class="max-w-md mb-4 font-light leading-relaxed text-gray-300 font-body">
            Estilo que perdura en el tiempo. Encuentra las mejores prendas vintage y contemporáneas 
            para expresar tu personalidad única.
          </p>
          
          <!-- Contact Info -->
          <div class="mb-6 space-y-2">
            <div class="flex items-center space-x-3">
              <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
              </svg>
              <a href="mailto:mvintageapp@gmail.com" class="text-sm text-gray-300 transition-colors font-body hover:text-white">
                mvintageapp@gmail.com
              </a>
            </div>
            <div class="flex items-center space-x-3">
              <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
              </svg>
              <a href="tel:+5491139471826" class="text-sm text-gray-300 transition-colors font-body hover:text-white">
                +54 9 11 3947-1826
              </a>
            </div>
          </div>
          
          <!-- Social Media -->
          <div class="mb-6">
            <h4 class="mb-4 text-sm font-medium tracking-wide text-white uppercase font-body">Síguenos</h4>
            <div class="flex space-x-4">
              <a href="https://instagram.com/matilda_vintage_" target="_blank" rel="noopener noreferrer" 
                 class="p-2 transition-colors duration-200 bg-gray-800 rounded-full group hover:bg-gray-700">
                <svg class="w-5 h-5 text-gray-300 group-hover:text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
                <span class="sr-only">Instagram</span>
              </a>
              
              <a href="https://tiktok.com/@mvintage" target="_blank" rel="noopener noreferrer"
                 class="p-2 transition-colors duration-200 bg-gray-800 rounded-full group hover:bg-gray-700">
                <svg class="w-5 h-5 text-gray-300 group-hover:text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-.04-.1z"/>
                </svg>
                <span class="sr-only">TikTok</span>
              </a>
              
              <a href="https://facebook.com/mvintage" target="_blank" rel="noopener noreferrer"
                 class="p-2 transition-colors duration-200 bg-gray-800 rounded-full group hover:bg-gray-700">
                <svg class="w-5 h-5 text-gray-300 group-hover:text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
                <span class="sr-only">Facebook</span>
              </a>
              
              <a href="https://whatsapp.com/mvintage" target="_blank" rel="noopener noreferrer"
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
            <li><router-link to="/shop?category=camisetas" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Camisetas</router-link></li>
            <li><router-link to="/shop?category=pantalones" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Pantalones</router-link></li>
            <li><router-link to="/shop?category=accesorios" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Accesorios</router-link></li>
            <li><router-link to="/shop?sort=newest" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Nuevos Arribos</router-link></li>
          </ul>
        </div>

        <!-- Customer Service -->
        <div class="footer-section fade-in-up stagger-2">
          <h4 class="mb-4 text-sm font-medium tracking-wide text-white uppercase font-body">Ayuda</h4>
          <ul class="space-y-3">
            <li><router-link to="/contact" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Contacto</router-link></li>
            <li><router-link to="/shipping" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Envíos y Devoluciones</router-link></li>
            <li><router-link to="/how-to-shop" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Guía de Compra</router-link></li>
            <li><router-link to="/size-guide" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Guía de Talles</router-link></li>
            <li><router-link to="/privacy" class="text-sm text-gray-300 transition-colors duration-200 font-body hover:text-white">Política de Privacidad</router-link></li>
          </ul>
        </div>
      </div>

      <!-- Payment Methods -->
      <div class="pt-8 mt-12 border-t border-gray-800">
        <div class="text-center">
          <h4 class="mb-6 text-sm font-medium tracking-wide text-white uppercase font-body">Métodos de Pago</h4>
          <div class="flex flex-wrap items-center justify-center max-w-4xl gap-4 mx-auto">
            <!-- Mercado Pago -->
            <div class="flex items-center px-3 py-2 space-x-2 bg-gray-800 rounded-md">
              <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" fill="#00b8d4"/>
                <path d="M9.5 8.5h5v7h-5v-7z" fill="white"/>
              </svg>
              <span class="text-xs font-medium text-gray-300 font-body">Mercado Pago</span>
            </div>

            <!-- Credit Cards -->
            <div class="flex items-center space-x-1">
              <!-- Visa -->
              <div class="px-2 py-1 bg-white rounded">
                <svg class="w-8 h-5" viewBox="0 0 40 24" fill="none">
                  <rect width="40" height="24" rx="4" fill="white"/>
                  <path d="M15.93 7.85h-3.34l-2.08 8.3h3.34l2.08-8.3zm7.17 5.28c.01-1.27-.4-2.01-1.28-2.01-.52 0-.84.29-1.01.52l.16-2.54h-3.08l-1.15 7.2h3.04l.52-2.2c.17-.69.48-.9.71-.9.34 0 .46.27.45.61l-.32 2.49h3.08l.34-2.59c.16-1.18-.21-1.78-.46-1.78z" fill="#1a1f71"/>
                </svg>
              </div>
              
              <!-- Mastercard -->
              <div class="px-2 py-1 bg-white rounded">
                <svg class="w-8 h-5" viewBox="0 0 40 24" fill="none">
                  <rect width="40" height="24" rx="4" fill="white"/>
                  <circle cx="15" cy="12" r="6" fill="#eb001b"/>
                  <circle cx="25" cy="12" r="6" fill="#f79e1b"/>
                  <path d="M20 7.5c1.26 1.26 2.04 3.01 2.04 4.96s-.78 3.7-2.04 4.96" fill="#ff5f00"/>
                </svg>
              </div>

              <!-- American Express -->
              <div class="px-2 py-1 bg-white rounded">
                <svg class="w-8 h-5" viewBox="0 0 40 24" fill="none">
                  <rect width="40" height="24" rx="4" fill="white"/>
                  <path d="M4 8h32v8H4V8z" fill="#006fcf"/>
                  <text x="20" y="13.5" text-anchor="middle" font-family="Arial" font-size="4" font-weight="bold" fill="white">AMEX</text>
                </svg>
              </div>

              <!-- Naranja -->
              <div class="px-2 py-1 bg-white rounded">
                <svg class="w-8 h-5" viewBox="0 0 40 24" fill="none">
                  <rect width="40" height="24" rx="4" fill="white"/>
                  <circle cx="20" cy="12" r="8" fill="#ff6600"/>
                  <text x="20" y="13.5" text-anchor="middle" font-family="Arial" font-size="3" font-weight="bold" fill="white">NARANJA</text>
                </svg>
              </div>

              <!-- Cabal -->
              <div class="px-2 py-1 bg-white rounded">
                <svg class="w-8 h-5" viewBox="0 0 40 24" fill="none">
                  <rect width="40" height="24" rx="4" fill="white"/>
                  <path d="M4 8h32v8H4V8z" fill="#004d9f"/>
                  <text x="20" y="13.5" text-anchor="middle" font-family="Arial" font-size="4" font-weight="bold" fill="white">CABAL</text>
                </svg>
              </div>
            </div>

            <!-- Bank Transfer -->
            <div class="flex items-center px-3 py-2 space-x-2 bg-gray-800 rounded-md">
              <svg class="w-5 h-5 text-gray-300" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
              <span class="text-xs font-medium text-gray-300 font-body">Transferencia</span>
            </div>

            <!-- Rapipago -->
            <div class="flex items-center px-3 py-2 space-x-2 bg-gray-800 rounded-md">
              <svg class="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
              <span class="text-xs font-medium text-gray-300 font-body">Rapipago</span>
            </div>

            <!-- Pago Fácil -->
            <div class="flex items-center px-3 py-2 space-x-2 bg-gray-800 rounded-md">
              <svg class="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
              <span class="text-xs font-medium text-gray-300 font-body">Pago Fácil</span>
            </div>
          </div>
          
          <!-- Security Info -->
          <div class="flex flex-col items-center justify-center gap-4 mt-6 text-xs text-gray-400 sm:flex-row">
            <div class="flex items-center space-x-2">
              <svg class="w-4 h-4 text-green-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M10,17L6,13L7.41,11.58L10,14.17L16.59,7.58L18,9L10,17Z"/>
              </svg>
              <span class="font-body">Compra 100% segura</span>
            </div>
            <div class="flex items-center space-x-2">
              <svg class="w-4 h-4 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17,9H7V7A5,5 0 0,1 12,2A5,5 0 0,1 17,7V9M21,16A2,2 0 0,1 19,18H5A2,2 0 0,1 3,16V10A2,2 0 0,1 5,8H19A2,2 0 0,1 21,10V16Z"/>
              </svg>
              <span class="font-body">Datos protegidos SSL</span>
            </div>
            <div class="flex items-center space-x-2">
              <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,16.5L6.5,12L7.91,10.59L11,13.67L16.59,8.09L18,9.5L11,16.5Z"/>
              </svg>
              <span class="font-body">Garantía de satisfacción</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Newsletter Signup -->
      <div class="pt-8 mt-12 border-t border-gray-800">
        <div class="max-w-md mx-auto text-center lg:max-w-none lg:text-left lg:flex lg:items-center lg:justify-between">
          <div class="lg:flex-1">
            <h4 class="mb-2 text-lg font-light text-white font-heading">Mantente al día</h4>
            <p class="text-sm text-gray-300 font-body">Recibe noticias sobre nuevas colecciones y ofertas exclusivas</p>
          </div>
          <div class="mt-6 lg:mt-0 lg:ml-8 lg:flex-shrink-0">
            <div class="flex flex-col gap-3 sm:flex-row">
              <input 
                type="email" 
                placeholder="Tu email"
                class="px-4 py-2 text-white placeholder-gray-400 bg-gray-800 border border-gray-700 rounded-md font-body focus:outline-none focus:ring-2 focus:ring-white focus:border-transparent"
              >
              <button class="btn-minimal btn-light whitespace-nowrap font-body">
                Suscribirse
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Section -->
      <div class="pt-8 mt-12 border-t border-gray-800">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <div class="flex flex-wrap items-center gap-6 text-sm text-gray-400">
            <p class="font-body">&copy; 2024 M-VINTAGE. Todos los derechos reservados.</p>
            <router-link to="/terms" class="transition-colors font-body hover:text-white">Términos y Condiciones</router-link>
            <router-link to="/privacy" class="transition-colors font-body hover:text-white">Política de Privacidad</router-link>
          </div>
          <div class="mt-4 lg:mt-0">
            <p class="text-xs font-body text-body-text">
              Diseñado con por 
              <a href="mailto:tecnofusion.it@gmail.com" class="underline transition-colors font-body hover:text-body-text">
                tecnofusion.dev
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
</script>
