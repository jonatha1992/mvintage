<template>
    <div class="flex items-center justify-center min-h-screen px-4 py-12 bg-gray-50 sm:px-6 lg:px-8">
        <div class="w-full max-w-md space-y-8">
            <div>
                <h2 class="mt-6 text-3xl font-extrabold text-center text-gray-900 font-heading">
                    {{ isLogin ? 'Iniciar Sesión' : 'Crear Cuenta' }}
                </h2>
                <p class="mt-2 text-sm text-center font-body text-body-text">
                    Accede a la administración de productos
                </p>
            </div>

            <div class="mt-8 space-y-6">
                <div v-if="error" class="px-4 py-3 text-red-700 bg-red-100 border border-red-400 rounded font-body">
                    {{ error }}
                </div>

                <div v-if="loading" class="text-center">
                    <div class="inline-block w-8 h-8 border-b-2 border-indigo-600 rounded-full animate-spin"></div>
                    <p class="mt-2 text-sm font-body text-body-text">Procesando...</p>
                </div>

                <!-- Login con Google -->
                <button @click="signInWithGoogle" :disabled="loading"
                    class="relative flex justify-center w-full px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md group hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50">
                    <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
                        <path fill="currentColor"
                            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                        <path fill="currentColor"
                            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                        <path fill="currentColor"
                            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                        <path fill="currentColor"
                            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                    </svg>
                    {{ loading ? 'Redirigiendo a Google...' : (isLogin ? 'Continuar con Google' : 'Registrarse con Google') }}
                </button>

                <div v-if="!loading" class="text-center">
                    <p class="text-xs font-body text-body-text">
                        Se abrirá una ventana popup para autenticarte con Google
                    </p>
                </div>

                <div class="relative">
                    <div class="absolute inset-0 flex items-center">
                        <div class="w-full border-t border-gray-300" />
                    </div>
                    <div class="relative flex justify-center text-sm">
                        <span class="px-2 font-body text-body-text bg-gray-50">O</span>
                    </div>
                </div>

                <!-- Formulario email/password -->
                <form @submit.prevent="handleSubmit" class="space-y-6">
                    <div>
                        <label for="email" class="sr-only">Email</label>
                        <input id="email" name="email" type="email" v-model="email" required
                            class="relative block w-full px-3 py-2 text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md appearance-none focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                            placeholder="Email" />
                    </div>
                    <div>
                        <label for="password" class="sr-only">Contraseña</label>
                        <div class="relative">
                            <input id="password" name="password" :type="showPassword ? 'text' : 'password'" v-model="password" required
                                class="relative block w-full px-3 py-2 pr-12 text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md appearance-none focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder="Contraseña" />
                            <button type="button" @click="showPassword = !showPassword" :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'" :aria-pressed="showPassword" class="absolute inset-y-0 right-0 z-20 flex items-center px-3 text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>
                            </button>
                        </div>
                    </div>

                    <div>
                        <button type="submit" :disabled="loading"
                            class="relative flex justify-center w-full px-4 py-2 text-sm font-medium text-white bg-gray-600 border border-transparent rounded-md group hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50">
                            <span class="text-white">{{ isLogin ? 'Iniciar Sesión' : 'Crear Cuenta' }}</span>
                        </button>
                    </div>
                </form>

                <div class="text-center">
                    <button @click="toggleMode" class="text-sm text-indigo-600 font-body hover:text-indigo-500">
                        {{ isLogin ? '¿No tienes cuenta? Crear cuenta' : '¿Ya tienes cuenta? Iniciar sesión' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import { auth } from '../../config/firebase'
import {
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signInWithPopup,
    signInWithRedirect,
    getRedirectResult,
    GoogleAuthProvider
} from 'firebase/auth'

const router = useRouter()
const authStore = useAuthStore()
const isLogin = ref(true)
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

// Observar cambios en el estado de autenticación
watch(() => authStore.isAuthenticated, (isAuth) => {
    if (isAuth) {
        router.push('/admin/products')
    }
}, { immediate: true })

// Verificar si hay resultado de redirect al cargar el componente
onMounted(async () => {
    try {
        // Esperar un momento para asegurar que Firebase esté completamente inicializado
        await new Promise(resolve => setTimeout(resolve, 500))
        
        const result = await getRedirectResult(auth)
        
        if (result && result.user) {
        } else {
            // Verificar si hay un usuario ya autenticado
            if (auth.currentUser) {
            }
        }
        
        if (result) {
            // Usuario autenticado exitosamente después del redirect
            // No redirigir manualmente aquí, el watch lo hará
        }
    } catch (err: any) {
        loading.value = false

        // Mensajes de error más específicos
        if (err.code === 'auth/unauthorized-domain') {
            error.value = 'Dominio no autorizado. Verifica configuración Firebase.'
        } else if (err.code === 'auth/operation-not-allowed') {
            error.value = 'Método de autenticación no habilitado.'
        } else if (err.code === 'auth/popup-blocked') {
            error.value = 'El navegador bloqueó la ventana de autenticación.'
        } else if (err.code === 'auth/cancelled-popup-request') {
            error.value = 'Autenticación cancelada.'
        } else if (err.code === 'auth/network-request-failed') {
            error.value = 'Error de conexión. Verifica tu internet.'
        } else if (err.code === 'auth/redirect-cancelled-by-user') {
            error.value = 'Autenticación cancelada por el usuario.'
        } else if (err.code === 'auth/redirect-operation-pending') {
            error.value = 'Ya hay una operación de redirect pendiente.'
        } else {
            error.value = `Error de autenticación: ${err.message} (${err.code})`
        }
    }
})

const toggleMode = () => {
    isLogin.value = !isLogin.value
    error.value = ''
}

const signInWithGoogle = async () => {
    try {
        loading.value = true
        error.value = ''
        
        const provider = new GoogleAuthProvider()
        
        // Agregar parámetros adicionales para mejor experiencia
        provider.setCustomParameters({
            prompt: 'select_account' // Permite seleccionar cuenta si hay multiples
        })

        const result = await signInWithPopup(auth, provider)
        loading.value = false

    } catch (err: any) {
        loading.value = false
        
        // Mensajes de error más específicos
        if (err.code === 'auth/unauthorized-domain') {
            error.value = 'Dominio no autorizado en Firebase Console'
        } else if (err.code === 'auth/popup-blocked') {
            error.value = 'Popup bloqueado. Permite popups para este sitio'
        } else if (err.code === 'auth/popup-closed-by-user') {
            error.value = 'Popup cerrado por el usuario'
        } else if (err.code === 'auth/cancelled-popup-request') {
            error.value = 'Autenticación cancelada'
        } else {
            error.value = `Error: ${err.message} (${err.code})`
        }
    }
}

const handleSubmit = async () => {
    loading.value = true
    error.value = ''

    try {
        let result
        if (isLogin.value) {
            result = await signInWithEmailAndPassword(auth, email.value, password.value)
        } else {
            result = await createUserWithEmailAndPassword(auth, email.value, password.value)
        }

        // El store detectará automáticamente el cambio y redirigirá
        // No necesitamos redirigir manualmente aquí
        loading.value = false
    } catch (err: any) {
        error.value = getErrorMessage(err.code) || err.message || 'Error de autenticación'
        loading.value = false
    }
}

// Función para traducir códigos de error de Firebase
const getErrorMessage = (errorCode: string): string => {
    switch (errorCode) {
        case 'auth/user-not-found':
            return 'Usuario no encontrado'
        case 'auth/wrong-password':
            return 'Contraseña incorrecta'
        case 'auth/email-already-in-use':
            return 'El email ya está en uso'
        case 'auth/weak-password':
            return 'La contraseña es muy débil'
        case 'auth/invalid-email':
            return 'Email inválido'
        case 'auth/popup-blocked':
            return 'El navegador bloqueó el popup. Intenta permitir popups para este sitio.'
        default:
            return ''
    }
}
</script>
