# Frontend Architecture - M-Vintage

## Overview

The M-Vintage frontend is built with Vue 3, TypeScript, and Tailwind CSS, providing a modern, responsive e-commerce experience. This document details the architectural patterns, optimizations, and component structure implemented as of the latest updates.

## Core Architecture

### Technology Stack
- **Framework**: Vue 3.5.18 with Composition API
- **Language**: TypeScript 5.8.3 for type safety
- **Build Tool**: Vite 7.0.4 for fast development and optimized builds
- **Styling**: Tailwind CSS 3.4.0 for utility-first styling
- **State Management**: Pinia 3.0.3 for reactive store management
- **HTTP Client**: Axios 1.11.0 for API communication
- **Authentication**: Firebase 12.0.0 for user authentication
- **Testing**: Vitest 2.0.4 for unit testing

### Project Structure

```
frontend/src/
├── components/           # Reusable Vue components
│   ├── admin/           # Admin-specific components
│   ├── cart/            # Shopping cart components
│   ├── layout/          # Page layout components
│   ├── products/        # Product display components
│   └── ui/              # Generic UI components
├── composables/         # Vue 3 composable functions
├── config/              # Application configuration
├── services/            # External service integrations
├── store/               # Pinia state stores
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
├── views/               # Page-level components (routes)
├── App.vue              # Root application component
├── router.ts            # Vue Router configuration
└── main.ts              # Application entry point
```

## Component Architecture

### Layout Components

#### App.vue - Root Component
Features implemented:
- **Smooth Loading Animation**: App loads with fade-in transition for better UX
- **Scroll-based Footer Visibility**: Footer appears when user scrolls 80% down the page
- **Global Progress Bar**: Navigation progress indication
- **Smart Loading States**: Coordinated loading spinners for different operations

```vue
<template>
  <div class="app-container" :class="{ 'app-loaded': appLoaded }">
    <Navbar />
    <router-view />
    <Footer v-if="!$route.path.includes('/checkout')"
            class="footer-transition"
            :class="{ 'footer-visible': showFooter }" />
    <!-- Global components -->
  </div>
</template>
```

#### HeroBanner.vue - Landing Hero Section
- **Router-based Navigation**: Uses `<router-link>` for proper SPA navigation
- **Video Background**: Autoplay video with image fallback
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Accessibility**: Proper ARIA labels and semantic HTML

### Product Components

#### ProductCard.vue - Optimized Product Display
Recent optimizations:
- **Simplified Image Handling**: Removed OptimizedImage dependency for better performance
- **Error-resistant Loading**: Local SVG fallback for failed image loads
- **Hover Effects**: Secondary image display on hover with smooth transitions
- **Production-ready**: All debug logs removed

```vue
<script setup lang="ts">
// Local SVG image from public directory
const defaultImage = '/imagen-portada.svg';

// Handle image load errors with graceful fallback
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  if (img.src !== defaultImage) {
    primaryImageFailed.value = true;
    img.src = defaultImage;
  }
};
</script>
```

#### OptimizedImage.vue - Advanced Image Component
Features:
- **Event Emission System**: Notifies parent components of load/error states
- **Lazy Loading**: Intersection Observer for performance
- **Fallback Support**: Graceful degradation on load failures
- **Loading States**: Visual feedback during image loading

### State Management

#### Pinia Stores

**Auth Store (`store/auth.ts`)**:
- Firebase authentication integration
- User role management
- Persistent login state
- Admin access control

**Cart Store (`store/cart.ts`)**:
- Shopping cart state management
- Product variant handling
- Persistent cart data
- Stock validation

### Routing Architecture

#### Router Configuration (`router.ts`)
- **Route Guards**: Authentication and authorization checks
- **Progress Bar Integration**: Visual navigation feedback
- **Scroll Behavior**: Smooth scrolling to anchors
- **Admin Route Protection**: Role-based access control

```typescript
// Admin route protection
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAdmin && authStore.isAuthenticated) {
    if (!authStore.hasAdminAccess) {
      next('/');
      return;
    }
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/auth');
  } else {
    next();
  }
});
```

## Performance Optimizations

