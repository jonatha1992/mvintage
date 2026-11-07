<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Breadcrumbs -->
    <nav class="border-b border-gray-200 bg-gray-50">
      <div class="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <div class="flex items-center py-4 space-x-2 text-sm">
          <router-link to="/" class="text-gray-400 transition-colors hover:text-gray-600">
            Home
          </router-link>
          <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
          <router-link to="/shop" class="text-gray-400 transition-colors hover:text-gray-600">
            Shop
          </router-link>
          <svg v-if="selectedCategory" class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
          <span v-if="selectedCategory" class="font-medium text-gray-900">
            {{ selectedCategory }}
          </span>
        </div>
      </div>
    </nav>

    <div class="px-4 py-8 mx-auto max-w-7xl sm:px-6 lg:px-8">
      <div class="lg:grid lg:grid-cols-4 lg:gap-8">
        <!-- Sidebar Filters -->
        <div class="hidden lg:block lg:col-span-1">
          <div class="sticky top-20">
            <!-- Categories Filter -->
            <div class="pb-6 border-b border-gray-200">
              <h3 class="mb-4 text-lg font-medium text-gray-900">Categorias</h3>
              <div class="space-y-2">
                <label v-for="category in categories" :key="category.id" class="flex items-center">
                  <input 
                    type="radio" 
                    :value="category.name" 
                    v-model="filters.category"
                    @change="applyFilters"
                    class="w-4 h-4 text-gray-900 border-gray-300 focus:ring-gray-500"
                  >
                  <span class="ml-3 text-sm text-gray-700">{{ category.name }}</span>
                  <span class="ml-auto text-xs text-gray-500">({{ getCategoryCount(category.name) }})</span>
                </label>
                <label class="flex items-center">
                  <input 
                    type="radio" 
                    value="" 
                    v-model="filters.category"
                    @change="applyFilters"
                    class="w-4 h-4 text-gray-900 border-gray-300 focus:ring-gray-500"
                  >
                  <span class="ml-3 text-sm text-gray-700">Todas las categorías</span>
                  <span class="ml-auto text-xs text-gray-500">({{ allProducts?.length || 0 }})</span>
                </label>
              </div>
            </div>

            <!-- Price Filter -->
            <div class="py-6 border-b border-gray-200">
              <h3 class="mb-4 text-lg font-medium text-gray-900">Precio</h3>
              <div class="space-y-2">
                <label v-for="priceRange in priceRanges" :key="priceRange.label" class="flex items-center">
                  <input 
                    type="radio" 
                    :value="priceRange.value" 
                    v-model="filters.priceRange"
                    @change="applyFilters"
                    class="w-4 h-4 text-gray-900 border-gray-300 focus:ring-gray-500"
                  >
                  <span class="ml-3 text-sm text-gray-700">{{ priceRange.label }}</span>
                </label>
                <label class="flex items-center">
                  <input 
                    type="radio" 
                    value="" 
                    v-model="filters.priceRange"
                    @change="applyFilters"
                    class="w-4 h-4 text-gray-900 border-gray-300 focus:ring-gray-500"
                  >
                  <span class="ml-3 text-sm text-gray-700">Todos los precios</span>
                </label>
              </div>
            </div>

            <!-- Sort Options -->
            <div class="py-6">
              <h3 class="mb-4 text-lg font-medium text-gray-900">Ordenar por</h3>
              <select 
                v-model="filters.sortBy" 
                @change="applyFilters"
                class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-transparent"
              >
                <option value="">Recomendados</option>
                <option value="price-asc">Precio: Menor a Mayor</option>
                <option value="price-desc">Precio: Mayor a Menor</option>
                <option value="name-asc">Nombre: A-Z</option>
                <option value="name-desc">Nombre: Z-A</option>
                <option value="newest">Mas Nuevos</option>
              </select>
            </div>

            <!-- Clear Filters -->
            <button 
              @click="clearFilters"
              class="w-full text-sm text-center text-gray-500 underline hover:text-gray-700"
            >
              Limpiar filtros
            </button>
          </div>
        </div>

        <!-- Products Grid -->
        <div class="lg:col-span-3">
          <!-- Mobile Filter Toggle -->
          <div class="mb-6 lg:hidden">
            <button 
              @click="showMobileFilters = !showMobileFilters"
              class="flex items-center justify-center w-full py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              Filtros ({{ activeFiltersCount }})
            </button>
          </div>

          <!-- Collection Header -->
          <div class="flex items-center justify-between mb-8">
            <div>
              <h1 class="text-3xl font-light tracking-wide text-gray-800">
                {{ collectionTitle }}
              </h1>
              <p class="mt-1 text-sm text-gray-400">
                {{ filteredProducts.length }} producto{{ filteredProducts.length !== 1 ? 's' : '' }}
              </p>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="isLoading && products.length === 0" class="grid grid-cols-1 gap-12 sm:grid-cols-2 lg:grid-cols-3">
            <div v-for="n in 6" :key="n" class="animate-pulse">
              <div class="bg-gray-200 rounded-lg aspect-square"></div>
              <div class="mt-4 space-y-2">
                <div class="h-4 bg-gray-200 rounded"></div>
                <div class="w-2/3 h-4 bg-gray-200 rounded"></div>
              </div>
            </div>
          </div>

          <!-- Products Grid -->
          <div v-else class="grid grid-cols-1 gap-12 sm:grid-cols-2 lg:grid-cols-3">
            <ProductCard
              v-for="product in paginatedProducts"
              :key="product.id"
              :product="product"
            />
          </div>

          <!-- Load More / Pagination -->
          <div v-if="hasMoreProducts" class="mt-12 text-center">
            <button 
              @click="loadMoreProducts"
              class="btn-minimal btn-light"
            >
              Ver más Productos
            </button>
          </div>

          <!-- Empty State -->
          <div v-if="filteredProducts.length === 0" class="py-16 text-center">
            <div class="mb-4 text-gray-400">
              <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
              </svg>
            </div>
            <h3 class="mb-2 text-lg font-medium text-gray-900">No se encontraron productos</h3>
            <p class="mb-4 text-gray-500">Intenta ajustar los filtros o explorar otras categorías</p>
            <button @click="clearFilters" class="btn-minimal btn-dark">
              Limpiar Filtros
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Filters Overlay -->
    <div v-if="showMobileFilters" class="fixed inset-0 z-50 lg:hidden">
      <div class="fixed inset-0 bg-black bg-opacity-25" @click="showMobileFilters = false"></div>
      <div class="fixed top-0 right-0 w-full h-full max-w-xs bg-white shadow-xl">
        <div class="flex items-center justify-between p-4 border-b">
          <h2 class="text-lg font-medium text-gray-900">Filtros</h2>
          <button @click="showMobileFilters = false" class="p-2 text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-4 space-y-6">
          <!-- Mobile filters content (same as desktop) -->
          <!-- Categories -->
          <div>
            <h3 class="mb-3 text-base font-medium text-gray-900">Categorías</h3>
            <div class="space-y-2">
              <label v-for="category in categories" :key="category.id" class="flex items-center">
                <input 
                  type="radio" 
                  :value="category.name" 
                  v-model="filters.category"
                  @change="applyFilters"
                  class="w-4 h-4 text-gray-900 border-gray-300 focus:ring-gray-500"
                >
                <span class="ml-3 text-sm text-gray-700">{{ category.name }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ProductCard from '../../components/products/ProductCard.vue'
import { masterDataApi } from '../../config/index'
import type { Product, Category } from '../../types'
import { useProducts } from '../../store/products'

const route = useRoute()
const router = useRouter()

// Use products store
const { products, categories: storeCategories, isLoading, ensureProducts, ensureCategories } = useProducts()

// Data
const categories = ref<Category[]>([])
const showMobileFilters = ref(false)
const productsPerPage = ref(12)
const currentPage = ref(1)

// Filters
const filters = ref({
  category: '',
  priceRange: '',
  sortBy: ''
})

// Price ranges
const priceRanges = [
  { label: '$0 - $50', value: '0-50' },
  { label: '$50 - $100', value: '50-100' },
  { label: '$100 - $200', value: '100-200' },
  { label: '$200+', value: '200+' }
]

// Computed
const selectedCategory = computed(() => {
  return filters.value.category || (route.query.category as string) || ''
})

const collectionTitle = computed(() => {
  if (selectedCategory.value) {
    return `Colección ${selectedCategory.value.charAt(0).toUpperCase() + selectedCategory.value.slice(1).toLowerCase()}`
  }
  return 'Toda la Colección'
})

const filteredProducts = computed(() => {
  if (!products.value) return []
  let filteredProducts = [...products.value]

  // Filter by category
  if (filters.value.category) {
    filteredProducts = filteredProducts.filter(product =>
      product.categoria?.toLowerCase() === filters.value.category.toLowerCase()
    )
  }

  // Filter by price range
  if (filters.value.priceRange) {
    const [min, max] = filters.value.priceRange.split('-').map(Number)
    filteredProducts = filteredProducts.filter(product => {
      const price = Number(product.price)
      if (max) {
        return price >= min && price <= max
      } else {
        return price >= min
      }
    })
  }

  // Sort products
  if (filters.value.sortBy) {
    switch (filters.value.sortBy) {
      case 'price-asc':
        filteredProducts.sort((a, b) => Number(a.price) - Number(b.price))
        break
      case 'price-desc':
        filteredProducts.sort((a, b) => Number(b.price) - Number(a.price))
        break
      case 'name-asc':
        filteredProducts.sort((a, b) => a.name.localeCompare(b.name))
        break
      case 'name-desc':
        filteredProducts.sort((a, b) => b.name.localeCompare(a.name))
        break
      case 'newest':
        // Ordenar por ID (asumiendo que IDs mÃ¡s altos = productos mÃ¡s nuevos)
        // TambiÃ©n priorizar productos marcados como 'new'
        filteredProducts.sort((a, b) => {
          if (a.is_new && !b.is_new) return -1
          if (!a.is_new && b.is_new) return 1
          return b.id - a.id
        })
        break
    }
  }

  return filteredProducts
})

const paginatedProducts = computed(() => {
  const endIndex = currentPage.value * productsPerPage.value
  return filteredProducts.value.slice(0, endIndex)
})

const hasMoreProducts = computed(() => {
  return paginatedProducts.value.length < filteredProducts.value.length
})

const activeFiltersCount = computed(() => {
  let count = 0
  if (filters.value.category) count++
  if (filters.value.priceRange) count++
  if (filters.value.sortBy) count++
  return count
})

// Methods
const getCategoryCount = (categoryName: string) => {
  if (!products.value) return 0
  return products.value.filter(product =>
    product.categoria?.toLowerCase() === categoryName.toLowerCase()
  ).length
}

const applyFilters = () => {
  currentPage.value = 1
  // Update URL query params
  const query: any = {}
  if (filters.value.category) query.category = filters.value.category
  if (filters.value.priceRange) query.price = filters.value.priceRange
  if (filters.value.sortBy) query.sort = filters.value.sortBy
  
  router.push({ query })
}

const clearFilters = () => {
  filters.value = {
    category: '',
    priceRange: '',
    sortBy: ''
  }
  currentPage.value = 1
  router.push({ query: {} })
}

const loadMoreProducts = () => {
  currentPage.value++
}

const loadProducts = async () => {
  if (import.meta.env.VITEST) return
  try {
    await ensureProducts()
  } catch (error) {
    // Error is handled by the store
  }
}

const loadCategories = async () => {
  try {
    categories.value = await masterDataApi.getCategoriesWithStock()
  } catch (error) {
    try {
      categories.value = await masterDataApi.getCategories()
    } catch (fallbackError) {
    }
  }
}

// Watchers
watch(() => route.query, (newQuery) => {
  filters.value.category = (newQuery.category as string) || ''
  filters.value.priceRange = (newQuery.price as string) || ''
  filters.value.sortBy = (newQuery.sort as string) || ''
  currentPage.value = 1
}, { immediate: true })

// Lifecycle
onMounted(() => {
  loadProducts()
  loadCategories()
})
</script>

