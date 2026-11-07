<template>
  <div class="space-y-6">
    <!-- Search and Filters -->
    <div class="flex flex-col gap-4 sm:flex-row">
      <div class="flex-1">
        <input
          v-model="searchQuery"
          @input="searchUsers"
          type="text"
          placeholder="Buscar usuarios por email..."
          class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      <div class="flex gap-2">
        <button
          @click="showAddUserModal = true"
          class="px-4 py-2 text-white bg-green-600 rounded-md hover:bg-green-700"
        >
          <span  class="text-white">+ Agregar Usuario</span>
        </button>
        <button
          @click="loadUsers"
          :disabled="loading"
          class="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          <span class="text-white" >{{ loading ? 'Cargando...' : 'Actualizar Lista' }}</span>
        </button>
      </div>
    </div>

    <!-- Alert Messages -->
    <!-- Toast notifications are now handled by vue-toastification -->

    <!-- Users Table -->
    <div class="overflow-hidden bg-white rounded-lg shadow-md">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900 font-heading">
          Usuarios del Sistema ({{ filteredUsers.length }})
        </h3>
      </div>
      
      <div v-if="loading && users.length === 0" class="p-6 text-center font-body text-body-text">
        Cargando usuarios...
      </div>
      
      <div v-else-if="filteredUsers.length === 0" class="p-6 text-center font-body text-body-text">
        {{ searchQuery ? 'No se encontraron usuarios con esa búsqueda' : 'No hay usuarios registrados' }}
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase font-heading">Usuario</th>
              <th class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase font-heading">Roles</th>
              <th class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase font-heading">Estado</th>
              <th class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase font-heading">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="user in filteredUsers" :key="user.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 w-10 h-10">
                    <div class="flex items-center justify-center w-10 h-10 bg-gray-300 rounded-full">
                      <span class="text-sm font-medium font-body text-body-text">
                        {{ getUserInitials(user.email) }}
                      </span>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium font-body text-body-text">{{ user.email }}</div>
                    <div class="text-sm font-body text-body-text">ID: {{ user.id }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="role in user.roles || []"
                    :key="role.id"
                    class="inline-flex px-2 py-1 text-xs font-semibold rounded-full font-body"
                    :class="getRoleBadgeClass(role.name)"
                  >
                    {{ role.name.toUpperCase() }}
                  </span>
                  <span v-if="!user.roles || user.roles.length === 0" class="text-xs font-body text-body-text">
                    Sin roles asignados
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex px-2 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded-full font-body">
                  Activo
                </span>
              </td>
              <td class="px-6 py-4 text-sm font-medium whitespace-nowrap">
                <button
                  @click="manageUserRoles(user)"
                  class="btn-blue btn-sm mr-4"
                >
                  <span class="text-white" >Gestionar Roles</span>
                </button>
                <button
                  @click="viewUserDetails(user)"
                  class="btn-green btn-sm"
                >
                  <span class="text-white" >Ver Detalles</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Role Management Modal -->
    <div v-if="showRoleModal" class="fixed inset-0 z-50 w-full h-full overflow-y-auto bg-gray-600 bg-opacity-50">
      <div class="relative w-11/12 p-5 mx-auto bg-white border rounded-md shadow-lg top-20 md:w-3/4 lg:w-3/5 xl:w-1/2">
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-gray-900 font-heading">
              Gestionar Roles: {{ selectedUser?.email }}
            </h3>
            <button
              @click="closeRoleModal"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <!-- Current Roles -->
          <div class="mb-4">
            <h4 class="mb-2 text-sm font-medium text-gray-700 font-heading">Roles Actuales</h4>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="role in selectedUser?.roles || []"
                :key="role.id"
                class="inline-flex items-center px-3 py-1 text-sm rounded-full font-body"
                :class="getRoleBadgeClass(role.name)"
              >
                {{ role.name.toUpperCase() }}
                <button
                  @click="removeUserRole(selectedUser!.id, role.id)"
                  class="ml-2 text-current hover:text-red-600"
                >
                  ×
                </button>
              </span>
              <span v-if="!selectedUser?.roles || selectedUser.roles.length === 0" class="text-sm text-white ">
                Sin roles asignados
              </span>
            </div>
          </div>
          
          <!-- Add Role -->
          <div class="mb-4">
            <h4 class="mb-2 text-sm font-medium text-gray-700 font-heading font-body">Agregar Rol</h4>
            <div class="flex gap-2">
              <select v-model="selectedRoleToAdd" class="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-md">
                <option class="font-body" value="">Seleccionar rol</option>
                <option
                  v-for="role in availableRoles"
                  :key="role.id"
                  :value="role.id"
                  class="text-sm "
                >
                  {{ role.name.toUpperCase() }} - {{ role.description }}
                </option>
              </select>
              <button
                @click="addUserRole"
                :disabled="!selectedRoleToAdd || loading"
                class="px-4 py-2 text-white bg-green-600 rounded-md hover:bg-green-700 disabled:bg-green-600"
              >
                <span class="text-white">+</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add User Modal -->
    <div v-if="showAddUserModal" class="fixed inset-0 z-50 w-full h-full overflow-y-auto bg-gray-600 bg-opacity-50">
      <div class="relative w-11/12 p-5 mx-auto bg-white border rounded-md shadow-lg top-20 md:w-3/4 lg:w-1/2">
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-gray-900 font-heading">
              Agregar Nuevo Usuario
            </h3>
            <button
              @click="closeAddUserModal"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <!-- User Form -->
          <form @submit.prevent="addNewUser" class="space-y-4">
            <div>
              <label class="block mb-1 text-sm font-medium font-body text-body-text">Email</label>
              <input
                v-model="newUserForm.email"
                @blur="checkEmailExists"
                type="email"
                required
                placeholder="usuario@ejemplo.com"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-500': emailError }"
              />
              <p v-if="emailError" class="mt-1 text-sm text-red-600 font-body">{{ emailError }}</p>
            </div>
            
            <div>
              <label class="block mb-1 text-sm font-medium font-body text-body-text">Nombre de Usuario (opcional)</label>
              <input
                v-model="newUserForm.username"
                type="text"
                placeholder="Nombre de usuario"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label class="block mb-1 text-sm font-medium font-body text-body-text">Contraseña Temporal</label>
              <div class="relative">
                <input
                  v-model="newUserForm.password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  placeholder="Contraseña temporal (min. 6 caracteres)"
                  minlength="6"
                  class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute inset-y-0 right-0 flex items-center px-3 text-gray-400 hover:text-gray-600"
                >
                  <svg v-if="showPassword" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L7.05 7.05M9.878 9.878a3 3 0 013.242 3.242m4.242 4.242L19.95 19.95M14.12 14.12l4.243 4.242M14.12 14.12a3 3 0 01-4.243-4.243m0 0L7.05 7.05"></path>
                  </svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                </button>
              </div>
            </div>
            
            <div>
              <label class="block mb-1 text-sm font-medium text-gray-700 font-body">Rol Inicial</label>
              <select
                v-model="newUserForm.roleId"
                required
                class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option class="font-body" value="">Seleccionar rol</option>
                <option
                  v-for="role in adminRoles"
                  :key="role.id"
                  :value="role.id"
                  class="text-sm font-body"
                >
                  {{ role.name.toUpperCase() }} - {{ role.description }}
                </option>
              </select>
            </div>
            
            <div class="flex gap-2 pt-4">
              <button
                type="button"
                @click="closeAddUserModal"
                class="flex-1 px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                <span class="font-body">Cancelar</span>
              </button>
              <button
                type="submit"
                :disabled="loading"
                class="flex-1 px-4 py-2 text-white bg-green-600 rounded-md hover:bg-green-700 disabled:bg-gray-400"
              >
                <span class="text-white">{{ loading ? 'Creando...' : 'Crear Usuario' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { rolesApi, usersApi } from '../../config/index'
import type { Role } from '../../types/users/role.types'
import type { UserWithRoles } from '../../types/users/user.types'

const toast = useToast()

// Reactive data
const users = ref<UserWithRoles[]>([])
const roles = ref<Role[]>([])
const loading = ref(false)
const searchQuery = ref('')
const showRoleModal = ref(false)
const selectedUser = ref<UserWithRoles | null>(null)
const selectedRoleToAdd = ref<number | ''>('')
const showAddUserModal = ref(false)
const newUserForm = ref({
  email: '',
  username: '',
  password: '',
  roleId: '' as number | ''
})
const showPassword = ref(false)
const emailError = ref('')

// Computed
const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  const query = searchQuery.value.toLowerCase()
  return users.value.filter((user: UserWithRoles) => 
    user.email.toLowerCase().includes(query) ||
    user.roles?.some((r: Role) => r.name.toLowerCase().includes(query))
  )
})

const availableRoles = computed(() => {
  if (!selectedUser.value) return roles.value
  const userRoleIds = (selectedUser.value.roles || []).map(r => r.id)
  return roles.value.filter(role => !userRoleIds.includes(role.id))
})

const adminRoles = computed(() => {
  return roles.value.filter(role => 
    ['admin', 'manager', 'employee'].includes(role.name.toLowerCase())
  )
})

// Methods
const loadUsers = async () => {
  try {
    loading.value = true
    const allUsers = await usersApi.getAllUsers()
    // Filtrar usuarios que tengan al menos un rol de manager, admin o employee
    const filteredUsers = allUsers.filter((user: UserWithRoles) => {
      if (!user.roles || user.roles.length === 0) return false
      return user.roles.some((role: Role) => 
        ['admin', 'manager', 'employee'].includes(role.name.toLowerCase())
      )
    })
    users.value = filteredUsers
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || 'Error al cargar usuarios'
    toast.error(`❌ ${errorMessage}`)
  } finally {
    loading.value = false
  }
}

const loadRoles = async () => {
  try {
    roles.value = await rolesApi.getAllRoles()
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || 'Error al cargar roles'
    toast.error(`❌ ${errorMessage}`)
  }
}

const searchUsers = () => {
  // Implement search logic if needed
}

const manageUserRoles = async (user: UserWithRoles) => {
  selectedUser.value = user
  showRoleModal.value = true
  selectedRoleToAdd.value = ''
  
  // Load user's current roles
  try {
    const userRoles = await rolesApi.getUserRoles(user.id)
    selectedUser.value.roles = userRoles
  } catch (error) {
  }
}

const closeRoleModal = () => {
  showRoleModal.value = false
  selectedUser.value = null
  selectedRoleToAdd.value = ''
}

const addUserRole = async () => {
  if (!selectedUser.value || !selectedRoleToAdd.value) return
  
  try {
    await rolesApi.assignRole(selectedUser.value.id, selectedRoleToAdd.value as number)
    toast.success('✅ Rol asignado correctamente')
    
    // Reload user roles
    const userRoles = await rolesApi.getUserRoles(selectedUser.value.id)
    selectedUser.value.roles = userRoles
    selectedRoleToAdd.value = ''
    
    // Update users list
    await loadUsers()
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || 'Error al asignar el rol'
    toast.error(`❌ ${errorMessage}`)
  }
}

const removeUserRole = async (userId: number, roleId: number) => {
  try {
    await rolesApi.removeRole(userId, roleId)
    toast.success('✅ Rol removido correctamente')
    
    // Reload user roles
    if (selectedUser.value) {
      const userRoles = await rolesApi.getUserRoles(selectedUser.value.id)
      selectedUser.value.roles = userRoles
    }
    
    // Update users list
    await loadUsers()
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || 'Error al remover el rol'
    toast.error(`❌ ${errorMessage}`)
  }
}

const viewUserDetails = (user: UserWithRoles) => {
  alert(`Detalles del usuario:\nEmail: ${user.email}\nID: ${user.id}\nRoles: ${(user.roles || []).map((r: Role) => r.name).join(', ') || 'Sin roles'}`)
}

const getUserInitials = (email: string) => {
  return email.split('@')[0].substring(0, 2).toUpperCase()
}

const getRoleBadgeClass = (roleName: string) => {
  const classes = {
    admin: 'bg-red-100 text-red-800',
    manager: 'bg-blue-100 text-blue-800',
    employee: 'bg-yellow-100 text-yellow-800',
    user: 'bg-gray-100 text-gray-800'
  }
  return classes[roleName as keyof typeof classes] || 'bg-gray-100 text-gray-800'
}

const closeAddUserModal = () => {
  showAddUserModal.value = false
  showPassword.value = false
  emailError.value = ''
  newUserForm.value = {
    email: '',
    username: '',
    password: '',
    roleId: ''
  }
}

const checkEmailExists = () => {
  emailError.value = ''
  
  if (!newUserForm.value.email) return
  
  // Verificar si el email ya existe en la lista de usuarios cargados
  const existingUser = users.value.find((user: UserWithRoles) => 
    user.email.toLowerCase() === newUserForm.value.email.toLowerCase()
  )
  
  if (existingUser) {
    emailError.value = 'Este email ya está registrado en el sistema'
  } else {
    emailError.value = ''
  }
}

const addNewUser = async () => {
  try {
    loading.value = true
    
    // Validar que se haya seleccionado un rol
    if (!newUserForm.value.roleId) {
      toast.error('❌ Debe seleccionar un rol para el usuario')
      return
    }
    
    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(newUserForm.value.email)) {
      toast.error('❌ Por favor ingrese un email válido')
      return
    }
    
    // Verificar email duplicado
    checkEmailExists()
    if (emailError.value) {
      toast.error(`❌ ${emailError.value}`)
      return
    }
    
    // Validar longitud de contraseña
    if (newUserForm.value.password.length < 6) {
      toast.error('❌ La contraseña debe tener al menos 6 caracteres')
      return
    }
    
    // Log del payload que se está enviando para debug
    const requestPayload = {
      email: newUserForm.value.email,
      password: newUserForm.value.password,
      name: newUserForm.value.username || newUserForm.value.email,
      role_id: newUserForm.value.roleId as number
    }

    // Crear usuario usando la API
    const result = await usersApi.createUser(requestPayload)
    
    toast.success(`✅ Usuario ${result.name} creado exitosamente`)
    
    // Cerrar modal y resetear formulario
    closeAddUserModal()
    
    // Recargar la lista de usuarios
    await loadUsers()
    
  } catch (error: any) {

    // Extraer mensaje de error específico
    let errorMessage = 'Error al crear usuario'
    
    if (error.response?.status === 400) {
      const detail = error.response.data?.detail
      if (typeof detail === 'string') {
        if (detail.includes('email ya está registrado')) {
          errorMessage = 'El email ya está registrado en el sistema'
        } else if (detail.includes('contraseña es muy débil') || detail.includes('WeakPasswordError')) {
          errorMessage = 'La contraseña es muy débil. Use al menos 6 caracteres con mayúsculas, minúsculas y números'
        } else if (detail.includes('Firebase')) {
          errorMessage = `Error de Firebase: ${detail}`
        } else {
          errorMessage = detail
        }
      } else {
        errorMessage = 'Error de validación. Verifique los datos ingresados'
      }
    } else if (error.response?.status === 500) {
      errorMessage = 'Error interno del servidor. Intente nuevamente'
    } else if (error.code === 'NETWORK_ERROR') {
      errorMessage = 'Error de conexión. Verifique su conexión a internet'
    } else {
      errorMessage = error.response?.data?.detail || error.message || 'Error al crear usuario'
    }
    
    toast.error(`❌ ${errorMessage}`)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadUsers()
  loadRoles()
})
</script>
