<template>
  <div 
    v-if="isVisible" 
    class="fixed top-0 left-0 z-[60] h-1 bg-gradient-to-r from-gray-400 to-gray-600 transition-all duration-300 ease-out shadow-sm"
    :style="{ 
      width: `${progress}%`,
      opacity: isVisible ? 1 : 0
    }"
  />
</template>

<script setup lang="ts">
import { watch } from 'vue'

interface Props {
  progress: number
  isVisible: boolean
}

const props = defineProps<Props>()

// Auto-hide cuando llega a 100%
watch(() => props.progress, (newProgress) => {
  if (newProgress >= 100) {
    // Pequeño delay para que se vea la finalización
    setTimeout(() => {
      // El parent component manejará isVisible
    }, 200)
  }
})
</script>
