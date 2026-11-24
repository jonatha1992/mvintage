const arsFormatter = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
  maximumFractionDigits: 0
})

export const MIN_DISCOUNT_PERCENTAGE = 1
export const MAX_DISCOUNT_PERCENTAGE = 90
export const MAX_PROMO_LABEL_LENGTH = 20

export interface DiscountableProduct {
  price: number
  has_discount?: boolean
  discount_percentage?: number | null
  promo_label?: string | null
  discount_starts_at?: string | null
  discount_ends_at?: string | null
  discount_active?: boolean
  discounted_price?: number | null
}

export const formatPrice = (amount?: number | string | null): string =>
  arsFormatter.format(Math.round(Number(amount ?? 0))).replace(/\s/g, '')

export const calculateDiscountedPrice = (price: number, percentage: number): number => {
  if (!Number.isFinite(price) || price <= 0) return 0
  if (!Number.isFinite(percentage) || percentage < MIN_DISCOUNT_PERCENTAGE || percentage > MAX_DISCOUNT_PERCENTAGE) {
    return Math.round(price)
  }
  return Math.round(price * (1 - percentage / 100))
}

export const calculatePercentageFromFinalPrice = (price: number, finalPrice: number): number | null => {
  if (!Number.isFinite(price) || price <= 0 || !Number.isFinite(finalPrice) || finalPrice <= 0 || finalPrice >= price) {
    return null
  }
  const raw = Number((((price - finalPrice) / price) * 100).toFixed(2))
  if (raw < MIN_DISCOUNT_PERCENTAGE || raw > MAX_DISCOUNT_PERCENTAGE) {
    return null
  }
  return raw
}

const parseDiscountDate = (value?: string | null): Date | null => {
  if (!value) return null
  const trimmed = value.trim()
  if (!trimmed) return null
  const hasTimezone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(trimmed)
  const normalized = hasTimezone ? trimmed : `${trimmed}Z`
  const parsed = new Date(normalized)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

export const isProductDiscountActive = (
  product?: DiscountableProduct | null,
  now: Date = new Date()
): boolean => {
  if (!product || !product.has_discount) return false
  if (typeof product.discount_active === 'boolean') return product.discount_active
  const pct = Number(product.discount_percentage)
  if (!Number.isFinite(pct) || pct < MIN_DISCOUNT_PERCENTAGE || pct > MAX_DISCOUNT_PERCENTAGE) {
    return false
  }
  const start = parseDiscountDate(product.discount_starts_at)
  const end = parseDiscountDate(product.discount_ends_at)
  if (start && now.getTime() < start.getTime()) return false
  if (end && now.getTime() > end.getTime()) return false
  return true
}

export const getEffectivePrice = (
  product?: DiscountableProduct | null,
  now: Date = new Date()
): number => {
  if (!product) return 0
  const basePrice = Number(product.price) || 0
  if (!isProductDiscountActive(product, now)) return basePrice
  if (typeof product.discounted_price === 'number' && Number.isFinite(product.discounted_price) && product.discounted_price > 0) {
    return Math.round(product.discounted_price)
  }
  return calculateDiscountedPrice(basePrice, Number(product.discount_percentage))
}

export const getDiscountPercentage = (
  product?: DiscountableProduct | null,
  now: Date = new Date()
): number => {
  if (!product || !isProductDiscountActive(product, now)) return 0
  if (typeof product.discount_percentage === 'number' && Number.isFinite(product.discount_percentage)) {
    return Math.round(product.discount_percentage)
  }
  const basePrice = Number(product.price) || 0
  const effective = getEffectivePrice(product, now)
  if (basePrice <= 0 || effective >= basePrice) return 0
  return Math.round(((basePrice - effective) / basePrice) * 100)
}

export const getPromoBadgeText = (
  product?: DiscountableProduct | null,
  now: Date = new Date()
): string | null => {
  if (!product || !isProductDiscountActive(product, now)) return null
  const label = product.promo_label?.trim()
  if (label) return label
  const pct = getDiscountPercentage(product, now)
  return pct > 0 ? `-${pct}%` : null
}
