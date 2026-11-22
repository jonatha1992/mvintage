import { ref, readonly } from 'vue'

// Estado global de la barra de progreso
const progress = ref(0)
const isVisible = ref(false)
let progressTimeout: NodeJS.Timeout | null = null
let hideTimeout: NodeJS.Timeout | null = null

export function useProgressBar() {

  const start = () => {
    // Limpiar timeouts previos
    if (progressTimeout) clearTimeout(progressTimeout)
    if (hideTimeout) clearTimeout(hideTimeout)

    // Resetear y mostrar
    progress.value = 0
    isVisible.value = true

    // Progresión realista simulada
    // Avance rápido inicial (simula DNS lookup, conexión)
    setTimeout(() => progress.value = 10, 50)
    setTimeout(() => progress.value = 25, 100)
    setTimeout(() => progress.value = 40, 200)

    // Avance más lento (simula descarga de recursos)
    setTimeout(() => progress.value = 60, 400)
    setTimeout(() => progress.value = 75, 700)
    setTimeout(() => progress.value = 85, 1000)

    // Se queda en 85% hasta que se llame complete()
  }

  const complete = () => {
    // Limpiar timeouts
    if (progressTimeout) clearTimeout(progressTimeout)
    if (hideTimeout) clearTimeout(hideTimeout)

    // Completar rápidamente
    progress.value = 100

    // Auto-hide después de mostrar finalización
    hideTimeout = setTimeout(() => {
      isVisible.value = false
      // Reset después de hide para próxima vez
      setTimeout(() => progress.value = 0, 300)
    }, 200)
  }

  const reset = () => {
    if (progressTimeout) clearTimeout(progressTimeout)
    if (hideTimeout) clearTimeout(hideTimeout)
    progress.value = 0
    isVisible.value = false
  }

  return {
    progress: readonly(progress),
    isVisible: readonly(isVisible),
    start,
    complete,
    reset
  }
}

// Export para uso global
export const globalProgressBar = useProgressBar()