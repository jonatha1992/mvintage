# Scroll Animations System

This document describes the scroll animation system implemented for the M-VINTAGE frontend.

## Overview

The scroll animation system provides performant, modern scroll-triggered animations using the Intersection Observer API for optimal performance.

## Files

- `useScrollAnimation.ts` - Main composable for scroll animations
- `../styles/scroll-animations.css` - CSS classes for animations

## Usage

### Basic Usage

```vue
<script setup lang="ts">
import { useScrollAnimation } from '@/composables/useScrollAnimation'

const { addElements } = useScrollAnimation()

onMounted(() => {
  // Add animations to elements
  addElements('.product-card', { delay: 0, once: true })
  addElements('.hero-title', { delay: 200, once: true })
})
</script>
```

### CSS Classes

Apply these classes directly to HTML elements:

```html
<!-- Fade in from bottom -->
<div class="fade-in-up">Content</div>

<!-- Fade in from left with delay -->
<div class="fade-in-left stagger-1">Content</div>

<!-- Scale in animation -->
<div class="scale-in">Content</div>
```

### Available Animation Classes

- `fade-in-up` - Fades in from bottom
- `fade-in-down` - Fades in from top
- `fade-in-left` - Fades in from left
- `fade-in-right` - Fades in from right
- `scale-in` - Scales in from 80%
- `slide-in-up` - Slides in from bottom (larger movement)
- `slide-in-down` - Slides in from top (larger movement)

### Stagger Classes

- `stagger-1` through `stagger-5` - Adds incremental delays (0.1s - 0.5s)

### Special Classes

- `hero-title` - Special animation for hero titles
- `product-card` - Optimized for product cards
- `footer-section` - For footer sections
- `card-hover` - Enhanced hover effects for cards

## Features

- **Performance**: Uses Intersection Observer API
- **Accessibility**: Respects `prefers-reduced-motion`
- **Customizable**: Configurable delays, thresholds, and options
- **Once option**: Animations can trigger once or on every scroll
- **Stagger support**: Built-in staggered animations for groups

## Implementation in Components

The system is automatically initialized in `App.vue` and will detect common selectors:

- `.product-card`
- `.hero-section h1, .hero-section h2`
- `.card`
- `.feature-item`
- `footer > div > div`

## Browser Support

Works in all modern browsers that support Intersection Observer API (95%+ browser support).