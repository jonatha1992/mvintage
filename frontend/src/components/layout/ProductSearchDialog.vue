<template>
  <dialog
    ref="dialogRef"
    closedby="any"
    aria-labelledby="product-search-title"
    class="search-dialog"
    @close="handleNativeClose"
    @pointerdown="handlePointerDown"
    @pointerup="handlePointerUp"
  >
    <div class="flex items-center justify-between gap-3 px-4 py-3 border-b border-gray-100">
      <h2 id="product-search-title" class="text-sm font-medium tracking-wider text-gray-900 uppercase font-heading">
        Buscar prendas
      </h2>
      <button
        type="button"
        @click="close"
        aria-label="Cerrar buscador"
        class="inline-flex items-center justify-center min-w-11 min-h-11 -mr-2 text-gray-500 transition-colors rounded-md hover:text-gray-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-900"
      >
        <svg class="w-5 h-5" aria-hidden="true" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <div class="px-4 py-3 border-b border-gray-100">
      <div class="relative flex items-center">
        <svg
          class="absolute left-3 w-4 h-4 text-gray-400 pointer-events-none"
          aria-hidden="true"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.75"
            d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 105.25 5.25a7.5 7.5 0 0011.4 11.4z"
          />
        </svg>
        <input
          ref="inputRef"
          v-model="query"
          type="search"
          autofocus
          autocomplete="off"
          placeholder="Buscá por prenda, categoría o color..."
          aria-label="Buscar prendas"
          @keydown="handleKeydown"
          class="w-full py-2.5 pl-9 pr-3 text-sm text-gray-900 placeholder-gray-400 bg-gray-50 border border-gray-200 rounded-md font-body focus:bg-white focus:border-gray-900 focus:outline-none"
        />
      </div>
    </div>

    <div class="flex-1 overflow-y-auto px-4 py-3">
      <p v-if="!trimmedQuery" class="py-6 text-sm text-center text-gray-500 font-body">
        Escribí el nombre, categoría o color de una prenda.
      </p>

      <p v-else-if="isLoading" class="py-6 text-sm text-center text-gray-500 font-body">
        Buscando prendas...
      </p>

      <p v-else-if="error" class="py-6 text-sm text-center text-red-600 font-body">
        {{ error }}
      </p>

      <div v-else-if="hasSearched && results.length === 0" class="py-6 text-center">
        <p class="text-sm text-gray-600 font-body">
          No encontramos prendas para «{{ trimmedQuery }}».
        </p>
      </div>

      <ul v-else-if="results.length > 0" class="divide-y divide-gray-100">
        <li v-for="product in results" :key="product.id">
          <button
            type="button"
            @click="selectProduct(product.id)"
            class="flex items-center w-full gap-3 py-2.5 text-left transition-colors rounded-md hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-900"
          >
            <div class="flex-shrink-0 w-14 h-16 overflow-hidden bg-gray-100 rounded">
              <img
                v-if="product.images?.[0]?.image_url"
                :src="buildImageVariantUrl(product.images[0].image_url, 160)"
                :alt="product.name"
                loading="lazy"
                class="object-cover w-full h-full"
              />
              <div v-else class="flex items-center justify-center w-full h-full text-xs text-gray-400">
                Sin foto
              </div>
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium text-gray-900 truncate font-body">
                  {{ product.name }}
                </span>
                <span
                  v-if="isOutOfStock(product)"
                  class="flex-shrink-0 px-1.5 py-0.5 text-[11px] font-medium text-gray-600 bg-gray-200 rounded"
                >
                  Sin stock
                </span>
              </div>
              <p v-if="product.categoria" class="text-xs tracking-wide text-gray-500 uppercase font-body">
                {{ categoryLabel(product.categoria) }}
              </p>
              <div class="flex items-center gap-2 mt-1">
                <span class="text-sm font-medium text-gray-900 font-body">
                  {{ formatPrice(getEffectivePrice(product)) }}
                </span>
                <template v-if="isProductDiscountActive(product)">
                  <span class="text-xs text-gray-400 line-through font-body">
                    {{ formatPrice(product.price) }}
                  </span>
                  <span
                    v-if="getPromoBadgeText(product)"
                    class="px-1.5 py-0.5 text-[11px] font-medium text-white bg-black rounded"
                  >
                    {{ getPromoBadgeText(product) }}
                  </span>
                </template>
              </div>
            </div>
          </button>
        </li>
      </ul>
    </div>

    <div v-if="trimmedQuery" class="px-4 py-3 border-t border-gray-100 bg-gray-50">
      <button
        type="button"
        @click="goToAllResults"
        class="w-full min-h-11 px-4 py-2 text-sm font-medium tracking-wide text-white uppercase transition-colors bg-black rounded-md font-body hover:bg-gray-800"
      >
        Ver todos los resultados
      </button>
    </div>
  </dialog>
