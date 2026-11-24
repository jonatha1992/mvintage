<template>
  <section class="max-w-3xl px-4 py-16 mx-auto" aria-labelledby="not-found-heading">
    <p class="text-sm text-gray-500">404</p>
    <h1 id="not-found-heading" class="mt-3 text-3xl font-light">Página no encontrada</h1>
    <p class="mt-4 text-gray-700">La dirección no existe o la página cambió de lugar.</p>
    <router-link to="/shop" class="inline-flex items-center min-h-12 px-5 mt-6 text-white bg-black rounded-md">Volver a la tienda</router-link>
  </section>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

let robots: HTMLMetaElement | null = null
onMounted(() => {
  robots = document.createElement('meta')
  robots.name = 'robots'
  robots.content = 'noindex'
  document.head.append(robots)
})
onUnmounted(() => robots?.remove())
</script>
