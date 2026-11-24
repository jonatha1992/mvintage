import { describe, it, expect } from 'vitest';
import {
  calculateDiscountedPrice,
  calculatePercentageFromFinalPrice,
  formatPrice,
  getDiscountPercentage,
  getEffectivePrice,
  getPromoBadgeText,
  isProductDiscountActive,
} from '../price';

describe('price utils & discounts', () => {
  it('formats ARS prices rounded to whole pesos without spaces', () => {
    expect(formatPrice(25000)).toBe('$25.000');
    expect(formatPrice(12345.6)).toBe('$12.346');
    expect(formatPrice(0)).toBe('$0');
  });

  it('calculates discounted price rounded to whole pesos within 1-90%', () => {
    expect(calculateDiscountedPrice(10000, 20)).toBe(8000);
    expect(calculateDiscountedPrice(12345, 15)).toBe(10493);
    expect(calculateDiscountedPrice(10000, 0)).toBe(10000);
    expect(calculateDiscountedPrice(10000, 95)).toBe(10000);
  });

  it('calculates discount percentage from final price and rejects out-of-range values', () => {
    expect(calculatePercentageFromFinalPrice(50000, 40000)).toBe(20);
    expect(calculatePercentageFromFinalPrice(10000, 7500)).toBe(25);
    expect(calculatePercentageFromFinalPrice(10000, 10000)).toBeNull();
    expect(calculatePercentageFromFinalPrice(10000, 500)).toBeNull(); // 95% > 90%
    expect(calculatePercentageFromFinalPrice(10000, 9990)).toBeNull(); // 0.1% < 1%
  });

  it('respects discount_starts_at and discount_ends_at when evaluating active status', () => {
    const now = new Date('2026-11-24T15:00:00Z');
    const active = {
      price: 40000,
      has_discount: true,
      discount_percentage: 25,
      discount_starts_at: '2026-11-24T10:00:00Z',
      discount_ends_at: '2026-11-25T10:00:00Z',
    };
    const future = {
      ...active,
      discount_starts_at: '2026-11-24T16:00:00Z',
    };
    const expired = {
      ...active,
      discount_ends_at: '2026-11-24T14:00:00Z',
    };

    expect(isProductDiscountActive(active, now)).toBe(true);
    expect(getEffectivePrice(active, now)).toBe(30000);

    expect(isProductDiscountActive(future, now)).toBe(false);
    expect(getEffectivePrice(future, now)).toBe(40000);

    expect(isProductDiscountActive(expired, now)).toBe(false);
    expect(getEffectivePrice(expired, now)).toBe(40000);
  });

  it('returns promo_label when present or -XX% badge otherwise', () => {
    const now = new Date('2026-11-24T15:00:00Z');
    expect(
      getPromoBadgeText({ price: 20000, has_discount: true, discount_percentage: 20, promo_label: 'Liquidación' }, now)
    ).toBe('Liquidación');
    expect(
      getPromoBadgeText({ price: 20000, has_discount: true, discount_percentage: 20, promo_label: '   ' }, now)
    ).toBe('-20%');
    expect(
      getPromoBadgeText({ price: 20000, has_discount: false, discount_percentage: 20 }, now)
    ).toBeNull();
    expect(
      getDiscountPercentage({ price: 20000, has_discount: true, discount_percentage: 19.6 }, now)
    ).toBe(20);
  });
});
