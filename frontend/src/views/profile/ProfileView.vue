<template>
  <div class="min-h-screen px-4 py-12 bg-gray-50 sm:px-6 lg:px-8">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="mb-8 md:flex md:items-center md:justify-between">
        <div class="flex-1 min-w-0">
          <h2 class="text-2xl font-light text-gray-900 font-heading">Mi Perfil</h2>
          <p class="mt-1 text-sm text-gray-500 font-body">
            Gestiona tu información personal y preferencias
          </p>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <!-- Sidebar -->
        <div class="lg:col-span-3">
          <nav class="space-y-1">
            <router-link to="/profile" class="flex items-center px-4 py-3 text-sm font-medium text-gray-900 bg-gray-100 rounded-lg">
              <UserIcon class="w-5 h-5 mr-3 text-gray-500" />
              Mi Perfil
            </router-link>
            <router-link to="/orders" class="flex items-center px-4 py-3 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-50">
              <ShoppingBagIcon class="w-5 h-5 mr-3 text-gray-400" />
              Mis Pedidos
            </router-link>
            <button @click="handleLogout" class="flex items-center w-full px-4 py-3 text-sm font-medium text-red-600 rounded-lg hover:bg-red-50">
              <ArrowLeftOnRectangleIcon class="w-5 h-5 mr-3 text-red-500" />
              Cerrar Sesión
            </button>
          </nav>
        </div>

        <!-- Main Content -->
        <div class="lg:col-span-9">
          <div class="overflow-hidden bg-white rounded-lg shadow">
            <div class="px-4 py-5 border-b border-gray-200 sm:px-6">
              <h3 class="text-lg font-medium leading-6 text-gray-900 font-heading">
                Información del Perfil
              </h3>
            </div>
            <div class="px-4 py-5 sm:p-6">
              <form @submit.prevent="handleSubmit" class="space-y-6">
                <div class="flex items-center mb-6 space-x-6">
                  <div class="relative w-20 h-20 overflow-hidden bg-gray-100 rounded-full">
                    <img
                      class="w-full h-full text-gray-300"
                      :src="userPhotoURL || 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'"
                      :alt="displayName || 'Usuario'"
                    />
                  </div>
                  <div>
                    <div class="text-lg font-medium text-gray-900 font-heading">{{ displayName || 'Usuario' }}</div>
                    <div class="text-sm text-gray-500 font-body">Cliente desde {{ formatJoinDate }}</div>
                  </div>
                </div>

                <div class="grid grid-cols-6 gap-6">
                  <div class="col-span-6 sm:col-span-3">
                    <label class="block text-sm font-medium text-gray-700 font-body">Nombre</label>
                    <input
                      type="text"
                      v-model="userForm.first_name"
                      class="block w-full px-3 py-2 mt-1 border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm"
                      placeholder="Ingresa tu nombre"
                    />
                  </div>

                  <div class="col-span-6 sm:col-span-3">
                    <label class="block text-sm font-medium text-gray-700 font-body">Apellido</label>
                    <input
                      type="text"
                      v-model="userForm.last_name"
                      class="block w-full px-3 py-2 mt-1 border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm"
                      placeholder="Ingresa tu apellido"
                    />
                  </div>

                  <div class="col-span-6 sm:col-span-3">
                    <label class="block text-sm font-medium text-gray-700 font-body">Correo electrónico</label>
                    <input
                      type="email"
                      v-model="userForm.email"
                      class="block w-full px-3 py-2 mt-1 border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm"
                      readonly
                      :title="'Email verificado por Firebase Auth'"
                    />
                  </div>

                  <div class="col-span-6 sm:col-span-3">
                    <label class="block text-sm font-medium text-gray-700 font-body">Teléfono</label>
                    <input
                      type="tel"
                      v-model="userForm.phone"
                      class="block w-full px-3 py-2 mt-1 border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm"
                      placeholder="Ej: +54 11 1234-5678"
                    />
                  </div>
                </div>

                <div class="flex justify-end mt-8 space-x-3">
                  <button type="button" @click="resetForm" class="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">
                    Cancelar
                  </button>
                  <button type="submit" :disabled="loading" class="px-4 py-2 text-sm font-medium text-white bg-black border border-transparent rounded-md hover:bg-gray-800 disabled:opacity-50">
                    {{ loading ? 'Guardando...' : 'Guardar cambios' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { UserIcon, ShoppingBagIcon, ArrowLeftOnRectangleIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '../../store/auth'
import { useToast } from 'vue-toastification'
import { authApi } from '../../config/api'
import type { UserUpdateData } from '../../types/users/user.types'

const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()

const loading = ref(false)
const userForm = ref<UserUpdateData>({
  name: '',
  first_name: '',
  last_name: '',
  email: '',
  phone: ''
})

// Computed properties para mostrar información del usuario
const displayName = computed(() => {
  if (authStore.backendUser?.name) {
    return authStore.backendUser.name
  }
  if (authStore.firebaseUser?.displayName) {
    return authStore.firebaseUser.displayName
  }
  if (userForm.value.first_name && userForm.value.last_name) {
    return `${userForm.value.first_name} ${userForm.value.last_name}`
  }
  return authStore.firebaseUser?.email?.split('@')[0] || 'Usuario'
})

const userPhotoURL = computed(() => {
  return authStore.firebaseUser?.photoURL
})

const formatJoinDate = computed(() => {
  if (authStore.firebaseUser?.metadata?.creationTime) {
    const date = new Date(authStore.firebaseUser.metadata.creationTime)
    return date.toLocaleDateString('es-ES', { 
      year: 'numeric', 
      month: 'long' 
    })
  }
  return 'Fecha no disponible'
})

// Función para inicializar el formulario con datos del usuario
const initializeForm = () => {
  if (authStore.backendUser) {
    userForm.value = {
      name: authStore.backendUser.name || '',
      first_name: authStore.backendUser.first_name || '',
      last_name: authStore.backendUser.last_name || '',
      email: authStore.backendUser.email || '',
      phone: authStore.backendUser.phone || ''
    }
  } else if (authStore.firebaseUser) {
    // Si solo tenemos datos de Firebase, usar esos
    const displayName = authStore.firebaseUser.displayName || ''
    const nameParts = displayName.split(' ')
    
    userForm.value = {
      name: displayName,
      first_name: nameParts[0] || '',
      last_name: nameParts.slice(1).join(' ') || '',
      email: authStore.firebaseUser.email || '',
      phone: authStore.firebaseUser.phoneNumber || ''
    }
  }
}

// Función para resetear el formulario
const resetForm = () => {
  initializeForm()
}

// Función para manejar el envío del formulario
const handleSubmit = async () => {
  loading.value = true
  try {
    // Llamar al API para actualizar el usuario
    const updatedUser = await authApi.updateCurrentUser(userForm.value)
    
    // Actualizar el store con los nuevos datos
    await authStore.fetchBackendUser()
    
    toast.success('Perfil actualizado correctamente')
    
  } catch (error: any) {
    // Manejar diferentes tipos de errores
    if (error.response?.status === 401) {
      toast.error('Sesión expirada. Por favor, inicia sesión nuevamente.')
      await authStore.logout()
      router.push('/auth')
    } else if (error.response?.status === 400) {
      toast.error('Datos inválidos. Verifica la información ingresada.')
    } else if (error.response?.data?.detail) {
      toast.error(`Error: ${error.response.data.detail}`)
    } else {
      toast.error('Error al actualizar el perfil. Intenta nuevamente.')
    }
  } finally {
    loading.value = false
  }
}

// Función para manejar el logout
const handleLogout = async () => {
  try {
    await authStore.logout()
    toast.success('Sesión cerrada correctamente')
    router.push('/auth')
  } catch (error) {
    toast.error('Error al cerrar sesión')
  }
}

// Watcher para actualizar el formulario cuando cambien los datos del usuario
watch([() => authStore.backendUser, () => authStore.firebaseUser], () => {
  initializeForm()
}, { immediate: true })

// Inicializar cuando el componente se monta
onMounted(() => {
  initializeForm()
})
</script>

