<template>
  <div class="relative h-[70vh] min-h-[420px] md:h-[78vh] hero-section bg-gray-900">
    <!-- Hero -->
    <div class="absolute inset-0">
      <img src="https://img.tecnofusion.dev/showroomisabella/image/upload/productos/K4Y2F_hjQGlF.jpg" alt="Prendas de Showroom Isabella" class="object-cover w-full h-full" fetchpriority="high" />
      <div class="absolute inset-0 bg-black/45"></div>
    </div>
    
    <!-- Hero Content -->
    <div class="relative z-10 flex flex-col items-center justify-center h-full px-4 text-center">
      <div class="max-w-2xl">
        <div class="flex items-center justify-center mb-6 space-x-3">
          <h1 class="text-5xl font-light tracking-wide text-white font-heading md:text-7xl hero-title">
            SHOWROOM ISABELLA
          </h1>
        </div>
        <p class="mb-8 text-lg font-light tracking-wide text-white font-body md:text-xl" style="color: white;">
          Prendas pensadas para acompañarte todos los días, con la calidad y el estilo que nos representa.
        </p>
        <div class="flex flex-wrap justify-center gap-3">
          <button @click="scrollToProducts" class="btn-minimal btn-light font-body">
            Ver Colección
          </button>
          <router-link to="/shop" class="btn-minimal btn-dark font-body">
            Nuevos Arribos
          </router-link>
        </div>
      </div>
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

