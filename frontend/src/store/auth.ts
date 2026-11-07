import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { auth } from '../config/index'
import { onAuthStateChanged, signOut, type User as FirebaseUser } from 'firebase/auth'
import { apiClient, rolesApi } from '../config/index'
import type { User } from '../types/users/user.types'
import type { Role } from '../types/users/role.types'
import { authCache } from '../utils/cache'

export const useAuthStore = defineStore('auth', () => {
    const firebaseUser = ref<FirebaseUser | null>(null)
    const backendUser = ref<User | null>(null)
    const userRoles = ref<Role[]>([])
    const token = ref<string | null>(null)
    const loading = ref(true)

    const isAuthenticated = computed(() => !!backendUser.value)

    const isAdmin = computed(() => {
        return userRoles.value.some(role => ['admin', 'manager'].includes(role.name.toLowerCase()))
    })

    const hasAdminAccess = computed(() => isAdmin.value)

    const fetchBackendUser = async () => {
        try {
            const response = await apiClient.get('/users/me')
            backendUser.value = response.data
            // TambiÃ©n obtener los roles del usuario (con cachÃ©)
            await fetchUserRoles(false)
        } catch (error) {
            // Si falla, probablemente el token no es valido, desloguear
            await logout()
        }
    }

    const fetchUserRoles = async (force = false) => {
        // Verificar cachÃ© primero si no es forzado
        if (!force) {
            const cached = authCache.get<Role[]>('userRoles')
            if (cached) {
                userRoles.value = cached
                return cached
            }
        }

        try {
            const roles = await rolesApi.getMyRoles()
            userRoles.value = roles
            // Guardar en cache por 5 minutos
            authCache.set('userRoles', roles, 300000)
            return roles
        } catch (error) {
            userRoles.value = []
            return []
        }
    }

    // Función para actualizar token manualmente (útil cuando expira)
    const refreshToken = async () => {
        if (firebaseUser.value) {
            try {
                const freshToken = await firebaseUser.value.getIdToken(true) // force refresh
                token.value = freshToken
                localStorage.setItem('firebase_jwt_token', freshToken)
                return freshToken
            } catch (error) {
                await logout()
                return null
            }
        }
        return null
    }

    const initAuth = () => {
        return new Promise<void>((resolve) => {
            let resolved = false

            // @ts-ignore - unsubscribe is intentionally not used in this context
            const unsubscribe = onAuthStateChanged(auth, async (fbUser) => {
                if (fbUser) {
                    firebaseUser.value = fbUser
                    try {
                        token.value = await fbUser.getIdToken()

                        // Guardar token en localStorage para frontend-test.html
                        localStorage.setItem('firebase_jwt_token', token.value)

                        // Sincronizar con el backend
                        await fetchBackendUser()
                    } catch (error) {
                        await logout()
                    }

                } else {
                    firebaseUser.value = null
                    backendUser.value = null
                    token.value = null

                    // Limpiar token de localStorage cuando no hay usuario
                    localStorage.removeItem('firebase_jwt_token')
                }

                loading.value = false

                // Solo resolvemos la primera vez
                if (!resolved) {
                    resolved = true
                    resolve()
                }
            })
        })
    }

    const logout = async () => {
        try {
            await signOut(auth)
        } catch (error) {
        } finally {
            firebaseUser.value = null
            backendUser.value = null
            userRoles.value = []
            token.value = null

            // Limpiar token de localStorage al hacer logout
            localStorage.removeItem('firebase_jwt_token')

            // Limpiar toda la caché de auth
            authCache.clear()
        }
    }

    return {
        firebaseUser,
        backendUser,
        userRoles,
        token,
        loading,
        isAuthenticated,
        isAdmin,
        hasAdminAccess,
        initAuth,
        logout,
        fetchBackendUser,
        fetchUserRoles,
        refreshToken
    }
})