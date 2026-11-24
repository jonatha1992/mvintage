<template>
  <Teleport to="body">
    <div class="sr-only" aria-live="polite" aria-atomic="true">{{ announcement }}</div>
    <section ref="panel" popover="manual" v-show="isNotificationVisible" class="cart-notice"
      role="region" aria-label="Aviso del carrito" @mouseenter="pauseDismissal" @mouseleave="resumeDismissal"
      @focusin="pauseDismissal" @focusout="resumeDismissal">
      <button class="notice-close" aria-label="Cerrar aviso" @click="dismiss">×</button>
      <p class="notice-title">{{ errorMessage || 'Agregado al carrito' }}</p>
      <div v-if="productData" class="notice-product">
        <img :src="productData.image" alt="" width="56" height="64" />
        <div>
          <p class="notice-name">{{ productData.name }}</p>
          <p class="notice-selection">Talle {{ productData.variant.size }} · Color {{ productData.variant.color }}</p>
        </div>
      </div>
      <button v-if="productData" class="notice-cart" @click="handleViewCart">Ver carrito</button>
    </section>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import { useCartNotification } from '../../composables/useCartNotification'
import { useCartModal } from '../../composables/useCartModal'

const { isNotificationVisible, productData, errorMessage, hideNotification, pauseDismissal, resumeDismissal } = useCartNotification()
const { openCartModal } = useCartModal()
const panel = ref<HTMLElement | null>(null)
let previousFocus: HTMLElement | null = null
const announcement = computed(() => !isNotificationVisible.value ? '' : errorMessage.value ||
  `Agregado al carrito. ${productData.value?.name}. Talle ${productData.value?.variant.size}, color ${productData.value?.variant.color}. Ver carrito disponible.`)
watch(isNotificationVisible, async (visible) => {
  if (visible) previousFocus = document.activeElement as HTMLElement | null
  await nextTick()
  if (panel.value && 'showPopover' in panel.value) {
    if (visible) panel.value.showPopover()
    else panel.value.hidePopover()
  }
})
const dismiss = () => {
  if (panel.value?.contains(document.activeElement)) previousFocus?.focus()
  hideNotification()
}
const handleViewCart = () => {
  dismiss()
  openCartModal()
}
</script>

<style scoped>
.cart-notice {
  position: fixed;
  inset: auto 12px calc(12px + env(safe-area-inset-bottom)) 12px;
  z-index: 2147483647;
  width: auto;
  max-width: 400px;
  max-height: calc(100dvh - 24px);
  overflow-y: auto;
  margin: 0 0 0 auto;
  padding: 18px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #fff;
  color: #111827;
  box-shadow: 0 8px 32px #0002;
  opacity: 1;
  transform: translateY(0);
  transition: opacity 180ms ease-out, transform 180ms cubic-bezier(0.23, 1, 0.32, 1), display 180ms, overlay 180ms;
  transition-behavior: allow-discrete;
}
.notice-title { font-size: 15px; font-weight: 600; padding-right: 36px; margin-bottom: 12px; }
.notice-close { position: absolute; top: 4px; right: 4px; min-width: 44px; min-height: 44px; font-size: 24px; }
.notice-product { display: flex; gap: 12px; align-items: center; }
.notice-product img { object-fit: cover; border-radius: 4px; flex-shrink: 0; }
.notice-product > div { min-width: 0; overflow-wrap: anywhere; }
.notice-name { font-size: 14px; font-weight: 500; }
.notice-selection { font-size: 13px; color: #4b5563; margin-top: 4px; }
.notice-cart { width: 100%; min-height: 44px; margin-top: 14px; background: #111; color: white; border-radius: 6px; font-size: 14px; }
.notice-cart, .notice-close { transition: transform 150ms ease-out; }
.notice-cart:active, .notice-close:active { transform: scale(0.97); }
@starting-style { .cart-notice { opacity: 0; transform: translateY(12px); } }
@media (min-width: 640px) { .cart-notice { left: auto; right: 24px; bottom: 24px; width: 380px; } }
@media (prefers-reduced-motion: reduce) {
  .cart-notice, .notice-cart, .notice-close { transition: none; transform: none; }
  @starting-style { .cart-notice { opacity: 1; transform: none; } }
}
</style>