### Image Loading Strategy
1. **Local Fallbacks**: SVG images served from public directory
2. **Error Handling**: Graceful degradation when external images fail
3. **Lazy Loading**: Intersection Observer for below-fold images
4. **Caching**: Browser-native image caching leveraged

### Build Optimization
- **Code Splitting**: Automatic route-based splitting
- **Tree Shaking**: Unused code elimination
- **Asset Optimization**: Vite's built-in optimization
- **TypeScript Compilation**: Zero-cost abstractions

### Bundle Analysis
Recent build metrics:
```
Production Build Results:
├── CSS: 77.49 kB (gzipped: 12.31 kB)
├── Vendor: 234.17 kB (gzipped: 88.63 kB)
├── Main App: 818.63 kB (gzipped: 202.66 kB)
└── UI Components: 43.25 kB (gzipped: 14.07 kB)
```

## Environment Configuration

### Multi-Environment Setup
- **Development** (`npm run dev`): Hot reload, source maps
- **Test** (`npm run build:test`): Test environment optimizations
- **Production** (`npm run build`): Full optimizations, minification

### Environment Variables
```typescript
// Frontend environment configuration
interface EnvironmentConfig {
  VITE_BACKEND_URL: string;
  VITE_FIREBASE_API_KEY: string;
  VITE_FIREBASE_AUTH_DOMAIN: string;
  VITE_FIREBASE_PROJECT_ID: string;
  // ... other Firebase config
}
```

## TypeScript Integration

### Type Safety
- **Strict Mode**: Full TypeScript strict mode enabled
- **Component Props**: Typed component interfaces
- **API Responses**: Typed HTTP responses
- **Store State**: Typed Pinia stores

### Type Definitions Structure
```
types/
├── cart/
│   ├── cart.types.ts
│   └── index.ts
├── products/
│   ├── product.types.ts
│   └── index.ts
├── users/
│   ├── user.types.ts
│   └── index.ts
└── index.ts              # Centralized exports
```

## Authentication Architecture

### Firebase Integration
- **Multiple Auth Methods**: Google OAuth, Email/Password
- **Adaptive Authentication**: Popup in development, redirect in production
- **Token Management**: Automatic token refresh
- **Role-based Access**: Backend role validation

### Auth Flow
1. User initiates login via AuthView
2. Firebase handles authentication
3. Frontend receives Firebase JWT token
4. Backend validates token and returns user data
5. Frontend stores user state in Pinia auth store
6. Route guards protect admin areas

## Development Workflow

### Code Quality
- **TypeScript Validation**: `vue-tsc --noEmit`
- **Build Testing**: Multi-environment build validation
- **Production Readiness**: Debug code removal
- **Component Architecture**: Reusable, maintainable components

### Testing Strategy
- **Unit Tests**: Vitest for component testing
- **Integration Tests**: Route and store testing
- **Build Validation**: Multi-environment build verification
- **TypeScript Checking**: Compile-time error detection

## Best Practices

### Component Design
1. **Single Responsibility**: Each component has one clear purpose
2. **Prop Validation**: TypeScript interfaces for all props
3. **Event Emission**: Clear parent-child communication
4. **Composition API**: Modern Vue 3 patterns

### Performance Guidelines
1. **Lazy Loading**: Components and images loaded on demand
2. **Bundle Optimization**: Route-based code splitting
3. **State Management**: Efficient Pinia store usage
4. **Asset Optimization**: Compressed images and fonts

### Accessibility
1. **Semantic HTML**: Proper heading hierarchy
2. **ARIA Labels**: Screen reader support
3. **Keyboard Navigation**: Full keyboard accessibility
4. **Color Contrast**: WCAG compliant color schemes

## Future Improvements

### Planned Enhancements
1. **Component Testing**: Comprehensive test suite
2. **PWA Features**: Service worker implementation
3. **Performance Monitoring**: Core Web Vitals tracking
4. **Accessibility Audit**: WCAG 2.1 AA compliance

### Architecture Evolution
1. **Micro-frontends**: Potential module federation
2. **State Management**: Possible Vuex migration evaluation
3. **Build Optimization**: Further bundle size reduction
4. **Type Safety**: Enhanced TypeScript coverage

---

*Last Updated: September 2024*
*Architecture Version: 2.1*