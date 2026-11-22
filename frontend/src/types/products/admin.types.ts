// Admin-specific interfaces for product management

export interface AdminProductVariant {
  id?: number;
  color: string | null;
  talle: string | null;
  stock: number;
}

export interface AdminProductImage {
  id: number;
  image_url: string;
}

export interface AdminProduct {
  id?: number;
  name: string;
  description: string | null;
  price: number;
  genero: string;
  estado: string;
  categoria?: string | null;
  is_unique: boolean;
  color?: string | null;
  talle?: string | null;
  stock?: number | null;
  has_discount: boolean;
  discount_percentage?: number | null;
  max_installments?: number;
  images: AdminProductImage[];
  variants: AdminProductVariant[];
}

export interface AdminProductCreate {
  name: string;
  description: string | null;
  price: number;
  genero: string;
  estado: string;
  categoria?: string | null;
  is_unique: boolean;
  color?: string | null;
  talle?: string | null;
  stock?: number | null;
  has_discount: boolean;
  discount_percentage?: number | null;
  max_installments?: number;
  images: string[];
  variants: Omit<AdminProductVariant, 'id'>[];
}