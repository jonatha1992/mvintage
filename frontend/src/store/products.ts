import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import { productsApi, categoriesApi } from '../config/api'
import type { Product, Category } from '../types/products/product.types'

interface ProductsState {
  products: Product[]
  categories: Category[]
  isLoading: boolean
  error: string | null
  lastFetch: number | null
  lastCategoryFetch: number | null
}

interface ProductsCache {
  data: Product[]
  timestamp: number
  categories: Category[]
  categoryTimestamp: number
}

export const useProductsStore = defineStore('products', () => {
  // State
  const products = ref<Product[]>([])
  const categories = ref<Category[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const lastFetch = ref<number | null>(null)
  const lastCategoryFetch = ref<number | null>(null)

  // Cache configuration
  const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes
  const CATEGORY_CACHE_DURATION = 30 * 60 * 1000 // 30 minutes

  // Computed
  const hasProducts = computed(() => products.value.length > 0)
  const hasCategories = computed(() => categories.value.length > 0)

  const isCacheValid = computed(() => {
    if (!lastFetch.value) return false
    return Date.now() - lastFetch.value < CACHE_DURATION
  })

  const isCategoryCacheValid = computed(() => {
    if (!lastCategoryFetch.value) return false
    return Date.now() - lastCategoryFetch.value < CATEGORY_CACHE_DURATION
  })

  // Actions
  const fetchProducts = async (forceRefresh = false): Promise<Product[]> => {
    // Return cached data if valid and not forcing refresh
    if (!forceRefresh && isCacheValid.value && hasProducts.value) {
      return products.value
    }

    isLoading.value = true
    error.value = null

    try {
      console.log('🔄 Fetching products...')
      const { products: fetchedProducts } = await productsApi.getProducts()
      console.log('✅ Products fetched:', fetchedProducts)
      console.log('📊 Products count:', fetchedProducts?.length)

      if (fetchedProducts && Array.isArray(fetchedProducts)) {
        products.value = fetchedProducts
        lastFetch.value = Date.now()
        error.value = null
        console.log('✅ Products stored in state:', products.value.length)
      } else {
        console.error('❌ Invalid response format:', fetchedProducts)
        throw new Error('Invalid response format')
      }

      return products.value
    } catch (err: any) {
      console.error('❌ Error fetching products:', err)
      error.value = err.response?.data?.detail || err.message || 'Error fetching products'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchCategories = async (forceRefresh = false): Promise<Category[]> => {
    // Return cached data if valid and not forcing refresh
    if (!forceRefresh && isCategoryCacheValid.value && hasCategories.value) {
      return categories.value
    }

    try {
      const fetchedCategories = await categoriesApi.getCategories()

      if (fetchedCategories && Array.isArray(fetchedCategories)) {
        categories.value = fetchedCategories
        lastCategoryFetch.value = Date.now()
      } else {
        throw new Error('Invalid categories response format')
      }

      return categories.value
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Error fetching categories'
      throw err
    }
  }

  const getProductById = (id: number): Product | undefined => {
    return products.value.find(product => product.id === id)
  }

  const getProductsByCategory = (categoryName: string): Product[] => {
    return products.value.filter(product =>
      product.categoria?.toLowerCase() === categoryName.toLowerCase()
    )
  }

  const searchProducts = (query: string): Product[] => {
    const searchTerm = query.toLowerCase()
    return products.value.filter(product =>
      product.name.toLowerCase().includes(searchTerm) ||
      product.description.toLowerCase().includes(searchTerm) ||
      product.categoria?.toLowerCase().includes(searchTerm)
    )
  }

  // Cache invalidation methods
  const invalidateCache = () => {
    lastFetch.value = null
    products.value = []
  }

  const invalidateCategoryCache = () => {
    lastCategoryFetch.value = null
    categories.value = []
  }

  const invalidateAll = () => {
    invalidateCache()
    invalidateCategoryCache()
  }

  // Product management methods (for admin)
  const addProduct = async (productData: any): Promise<Product> => {
    try {
      const newProduct = await productsApi.createProduct(productData)

      // Add to cache
      products.value.unshift(newProduct)

      return newProduct
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Error adding product'
      throw err
    }
  }

  const updateProduct = async (id: number, productData: any): Promise<Product> => {
    try {
      const updatedProduct = await productsApi.updateProduct(id, productData)

      // Update in cache
      const index = products.value.findIndex(p => p.id === id)
      if (index !== -1) {
        products.value[index] = updatedProduct
      }

      return updatedProduct
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Error updating product'
      throw err
    }
  }

  const deleteProduct = async (id: number): Promise<void> => {
    try {
      await productsApi.deleteProduct(id)

      // Remove from cache
      const index = products.value.findIndex(p => p.id === id)
      if (index !== -1) {
        products.value.splice(index, 1)
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Error deleting product'
      throw err
    }
  }

  // Initialize store
  const initialize = async () => {
    try {
      await Promise.all([
        fetchProducts(),
        fetchCategories()
      ])
    } catch (err) {
      // Initialization errors are handled by individual methods
    }
  }

  return {
    // State
    products,
    categories: readonly(categories),
    isLoading: readonly(isLoading),
    error: readonly(error),
    lastFetch: readonly(lastFetch),
    lastCategoryFetch: readonly(lastCategoryFetch),

    // Computed
    hasProducts,
    hasCategories,
    isCacheValid,
    isCategoryCacheValid,

    // Actions
    fetchProducts,
    fetchCategories,
    getProductById,
    getProductsByCategory,
    searchProducts,

    // Cache management
    invalidateCache,
    invalidateCategoryCache,
    invalidateAll,

    // Product management
    addProduct,
    updateProduct,
    deleteProduct,

    // Initialization
    initialize
  }
})

// Helper composable for easy usage
export function useProducts() {
  const store = useProductsStore()

  return {
    // Explicitly expose store properties for proper reactivity
    products: store.products,
    categories: store.categories,
    isLoading: store.isLoading,
    error: store.error,
    hasProducts: store.hasProducts,
    hasCategories: store.hasCategories,
    isCacheValid: store.isCacheValid,
    isCategoryCacheValid: store.isCategoryCacheValid,

    // Store actions
    fetchProducts: store.fetchProducts,
    fetchCategories: store.fetchCategories,
    getProductById: store.getProductById,
    getProductsByCategory: store.getProductsByCategory,
    searchProducts: store.searchProducts,
    invalidateCache: store.invalidateCache,
    invalidateCategoryCache: store.invalidateCategoryCache,
    invalidateAll: store.invalidateAll,
    addProduct: store.addProduct,
    updateProduct: store.updateProduct,
    deleteProduct: store.deleteProduct,
    initialize: store.initialize,

    // Convenience methods
    async ensureProducts() {
      if (!store.hasProducts || !store.isCacheValid) {
        await store.fetchProducts()
      }
      return store.products
    },

    async ensureCategories() {
      if (!store.hasCategories || !store.isCategoryCacheValid) {
        await store.fetchCategories()
      }
      return store.categories
    }
  }
}