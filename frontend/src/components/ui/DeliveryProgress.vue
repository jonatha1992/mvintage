<template>
  <div class="w-full max-w-2xl py-3 mx-auto">
    <!-- Progress Steps -->
    <div class="flex items-center justify-between mb-4">
      <!-- Step 1: Carrito -->
      <div class="flex flex-col items-center">
        <button 
          @click="$emit('go-to-step', 1)"
          class="flex items-center justify-center w-8 h-8 text-sm font-medium transition-all duration-300 rounded-full cursor-pointer hover:shadow-lg"
          :class="getStepClasses(1)"
        >
          <CheckIcon v-if="currentStep > 1" class="w-4 h-4" />
          <ShoppingCartIcon v-else-if="currentStep === 1" class="w-4 h-4" />
          <span class="font-body" v-else>1</span>
        </button>
        <span class="mt-2 text-xs font-body text-body-text">Carrito</span>
      </div>

      <!-- Progress Line 1 -->
      <div class="flex-1 h-0.5 mx-2 bg-gray-200 relative">
        <div 
          class="h-full transition-all duration-500 bg-gray-800"
          :style="{ width: currentStep > 1 ? '100%' : '0%' }"
        ></div>
      </div>

      <!-- Step 2: Retiro -->
      <div class="flex flex-col items-center">
        <button 
          @click="$emit('go-to-step', 2)"
          :class="[
            'flex items-center justify-center w-8 h-8 text-sm font-medium transition-all duration-300 rounded-full cursor-pointer hover:shadow-lg',
            currentStep >= 2 
              ? 'bg-gray-800 text-white' 
              : 'bg-gray-200 text-gray-600',
            currentStep === 2 ? 'ring-2 ring-gray-800 ring-offset-2' : ''
          ]"
        >
          <CheckIcon v-if="currentStep > 2" class="w-4 h-4" />
          <MapPinIcon v-else class="w-4 h-4" />
        </button>
        <span class="mt-2 text-xs font-body text-body-text">Retiro</span>
      </div>

      <!-- Progress Line 2 -->
      <div class="flex-1 h-0.5 mx-2 bg-gray-200 relative">
        <div 
          class="h-full transition-all duration-500 bg-gray-800"
          :style="{ width: currentStep >= 3 ? '100%' : '0%' }"
        ></div>
      </div>

      <!-- Step 3: Pago -->
      <div class="flex flex-col items-center">
        <button 
          @click="$emit('go-to-step', 3)"
          :class="[
            'flex items-center justify-center w-8 h-8 text-sm font-medium transition-all duration-300 rounded-full cursor-pointer hover:shadow-lg',
            currentStep >= 3 
              ? 'bg-gray-800 text-white' 
              : 'bg-gray-200 text-gray-600',
            currentStep === 3 ? 'ring-2 ring-gray-800 ring-offset-2' : ''
          ]"
        >
          <svg v-if="currentStep > 3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" data-slot="icon" class="w-4 h-4">
            <path fill-rule="evenodd" d="M19.916 4.626a.75.75 0 0 1 .208 1.04l-9 13.5a.75.75 0 0 1-1.154.114l-6-6a.75.75 0 0 1 1.06-1.06l5.353 5.353 8.493-12.74a.75.75 0 0 1 1.04-.207Z" clip-rule="evenodd" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" data-slot="icon" class="w-4 h-4">
            <path d="M4.5 3.75a3 3 0 0 0-3 3v.75h21v-.75a3 3 0 0 0-3-3h-15Z" />
            <path fill-rule="evenodd" d="M22.5 9.75h-21v7.5a3 3 0 0 0 3 3h15a3 3 0 0 0 3-3v-7.5Zm-18 3.75a.75.75 0 0 1 .75-.75h6a.75.75 0 0 1 0 1.5h-6a.75.75 0 0 1-.75-.75Zm.75 2.25a.75.75 0 0 0 0 1.5h3a.75.75 0 0 0 0-1.5h-3Z" clip-rule="evenodd" />
          </svg>
        </button>
        <span class="mt-2 text-xs font-body text-body-text">Pago</span>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { CheckIcon, ShoppingCartIcon, MapPinIcon } from '@heroicons/vue/24/solid'

interface Props {
  currentStep: number
}

const props = defineProps<Props>()

// Define emits for step navigation
const emit = defineEmits<{
  'go-to-step': [step: number]
}>()

const getStepClasses = (step: number) => {
  if (props.currentStep > step) {
    // Completed step
    return 'bg-gray-800 text-white'
  } else if (props.currentStep === step) {
    // Current step
    return 'bg-gray-800 text-white ring-2 ring-gray-800 ring-offset-2'
  } else {
    // Future step
    return 'bg-gray-200 text-white'
  }
}
</script>

<style scoped>
/* Additional animations if needed */
.step-transition {
  transition: all 0.3s ease-in-out;
}
</style>

