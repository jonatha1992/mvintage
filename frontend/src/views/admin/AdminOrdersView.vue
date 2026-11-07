<template>
  <div class="min-h-screen bg-gray-50">
    <div class="px-4 py-8 mx-auto max-w-7xl sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 font-heading">Gestión de Envíos</h1>
        <p class="mt-2 text-sm text-gray-600 font-body">
          Administra pedidos, asigna números de seguimiento y controla el estado de los envíos
        </p>
      </div>

      <!-- Admin Navigation Tabs -->
      <div class="mb-6 border-b border-gray-200">
        <nav class="flex space-x-8">
          <router-link 
            to="/admin/products" 
            class="px-1 py-4 text-sm font-medium text-gray-500 transition-colors border-b-2 border-transparent hover:text-gray-700 hover:border-gray-300 whitespace-nowrap"
          >
            <span class="font-body">Productos</span>
          </router-link>
          <router-link 
            to="/admin/users" 
            class="px-1 py-4 text-sm font-medium text-gray-500 transition-colors border-b-2 border-transparent hover:text-gray-700 hover:border-gray-300 whitespace-nowrap"
          >
            <span class="font-body">Usuarios</span>
          </router-link>
          <router-link 
            to="/admin/orders" 
            class="px-1 py-4 text-sm font-medium text-gray-900 border-b-2 border-black whitespace-nowrap"
          >
            <span class="font-body">Pedidos</span>
          </router-link>
        </nav>
      </div>

      <!-- Statistics Cards -->
      <div v-if="statistics" class="grid grid-cols-1 gap-6 mb-8 md:grid-cols-2 lg:grid-cols-4">
        <div class="overflow-hidden bg-white rounded-lg shadow">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="w-6 h-6 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="flex-1 w-0 ml-5">
                <dl>
                  <dt class="text-sm font-medium text-gray-600 truncate font-body">Pendientes de Envío</dt>
                  <dd class="text-lg font-medium text-gray-900 font-body">{{ statistics.pending_shipment }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="overflow-hidden bg-white rounded-lg shadow">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <div class="flex-1 w-0 ml-5">
                <dl>
                  <dt class="text-sm font-medium text-gray-600 truncate font-body">Enviados</dt>
                  <dd class="text-lg font-medium text-gray-900 font-body">{{ statistics.shipped_orders }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="overflow-hidden bg-white rounded-lg shadow">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div class="flex-1 w-0 ml-5">
                <dl>
                  <dt class="text-sm font-medium text-gray-600 truncate font-body">Tasa de Envío</dt>
                  <dd class="text-lg font-medium text-gray-900 font-body">{{ statistics.shipping_rate_percent }}%</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="overflow-hidden bg-white rounded-lg shadow">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="flex-1 w-0 ml-5">
                <dl>
                  <dt class="text-sm font-medium text-gray-600 truncate font-body">Tiempo Promedio</dt>
                  <dd class="text-lg font-medium text-gray-900 font-body">{{ statistics.avg_processing_hours }}h</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filter and Action Bar -->
      <div class="flex items-center justify-between p-4 mb-6 bg-white rounded-lg shadow">
        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-2">
            <label for="statusFilter" class="text-sm font-medium text-gray-700">Filtrar por estado:</label>
            <select v-model="statusFilter" @change="loadOrders" 
              class="w-full max-w-xs px-3 py-2 text-sm bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              <option value="">Todos</option>
              <option value="pending">Pendientes</option>
              <option value="prepared">Preparados</option>
              <option value="shipped">Enviados</option>
              <option value="with_tracking">Con Tracking</option>
            </select>
          </div>
          
          <button @click="loadOrders" :disabled="loading"
            class="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            title="Actualizar lista de pedidos">
            <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>

        <!-- Bulk Actions -->
        <div v-if="selectedOrders.length > 0" class="flex items-center space-x-2">
          <span class="text-sm text-gray-500">{{ selectedOrders.length }} seleccionados</span>
          
          <button @click="deleteSelectedOrders" :disabled="loading"
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md shadow-sm hover:bg-red-700 disabled:opacity-50">
            <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Eliminar
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading && allOrders.length === 0" class="py-12 text-center">
        <div class="inline-block w-8 h-8 border-b-2 border-gray-900 rounded-full animate-spin"></div>
        <p class="mt-2 text-gray-600">Cargando pedidos...</p>
      </div>

      <!-- Orders Table -->
      <div v-else class="overflow-hidden bg-white rounded-lg shadow">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="relative w-10 px-2 sm:px-3">
                  <div class="flex items-center justify-center">
                    <label class="inline-flex items-center cursor-pointer group">
                      <input type="checkbox" 
                        :checked="selectAll"
                        :indeterminate="selectedOrders.length > 0 && !selectAll"
                        @change="toggleSelectAll"
                        :disabled="filteredOrders.length === 0"
                        class="sr-only peer">
                      <div class="relative w-5 h-5 transition-colors duration-200 bg-white border-2 border-blue-500 rounded-md peer-checked:bg-blue-500 peer-checked:border-blue-500 peer-hover:bg-blue-50">
                        <svg class="absolute inset-0 w-4 h-4 m-auto text-white transition-opacity duration-200 opacity-0 peer-checked:opacity-100" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <span class="sr-only">Seleccionar pedidos</span>
                    </label>
                  </div>
                  <div class="absolute inset-0" title="Seleccionar todos los pedidos" data-tooltip-placement="bottom"></div>
                </th>
                <th scope="col" class="px-3 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">
                  Pedido
                </th>
                <th scope="col" class="px-3 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">
                  Cliente
                </th>
                <th scope="col" class="px-2 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">
                  Total
                </th>
                <th scope="col" class="px-2 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">
                  Dirección
                </th>
                <th scope="col" class="px-2 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">
                  Entrega
                </th>
                <th scope="col" class="px-2 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">
                  Estado
                </th>
                <th scope="col" class="px-2 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">
                  Seguimiento
                </th>
                <th scope="col" class="px-3 py-3 text-xs font-medium tracking-wider text-right text-gray-500 uppercase">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="order in filteredOrders" :key="order.order_id" class="hover:bg-gray-50">
                <td class="relative w-10 px-2 sm:px-3">
                  <div class="flex items-center justify-center">
                    <label class="inline-flex items-center cursor-pointer group">
                      <input 
                        type="checkbox" 
                        :value="order.order_id"
                        :checked="selectedOrders.includes(order.order_id)"
                        @change="(e) => toggleRowSelection(order.order_id, (e.target as HTMLInputElement).checked)"
                        class="sr-only peer"
                        :title="order.can_mark_shipped ? 'Marcar como enviado' : 'Agregar seguimiento'">
                      <div class="relative w-5 h-5 transition-colors duration-200 bg-white border-2 border-blue-500 rounded-md peer-checked:bg-blue-500 peer-checked:border-blue-500 peer-hover:bg-blue-50">
                        <svg class="absolute inset-0 w-4 h-4 m-auto text-white transition-opacity duration-200 opacity-0 peer-checked:opacity-100" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <span class="sr-only">{{ order.can_mark_shipped ? 'Marcar como enviado' : 'Agregar seguimiento' }}</span>
                    </label>
                  </div>
                </td>
                <td class="px-3 py-3 whitespace-nowrap">
                  <div class="flex items-center">
                    <div>
                      <div class="text-sm font-medium text-gray-900">#{{ order.order_id }}</div>
                      <div class="text-xs text-gray-500">{{ formatDate(order.created_at) }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-3 py-3">
                  <div class="text-sm text-gray-900 truncate max-w-32">{{ order.customer_name }}</div>
                  <div class="text-xs text-gray-500 truncate max-w-32">{{ order.customer_email }}</div>
                  <div v-if="order.customer_phone" class="text-xs text-gray-500 truncate">{{ order.customer_phone }}</div>
                </td>
                <td class="px-2 py-3 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">${{ order.total.toLocaleString() }}</div>
                  <div class="text-xs">
                    <span :class="getPaymentStatusClass(order.payment_status)" class="inline-flex px-1 py-0.5 text-xs font-medium rounded">
                      {{ getPaymentStatusText(order.payment_status) }}
                    </span>
                  </div>
                </td>
                <td class="px-2 py-3 max-w-32">
                  <div class="text-xs text-gray-900 truncate">
                    {{ getFormattedAddress(order) || 'Sin dirección' }}
                  </div>
                </td>
                <td class="px-2 py-3 whitespace-nowrap">
                  <span :class="getDeliveryMethodClass(order.delivery_method)" 
                    class="inline-flex px-1 py-0.5 text-xs font-medium rounded">
                    {{ getDeliveryMethodText(order.delivery_method) }}
                  </span>
                </td>
                <td class="px-2 py-3 whitespace-nowrap">
                  <span :class="getShippingStatusClass(order.shipping_status || order.status)" 
                    class="inline-flex px-1 py-0.5 text-xs font-medium rounded">
                    {{ getShippingStatusText(order.shipping_status || order.status) }}
                  </span>
                </td>
                <td class="px-2 py-3 whitespace-nowrap">
                  <div v-if="order.tracking_number" class="text-xs">
                    <div class="font-mono text-gray-900 truncate max-w-24">{{ order.tracking_number }}</div>
                    <div v-if="order.provider_name" class="text-gray-500 truncate">{{ order.provider_name }}</div>
                  </div>
                  <div v-else class="text-xs text-gray-400">Sin asignar</div>
                </td>
                <td class="px-3 py-3 text-sm font-medium text-right whitespace-nowrap">
                  <div class="flex items-center justify-end space-x-2">
                    <!-- Verify Payment Button -->
                    <button @click="openPaymentVerificationModal(order)" class="p-1 text-orange-600 hover:text-orange-800" title="Verificar pago">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </button>

                    <!-- Add Tracking Button -->
                    <button @click="openTrackingModal(order)" class="p-1 text-green-600 hover:text-green-800" title="Agregar seguimiento">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                      </svg>
                    </button>

                    <!-- Delete Order Button -->
                    <button @click="deleteIndividualOrder(order.order_id)" class="p-1 text-red-600 hover:text-red-800" title="Eliminar pedido">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                    
                    <!-- View Details Button -->
                    <button @click="viewOrderDetails(order)" class="p-1 text-gray-600 hover:text-gray-800" title="Ver detalles">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty State -->
        <div v-if="!loading && filteredOrders.length === 0" class="py-12 text-center">
          <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">No hay pedidos</h3>
          <p class="mt-1 text-sm text-gray-500">No se encontraron pedidos con los filtros seleccionados.</p>
        </div>
      </div>

      <!-- Add/Edit Tracking Modal -->
      <div v-if="showTrackingModal" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="flex items-end justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="closeTrackingModal"></div>
          
          <div class="inline-block overflow-hidden text-left align-bottom transition-all transform bg-white rounded-lg shadow-xl sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
            <form @submit.prevent="saveTrackingInfo">
              <div class="px-4 pt-5 pb-4 bg-white sm:p-6 sm:pb-4">
                <div class="sm:flex sm:items-start">
                  <div class="flex items-center justify-center flex-shrink-0 w-12 h-12 mx-auto bg-blue-100 rounded-full sm:mx-0 sm:h-10 sm:w-10">
                    <svg class="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                  </div>
                  <div class="w-full mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                    <h3 class="text-lg font-medium leading-6 text-gray-900">
                      Gestionar Envío - Pedido #{{ selectedOrder?.order_id }}
                    </h3>
                    <div class="grid grid-cols-1 gap-4">
                      <!-- Current Status Display -->
                      <div class="p-3 rounded-md bg-gray-50">
                        <label class="block text-sm font-medium text-gray-700">Estado Actual:</label>
                        <span :class="getShippingStatusClass(selectedOrder?.shipping_status || selectedOrder?.status)" class="inline-flex px-2 py-1 text-xs font-medium rounded">
                          {{ getShippingStatusText(selectedOrder?.shipping_status || selectedOrder?.status) }}
                        </span>
                      </div>
                      
                      <!-- Status Change Selector -->
                      <div>
                        <label for="shippingStatusSelect" class="block mb-1 text-sm font-medium text-gray-700">
                          Cambiar Estado de Envío
                        </label>
                        <select 
                          id="shippingStatusSelect" 
                          v-model="newShippingStatus" 
                          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                          <option value="">Mantener estado actual</option>
                          <option value="pending">🟡 Pendiente (pedido creado)</option>
                          <option value="prepared">🔵 Preparado (listo para enviar)</option>
                          <option value="shipped">🟣 Enviado (llevado al correo)</option>
                        </select>
                      </div>
                      
                      <!-- Divider -->
                      <div class="pt-4 border-t border-gray-200">
                        <h4 class="mb-3 text-sm font-medium text-gray-700">Información de Seguimiento (Opcional)</h4>
                      </div>
                      
                      <div>
                        <label class="block mb-1 text-sm font-medium text-gray-700">
                          Número de seguimiento
                        </label>
                        <input 
                          v-model="trackingForm.trackingNumber"
                          type="text" 
                          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="Ingrese el número de seguimiento"
                        >
                      </div>

                      <div>
                        <label class="block mb-1 text-sm font-medium text-gray-700">
                          Notas del pedido
                        </label>
                        <textarea 
                          v-model="trackingForm.shippingNotes"
                          rows="3"
                          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="Notas sobre el pedido..."
                        ></textarea>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="px-4 py-3 bg-gray-50 sm:px-6 sm:flex sm:flex-row-reverse">
                <button type="submit" :disabled="trackingLoading"
                  class="inline-flex justify-center w-full px-4 py-2 text-base font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 disabled:opacity-50 sm:ml-3 sm:w-auto sm:text-sm">
                  <span class="text-white" v-if="trackingLoading">Guardando...</span>
                  <span class="text-white" v-else>Guardar</span>
                </button>
                <button type="button" @click="closeTrackingModal"
                  class="inline-flex justify-center w-full px-4 py-2 mt-3 text-base font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Payment Verification Modal -->
      <div v-if="showPaymentVerificationModal && selectedOrder" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="flex items-end justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="closePaymentVerificationModal"></div>
          
          <div class="inline-block overflow-hidden text-left align-bottom transition-all transform bg-white rounded-lg shadow-xl sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
            <div class="px-4 pt-5 pb-4 bg-white sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="flex items-center justify-center flex-shrink-0 w-12 h-12 mx-auto bg-orange-100 rounded-full sm:mx-0 sm:h-10 sm:w-10">
                  <svg class="w-6 h-6 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="w-full mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                  <h3 class="text-lg font-medium leading-6 text-gray-900">
                    Verificar Pago - Pedido #{{ selectedOrder.order_id }}
                  </h3>
                  
                  <div class="mt-4 space-y-4">
                    <!-- Payment Method Info -->
                    <div class="p-3 rounded-md bg-gray-50">
                      <p class="text-sm font-medium text-gray-700">Método de Pago:</p>
                      <p class="text-sm text-gray-900">{{ getPaymentMethodText(selectedOrder.payment_method) }}</p>
                    </div>
                    
                    <!-- Payment Status -->
                    <div class="p-3 rounded-md bg-gray-50">
                      <p class="text-sm font-medium text-gray-700">Estado de Pago Actual:</p>
                      <span :class="getPaymentStatusClass(selectedOrder.payment_status)" 
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                        {{ getPaymentStatusText(selectedOrder.payment_status) }}
                      </span>
                    </div>
                    
                    <!-- Total Amount -->
                    <div class="p-3 rounded-md bg-gray-50">
                      <p class="text-sm font-medium text-gray-700">Total:</p>
                      <p class="text-lg font-bold text-gray-900">${{ selectedOrder.total?.toLocaleString() }}</p>
                    </div>
                    
                    <!-- Payment Status Selection -->
                    <div>
                      <label class="block mb-1 text-sm font-medium text-gray-700">
                        Estado del Pago
                      </label>
                      <select 
                        v-model="selectedPaymentStatus"
                        class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      >
                        <option value="pending">Pendiente</option>
                        <option value="paid">Pagado</option>
                        <option value="cancelled">Cancelado</option>
                      </select>
                    </div>

                    <!-- Admin Notes -->
                    <div>
                      <label class="block mb-1 text-sm font-medium text-gray-700">
                        Notas de Verificación
                      </label>
                      <textarea 
                        v-model="verificationNotes"
                        rows="3"
                        class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                        placeholder="Notas sobre la verificación del pago..."
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="px-4 py-3 bg-gray-50 sm:px-6 sm:flex sm:flex-row-reverse">
              <button @click="updatePaymentStatus" :disabled="loading"
                class="inline-flex justify-center w-full px-4 py-2 text-base font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 disabled:opacity-50 sm:ml-3 sm:w-auto sm:text-sm">
                Actualizar Estado
              </button>
              <button @click="closePaymentVerificationModal"
                class="inline-flex justify-center w-full px-4 py-2 mt-3 text-base font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
                Cancelar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Order Status Modal -->
      <OrderStatusModal
        v-if="selectedOrder && selectedOrder.order_id"
        :is-open="showStatusModal"
        :order="selectedOrder as Order"
        @close="closeStatusModal"
        @update-status="updateOrderStatus"
      />


      <!-- Shipping Modal -->
      <ShippingModal
        v-if="selectedOrder && selectedOrder.order_id"
        :is-open="showShippingModal"
        :order="selectedOrder as Order"
        @close="closeShippingModal"
        @update-shipping="updateOrderShipping"
      />

      <!-- Order Details Modal -->
      <div v-if="showOrderDetailsModal && selectedOrder" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="flex items-end justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="closeOrderDetailsModal"></div>
          
          <div class="inline-block overflow-hidden text-left align-bottom transition-all transform bg-white rounded-lg shadow-xl sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full">
            <div class="px-4 pt-5 pb-4 bg-white sm:p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-medium leading-6 text-gray-900">
                  Detalles del Pedido #{{ selectedOrder.order_id }}
                </h3>
                <button @click="closeOrderDetailsModal" class="text-gray-400 hover:text-gray-500">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
                <!-- Customer Information -->
                <div class="p-4 rounded-lg bg-gray-50">
                  <h4 class="mb-3 text-sm font-semibold text-gray-900">Información del Cliente</h4>
                  <div class="space-y-2">
                    <div>
                      <span class="text-xs text-gray-500">Nombre:</span>
                      <p class="text-sm text-gray-900">{{ getCustomerName(selectedOrder) }}</p>
                    </div>
                    <div>
                      <span class="text-xs text-gray-500">Email:</span>
                      <p class="text-sm text-gray-900">{{ getCustomerEmail(selectedOrder) }}</p>
                    </div>
                    <div v-if="getCustomerPhone(selectedOrder) !== 'N/A'">
                      <span class="text-xs text-gray-500">Teléfono:</span>
                      <p class="text-sm text-gray-900">{{ getCustomerPhone(selectedOrder) }}</p>
                    </div>
                  </div>
                </div>

                <!-- Order Information -->
                <div class="p-4 rounded-lg bg-gray-50">
                  <h4 class="mb-3 text-sm font-semibold text-gray-900">Información del Pago</h4>
                  <div class="space-y-2">
                    <div>
                      <span class="text-xs text-gray-500">Estado del Pago:</span>
                      <span  
                        class="inline-flex px-2 py-1 ml-1 text-xs font-semibold rounded-full">
                        {{ getShippingStatusText(selectedOrder.payment_status) }}
                      </span>
                    </div>
                    <div>
                      <span class="text-xs text-gray-500">Total:</span>
                      <p class="text-sm font-semibold text-gray-900">${{ selectedOrder.total?.toLocaleString() }}</p>
                    </div>
                    <div>
                      <span class="text-xs text-gray-500">Fecha:</span>
                      <p class="text-sm text-gray-900">{{ formatDate(selectedOrder.created_at) }}</p>
                    </div>
                    <div>
                      <span class="text-xs text-gray-500">Método de Pago:</span>
                      <p class="text-sm text-gray-900">{{ getPaymentMethodText(selectedOrder.payment_method) }}</p>
                    </div>
                  </div>
                </div>

                <!-- Shipping Information -->
                <div class="p-4 rounded-lg bg-gray-50 md:col-span-2">
                  <h4 class="mb-3 text-sm font-semibold text-gray-900">Información de Envío</h4>
                  <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                    <div>
                      <span class="text-xs text-gray-500">Dirección de Envío:</span>
                      <p class="text-sm text-gray-900">
                        {{ getFormattedAddress(selectedOrder) || 'No especificada' }}
                      </p>
                    </div>
                    <div>
                      <span class="text-xs text-gray-500">Método de Entrega:</span>
                      <span :class="getDeliveryMethodClass(selectedOrder.delivery_method)" 
                        class="inline-flex px-2 py-1 ml-1 text-xs font-semibold rounded-full">
                        {{ getDeliveryMethodText(selectedOrder.delivery_method) }}
                      </span>
                    </div>
                    <div>
                      <span class="text-xs text-gray-500">Estado de Envío:</span>
                      <span :class="getShippingStatusClass(selectedOrder.shipping_status)" 
                        class="inline-flex px-2 py-1 ml-1 text-xs font-semibold rounded-full">
                        {{ getShippingStatusText(selectedOrder.shipping_status) }}
                      </span>
                    </div>
                    <div v-if="selectedOrder.tracking_number">
                      <span class="text-xs text-gray-500">Número de Seguimiento:</span>
                      <p class="font-mono text-sm text-gray-900">{{ selectedOrder.tracking_number }}</p>
                      <p v-if="selectedOrder.provider_name" class="text-xs text-gray-500">{{ selectedOrder.provider_name }}</p>
                    </div>
                  </div>
                  <div v-if="selectedOrder.shipped_at" class="mt-4">
                    <span class="text-xs text-gray-500">Fecha de Envío:</span>
                    <p class="text-sm text-gray-900">{{ formatDate(selectedOrder.shipped_at) }}</p>
                    <div v-if="selectedOrder.estimated_delivery" class="mt-1">
                      <span class="text-xs text-gray-500">Fecha Estimada de Entrega:</span>
                      <p class="text-sm text-gray-900">{{ formatDate(selectedOrder.estimated_delivery) }}</p>
                    </div>
                  </div>
                </div>

                <!-- Notes -->
                <div v-if="selectedOrder.notes" class="p-4 rounded-lg bg-gray-50 md:col-span-2">
                  <h4 class="mb-2 text-sm font-semibold text-gray-900">Notas</h4>
                  <p class="text-sm text-gray-700">{{ selectedOrder.notes }}</p>
                </div>
              </div>
            </div>
            
            <div class="px-4 py-3 bg-gray-50 sm:px-6 sm:flex sm:flex-row-reverse">
              <button @click="closeOrderDetailsModal"
                class="inline-flex justify-center w-full px-4 py-2 text-base font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 sm:mt-0 sm:w-auto sm:text-sm">
                Cerrar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../../store/auth';
import type { Order, AdminStats, OrderStatistics } from '../../types/orders/order.types';
import type { ShippingProvider } from '../../types/orders/shipping.types';
import { 
  createCompleteOrder, 
  formatDate, 
  safeString, 
  toStringOrNull 
} from '../../utils/orderUtils';
import OrderStatusModal from '../../components/orders/OrderStatusModal.vue';
import ShippingModal from '../../components/checkout/ShippingModal.vue';
import { useToast } from 'vue-toastification';
import { useRouter } from 'vue-router';
import { ordersApi } from '../../config/api';
import { 
  getPaymentStatusClass, 
  getPaymentStatusText,
  getShippingStatusClass, 
  getShippingStatusText,
  getDeliveryMethodClass,
  getDeliveryMethodText 
} from '../../utils/orderStatusUtils';

const authStore = useAuthStore();
const toast = useToast();
const router = useRouter();

// Status functions now imported from centralized orderStatusUtils

// Shipping status and delivery method functions now imported from centralized orderStatusUtils


const getFormattedAddress = (order: Order | null): string => {
  if (!order) return '';
  
  // Handle both nested customer object and flat properties
  const customer = order.customer || {
    address: order.shipping_address,
    city: undefined,
    postal_code: undefined,
    province: undefined
  };
  
  const addressParts: string[] = [];
  
  if (customer.address) addressParts.push(customer.address);
  if (customer.city) addressParts.push(customer.city);
  if (customer.postal_code) addressParts.push(`CP ${customer.postal_code}`);
  if (customer.province) addressParts.push(customer.province);
  
  return addressParts.join(', ');
};

// Helper functions for customer data display with fallbacks
const getCustomerName = (order: Order | null): string => {
  return order?.customer?.name || order?.customer_name || 'N/A';
};

const getCustomerEmail = (order: Order | null): string => {
  return order?.customer?.email || order?.customer_email || 'N/A';
};

const getCustomerPhone = (order: Order | null): string => {
  return order?.customer?.phone || order?.customer_phone || 'N/A';
};

const getPaymentMethodText = (method: string | undefined): string => {
  if (!method) return 'No especificado';
  const methodTexts: Record<string, string> = {
    'transfer': 'Transferencia Bancaria',
    'mercadopago': 'MercadoPago',
    'cash': 'Efectivo Contra Entrega'
  };
  return methodTexts[method.toLowerCase()] || method;
};

// State
const loading = ref(true);
const trackingLoading = ref(false);
const allOrders = ref<Order[]>([]); // Almacena todos los pedidos

// Form and modal state
const trackingForm = ref({
  trackingNumber: '',
  shippingNotes: ''
});

// Modal visibility states
const showTrackingModal = ref(false);
const showOrderDetailsModal = ref(false);
const showShippingModal = ref(false);
const showStatusModal = ref(false);
const showPaymentVerificationModal = ref(false);

// Selection and data
const selectedOrders = ref<number[]>([]);
const selectAll = ref(false);
const statistics = ref<any>(null);
const statusFilter = ref('');
const selectedOrder = ref<Order | null>(null);
const trackingNumber = ref('');
const selectedProvider = ref('');
const verificationNotes = ref('');
const selectedPaymentStatus = ref('pending');
const newShippingStatus = ref('');

// Propiedad computada para los pedidos filtrados
const filteredOrders = computed(() => {
  if (!statusFilter.value) return allOrders.value;
  
  return allOrders.value.filter(order => {
    switch(statusFilter.value) {
      case 'pending':
        return order.status === 'pending';
      case 'prepared':
        return order.status === 'prepared';
      case 'shipped':
        return order.status === 'shipped';
      case 'with_tracking':
        return Boolean(order.tracking_number) && order.status === 'shipped';
      default:
        return true;
    }
  });
});

// Helper function to update selectedOrder with fresh data
const updateSelectedOrder = () => {
  if (selectedOrder.value) {
    const updatedOrder = allOrders.value.find(order => order.order_id === selectedOrder.value!.order_id);
    if (updatedOrder) {
      selectedOrder.value = { ...updatedOrder };
    }
  }
};

// Modal handlers
const openStatusModal = (order: Order) => {
  if (!order?.order_id) return;
  selectedOrder.value = createCompleteOrder(order);
  showStatusModal.value = true;
};

const closeStatusModal = () => {
  showStatusModal.value = false;
  selectedOrder.value = null;
};

const openTrackingModal = (order: Order) => {
  if (!order) return;
  // Crear un objeto Order completo con valores por defecto
  const orderWithDefaults: Order = {
    order_id: order.order_id,
    customer_name: order.customer_name,
    customer_email: order.customer_email,
    customer_phone: order.customer_phone || '',
    shipping_address: order.shipping_address,
    status: order.status,
    shipping_status: order.shipping_status,
    tracking_number: order.tracking_number || '',
    shipping_provider: order.shipping_provider || '',
    provider_name: order.provider_name || '',
    notes: order.notes || '',
    can_add_tracking: order.can_add_tracking || false,
    can_mark_shipped: order.can_mark_shipped || false,
    can_coordinate_pickup: order.can_coordinate_pickup || false,
    created_at: order.created_at || new Date().toISOString(),
    shipped_at: order.shipped_at,
    estimated_delivery: order.estimated_delivery || '',
    delivery_method: order.delivery_method || 'standard',
    total: order.total || 0,
    payment_method: order.payment_method || 'unknown',
    payment_status: (order as any).payment_status || (order as any).paymentStatus || 'pending'
  };
  
  // Initialize tracking form with order data
  trackingForm.value = {
    trackingNumber: order.tracking_number || '',
    shippingNotes: order.notes || ''
  };
  
  selectedOrder.value = orderWithDefaults;
  showTrackingModal.value = true;
};

const closeTrackingModal = () => {
  showTrackingModal.value = false;
  trackingForm.value = {
    trackingNumber: '',
    shippingNotes: ''
  };
  newShippingStatus.value = '';
  selectedOrder.value = null;
};

const closeShippingModal = () => {
  showShippingModal.value = false;
  selectedOrder.value = null;
};

const closeOrderDetailsModal = () => {
  showOrderDetailsModal.value = false;
  selectedOrder.value = null;
};

const openPaymentVerificationModal = (order: Order) => {
  selectedOrder.value = { ...order, payment_status: (order as any).payment_status || (order as any).paymentStatus || 'pending' };
  // Initialize select with current payment status or general status
  selectedPaymentStatus.value = order.payment_status || order.status || 'pending';
  showPaymentVerificationModal.value = true;
};

const closePaymentVerificationModal = () => {
  showPaymentVerificationModal.value = false;
  selectedOrder.value = null;
  verificationNotes.value = '';
  selectedPaymentStatus.value = 'pending';
};

const updatePaymentStatus = async () => {
  if (!selectedOrder.value) return;
  
  try {
    loading.value = true;
    await ordersApi.updateOrderPaymentStatus(selectedOrder.value.order_id, {
      status: selectedPaymentStatus.value,
      adminNotes: verificationNotes.value
    });
    
    await loadOrders();
    updateSelectedOrder();
    
    // Dynamic success message based on selected status
    const statusMessages: Record<string, string> = {
      'pending': 'Estado cambiado a pendiente',
      'paid': 'Pedido marcado como pagado',
      'cancelled': 'Pedido cancelado'
    };

    toast.success(statusMessages[selectedPaymentStatus.value] || 'Estado actualizado');
    closePaymentVerificationModal();
  } catch (error) {
    toast.error('Error al actualizar el estado del pago');
  } finally {
    loading.value = false;
  }
};


const viewOrderDetails = (order: Order) => {
  selectedOrder.value = { ...order };
  showOrderDetailsModal.value = true;
};

// Save tracking information and status
const saveTrackingInfo = async () => {
  if (!selectedOrder.value) return;
  
  try {
    trackingLoading.value = true;
    
    // If admin provided both a manual shipping status and a tracking number,
    // clarify precedence: we'll apply the tracking update first and then
    // the manual shipping status so the explicit choice by the admin takes
    // final precedence when both are sent together.
    if (trackingForm.value.trackingNumber || trackingForm.value.shippingNotes) {
      const shippingData = {
        trackingNumber: trackingForm.value.trackingNumber,
        // Include provider when available to satisfy API typing
        shippingProvider: (selectedOrder.value as any)?.shipping_provider || (selectedOrder.value as any)?.provider_name || '',
        shippingNotes: trackingForm.value.shippingNotes
      };
      await ordersApi.updateOrderShipping(selectedOrder.value.order_id, shippingData);
    }

    // Finally, update shipping status if changed (apply last so admin explicit choice wins)
    if (newShippingStatus.value) {
      await ordersApi.updateOrderShippingStatus(selectedOrder.value.order_id, newShippingStatus.value);
    }

    // Small delay to ensure backend has processed the update
    await new Promise(resolve => setTimeout(resolve, 500));
    await loadOrders();
    updateSelectedOrder();
    
    showTrackingModal.value = false;
    
    // Show appropriate message based on what was updated
    if (newShippingStatus.value && trackingForm.value.trackingNumber) {
      const statusMessages: Record<string, string> = {
        'pending': 'Pendiente',
        'prepared': 'Preparado', 
        'shipped': 'Enviado'
      };
      toast.success(`Estado cambiado a ${statusMessages[newShippingStatus.value] || newShippingStatus.value} y tracking agregado`);
    } else if (newShippingStatus.value) {
      const statusMessages: Record<string, string> = {
        'pending': 'Estado cambiado a Pendiente',
        'prepared': 'Estado cambiado a Preparado',
        'shipped': 'Estado cambiado a Enviado'
      };
      toast.success(statusMessages[newShippingStatus.value] || `Estado cambiado a ${newShippingStatus.value}`);
    } else if (trackingForm.value.trackingNumber) {
      toast.success('Número de seguimiento agregado - El pedido ahora está marcado como enviado');
    } else {
      toast.success('Información de envío actualizada');
    }
    
    // Reset form
    trackingForm.value = {
      trackingNumber: '',
      shippingNotes: ''
    };
    newShippingStatus.value = '';
  } catch (error) {
    toast.error('Error al guardar la información de envío');
  } finally {
    trackingLoading.value = false;
  }
};

// Coordinate pickup for an order
const coordinatePickup = async (order: Order) => {
  try {
    loading.value = true;
    await ordersApi.updateOrderShippingStatus(order.order_id, 'ready_for_pickup');
    await loadOrders();
    toast.success('Pedido listo para recogida. Se notificará al cliente.');
  } catch (error) {
    toast.error('Error al coordinar la recogida');
  } finally {
    loading.value = false;
  }
};

const markAsShipped = async (order: Order | number) => {
  const orderId = typeof order === 'number' ? order : order.order_id;
  
  try {
    loading.value = true;
    await ordersApi.updateOrderShippingStatus(orderId, 'shipped');
    await loadOrders();
    toast.success('Pedido marcado como enviado');
  } catch (error) {
    toast.error('Error al marcar el pedido como enviado');
  } finally {
    loading.value = false;
  }
};

const updateOrderStatus = async (orderId: number, status: string, notes: string = '') => {
  try {
    loading.value = true;
    await ordersApi.updateOrderStatus(orderId, { status, adminNotes: notes });
    await loadOrders();
    toast.success('Estado del pedido actualizado');
  } catch (error) {
    toast.error('Error al actualizar el estado del pedido');
  } finally {
    loading.value = false;
  }
};

// Order actions
const toggleSelectAll = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.checked) {
    // Seleccionar todos los pedidos visibles
    const newSelected = new Set(selectedOrders.value);
    filteredOrders.value.forEach((order: Order) => newSelected.add(order.order_id));
    selectedOrders.value = Array.from(newSelected);
  } else {
    // Deseleccionar solo los pedidos visibles
    const visibleOrderIds = new Set(filteredOrders.value.map((o: Order) => o.order_id));
    selectedOrders.value = selectedOrders.value.filter(id => !visibleOrderIds.has(id));
  }
  updateSelectAllState();
};

// Actualizar el estado del checkbox de selección múltiple
const updateSelectAllState = () => {
  if (filteredOrders.value.length === 0) {
    selectAll.value = false;
    return;
  }
  
  // Verificar si todos los pedidos visibles están seleccionados
  const allSelected = filteredOrders.value.every((order: Order) => 
    selectedOrders.value.includes(order.order_id)
  );
  
  selectAll.value = allSelected;
};

// Alternar selección de una fila individual
const toggleRowSelection = (orderId: number, isChecked: boolean) => {
  if (isChecked) {
    if (!selectedOrders.value.includes(orderId)) {
      selectedOrders.value = [...selectedOrders.value, orderId];
    }
  } else {
    selectedOrders.value = selectedOrders.value.filter(id => id !== orderId);
  }
  updateSelectAllState();
};

const bulkMarkShipped = async () => {
  if (selectedOrders.value.length === 0) return;
  
  try {
    loading.value = true;
    await ordersApi.bulkMarkAsShipped(selectedOrders.value);
    await loadOrders();
    selectedOrders.value = [];
    selectAll.value = false;
    toast.success('Pedidos marcados como enviados correctamente');
  } catch (error) {
    toast.error('Error al actualizar los pedidos');
  } finally {
    loading.value = false;
  }
};

const loadOrders = async () => {
  try {
    loading.value = true;
    const response = await ordersApi.getOrdersWithCustomerInfo();
    
    // Guardar todos los pedidos
    allOrders.value = response.map((order: any): Order => {
      // Preserve original internal status and prefer backend-provided `shipping_status` when present
      const origStatus = order.status || 'pending';
      const normShippingStatus = order.shipping_status || origStatus;

      return {
        order_id: Number(order.order_id || order.id) || 0,
        // Keep the original order.status as-is (internal status)
        status: origStatus,
        // Keep payment_status explicit
        payment_status: order.payment_status || 'pending',
        // Expose shipping_status separately (preferred for shipping UI)
        shipping_status: normShippingStatus,
        customer_name: order.customer?.name || order.customer_name || 'Cliente no encontrado',
        customer_email: order.customer?.email || order.customer_email || '',
        shipping_address: order.shipping_address || '',
        total: Number(order.total) || 0,
        payment_method: order.payment_method || 'credit_card',
        created_at: order.created_at || new Date().toISOString(),
        customer_phone: toStringOrNull(order.customer?.phone || order.customer_phone),
        tracking_number: toStringOrNull(order.tracking_number),
        shipping_provider: toStringOrNull(order.shipping_provider),
        provider_name: toStringOrNull(order.provider_name),
        notes: toStringOrNull(order.notes),
        shipped_at: order.shipped_at || undefined,
        estimated_delivery: order.estimated_delivery || undefined,
        delivery_method: order.delivery_method || undefined,
        // Use normalized shipping status when deciding allowed actions
        can_add_tracking: Boolean(order.can_add_tracking) || (normShippingStatus === 'preparing' || normShippingStatus === 'ready_to_ship'),
        can_mark_shipped: Boolean(order.can_mark_shipped) || (normShippingStatus === 'ready_to_ship' || Boolean(order.tracking_number)),
        can_coordinate_pickup: Boolean(order.can_coordinate_pickup) || (order.delivery_method === 'local_pickup' && order.payment_status === 'approved'),
        // IMPORTANTE: Preservar el objeto customer completo con fallbacks
        customer: order.customer ? {
          ...order.customer,
          name: order.customer.name || order.customer_name,
          email: order.customer.email || order.customer_email,
          phone: order.customer.phone || order.customer_phone,
          address: order.customer.address || order.shipping_address
        } : {
          name: order.customer_name || '',
          email: order.customer_email || '',
          phone: order.customer_phone || '',
          address: order.shipping_address || ''
        }
      };
    });
    
  } catch (error: any) {
    toast.error('Error al cargar los pedidos');
    allOrders.value = [];
  } finally {
    loading.value = false;
  }
};

const updateOrderShipping = async (orderId: number, shippingData: any) => {
  try {
    await ordersApi.updateOrderShipping(orderId, shippingData);
    
    toast.success('Información de envío actualizada exitosamente');
    closeShippingModal();
    await loadOrders();
  } catch (error) {
    toast.error('Error al actualizar la información de envío');
  }
};

// Load statistics
const loadStatistics = async () => {
  try {
    // Fallback to default stats if API call fails
    statistics.value = {
      pending_shipment: 0,
      shipped: 0,
      delivered: 0,
      total: 0
    };
  } catch (error) {
  }
};


// Delete selected orders
const deleteSelectedOrders = async () => {
  if (selectedOrders.value.length === 0) {
    toast.warning('Por favor selecciona al menos un pedido para eliminar');
    return;
  }

  if (!confirm(`¿Estás seguro de que quieres eliminar ${selectedOrders.value.length} pedido(s)?`)) {
    return;
  }

  try {
    loading.value = true;
    await Promise.all(selectedOrders.value.map(id => ordersApi.deleteOrder(id)));
    toast.success('Pedidos eliminados exitosamente');
    selectedOrders.value = [];
    selectAll.value = false;
    await loadOrders();
  } catch (error) {
    toast.error('Error al eliminar pedidos');
  } finally {
    loading.value = false;
  }
};

// Delete individual order
const deleteIndividualOrder = async (orderId: number) => {
  if (!confirm('¿Estás seguro de que quieres eliminar este pedido?')) {
    return;
  }

  try {
    loading.value = true;
    await ordersApi.deleteOrder(orderId);
    toast.success('Pedido eliminado exitosamente');
    await loadOrders();
  } catch (error) {
    toast.error('Error al eliminar pedido');
  } finally {
    loading.value = false;
  }
};

// Initialize
onMounted(async () => {
  
  // Check admin access
  if (!authStore.hasAdminAccess) {
    toast.error('No tienes permisos para acceder a esta página');
    router.push('/');
    return;
  }
  
  try {
    await Promise.all([
      loadOrders(),
      loadStatistics()
    ]);
  } catch (error) {
  } finally {
    loading.value = false;
  }
});
</script>
