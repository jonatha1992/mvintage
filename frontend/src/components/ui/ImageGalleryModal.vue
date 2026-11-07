<template>
  <!-- Modal Overlay -->
  <transition name="overlay-fade">
    <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-90">
      <!-- Contenedor principal -->
      <transition name="dialog-scale" appear>
        <div class="relative flex flex-col w-full h-full max-w-6xl p-4 mx-auto">
      
      <!-- Header con boton cerrar -->
      <div class="absolute z-10 top-4 right-4">
        <button 
          @click="closeModal" 
          class="flex items-center justify-center w-12 h-12 text-3xl text-white transition-colors bg-black bg-opacity-50 rounded-full hover:text-gray-300 hover:bg-opacity-70"
        >
          ×
        </button>
      </div>
      
      <!-- Imagen principal -->
      <div class="relative flex items-center justify-center flex-1 min-h-0">
          <img 
            ref="modalImgRef"
            :src="currentImage" 
            :alt="alt" 
            class="object-contain max-w-full max-h-full modal-image"
            @load="handleImageLoad"
            @error="handleImageError"
          />
        
        <!-- Loading spinner -->
        <div v-if="imageLoading" class="absolute inset-0 flex items-center justify-center">
          <div class="w-12 h-12 border-b-2 border-white rounded-full animate-spin"></div>
        </div>
        
        <!-- Botones navegacin -->
        <button 
          v-if="images.length > 1"
          @click="previousImage" 
          :disabled="currentIndex === 0"
          class="absolute flex items-center justify-center w-12 h-12 text-4xl text-white transition-colors bg-black bg-opacity-50 rounded-full left-4 hover:text-gray-300 hover:bg-opacity-70 disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <
        </button>
        
        <button 
          v-if="images.length > 1"
          @click="nextImage" 
          :disabled="currentIndex === images.length - 1"
          class="absolute flex items-center justify-center w-12 h-12 text-4xl text-white transition-colors bg-black bg-opacity-50 rounded-full right-4 hover:text-gray-300 hover:bg-opacity-70 disabled:opacity-30 disabled:cursor-not-allowed"
        >
          >
        </button>
      </div>
      
      <!-- Contador (se eliminó la tira de thumbnails para evitar recuadro abajo) -->
      <div v-if="images.length > 1" class="flex items-center justify-center mt-4">
        <div class="text-sm text-center text-white font-body">
          {{ currentIndex + 1 }} / {{ images.length }}
        </div>
      </div>
        </div>
      </transition>
    </div>
  </transition>
</template>

<style scoped>
/* Improved overlay fade with smoother timing */
.overlay-fade-enter-active {
  transition: opacity 300ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.overlay-fade-leave-active {
  transition: opacity 250ms cubic-bezier(0.55, 0.06, 0.68, 0.19);
}
.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}
.overlay-fade-enter-to,
.overlay-fade-leave-from {
  opacity: 1;
}

/* Enhanced dialog transitions with better easing */
.dialog-scale-enter-active {
  transition: 
    opacity 300ms cubic-bezier(0.25, 0.46, 0.45, 0.94),
    transform 300ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.dialog-scale-leave-active {
  transition: 
    opacity 250ms cubic-bezier(0.55, 0.06, 0.68, 0.19),
    transform 250ms cubic-bezier(0.55, 0.06, 0.68, 0.19);
}
.dialog-scale-enter-from {
  opacity: 0;
  transform: translateY(12px) scale(0.96);
}
.dialog-scale-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
}
.dialog-scale-enter-to,
.dialog-scale-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}

/* Smooth image transitions */
.modal-image {
  transition: opacity 200ms ease-out;
}

/* Hardware acceleration for better performance */
.dialog-scale-enter-active,
.dialog-scale-leave-active {
  will-change: transform, opacity;
  backface-visibility: hidden;
}
</style>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import type { ProductImage } from '../../types/products/product.types';

interface Props {
  isOpen: boolean;
  images: ProductImage[];
  initialIndex?: number;
  alt?: string;
  // Optional CSS selector for the image in product detail to create a shared-element animation
  sharedSelector?: string;
}

interface Emits {
  (e: 'close'): void;
}

const props = withDefaults(defineProps<Props>(), {
  initialIndex: 0,
  alt: 'Imagen del producto'
});

const emit = defineEmits<Emits>();

const currentIndex = ref(0);
const imageLoading = ref(false);
const modalImgRef = ref<HTMLImageElement | null>(null);
const isAnimatingShared = ref(false);

/**
 * Improved shared-element animation with smoother transitions and better timing
 */
