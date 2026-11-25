import { onScopeDispose, ref, watch } from 'vue'
import { productsApi } from '../config/index'
import type { Product } from '../types'

export const SEARCH_DEBOUNCE_MS = 220
export const SEARCH_RESULT_LIMIT = 8

function isAbortError(err: unknown): boolean {
  if (!err || typeof err !== 'object') return false
  const maybe = err as { name?: string; code?: string }
  return maybe.name === 'AbortError' || maybe.name === 'CanceledError' || maybe.code === 'ERR_CANCELED'
}

export function useProductSearch(options?: { debounceMs?: number; limit?: number }) {
  const debounceMs = options?.debounceMs ?? SEARCH_DEBOUNCE_MS
  const limit = options?.limit ?? SEARCH_RESULT_LIMIT

  const query = ref('')
  const results = ref<Product[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const hasSearched = ref(false)

  let timer: ReturnType<typeof setTimeout> | null = null
  let activeController: AbortController | null = null

  const cancelPending = () => {
    if (timer !== null) {
      clearTimeout(timer)
      timer = null
    }
    if (activeController) {
      activeController.abort()
      activeController = null
    }
  }

  watch(query, (rawValue) => {
    cancelPending()
    const trimmed = rawValue.trim()
    if (!trimmed) {
      results.value = []
      isLoading.value = false
      error.value = null
      hasSearched.value = false
      return
    }

    isLoading.value = true
    error.value = null

    timer = setTimeout(async () => {
      timer = null
      const controller = new AbortController()
      activeController = controller
      try {
        const { products } = await productsApi.getProducts(
          { search: trimmed, limit },
          { signal: controller.signal }
        )
        if (controller.signal.aborted) return
        results.value = products
        hasSearched.value = true
      } catch (err) {
        if (controller.signal.aborted || isAbortError(err)) return
        results.value = []
        error.value = 'No pudimos buscar prendas. Intentá de nuevo.'
        hasSearched.value = true
      } finally {
        if (activeController === controller) {
          activeController = null
          isLoading.value = false
        }
      }
    }, debounceMs)
  })

  const reset = () => {
    cancelPending()
    query.value = ''
    results.value = []
    isLoading.value = false
    error.value = null
    hasSearched.value = false
  }

  onScopeDispose(cancelPending)

  return {
    query,
    results,
    isLoading,
    error,
    hasSearched,
    reset,
  }
}
