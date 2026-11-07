<template>
  <div class="min-h-screen bg-gray-50">
    <div class="px-4 py-8 mx-auto max-w-7xl sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 font-heading">Gestin de Pagos</h1>
        <p class="mt-2 text-sm font-body text-body-text">
          Administra verificaciones de transferencias, entregas y estados de pago
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
            class="px-1 py-4 text-sm font-medium text-gray-900 border-b-2 border-transparent border-black whitespace-nowrap"
          >
            <span class="font-body">Pedidos</span>
          </router-link>
        </nav>
      </div>

      <!-- Statistics Cards -->
      <div v-if="stats" class="grid grid-cols-1 gap-6 mb-8 md:grid-cols-2 lg:grid-cols-4">
        <div class="overflow-hidden bg-white rounded-lg shadow">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="w-6 h-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="flex-1 w-0 ml-5">
                <dl>
                  <dt class="text-sm font-medium truncate font-body text-body-text">Pendientes de verificacin</dt>
                  <dd class="text-lg font-medium font-body text-body-text">{{ stats.pending_verification }}</dd>
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
                  <dt class="text-sm font-medium truncate font-body text-body-text">Entregas pendientes</dt>
                  <dd class="text-lg font-medium font-body text-body-text">{{ stats.pending_delivery }}</dd>
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3a4 4 0 118 0v4m-4 12v-7" />
                </svg>
              </div>
              <div class="flex-1 w-0 ml-5">
                <dl>
                  <dt class="text-sm font-medium truncate font-body text-body-text">Entregas programadas</dt>
                  <dd class="text-lg font-medium font-body text-body-text">{{ stats.scheduled_delivery }}</dd>
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <div class="flex-1 w-0 ml-5">
                <dl>
                  <dt class="text-sm font-medium truncate font-body text-body-text">Monto pendiente</dt>
                  <dd class="text-lg font-medium font-body text-body-text">${{ stats.total_pending_amount.toLocaleString() }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="p-6 mb-6 bg-white rounded-lg shadow">
        <h2 class="mb-4 text-lg font-medium text-gray-900 font-heading">Filtros</h2>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div>
            <label for="paymentMethod" class="block text-sm font-medium font-body text-body-text">MÃ©todo de pago</label>
            <select
              v-model="filters.payment_method"
              id="paymentMethod"
              @change="loadOrders"
              class="block w-full px-3 py-2 mt-1 border border-gray-300 rounded-md shadow-sm focus:border-black focus:ring-black"
            >
              <option class="font-body" value="">Todos</option>
              <option class="font-body" value="transfer">Transferencia</option>
              <option class="font-body" value="mercadopago">MercadoPago</option>
              <option class="font-body" value="cash">Efectivo</option>
            </select>
          </div>

          <div>
            <label for="paymentStatus" class="block text-sm font-medium font-body text-body-text">Estado del pago</label>
            <select
              v-model="filters.payment_status"
              id="paymentStatus"
              @change="loadOrders"
              class="block w-full px-3 py-2 mt-1 border border-gray-300 rounded-md shadow-sm focus:border-black focus:ring-black"
            >
              <option class="font-body" value="">Todos</option>
              <option class="font-body" value="pending">Pendiente</option>
              <option class="font-body" value="pending_payment">Pendiente de pago</option>
              <option class="font-body" value="approved">Aprobado</option>
              <option class="font-body" value="rejected">Rechazado</option>
            </select>
          </div>

          <div>
            <label for="verificationRequired" class="block text-sm font-medium font-body text-body-text">Verificacin</label>
            <select
              v-model="filters.verification_required"
              id="verificationRequired"
              @change="loadOrders"
              class="block w-full px-3 py-2 mt-1 border border-gray-300 rounded-md shadow-sm focus:border-black focus:ring-black"
            >
              <option class="font-body" value="">Todos</option>
              <option class="font-body" value="true">Requiere verificacin</option>
              <option class="font-body" value="false">No requiere verificacin</option>
            </select>
          </div>

          <div>
            <label for="deliveryStatus" class="block text-sm font-medium font-body text-body-text">Estado de entrega</label>
            <select
              v-model="filters.delivery_status"
              id="deliveryStatus"
              @change="loadOrders"
              class="block w-full px-3 py-2 mt-1 border border-gray-300 rounded-md shadow-sm focus:border-black focus:ring-black"
            >
              <option class="font-body" value="">Todos</option>
              <option class="font-body" value="pending">Pendiente</option>
              <option class="font-body" value="scheduled">Programada</option>
              <option class="font-body" value="delivered">Entregada</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Orders Table -->
      <div class="overflow-hidden bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-medium text-gray-900 font-heading">Ã“rdenes</h2>
            <button
              @click="loadOrders"
              :disabled="loading"
              class="btn-outline"
            >
              <svg v-if="loading" class="w-4 h-4 mr-2 -ml-1 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="font-body">{{ loading ? 'Cargando...' : 'Actualizar' }}</span>
            </button>
          </div>
        </div>

        <div v-if="orders.length === 0 && !loading" class="px-6 py-12 text-center">
          <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900 font-heading">No hay rdenes</h3>
          <p class="mt-1 text-sm font-body text-body-text">No se encontraron rdenes con los filtros seleccionados.</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase font-heading">Orden</th>
                <th class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase font-heading">Cliente</th>
                <th class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase font-heading">Total</th>
                <th class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase font-heading">MÃ©todo</th>
                <th class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase font-heading">Estado</th>
                <th class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase font-heading">Fecha</th>
                <th class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase font-heading">Acciones</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="order in orders" :key="order.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium font-body text-body-text">#{{ order.id }}</div>
                  <div v-if="order.verification_required" class="text-xs text-orange-600 font-body">
                    Requiere verificacin
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-body text-body-text">{{ order.customer?.name || 'N/A' }}</div>
                  <div class="text-sm font-body text-body-text">{{ order.customer?.email || 'N/A' }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium font-body text-body-text">${{ order.total?.toLocaleString() }}</div>
                  <div v-if="order.delivery_cost" class="text-xs font-body text-body-text">
                    Envío: ${{ order.delivery_cost.toLocaleString() }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="font-body inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="getPaymentMethodClass(order.payment_method)">
                    {{ getPaymentMethodText(order.payment_method) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="font-body inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="getPaymentStatusClass(order.payment_status || '')">
                    {{ getPaymentStatusText(order.payment_status || '') }}
                  </span>
                  <div v-if="order.delivery_status" class="mt-1">
                    <span class="font-body inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                          :class="getDeliveryStatusClass(order.delivery_status)">
                      {{ getDeliveryStatusText(order.delivery_status) }}
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 whitespace-nowrap">
                  <span class="font-body">{{ formatDate(order.created_at) }}</span>
                </td>
                <td class="px-6 py-4 space-x-2 text-sm font-medium whitespace-nowrap">
                  <!-- Transfer Actions -->
                  <button
                    v-if="order.payment_method === 'transfer' && !order.transfer_verified"
                    @click="openTransferModal(order)"
                    class="btn-blue btn-sm"
                  >
                    <span class="font-body">Verificar</span>
                  </button>
                  
                  <!-- Cash Delivery Actions -->
                  <button
                    v-if="order.payment_method === 'cash' && order.delivery_status === 'pending'"
                    @click="openDeliveryModal(order)"
                    class="btn-green btn-sm"
                  >
                    <span class="font-body">Programar</span>
                  </button>
                  
                  <button
                    v-if="order.payment_method === 'cash' && order.delivery_status === 'scheduled'"
                    @click="markAsDelivered(order)"
                    class="btn-purple btn-sm"
                  >
                    <span class="font-body">Entregado</span>
                  </button>
                  
                  <!-- View Details -->
                  <button
                    @click="openOrderModal(order)"
                    class="btn-primary btn-sm"
                  >
                    <span class="font-body">Ver</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Transfer Verification Modal -->
    <div v-if="showTransferModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-600 bg-opacity-50">
      <div class="w-full max-w-md p-6 bg-white rounded-lg">
        <h3 class="mb-4 text-lg font-medium text-gray-900 font-heading">Verificar Transferencia</h3>
        <div class="space-y-4">
          <div>
            <p class="mb-2 text-sm font-body text-body-text">Orden #{{ selectedOrder?.id }}</p>
            <p class="mb-2 text-sm font-body text-body-text">Total: ${{ selectedOrder?.total?.toLocaleString() }}</p>
            <p class="mb-4 text-sm font-body text-body-text">Cliente: {{ selectedOrder?.customer?.name }}</p>
          </div>
          
          <div>
            <label for="adminNotes" class="block text-sm font-medium font-body text-body-text">Notas de verificacin</label>
            <textarea
              v-model="transferForm.admin_notes"
              id="adminNotes"
              rows="3"
              class="block w-full px-3 py-2 mt-1 border border-gray-300 rounded-md shadow-sm focus:border-black focus:ring-black"
              placeholder="Detalles de la verificacin..."
            ></textarea>
          </div>
          
          <div class="flex space-x-3">
            <button
              @click="verifyTransfer(true)"
              :disabled="processingTransfer"
              class="flex-1 px-4 py-2 font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:bg-gray-400"
            >
              <span class="font-body">Aprobar</span>
            </button>
            <button
              @click="verifyTransfer(false)"
              :disabled="processingTransfer"
              class="flex-1 px-4 py-2 font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:bg-gray-400"
            >
              <span class="font-body">Rechazar</span>
            </button>
          </div>
          
          <button
            @click="closeTransferModal"
            class="w-full px-4 py-2 font-medium text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            <span class="font-body">Cancelar</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Delivery Scheduling Modal -->
    <div v-if="showDeliveryModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-600 bg-opacity-50">
      <div class="w-full max-w-md p-6 bg-white rounded-lg">
        <h3 class="mb-4 text-lg font-medium text-gray-900 font-heading">Programar Entrega</h3>
        <div class="space-y-4">
          <div>
            <p class="mb-2 text-sm font-body text-body-text">Orden #{{ selectedOrder?.id }}</p>
            <p class="mb-2 text-sm font-body text-body-text">Total: ${{ selectedOrder?.total?.toLocaleString() }}</p>
            <p class="mb-4 text-sm font-body text-body-text">{{ formatCustomerAddress(selectedOrder?.customer) }}</p>
          </div>
          
          <div>
            <label for="scheduledDate" class="block text-sm font-medium font-body text-body-text">Fecha de entrega</label>
            <input
              v-model="deliveryForm.scheduled_date"
              type="date"
              id="scheduledDate"
              :min="tomorrow"
              required
              class="block w-full px-3 py-2 mt-1 border border-gray-300 rounded-md shadow-sm focus:border-black focus:ring-black"
            >
          </div>
          
          <div>
            <label for="timeSlot" class="block text-sm font-medium font-body text-body-text">Horario</label>
            <select
              v-model="deliveryForm.time_slot"
              id="timeSlot"
              required
              class="block w-full px-3 py-2 mt-1 border border-gray-300 rounded-md shadow-sm focus:border-black focus:ring-black"
            >
              <option class="font-body" value="maÃ±ana">MaÃ±ana (9:00 - 13:00)</option>
              <option class="font-body" value="tarde">Tarde (14:00 - 18:00)</option>
              <option class="font-body" value="noche">Noche (18:00 - 21:00)</option>
            </select>
          </div>
          
          <div>
            <label for="deliveryNotes" class="block text-sm font-medium font-body text-body-text">Notas para el delivery</label>
            <textarea
              v-model="deliveryForm.notes"
              id="deliveryNotes"
              rows="2"
              class="block w-full px-3 py-2 mt-1 border border-gray-300 rounded-md shadow-sm focus:border-black focus:ring-black"
              placeholder="Instrucciones especiales..."
            ></textarea>
          </div>
          
          <div class="flex space-x-3">
            <button
              @click="scheduleDelivery"
              :disabled="processingDelivery || !deliveryForm.scheduled_date || !deliveryForm.time_slot"
              class="flex-1 px-4 py-2 font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
            >
              <span class="font-body">Programar</span>
            </button>
            <button
              @click="closeDeliveryModal"
              class="flex-1 px-4 py-2 font-medium text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <span class="font-body">Cancelar</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Order Details Modal -->
    <div v-if="showOrderModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-600 bg-opacity-50">
      <div class="w-full max-w-2xl p-6 overflow-y-auto bg-white rounded-lg max-h-96">
        <h3 class="mb-4 text-lg font-medium text-gray-900 font-heading">Detalles de la Orden #{{ selectedOrder?.id }}</h3>
        <div v-if="selectedOrder" class="space-y-4">
          <!-- Order Info -->
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div class="font-body"><strong>Cliente:</strong> {{ selectedOrder.customer?.name }}</div>
            <div class="font-body"><strong>Email:</strong> {{ selectedOrder.customer?.email }}</div>
            <div class="font-body"><strong>TelÃ©fono:</strong> {{ selectedOrder.customer?.phone }}</div>
            <div class="font-body"><strong>Total:</strong> ${{ selectedOrder.total?.toLocaleString() }}</div>
            <div class="font-body"><strong>MÃ©todo:</strong> {{ getPaymentMethodText(selectedOrder.payment_method) }}</div>
            <div class="font-body"><strong>Estado:</strong> {{ getPaymentStatusText(selectedOrder.payment_status || '') }}</div>
          </div>
          
          <!-- Address Info -->
          <div v-if="selectedOrder.customer" class="pt-4 border-t">
            <h4 class="mb-2 font-medium font-heading">Direccin de entrega</h4>
            <p class="text-sm font-body text-body-text">{{ formatCustomerAddress(selectedOrder.customer) }}</p>
            <div v-if="selectedOrder.customer.address_reference" class="mt-1 text-sm font-body text-body-text">
              <strong>Ref:</strong> {{ selectedOrder.customer.address_reference }}
            </div>
            <div v-if="selectedOrder.customer.delivery_notes" class="mt-1 text-sm font-body text-body-text">
              <strong>Notas:</strong> {{ selectedOrder.customer.delivery_notes }}
            </div>
          </div>
          
          <!-- Admin Notes -->
          <div v-if="selectedOrder.admin_notes" class="pt-4 border-t">
            <h4 class="mb-2 font-medium font-heading">Notas del administrador</h4>
            <p class="text-sm font-body text-body-text">{{ selectedOrder.admin_notes }}</p>
          </div>
        </div>
        
        <div class="mt-6">
          <button
            @click="closeOrderModal"
            class="w-full px-4 py-2 font-medium text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            <span class="font-body">Cerrar</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'vue-toastification';
import { ordersApi } from '../../config/api';
import type { Order, AdminOrderFilters, AdminStats } from '../../types';

const toast = useToast();

// State
const loading = ref(false);
const orders = ref<Order[]>([]);
const stats = ref<AdminStats | null>(null);

// Filters
const filters = ref<AdminOrderFilters>({
  payment_method: '',
  payment_status: '',
  verification_required: '',
  delivery_status: ''
});

// Modals
const showTransferModal = ref(false);
const showDeliveryModal = ref(false);
const showOrderModal = ref(false);
const selectedOrder = ref<Order | null>(null);

// Form data
const transferForm = ref({
  admin_notes: ''
});

const deliveryForm = ref({
  scheduled_date: '',
  time_slot: 'maÃ±ana',
  notes: ''
});

// Processing states
const processingTransfer = ref(false);
const processingDelivery = ref(false);

// Computed
const tomorrow = computed(() => {
  const date = new Date();
  date.setDate(date.getDate() + 1);
  return date.toISOString().split('T')[0];
});

// Methods
const loadOrders = async () => {
  loading.value = true;
  try {
    // Convert filter values
    const processedFilters = { ...filters.value };
    if (processedFilters.verification_required === 'true') {
      processedFilters.verification_required = true;
    } else if (processedFilters.verification_required === 'false') {
      processedFilters.verification_required = false;
    } else {
      delete processedFilters.verification_required;
    }
    
    orders.value = await ordersApi.getOrdersWithFilters(processedFilters);
  } catch (error) {
    toast.error('Error cargando rdenes');
  } finally {
    loading.value = false;
  }
};

const loadStats = async () => {
  try {
    stats.value = await ordersApi.getAdminStats();
  } catch (error) {
  }
};

// Transfer verification
const openTransferModal = (order: Order) => {
  selectedOrder.value = order;
  transferForm.value.admin_notes = '';
  showTransferModal.value = true;
};

const closeTransferModal = () => {
  showTransferModal.value = false;
  selectedOrder.value = null;
  transferForm.value.admin_notes = '';
};

const verifyTransfer = async (verified: boolean) => {
  if (!selectedOrder.value) return;
  
  processingTransfer.value = true;
  try {
    await ordersApi.verifyTransfer(
      selectedOrder.value.id,
      verified,
      transferForm.value.admin_notes
    );
    
    toast.success(verified ? 'Transferencia aprobada' : 'Transferencia rechazada');
    closeTransferModal();
    await loadOrders();
    await loadStats();
  } catch (error) {
    toast.error('Error verificando transferencia');
  } finally {
    processingTransfer.value = false;
  }
};

// Delivery scheduling
const openDeliveryModal = (order: Order) => {
  selectedOrder.value = order;
  deliveryForm.value.scheduled_date = '';
  deliveryForm.value.time_slot = order.customer?.preferred_delivery_time || 'maÃ±ana';
  deliveryForm.value.notes = '';
  showDeliveryModal.value = true;
};

const closeDeliveryModal = () => {
  showDeliveryModal.value = false;
  selectedOrder.value = null;
  deliveryForm.value = {
    scheduled_date: '',
    time_slot: 'maÃ±ana',
    notes: ''
  };
};

const scheduleDelivery = async () => {
  if (!selectedOrder.value) return;
  
  processingDelivery.value = true;
  try {
    await ordersApi.scheduleDelivery(
      selectedOrder.value.id,
      new Date(deliveryForm.value.scheduled_date),
      deliveryForm.value.time_slot,
      deliveryForm.value.notes
    );
    
    toast.success('Entrega programada exitosamente');
    closeDeliveryModal();
    await loadOrders();
    await loadStats();
  } catch (error) {
    toast.error('Error programando entrega');
  } finally {
    processingDelivery.value = false;
  }
};

const markAsDelivered = async (order: Order) => {
  if (!confirm('¿Confirmar que la orden ha sido entregada?')) return;
  
  try {
    await ordersApi.markAsDelivered(order.id, 'Entregado por admin');
    toast.success('Orden marcada como entregada');
    await loadOrders();
    await loadStats();
  } catch (error) {
    toast.error('Error marcando como entregada');
  }
};

// Order details modal
const openOrderModal = (order: Order) => {
  selectedOrder.value = order;
  showOrderModal.value = true;
};

const closeOrderModal = () => {
  showOrderModal.value = false;
  selectedOrder.value = null;
};

// Utility functions
const getPaymentMethodText = (method: string) => {
  const map: Record<string, string> = {
    'transfer': 'Transferencia',
    'mercadopago': 'MercadoPago',
    'cash': 'Efectivo'
  };
  return map[method] || method;
};

const getPaymentMethodClass = (method: string) => {
  const map: Record<string, string> = {
    'transfer': 'bg-blue-100 text-blue-800',
    'mercadopago': 'bg-purple-100 text-purple-800',
    'cash': 'bg-green-100 text-green-800'
  };
  return map[method] || 'bg-gray-100 text-gray-800';
};

const getPaymentStatusText = (status: string) => {
  const map: Record<string, string> = {
    'pending': 'Pendiente',
    'pending_payment': 'Pendiente de pago',
    'approved': 'Aprobado',
    'rejected': 'Rechazado',
    'cancelled': 'Cancelado'
  };
  return map[status] || status;
};

const getPaymentStatusClass = (status: string) => {
  const map: Record<string, string> = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'pending_payment': 'bg-orange-100 text-orange-800',
    'approved': 'bg-green-100 text-green-800',
    'rejected': 'bg-red-100 text-red-800',
    'cancelled': 'bg-gray-100 text-gray-800'
  };
  return map[status] || 'bg-gray-100 text-gray-800';
};

const getDeliveryStatusText = (status: string) => {
  const map: Record<string, string> = {
    'pending': 'Pendiente',
    'scheduled': 'Programada',
    'delivered': 'Entregada'
  };
  return map[status] || status;
};

const getDeliveryStatusClass = (status: string) => {
  const map: Record<string, string> = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'scheduled': 'bg-blue-100 text-blue-800',
    'delivered': 'bg-green-100 text-green-800'
  };
  return map[status] || 'bg-gray-100 text-gray-800';
};

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('es-AR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const formatCustomerAddress = (customer: any) => {
  if (!customer) return 'N/A';
  const parts: string[] = [];
  if (customer.address) parts.push(customer.address);
  if (customer.city) parts.push(customer.city);
  if (customer.postal_code) parts.push(`CP ${customer.postal_code}`);
  if (customer.province) parts.push(customer.province);
  return parts.join(', ') || 'Direccin no especificada';
};

// Initialize
onMounted(async () => {
  await Promise.all([loadOrders(), loadStats()]);
});
</script>
