import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import ProductCard from '../ProductCard.vue';
import type { Product } from '../../../types/products/product.types';

const makeProduct = (overrides: Partial<Product> = {}): Product => ({
  id: 1,
  name: 'Remera Test',
  description: 'Desc',
  price: 25000,
  genero: 'Femenino',
  estado: 'Disponible',
  is_unique: true,
  has_discount: false,
  stock: 3,
  images: [
    { id: 1, image_url: 'https://img.tecnofusion.dev/showroomisabella/image/upload/productos/1.webp' },
    { id: 2, image_url: 'https://img.tecnofusion.dev/showroomisabella/image/upload/productos/2.webp' },
  ],
  variants: [],
  ...overrides,
});

const mockMatchMedia = (matches: boolean) => {
  const orig = window.matchMedia;
  window.matchMedia = ((query: string) => ({
    matches: matches && query === '(hover: hover) and (pointer: fine)',
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  })) as typeof window.matchMedia;
  return () => {
    window.matchMedia = orig;
  };
};

describe('ProductCard', () => {
  const mountCard = (product: Product, index = 0) =>
    mount(ProductCard, {
      props: { product, index },
      global: {
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    });

  it('does not render hover image until pointerenter on hover-capable desktop', async () => {
    const restore = mockMatchMedia(true);
    try {
      const wrapper = mountCard(makeProduct());
      expect(wrapper.findAll('img').length).toBe(1);
      await wrapper.find('.aspect-square').trigger('pointerenter', { pointerType: 'mouse' });
      expect(wrapper.findAll('img').length).toBe(2);
      expect(wrapper.findAll('img')[1].attributes('fetchpriority')).toBe('low');
    } finally {
      restore();
    }
  });

  it('never renders hover image on touch/mobile devices', async () => {
    const restore = mockMatchMedia(false);
    try {
      const wrapper = mountCard(makeProduct());
      await wrapper.find('.aspect-square').trigger('pointerenter', { pointerType: 'touch' });
      expect(wrapper.findAll('img').length).toBe(1);
    } finally {
      restore();
    }
  });

  it('sets 400w/800w srcset, sizes, width/height and priority attributes', () => {
    const first = mountCard(makeProduct(), 0);
    const fifth = mountCard(makeProduct(), 4);
    const img0 = first.find('img');
    const img4 = fifth.find('img');

    expect(img0.attributes('srcset')).toContain('w_400,q_80,f_webp');
    expect(img0.attributes('srcset')).toContain('w_800,q_80,f_webp');
    expect(img0.attributes('sizes')).toBeTruthy();
    expect(img0.attributes('width')).toBe('400');
    expect(img0.attributes('height')).toBe('400');
    expect(img0.attributes('loading')).toBe('eager');
    expect(img0.attributes('fetchpriority')).toBe('high');
    expect(img0.attributes('decoding')).toBeUndefined();

    expect(img4.attributes('loading')).toBe('lazy');
    expect(img4.attributes('fetchpriority')).toBeUndefined();
    expect(img4.attributes('decoding')).toBe('async');
  });
});
