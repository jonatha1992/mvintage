<template>
  <nav class="sticky top-0 z-50 bg-white border-b border-gray-100">
    <div class="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <div class="flex-shrink-0">
          <router-link to="/" class="flex items-center space-x-2 text-2xl font-light tracking-wider text-gray-900 font-heading hover:text-gray-700">
            <img src="/imagen-portada.svg" alt="MATILDA VINTAGE Logo" class="w-10 h-10" />
            <span>MATILDA VINTAGE</span>
          </router-link>
        </div>

        <!-- Desktop Menu -->
        <div class="items-center hidden space-x-4 md:flex">
          <div class="flex items-baseline space-x-4">
            <div class="relative">
              <button @click.stop="toggleShopMenu"
                class="px-3 py-2 text-sm font-normal tracking-wide text-gray-900 uppercase transition-colors font-body hover:text-gray-600">
                SHOP
              </button>
              <div v-if="isShopMenuOpen" @click.stop
                class="absolute z-10 w-48 mt-2 bg-white border border-gray-100 shadow-lg">
                <div class="py-1" role="menu" aria-orientation="vertical">
                  <div v-if="categories.length === 0" class="px-4 py-2 text-sm italic text-gray-500 font-body">
                    No hay stock con categorias
                  </div>
                  <router-link v-else v-for="category in categories" :key="category.id"
                    :to="`/shop?category=${category.name.toLowerCase()}`" @click="closeMenus"
                    class="block px-4 py-2 text-sm tracking-wide text-gray-900 uppercase transition-colors font-body hover:bg-gray-50" role="menuitem">{{
                    category.name }}</router-link>
                </div>
              </div>
            </div>
            <!-- Admin Menu - Solo visible para administradores -->
            <div v-if="isAdmin" class="relative">
              <button @click.stop="toggleAdminMenu"
                class="px-3 py-2 text-sm font-normal tracking-wide text-gray-900 uppercase transition-colors font-body hover:text-gray-600">ADMIN</button>
              <div v-if="isAdminMenuOpen" @click.stop
                class="absolute z-50 w-48 mt-2 bg-white border border-gray-200 rounded-md shadow-lg"
                style="top: 100%; left: 0; min-width: 200px;">
                <div class="py-1" role="menu" aria-orientation="vertical">
                  <router-link to="/admin/products" @click="closeMenus"
                    class="block px-4 py-2 text-sm font-normal tracking-wide text-gray-900 uppercase font-body hover:bg-gray-100" role="menuitem">
                    Productos
                  </router-link>
                  <router-link to="/admin/users" @click="closeMenus"
                    class="block px-4 py-2 text-sm font-normal tracking-wide text-gray-900 uppercase font-body hover:bg-gray-100" role="menuitem">
                    Usuarios
                  </router-link>
                  <router-link to="/admin/orders" @click="closeMenus"
                    class="block px-4 py-2 text-sm font-normal tracking-wide text-gray-900 uppercase font-body hover:bg-gray-100" role="menuitem">
                    Pedidos
                  </router-link>
                </div>
              </div>
            </div>
            
            <router-link to="/contact" class="px-3 py-2 text-sm font-normal tracking-wide text-gray-900 uppercase transition-colors font-body hover:text-gray-600">CONTACTO</router-link>
            <router-link to="/how-to-shop" class="px-3 py-2 text-sm font-normal tracking-wide text-gray-900 uppercase transition-colors font-body hover:text-gray-600">CÓMO COMPRAR</router-link>
            <router-link to="/shipping" class="px-3 py-2 text-sm font-normal tracking-wide text-gray-900 uppercase transition-colors font-body hover:text-gray-600">ENVÍOS</router-link>
          </div>

          <!-- Desktop Auth & Cart -->
          <div class="flex items-center space-x-4">
            <button @click="openCartModal" class="relative p-2 text-gray-900 transition-colors hover:text-gray-600 focus:outline-none">
              <span class="sr-only">Carrito</span>
              <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
              <!-- Cart Badge -->
              <span 
                v-if="cartStore.itemCount > 0" 
                class="absolute -top-1 -right-1 bg-black text-white text-xs rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1  font-medium"
              >
                {{ cartStore.itemCount > 99 ? '99+' : cartStore.itemCount }}
              </span>
            </button>
            <!-- User Account Menu -->
            <div v-if="authStore.isAuthenticated" class="relative">
              <button @click.stop="toggleAccountMenu"
                class="px-3 py-2 text-sm font-normal tracking-wide text-gray-900 uppercase transition-colors font-body hover:text-gray-600">
                MI CUENTA
              </button>
              <div v-if="isAccountMenuOpen" @click.stop
                class="absolute z-50 w-48 mt-2 bg-white border border-gray-200 rounded-md shadow-lg"
                style="top: 100%; right: 0; min-width: 200px;">
                <div class="py-1" role="menu" aria-orientation="vertical">
                  <router-link to="/orders" @click="closeMenus"
                    class="block px-4 py-2 text-sm font-normal tracking-wide text-gray-900 uppercase font-body hover:bg-gray-100" role="menuitem">
                    Mis Pedidos
                  </router-link>
                  <router-link to="/profile" @click="closeMenus"
                    class="block px-4 py-2 text-sm font-normal tracking-wide text-gray-900 uppercase font-body hover:bg-gray-100" role="menuitem">
                    Mi Perfil
                  </router-link>
                  <div class="border-t border-gray-100"></div>
                  <button @click="handleLogout" 
                    class="block w-full px-4 py-2 text-sm font-normal tracking-wide text-left text-gray-900 uppercase font-body hover:bg-gray-100" role="menuitem">
                    Cerrar Sesión
                  </button>
                </div>
              </div>
            </div>
            <router-link v-else to="/auth" class="px-3 py-2 text-sm font-normal tracking-wide text-gray-900 uppercase transition-colors font-body hover:text-gray-600">Iniciar Sesión</router-link>
          </div>
        </div>

        <!-- Mobile Menu Button -->
        <div class="flex items-center md:hidden">
          <button @click="openCartModal" class="relative p-2 mr-4 text-gray-900 transition-colors hover:text-gray-600 focus:outline-none">
            <span class="sr-only">Carrito</span>
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            <!-- Mobile Cart Badge -->
            <span 
              v-if="cartStore.itemCount > 0" 
              class="absolute -top-1 -right-1 bg-black text-white text-xs rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1 "
            >
              {{ cartStore.itemCount > 99 ? '99+' : cartStore.itemCount }}
            </span>
          </button>
          <button @click.stop="toggleMobileMenu" class="inline-flex items-center justify-center p-2 text-gray-900 transition-colors hover:text-gray-600 focus:outline-none">
            <span class="sr-only">Open main menu</span>
            <svg v-if="!isMobileMenuOpen" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" /></svg>
            <svg v-else class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile Menu -->
    <div v-if="isMobileMenuOpen" class="bg-white border-t border-gray-100 md:hidden">
      <div class="px-4 pt-4 pb-6 space-y-2">
        <button @click.stop="toggleMobileShopMenu" class="block w-full px-3 py-3 text-sm font-normal tracking-wide text-left text-gray-900 uppercase transition-colors font-body hover:text-gray-600">SHOP</button>
        <div v-if="isMobileShopMenuOpen" class="pl-4 space-y-1">
          <div v-if="categories.length === 0" class="px-3 py-2 text-sm italic text-gray-500 font-body">
            - No hay stock con categorías
          </div>
          <router-link v-else v-for="category in categories" :key="category.id" :to="`/shop?category=${category.name.toLowerCase()}`" @click="closeMenus" class="block px-3 py-2 text-sm tracking-wide text-gray-700 uppercase transition-colors font-body hover:text-gray-900">- {{ category.name }}</router-link>
        </div>
        <!-- Admin Menu Mobile - Solo visible para administradores -->
        <div v-if="isAdmin">
          <button @click.stop="toggleMobileAdminMenu" class="block w-full px-3 py-3 text-sm font-normal tracking-wide text-left text-gray-900 uppercase transition-colors font-body hover:text-gray-600">ADMIN</button>
          <div v-if="isMobileAdminMenuOpen" class="pl-4 space-y-1">
            <router-link to="/admin/products" @click="closeMenus" class="block px-3 py-2 text-sm font-normal tracking-wide text-gray-700 uppercase transition-colors font-body hover:text-gray-900">- Productos</router-link>
            <router-link to="/admin/users" @click="closeMenus" class="block px-3 py-2 text-sm font-normal tracking-wide text-gray-700 uppercase transition-colors font-body hover:text-gray-900">- Usuarios</router-link>
            <router-link to="/admin/orders" @click="closeMenus" class="block px-3 py-2 text-sm font-normal tracking-wide text-gray-700 uppercase transition-colors font-body hover:text-gray-900">- Pedidos</router-link>
          </div>
        </div>
        <!-- User Menu Mobile -->
        <div v-if="authStore.isAuthenticated" class="pt-2 mt-2 border-t border-gray-200">
          <div class="relative">
            <button @click.stop="toggleMobileAccountMenu" class="flex items-center justify-between w-full px-3 py-3 text-sm font-normal tracking-wide text-left text-gray-900 uppercase transition-colors font-body hover:text-gray-600">
              MI CUENTA
              <svg :class="{'transform rotate-180': isMobileAccountMenuOpen}" class="w-4 h-4 text-gray-500 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div v-if="isMobileAccountMenuOpen" class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg">
              <div class="py-1" role="menu" aria-orientation="vertical">
                <router-link to="/orders" @click="closeMenus" class="block px-4 py-2 text-sm font-normal tracking-wide text-gray-900 uppercase font-body hover:bg-gray-100" role="menuitem">
                  Mis Pedidos
                </router-link>
                <router-link to="/profile" @click="closeMenus" class="block px-4 py-2 text-sm font-normal tracking-wide text-gray-900 uppercase font-body hover:bg-gray-100" role="menuitem">
                  Mi Perfil
                </router-link>
                <div class="border-t border-gray-100"></div>
                <button @click="handleLogout" class="block w-full px-4 py-2 text-sm font-normal tracking-wide text-left text-gray-900 uppercase font-body hover:bg-gray-100" role="menuitem">
                  Cerrar Sesión
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="pt-2 mt-2 border-t border-gray-200">
          <router-link to="/auth" @click="closeMenus" class="block px-3 py-3 text-sm font-normal tracking-wide text-gray-900 uppercase transition-colors font-body hover:text-gray-600">
            Iniciar Sesión
          </router-link>
        </div>
        
        <router-link to="/contact" @click="closeMenus" class="block px-3 py-3 text-sm font-normal tracking-wide text-gray-900 uppercase transition-colors font-body hover:text-gray-600">CONTACTO</router-link>
        <router-link to="/how-to-shop" @click="closeMenus" class="block px-3 py-3 text-sm font-normal tracking-wide text-gray-900 uppercase transition-colors font-body hover:text-gray-600">CÓMO COMPRAR</router-link>
        <router-link to="/shipping" @click="closeMenus" class="block px-3 py-3 text-sm font-normal tracking-wide text-gray-900 uppercase transition-colors font-body hover:text-gray-600">ENVÍOS</router-link>
        
        <div class="pt-4 mt-4 border-t border-gray-200">
          <div v-if="authStore.isAuthenticated" class="flex items-center px-3 mb-3">
            <div class="mr-3">
              <img 
                :src="authStore.firebaseUser?.photoURL || '/user-avatar-placeholder.png'" 
                :alt="authStore.firebaseUser?.displayName || 'Usuario'"
                class="object-cover w-10 h-10 rounded-full"
                onerror="this.src='/user-avatar-placeholder.png'"
              >
            </div>
            <div>
              <div class="text-sm font-medium text-gray-900 font-body">{{ authStore.firebaseUser?.displayName || 'Usuario' }}</div>
              <div class="text-xs text-gray-500 font-body">{{ authStore.firebaseUser?.email || '' }}</div>
            </div>
          </div>
          <div class="space-y-1">
            <button v-if="authStore.isAuthenticated" @click="handleLogout" class="block w-full px-3 py-3 text-sm font-normal tracking-wide text-left text-gray-900 uppercase transition-colors font-body hover:text-gray-600">Cerrar Sesión</button>
            <router-link v-else to="/auth" @click="closeMenus" class="block px-3 py-3 text-sm font-normal tracking-wide text-gray-900 uppercase transition-colors font-body hover:text-gray-600">Iniciar Sesión</router-link>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useAuthStore } from '../../store/auth';
