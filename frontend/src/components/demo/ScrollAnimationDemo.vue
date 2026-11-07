<template>
  <div class="py-16 bg-gray-50">
    <div class="max-w-4xl mx-auto px-4">
      <!-- Demo Header -->
      <div class="text-center mb-16">
        <h2 class="text-3xl font-light text-gray-900 mb-4 fade-in-up">
          Scroll Animation Demo
        </h2>
        <p class="text-gray-600 fade-in-up stagger-1">
          Scroll down to see elements animate into view
        </p>
      </div>

      <!-- Demo Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
        <div
          v-for="n in 6"
          :key="n"
          class="bg-white p-6 rounded-lg shadow-sm border card-hover fade-in-up"
        >
          <div class="w-12 h-12 bg-gray-200 rounded-lg mb-4"></div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Card {{ n }}</h3>
          <p class="text-gray-600 text-sm">
            This card will animate in when it comes into view
          </p>
        </div>
      </div>

      <!-- Different Animation Types -->
      <div class="space-y-12">
        <div class="text-center">
          <h3 class="text-2xl font-light text-gray-900 mb-8 fade-in-down">
            Different Animation Types
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div class="p-6 bg-white rounded-lg fade-in-left">
            <h4 class="text-lg font-medium mb-2">Fade In Left</h4>
            <p class="text-gray-600">This box slides in from the left</p>
          </div>

          <div class="p-6 bg-white rounded-lg fade-in-right">
            <h4 class="text-lg font-medium mb-2">Fade In Right</h4>
            <p class="text-gray-600">This box slides in from the right</p>
          </div>
        </div>

        <div class="text-center">
          <div class="p-8 bg-white rounded-lg inline-block scale-in">
            <h4 class="text-xl font-medium mb-2">Scale In</h4>
            <p class="text-gray-600">This box scales up when it appears</p>
          </div>
        </div>

        <div class="space-y-4">
          <div class="p-4 bg-white rounded-lg slide-in-up stagger-1">
            <p>Slide in animation with stagger delay 1</p>
          </div>
          <div class="p-4 bg-white rounded-lg slide-in-up stagger-2">
            <p>Slide in animation with stagger delay 2</p>
          </div>
          <div class="p-4 bg-white rounded-lg slide-in-up stagger-3">
            <p>Slide in animation with stagger delay 3</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// This component demonstrates the scroll animation system
// The animations are automatically handled by the global scroll animation system
</script>

<style scoped>
/* Additional demo-specific styles if needed */
</style>