import { productsApi } from '../config/api';
import type { StockCheckItem, StockCheckResponse } from '../types/stock';

export const stockService = {
  /**
   * Verifica el stock de múltiples productos/variantes
   * @param items Array de ítems a verificar
   * @returns Promise con el resultado de la verificación de stock
   */
  async checkStock(items: StockCheckItem[]): Promise<StockCheckResponse> {
    try {
      return await productsApi.checkStock(items);
    } catch (error) {
      // En caso de error, asumimos que no hay stock disponible
      return {
        items: items.map(item => ({
          product_id: item.product_id,
          variant_id: item.variant_id,
          available: false,
          available_stock: 0,
          requested_quantity: item.quantity,
          has_enough_stock: false,
        })),
        all_available: false,
      };
    }
  },
};

export default stockService;
