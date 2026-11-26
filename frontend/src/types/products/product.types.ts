export interface ProductImage {
  id: number;
  image_url: string;
}

export interface ProductVariant {
  id?: number;
  color_id?: number;
  size_id?: number;
  color?: string;
  talle?: string;
  image_url?: string;
  size?: string;
  stock: number;
}

export interface VariantOption {
  id: number | string;
  name: string;
  hex_code?: string;
}

export interface Color {
  id: number;
  name: string;
  hex_code: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
  slug?: string;
  parent_id?: number | null;
  order?: number;
}

export interface Size {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
  numeric_size?: number;  // Añadido para compatibilidad
  order?: number;
  type?: string;
}

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  original_price?: number;
  is_new?: boolean;
  is_sale?: boolean;
  genero?: string;
  estado?: string;
  categoria?: string;
  edad_destino?: string;
  is_unique: boolean;
  color?: string | null;
  talle?: string | null;
  stock?: number | null;
  has_discount: boolean;
  discount_percentage?: number | null;
  promo_label?: string | null;
  discount_starts_at?: string | null;
  discount_ends_at?: string | null;
  discount_active?: boolean;
  max_installments?: number;
  discounted_price?: number;
  discount_amount?: number;
  images: ProductImage[];
  variants: ProductVariant[];
}

// Product creation data
export interface ProductCreateData {
  name: string;
  description: string;
  price: number;
  compare_at_price?: number;
  cost_per_item?: number;
  sku?: string;
  barcode?: string;
  quantity: number;
  is_active: boolean;
  is_featured?: boolean;
  requires_shipping?: boolean;
  weight?: number;
  weight_unit?: string;
  category_id: number;
  images?: File[];
  variants?: Array<{
    color_id: number;
    size_id: number;
    image_url: string;
    stock: number;
    price?: number;
    sku?: string;
    barcode?: string;
  }>;
}

// Product update data
export interface ProductUpdateData extends Partial<Omit<ProductCreateData, 'images' | 'variants'>> {
  images_to_remove?: number[];
  variants_to_remove?: number[];
  variants_to_update?: Array<{
    id?: number;
    color_id: number;
    size_id: number;
    image_url: string;
    stock: number;
    price?: number;
    sku?: string;
    barcode?: string;
  }>;
}
