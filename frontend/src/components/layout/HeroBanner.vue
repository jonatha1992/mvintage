<template>
  <div class="relative h-screen hero-section bg-gray-50">
    <!-- Hero Video -->
    <div class="absolute inset-0">
      <video 
        class="object-cover w-full h-full" 
        autoplay 
        loop 
        muted 
        playsinline
      >
        <source src="/Video.mp4" type="video/mp4">
        <!-- Fallback image if video fails to load -->
        <img 
          src="https://images.unsplash.com/photo-1445205170230-053b83016050?ixlib=rb-4.0.3&auto=format&fit=crop&w=2071&q=80" 
          alt="M-VINTAGE Collection" 
          class="object-cover w-full h-full"
        />
      </video>
      <div class="absolute inset-0 bg-black bg-opacity-30"></div>
    </div>
    
    <!-- Hero Content -->
    <div class="relative z-10 flex flex-col items-center justify-center h-full px-4 text-center">
      <div class="max-w-2xl">
        <div class="flex items-center justify-center mb-6 space-x-3">
          <h1 class="text-5xl font-light tracking-wide text-white font-heading md:text-7xl hero-title">
            MATILDA VINTAGE
          </h1>
        </div>
        <p class="mb-8 text-xl font-light tracking-wide text-white font-body md:text-2xl" style="color: white;">
          Estilo que perdura en el tiempo
        </p>
        <div class="space-y-4">
          <button @click="scrollToProducts" class="mr-4 btn-minimal btn-light font-body">
            Ver Colección
          </button>
          <router-link to="/shop" class="btn-minimal btn-dark font-body">
            Nuevos Arribos
          </router-link>
        </div>
      </div>
    </div>
    
    <!-- Scroll Indicator -->
    <div class="absolute transform -translate-x-1/2 bottom-8 left-1/2 animate-bounce">
      <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
// Función para hacer scroll suave hacia los productos
const scrollToProducts = () => {
  // Buscar el elemento ProductGrid o un contenedor de productos
  const productSection = document.querySelector('.product-grid') ||
                        document.querySelector('[class*="product"]') ||
                        document.querySelector('.min-h-screen') // Fallback al contenedor principal

  if (productSection) {
    // Calcular la posición para hacer scroll, dejando un poco de espacio arriba
    const offsetTop = (productSection as HTMLElement).offsetTop - 100

    window.scrollTo({
      top: offsetTop,
      behavior: 'smooth'
    })
  } else {
    // Si no encuentra el elemento, hace scroll hacia abajo aproximadamente donde estarían los productos
    window.scrollTo({
      top: window.innerHeight * 0.9, // Aproximadamente 90% de la altura de viewport
      behavior: 'smooth'
    })
  }
}
</script>

<style scoped>
@keyframes bounce {
  0%, 20%, 53%, 80%, 100% {
    transform: translateY(0) translateX(-50%);
  }
  40%, 43% {
    transform: translateY(-10px) translateX(-50%);
  }
  70% {
    transform: translateY(-5px) translateX(-50%);
  }
  90% {
    transform: translateY(-2px) translateX(-50%);
  }
}
</style>