const animateSharedElement = async (fromEl: HTMLElement | null, toEl: HTMLElement | null, isClosing: boolean = false) => {
  if (!fromEl || !toEl) return;
  isAnimatingShared.value = true;
  
  const fromRect = fromEl.getBoundingClientRect();
  const toRect = toEl.getBoundingClientRect();

  // Create a more accurate clone
  const clone = fromEl.cloneNode(true) as HTMLElement;
  
  // Enhanced clone styling for smoother animation
  Object.assign(clone.style, {
    position: 'fixed',
    left: `${fromRect.left}px`,
    top: `${fromRect.top}px`,
    width: `${fromRect.width}px`,
    height: `${fromRect.height}px`,
    margin: '0',
    padding: '0',
    border: 'none',
    borderRadius: fromEl.style.borderRadius || '0',
    transition: 'all 350ms cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    transformOrigin: 'center center',
    zIndex: '10000',
    pointerEvents: 'none',
    willChange: 'transform, opacity',
    backfaceVisibility: 'hidden'
  });
  
  document.body.appendChild(clone);

  // Calculate transform values
  const scaleX = toRect.width / fromRect.width;
  const scaleY = toRect.height / fromRect.height;
  const translateX = toRect.left - fromRect.left + (toRect.width - fromRect.width) / 2;
  const translateY = toRect.top - fromRect.top + (toRect.height - fromRect.height) / 2;

  // Start animation immediately after next frame
  await new Promise(resolve => requestAnimationFrame(resolve));
  
  // Apply the transform
  clone.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scaleX}, ${scaleY})`;
  
  // Handle opacity based on animation direction
  if (isClosing) {
    clone.style.opacity = '0';
  }

  // Wait for animation to complete
  return new Promise<void>((resolve) => {
    const cleanup = () => {
      clone.remove();
      isAnimatingShared.value = false;
      resolve();
    };
    
    const onTransitionEnd = (e: TransitionEvent) => {
      if (e.target === clone && (e.propertyName === 'transform' || e.propertyName === 'all')) {
        clone.removeEventListener('transitionend', onTransitionEnd);
        cleanup();
      }
    };
    
    clone.addEventListener('transitionend', onTransitionEnd);
    
    // Fallback cleanup
    setTimeout(cleanup, 450);
  });
};

const currentImage = computed(() => {
  if (props.images && props.images[currentIndex.value]) {
    return props.images[currentIndex.value].image_url;
  }
  return '';
});

const closeModal = async () => {
  // If there's a shared-element target on the product detail, animate back first
  if (props.sharedSelector && modalImgRef.value) {
    const target = document.querySelector(props.sharedSelector) as HTMLElement | null;
    if (target) {
      // Hide modal content immediately to prevent double image
      if (modalImgRef.value) {
        modalImgRef.value.style.opacity = '0';
      }
      
      // Animate from modal image to target, then emit close
      try {
        await animateSharedElement(modalImgRef.value, target, true);
      } finally {
        emit('close');
      }
      return;
    }
  }

  emit('close');
};

const selectImage = (index: number) => {
  if (index !== currentIndex.value) {
    imageLoading.value = true;
    currentIndex.value = index;
  }
};

const nextImage = () => {
  if (currentIndex.value < props.images.length - 1) {
    selectImage(currentIndex.value + 1);
  }
};

const previousImage = () => {
  if (currentIndex.value > 0) {
    selectImage(currentIndex.value - 1);
  }
};

const handleImageLoad = () => {
  imageLoading.value = false;
};

const handleImageError = () => {
  imageLoading.value = false;
};

const handleKeydown = (event: KeyboardEvent) => {
  if (!props.isOpen) return;
  
  switch (event.key) {
    case 'Escape':
      closeModal();
      break;
    case 'ArrowLeft':
      previousImage();
      break;
    case 'ArrowRight':
      nextImage();
      break;
  }
};

// Touch gestures
const startX = ref(0);
const startY = ref(0);

const handleTouchStart = (e: TouchEvent) => {
  startX.value = e.touches[0].clientX;
  startY.value = e.touches[0].clientY;
};

const handleTouchEnd = (e: TouchEvent) => {
  const endX = e.changedTouches[0].clientX;
  const endY = e.changedTouches[0].clientY;
  const deltaX = endX - startX.value;
  const deltaY = endY - startY.value;
  
  // Verificar que sea un swipe horizontal (no vertical) y con suficiente distancia
  if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
    if (deltaX > 0) {
      previousImage();
    } else {
      nextImage();
    }
  }
};

// Watchers
watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    currentIndex.value = props.initialIndex;
    imageLoading.value = true;
    
    // Enhanced shared-element opening animation
    if (props.sharedSelector) {
      const source = document.querySelector(props.sharedSelector) as HTMLElement | null;
      
      if (source && modalImgRef.value) {
        // Hide modal image initially to prevent double image
        modalImgRef.value.style.opacity = '0';
        
        // Start animation after modal is fully rendered
        requestAnimationFrame(() => {
          requestAnimationFrame(async () => {
            if (modalImgRef.value && source) {
              try {
                await animateSharedElement(source, modalImgRef.value, false);
                // Show modal image after animation
                if (modalImgRef.value) {
                  modalImgRef.value.style.opacity = '1';
                }
              } catch (error) {
                // Fallback: just show the modal image
                if (modalImgRef.value) {
                  modalImgRef.value.style.opacity = '1';
                }
              }
            }
          });
        });
      }
    }
  }
});

watch(() => props.initialIndex, (newValue) => {
  if (props.isOpen) {
    currentIndex.value = newValue;
    imageLoading.value = true;
  }
});

// Lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleKeydown);
  document.addEventListener('touchstart', handleTouchStart);
  document.addEventListener('touchend', handleTouchEnd);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
  document.removeEventListener('touchstart', handleTouchStart);
  document.removeEventListener('touchend', handleTouchEnd);
});
</script>