</template>

<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProductSearch } from '../../composables/useProductSearch'
import type { Product } from '../../types'
import { categoryLabel } from '../../utils/category'
import { buildImageVariantUrl } from '../../utils/imageUrl'
import {
  formatPrice,
  getEffectivePrice,
  getPromoBadgeText,
  isProductDiscountActive,
} from '../../utils/price'

const router = useRouter()
const dialogRef = ref<HTMLDialogElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)
const { query, results, isLoading, error, hasSearched, reset } = useProductSearch()

const trimmedQuery = computed(() => query.value.trim())

const supportsClosedBy = () =>
  typeof HTMLDialogElement !== 'undefined' && 'closedBy' in HTMLDialogElement.prototype

let pointerDownOutside = false

const isOutsideDialog = (event: PointerEvent, el: HTMLDialogElement): boolean => {
  const rect = el.getBoundingClientRect()
  return (
    event.clientX < rect.left ||
    event.clientX > rect.right ||
    event.clientY < rect.top ||
    event.clientY > rect.bottom
  )
}

const handlePointerDown = (event: PointerEvent) => {
  if (supportsClosedBy() || !dialogRef.value?.open) return
  pointerDownOutside = isOutsideDialog(event, dialogRef.value)
}

const handlePointerUp = (event: PointerEvent) => {
  if (supportsClosedBy() || !dialogRef.value?.open) return
  if (pointerDownOutside && isOutsideDialog(event, dialogRef.value)) {
    close()
  }
  pointerDownOutside = false
}

const isOutOfStock = (product: Product): boolean => {
  if (product.is_unique || !product.variants || product.variants.length === 0) {
    return (product.stock ?? 0) <= 0
  }
  return product.variants.reduce((total, variant) => total + (variant.stock || 0), 0) <= 0
}

const open = () => {
  const dialog = dialogRef.value
  if (!dialog) return
  if (!dialog.open) {
    dialog.showModal()
  }
  nextTick(() => {
    inputRef.value?.focus()
  })
}

const close = () => {
  const dialog = dialogRef.value
  if (dialog?.open) {
    dialog.close()
  }
}

const handleNativeClose = () => {
  pointerDownOutside = false
  reset()
}

const selectProduct = (productId: number) => {
  close()
  router.push(`/product/${productId}`)
}

const goToAllResults = () => {
  const q = trimmedQuery.value
  if (!q) return
  close()
  router.push({ path: '/shop', query: { q } })
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key !== 'Enter') return
  if (event.isComposing || event.keyCode === 229) return
  event.preventDefault()
  goToAllResults()
}

defineExpose({ open, close })
</script>

<style scoped>
dialog {
  margin: 4rem auto auto;
  width: min(calc(100% - 2rem), 40rem);
  max-height: calc(100dvh - 6rem);
  padding: 0;
  border: 1px solid rgb(229 231 235);
  border-radius: 0.75rem;
  background: #ffffff;
  box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.12), 0 8px 10px -6px rgb(0 0 0 / 0.08);
  overflow: hidden;
}

dialog[open] {
  display: flex;
  flex-direction: column;
}

dialog:modal {
  overscroll-behavior: contain;
}

dialog::backdrop {
  background: rgb(0 0 0 / 0.4);
  overflow: hidden;
  overscroll-behavior: contain;
}
</style>