import { useCartStore } from '../../store/cart';
import { useCartModal } from '../../composables/useCartModal';
import { useRouter } from 'vue-router';
import { masterDataApi } from '../../config/index';
import type { Category } from '../../types';

const isMobileMenuOpen = ref(false);
const isMobileShopMenuOpen = ref(false);
const isMobileAdminMenuOpen = ref(false);
const isMobileAccountMenuOpen = ref(false);
const isShopMenuOpen = ref(false);
const isAdminMenuOpen = ref(false);
const isAccountMenuOpen = ref(false);
const authStore = useAuthStore();
const cartStore = useCartStore();
const router = useRouter();
const { openCartModal } = useCartModal();
const categories = ref<Category[]>([]);

// Computed memoizado para admin access (evitar múltiples evaluaciones)
const isAdmin = computed(() => authStore.hasAdminAccess);

const toggleShopMenu = () => {
  isShopMenuOpen.value = !isShopMenuOpen.value;
};

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const toggleMobileShopMenu = () => {
  isMobileShopMenuOpen.value = !isMobileShopMenuOpen.value;
}

const toggleAdminMenu = () => {
  isAdminMenuOpen.value = !isAdminMenuOpen.value;
};

const toggleMobileAdminMenu = () => {
  isMobileAdminMenuOpen.value = !isMobileAdminMenuOpen.value;
};

const toggleMobileAccountMenu = () => {
  isMobileAccountMenuOpen.value = !isMobileAccountMenuOpen.value;
};

const toggleAccountMenu = () => {
  isAccountMenuOpen.value = !isAccountMenuOpen.value;
};

const handleLogout = async () => {
  try {
    await authStore.logout();
    closeMenus();
    router.push('/');
  } catch (error) {
  }
};

const loadCategories = async () => {
  try {
    // Usar endpoint que solo devuelve categorías con stock
    categories.value = await masterDataApi.getCategoriesWithStock();
  } catch (error) {
    // Fallback a todas las categorías si falla
    try {
      categories.value = await masterDataApi.getCategories();
    } catch (fallbackError) {
    }
  }
};

const closeMenus = () => {
  isMobileMenuOpen.value = false;
  isMobileShopMenuOpen.value = false;
  isMobileAdminMenuOpen.value = false;
  isMobileAccountMenuOpen.value = false;
  isShopMenuOpen.value = false;
  isAdminMenuOpen.value = false;
  isAccountMenuOpen.value = false;
};

onMounted(() => {
  loadCategories();
  document.addEventListener('click', closeMenus);
});

onUnmounted(() => {
  document.removeEventListener('click', closeMenus);
});
</script>

