import { defineStore } from 'pinia';
import type {
  Product,
  ProductVariant,
  ColorType as Color,
  SizeType as Size
} from '../types/products';
import { useCartNotification } from '../composables/useCartNotification';
import { stockService } from '../services/stockService';
import type { StockCheckItem, StockCheckResponse } from '../types/stock';
import { useToast } from 'vue-toastification';

export interface CartItem {
  id: string; // Unique identifier for cart item
  product: Product;
  variant?: {
    variant: ProductVariant;
    color: Color;
    size: Size;
  };
  quantity: number;
  selectedColor?: Color; // For unique products
  selectedSize?: Size; // For unique products
}

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [] as CartItem[],
    lastSaved: null as number | null, // Timestamp when cart was last saved
    sessionTimeout: 60 * 60 * 1000, // 60 minutes in milliseconds (increased from 20 min)
  }),

  getters: {
    // Calculate total price considering discounts
    totalPrice: (state) => {
      return state.items.reduce((total, item) => {
        const price = item.product.has_discount && item.product.discounted_price
          ? item.product.discounted_price
          : item.product.price;
        return total + (price * item.quantity);
      }, 0);
    },

    // Calculate total price without discounts
    totalOriginalPrice: (state) => {
      return state.items.reduce((total, item) => total + (item.product.price * item.quantity), 0);
    },

    // Calculate total savings
    totalSavings: (state) => {
      return state.items.reduce((total, item) => {
        if (item.product.has_discount && item.product.discount_amount) {
          return total + (item.product.discount_amount * item.quantity);
        }
        return total;
      }, 0);
    },

    // Calculate average discount percentage across all items
    averageDiscountPercentage: (state) => {
      const discountedItems = state.items.filter(item => item.product.has_discount && item.product.discount_amount);
      if (discountedItems.length === 0) return 0;

      const totalOriginal = discountedItems.reduce((total, item) => total + (item.product.price * item.quantity), 0);
      const totalSavings = discountedItems.reduce((total, item) => {
        if (item.product.discount_amount) {
          return total + (item.product.discount_amount * item.quantity);
        }
        return total;
      }, 0);

      return totalOriginal > 0 ? Math.round((totalSavings / totalOriginal) * 100) : 0;
    },

    itemCount: (state) => {
      return state.items.reduce((total, item) => total + item.quantity, 0);
    },

    // Check if cart is empty
    isEmpty: (state) => state.items.length === 0,

    // Get items with discount
    discountedItems: (state) => {
      return state.items.filter(item => item.product.has_discount);
    },

    // Calculate total weight for shipping quotes (estimated weight per item: 0.5kg for clothing)
    totalWeight: (state) => {
      const estimatedWeightPerItem = 0.5; // kg - average weight for vintage clothing items
      return state.items.reduce((total, item) => total + (estimatedWeightPerItem * item.quantity), 0);
    }
  },

  actions: {
    // Generate unique ID for cart item
    generateCartItemId(product: Product, variantId?: number, colorId?: number, sizeId?: number): string {
      if (product.is_unique) {
        return `${product.id}-${colorId || 'no-color'}-${sizeId || 'no-size'}`;
      } else {
        return `${product.id}-variant-${variantId}`;
      }
    },

    addToCart(
      product: Product,
      quantity: number = 1,
      variantInfo?: { variant: ProductVariant; color: Color; size: Size },
      uniqueProductInfo?: { color?: Color; size?: Size }
    ) {
      // Check session validity before adding
      if (!this.isSessionValid()) {
        this.clearCart();
      }
      let cartItemId: string;

      if (product.is_unique) {
        // For unique products, use color and size if provided
        cartItemId = this.generateCartItemId(
          product,
          undefined,
          uniqueProductInfo?.color?.id,
          uniqueProductInfo?.size?.id
        );
      } else {
        // For variant products, use variant ID
        if (!variantInfo) {
          throw new Error('Variant information is required for non-unique products');
        }
        cartItemId = this.generateCartItemId(product, variantInfo.variant.id);
      }

      // Check if item already exists in cart
      const existingItemIndex = this.items.findIndex(item => item.id === cartItemId);

      if (existingItemIndex >= 0) {
        // Update quantity of existing item instead of incrementing
        this.items[existingItemIndex].quantity = quantity;
      } else {
        // Add new item to cart
        const newItem: CartItem = {
          id: cartItemId,
          product,
          quantity,
          variant: variantInfo,
          selectedColor: uniqueProductInfo?.color,
          selectedSize: uniqueProductInfo?.size
        };

        this.items.push(newItem);
      }

      // Save to localStorage
      this.saveToStorage();

      // Mostrar notificacin personalizada cuando se agrega producto
      const { showNotification } = useCartNotification();
      if (variantInfo) {
        showNotification(product, quantity, variantInfo);
      } else {
        showNotification(product, quantity);
      }
    },

    removeFromCart(cartItemId: string) {
      this.items = this.items.filter(item => item.id !== cartItemId);
      this.saveToStorage();
    },

    updateQuantity(cartItemId: string, quantity: number) {
      const itemIndex = this.items.findIndex(item => item.id === cartItemId);

      if (itemIndex >= 0) {
        if (quantity <= 0) {
          this.items.splice(itemIndex, 1);
        } else {
          this.items[itemIndex].quantity = quantity;
        }
        this.saveToStorage();
      }
    },

    clearCart() {
      this.items = [];
      this.saveToStorage();
    },

    // Persistence methods
    saveToStorage() {
      if (typeof window !== 'undefined') {
        const cartData = {
          items: this.items,
          timestamp: Date.now()
        };
        localStorage.setItem('cart', JSON.stringify(cartData));
        this.lastSaved = Date.now();
      }
    },

    loadFromStorage() {
      if (typeof window !== 'undefined') {
        const saved = localStorage.getItem('cart');
        if (saved) {
          try {
            const cartData = JSON.parse(saved);

            // Handle legacy format (just items array)
            if (Array.isArray(cartData)) {
              this.items = this.validateCartItems(cartData);
              this.saveToStorage(); // Save in new format
              return;
            }

            // Handle new format with timestamp
            if (cartData && typeof cartData === 'object' && cartData.items) {
              const now = Date.now();
              const timeDiff = now - (cartData.timestamp || 0);

              // Check if cart has expired (60 minutes)
              if (timeDiff > this.sessionTimeout) {
                this.clearStorage();
                this.items = [];
                return;
              }

              // Load valid cart
              this.items = this.validateCartItems(cartData.items);
              this.lastSaved = cartData.timestamp;

              // If we filtered out invalid items, save the cleaned cart
              if (this.items.length !== cartData.items.length) {
                this.saveToStorage();
              }
            } else {
              this.clearStorage();
              this.items = [];
            }
          } catch (error) {
            this.clearStorage();
            this.items = [];
          }
        } else {
          this.items = [];
        }
      }
    },

    // Validate stock availability by checking with the backend
    async validateStock() {
      if (this.items.length === 0) return { hasStockIssues: false };

      // Prepare items for stock check
      const stockCheckItems: StockCheckItem[] = this.items.map(item => ({
        product_id: item.product.id,
        variant_id: item.variant?.variant.id,
        quantity: item.quantity
      }));

      try {
        // Check stock with backend
        const response = await stockService.checkStock(stockCheckItems);

        const itemsToRemove: string[] = [];
        let hasStockIssues = false;

        // Process each item in the cart
        this.items.forEach((item, index) => {
          const stockResult = response.items[index];

          if (!stockResult.available) {
            // Product is not available at all
            itemsToRemove.push(item.id);
            hasStockIssues = true;
          } else if (!stockResult.has_enough_stock) {
            // Not enough stock for requested quantity
            const availableStock = stockResult.available_stock;
            if (availableStock > 0) {
              // Adjust quantity to available stock
              this.updateQuantity(item.id, availableStock);
              hasStockIssues = true;
            } else {
              // No stock available, remove from cart
              itemsToRemove.push(item.id);
              hasStockIssues = true;
            }
          }

          // Update local stock information
          if (item.product.is_unique) {
            item.product.stock = stockResult.available_stock;
          } else if (item.variant) {
            item.variant.variant.stock = stockResult.available_stock;
          }
        });

        // Remove items with no stock
        itemsToRemove.forEach(itemId => {
          this.removeFromCart(itemId);
        });

        // Show notifications if needed
        if (hasStockIssues && typeof window !== 'undefined') {
          this.showStockNotification(itemsToRemove.length > 0);
        }

        return { hasStockIssues, allAvailable: response.all_available };
      } catch (error) {
        // En caso de error, mostramos un mensaje al usuario
        this.showStockNotification(false, true);
        return { hasStockIssues: true, allAvailable: false, error: true };
      }
    },

    // Show stock notification
    showStockNotification(itemsRemoved: boolean, isError: boolean = false) {
      if (typeof window === 'undefined') return;

      try {
        const toast = useToast();

        if (isError) {
          toast.error('Error al verificar el stock. Por favor, intente nuevamente.');
        } else if (itemsRemoved) {
          toast.warning('Algunos productos fueron removidos del carrito por falta de stock');
        } else {
          toast.info('Se ajustó la cantidad de algunos productos por stock limitado');
        }
      } catch (error) {
        // Stock validation completed with adjustments
      }
    },

    // Get item price (considering discounts)
    getItemPrice(item: CartItem): number {
      return item.product.has_discount && item.product.discounted_price
        ? item.product.discounted_price
        : item.product.price;
    },

    // Get item total price
    getItemTotal(item: CartItem): number {
      return this.getItemPrice(item) * item.quantity;
    },

    // Get item discount percentage
    getItemDiscountPercentage(item: CartItem): number {
      if (!item.product.has_discount || !item.product.discount_amount) {
        return 0;
      }

      return Math.round((item.product.discount_amount / item.product.price) * 100);
    },

    // Get item total savings
    getItemSavings(item: CartItem): number {
      if (!item.product.has_discount || !item.product.discount_amount) {
        return 0;
      }

      return item.product.discount_amount * item.quantity;
    },

    // Debug function to check cart state
    debugCart() {
      // Debug info available in dev tools if needed
    },

    // Validate cart items helper method
    validateCartItems(items: any[]): CartItem[] {
      if (!Array.isArray(items)) return [];

      return items.filter(item =>
        item &&
        typeof item === 'object' &&
        item.id &&
        item.product &&
        typeof item.quantity === 'number' &&
        item.quantity > 0
      );
    },

    // Check if cart session is still valid
    isSessionValid(): boolean {
      if (!this.lastSaved) return true; // No timestamp means fresh session

      const now = Date.now();
      const timeDiff = now - this.lastSaved;
      return timeDiff <= this.sessionTimeout;
    },

    // Clear localStorage cart data
    clearStorage() {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('cart');
        this.lastSaved = null;
      }
    },

    // Initialize cart - call this on app startup
    initializeCart() {
      this.loadFromStorage();

      // Set up periodic session validation (every 10 minutes)
      if (typeof window !== 'undefined') {
        setInterval(() => {
          if (!this.isSessionValid() && !this.isEmpty) {
            this.clearCart();
          }
        }, 10 * 60 * 1000); // Check every 10 minutes (reduced frequency)
      }
    }
  },
});
