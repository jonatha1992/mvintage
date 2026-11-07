<template>
  <div class="flex flex-col justify-center min-h-screen py-12 bg-gray-50 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <h2 class="text-3xl font-light text-gray-900">Verifica tu Email</h2>
        <p class="mt-2 text-sm text-gray-600">
          Te hemos enviado un cdigo de verificacin a tu email
        </p>
      </div>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="px-4 py-8 bg-white shadow sm:rounded-lg sm:px-10">
        
        <!-- Success State -->
        <div v-if="verificationStatus === 'success'" class="text-center">
          <div class="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-green-100 rounded-full">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <h3 class="mb-2 text-lg font-medium text-gray-900">¡Email Verificado!</h3>
          <p class="mb-4 text-sm text-gray-600">Tu email ha sido verificado exitosamente.</p>
          <router-link to="/" class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-gray-800 border border-transparent rounded-md hover:bg-gray-900">
            Continuar a la Tienda
          </router-link>
        </div>

        <!-- Error State -->
        <div v-else-if="verificationStatus === 'error'" class="text-center">
          <div class="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-red-100 rounded-full">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </div>
          <h3 class="mb-2 text-lg font-medium text-gray-900">Error de Verificacin</h3>
          <p class="mb-4 text-sm text-gray-600">{{ errorMessage }}</p>
          <button 
            @click="showManualForm = true; verificationStatus = 'pending'"
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-gray-800 border border-transparent rounded-md hover:bg-gray-900"
          >
            Intentar Nuevamente
          </button>
        </div>

        <!-- Loading State -->
        <div v-else-if="verificationStatus === 'loading'" class="text-center">
          <div class="flex items-center justify-center w-12 h-12 mx-auto mb-4">
            <div class="w-8 h-8 border-b-2 border-black rounded-full animate-spin"></div>
          </div>
          <p class="text-sm text-gray-600">Verificando tu email...</p>
        </div>

        <!-- Manual Verification Form -->
        <form v-else @submit.prevent="verifyWithCode" class="space-y-6">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
            <input
              v-model="verificationForm.email"
              type="email"
              id="email"
              required
              class="block w-full px-3 py-2 mt-1 border border-gray-300 rounded-md shadow-sm focus:border-black focus:ring-black"
              placeholder="tu@email.com"
            >
          </div>

          <div>
            <label for="code" class="block text-sm font-medium text-gray-700">Cdigo de Verificacin</label>
            <input
              v-model="verificationForm.code"
              type="text"
              id="code"
              required
              maxlength="6"
              class="block w-full px-3 py-2 mt-1 font-mono text-lg tracking-widest text-center border border-gray-300 rounded-md shadow-sm focus:border-black focus:ring-black"
              placeholder="123456"
              @input="formatCode"
            >
            <p class="mt-1 text-xs text-gray-500">Ingresa el cdigo de 6 dígitos que recibiste por email</p>
          </div>

          <button
            type="submit"
            :disabled="processing"
            class="flex justify-center w-full px-4 py-2 text-sm font-medium text-white bg-gray-800 border border-transparent rounded-md shadow-sm hover:bg-gray-900 disabled:bg-gray-400"
          >
            <span v-if="processing" class="flex items-center">
              <div class="w-4 h-4 mr-2 -ml-1 border-b-2 border-white rounded-full animate-spin"></div>
              Verificando...
            </span>
            <span v-else>Verificar Email</span>
          </button>

          <div class="text-center">
            <button
              type="button"
              @click="resendVerificationEmail"
              :disabled="resending || resendCooldown > 0"
              class="text-sm text-gray-600 hover:text-gray-900 disabled:text-gray-400"
            >
              <span v-if="resending">Reenviando...</span>
              <span v-else-if="resendCooldown > 0">Reenviar en {{ resendCooldown }}s</span>
              <span v-else>¿No recibiste el código? Reenviar</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../../store/auth';
import { useToast } from 'vue-toastification';
import { emailVerificationService, type VerifyEmailRequest } from '../../services/emailVerificationService';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

// State
const verificationStatus = ref<'pending' | 'loading' | 'success' | 'error'>('pending');
const processing = ref(false);
const resending = ref(false);
const resendCooldown = ref(0);
const errorMessage = ref('');
const showManualForm = ref(false);

// Form
const verificationForm = ref({
  email: '',
  code: ''
});

// Auto-verify if token in URL
onMounted(async () => {
  const token = route.query.token as string;
  
  if (authStore.isAuthenticated && authStore.backendUser) {
    verificationForm.value.email = authStore.backendUser.email;
  }
  
  if (token && verificationForm.value.email) {
    await verifyWithToken(token);
  } else {
    showManualForm.value = true;
  }
});

// Methods
const verifyWithToken = async (token: string) => {
  verificationStatus.value = 'loading';
  
  try {
    const request: VerifyEmailRequest = {
      token: token,
      email: verificationForm.value.email
    };
    
    const response = await emailVerificationService.verifyEmail(request);
    
    if (response.success) {
      verificationStatus.value = 'success';
      toast.success('Email verificado exitosamente');
      
      // Update auth store if needed
      if (authStore.backendUser) {
        authStore.backendUser.email_verified = true;
      }
      
      // Redirect after delay
      setTimeout(() => {
        router.push('/');
      }, 3000);
    } else {
      verificationStatus.value = 'error';
      errorMessage.value = response.message;
    }
  } catch (error) {
    verificationStatus.value = 'error';
    errorMessage.value = 'Error al verificar el email. Por favor intenta nuevamente.';
  }
};

const verifyWithCode = async () => {
  if (!verificationForm.value.code || !verificationForm.value.email) {
    toast.error('Por favor completa todos los campos');
    return;
  }
  
  processing.value = true;
  
  try {
    const request: VerifyEmailRequest = {
      code: verificationForm.value.code,
      email: verificationForm.value.email
    };
    
    const response = await emailVerificationService.verifyEmail(request);
    
    if (response.success) {
      verificationStatus.value = 'success';
      toast.success('Email verificado exitosamente');
      
      // Update auth store if needed
      if (authStore.backendUser) {
        authStore.backendUser.email_verified = true;
      }
      
      // Redirect after delay
      setTimeout(() => {
        router.push('/');
      }, 3000);
    } else {
      toast.error(response.message);
    }
  } catch (error) {
    toast.error('Error al verificar el email. Por favor intenta nuevamente.');
  } finally {
    processing.value = false;
  }
};

const formatCode = (event: Event) => {
  const input = event.target as HTMLInputElement;
  // Only allow numbers
  input.value = input.value.replace(/[^0-9]/g, '');
  verificationForm.value.code = input.value;
};

const resendVerificationEmail = async () => {
  if (!verificationForm.value.email) {
    toast.error('Por favor ingresa tu email');
    return;
  }
  
  resending.value = true;
  
  try {
    await emailVerificationService.resendVerificationEmail({
      email: verificationForm.value.email
    });
    
    toast.success('Cdigo de verificacin reenviado');
    
    // Start cooldown
    resendCooldown.value = 60;
    const interval = setInterval(() => {
      resendCooldown.value--;
      if (resendCooldown.value <= 0) {
        clearInterval(interval);
      }
    }, 1000);
    
  } catch (error) {
    toast.error('Error al reenviar el cdigo');
  } finally {
    resending.value = false;
  }
};
</script>
