<template>
  <div class="relative">
    <label :for="inputId" class="font-body block text-sm font-medium text-body-text">
      {{ label }}
    </label>
    <div class="mt-1 relative">
      <input
        :id="inputId"
        ref="inputRef"
        v-model="searchQuery"
        @input="onInput"
        @focus="onFocus"
        @blur="onBlur"
        @keydown="onKeyDown"
        type="text"
        :placeholder="placeholder"
        :required="required"
        class="block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
        :class="{ 'border-red-300': error }"
      />
      
      <!-- Loading indicator -->
      <div v-if="loading" class="absolute right-3 top-1/2 transform -translate-y-1/2">
        <svg class="animate-spin h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- Suggestions dropdown -->
      <div 
        v-if="showSuggestions && suggestions.length > 0"
        class="absolute z-[9999] w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto"
      >
        <!-- Close button -->
        <div class="flex justify-end p-2 border-b border-gray-100">
          <button
            @mousedown="closeSuggestions"
            class="text-gray-400 hover:text-gray-600 transition-colors"
            type="button"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div
          v-for="(suggestion, index) in suggestions"
          :key="suggestion.place_id"
          @mousedown="selectSuggestion(suggestion)"
          class="px-4 py-2 cursor-pointer hover:bg-gray-100 border-b border-gray-100 last:border-b-0"
          :class="{ 'bg-gray-100': index === selectedIndex }"
        >
          <div class="text-sm font-body text-gray-900">
            {{ formatAddressMain(suggestion) }}
          </div>
          <div class="text-xs font-body text-gray-500 mt-1">
            {{ formatAddressSecondary(suggestion) }}
          </div>
        </div>
      </div>

      <!-- No results message -->
      <div 
        v-if="showSuggestions && !loading && searchQuery.length >= 3 && suggestions.length === 0"
        class="absolute z-[9999] w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg"
      >
        <div class="px-4 py-3 text-sm font-body text-gray-500">
          No se encontraron direcciones. Intenta con más detalles.
        </div>
      </div>
    </div>

    <!-- Error message -->
    <p v-if="error" class="mt-1 text-sm font-body text-red-600">
      {{ error }}
    </p>

    <!-- Helper text -->
    <p v-if="!error && helperText" class="mt-1 text-xs font-body text-gray-500">
      {{ helperText }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useAddressAutocomplete, type AddressSuggestion, type ParsedAddress } from '../../composables/useAddressAutocomplete'

interface Props {
  modelValue: string
  label?: string
  placeholder?: string
  required?: boolean
  inputId?: string
  countryCode?: string
  helperText?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'address-selected', address: ParsedAddress): void
}

const props = withDefaults(defineProps<Props>(), {
  label: 'Dirección',
  placeholder: 'Comenzá a escribir tu dirección...',
  required: false,
  inputId: 'address',
  countryCode: 'AR',
  helperText: 'Escribí al menos 3 caracteres para ver sugerencias'
})

const emit = defineEmits<Emits>()

const { suggestions, loading, error, searchAddresses, parseAddress, clearSuggestions } = useAddressAutocomplete()

const inputRef = ref<HTMLInputElement>()
const searchQuery = ref(props.modelValue)
const showSuggestions = ref(false)
const selectedIndex = ref(-1)
const searchTimeout = ref<number>()

// Debounced search
const onInput = () => {
  emit('update:modelValue', searchQuery.value)
  
  clearTimeout(searchTimeout.value)
  selectedIndex.value = -1
  
  if (searchQuery.value.length >= 3) {
    searchTimeout.value = window.setTimeout(() => {
      performSearch()
    }, 500) // 500ms debounce
  } else {
    clearSuggestions()
    showSuggestions.value = false
  }
}

const performSearch = async () => {
  if (searchQuery.value.length >= 3) {
    try {
      await searchAddresses(searchQuery.value, props.countryCode)
      showSuggestions.value = true
    } catch (err) {
    }
  }
}

const onFocus = () => {
  if (suggestions.value.length > 0 && searchQuery.value.length >= 3) {
    showSuggestions.value = true
  }
}

const onBlur = () => {
  // Delay hiding suggestions to allow click selection
  setTimeout(() => {
    showSuggestions.value = false
    selectedIndex.value = -1
  }, 150)
}

const onKeyDown = (event: KeyboardEvent) => {
  if (!showSuggestions.value || suggestions.value.length === 0) return

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      selectedIndex.value = Math.min(selectedIndex.value + 1, suggestions.value.length - 1)
      break
    case 'ArrowUp':
      event.preventDefault()
      selectedIndex.value = Math.max(selectedIndex.value - 1, -1)
      break
    case 'Enter':
      event.preventDefault()
      if (selectedIndex.value >= 0 && suggestions.value[selectedIndex.value]) {
        selectSuggestion(suggestions.value[selectedIndex.value])
      }
      break
    case 'Escape':
      showSuggestions.value = false
      selectedIndex.value = -1
      inputRef.value?.blur()
      break
  }
}

const selectSuggestion = (suggestion: AddressSuggestion) => {
  const parsedAddress = parseAddress(suggestion)
  
  // Update the input with the main street address
  searchQuery.value = parsedAddress.street || parsedAddress.fullAddress.split(',')[0]
  emit('update:modelValue', searchQuery.value)
  
  // Emit the full parsed address
  emit('address-selected', parsedAddress)
  
  // Hide suggestions
  showSuggestions.value = false
  selectedIndex.value = -1
  
  // Focus stays on input for better UX
  nextTick(() => {
    inputRef.value?.focus()
  })
}

const closeSuggestions = () => {
  showSuggestions.value = false
  selectedIndex.value = -1
  clearSuggestions()
}

const formatAddressMain = (suggestion: AddressSuggestion): string => {
  const parts = suggestion.display_name.split(',')
  // Show first 2 parts (street and neighborhood/area)
  return parts.slice(0, 2).join(', ').trim()
}

const formatAddressSecondary = (suggestion: AddressSuggestion): string => {
  const parts = suggestion.display_name.split(',')
  // Show city, province, country
  return parts.slice(2).join(', ').trim()
}

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  if (newValue !== searchQuery.value) {
    searchQuery.value = newValue
  }
})

// Clear suggestions when country changes
watch(() => props.countryCode, () => {
  clearSuggestions()
  showSuggestions.value = false
})
</script>
