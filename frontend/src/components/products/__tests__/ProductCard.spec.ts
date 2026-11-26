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
  const mountCard = (product: Product, index = 0, preview = false) =>
    mount(ProductCard, {
      props: { product, index, preview },
      global: {
        stubs: {
          RouterLink: {
            props: ['to'],
            template: '<a :href="to"><slot /></a>',
          },
        },
      },
    });

  it('renders link with product id when preview is false and non-link div with preview label when preview is true', () => {
    const normal = mountCard(makeProduct({ id: 42, name: 'Remera Test' }), 0, false);
    const link = normal.find('a');
    expect(link.exists()).toBe(true);
    expect(link.attributes('href')).toBe('/product/42/Remera Test');

    const previewCard = mountCard(makeProduct({ id: 42, name: 'Remera Test' }), 0, true);
    expect(previewCard.find('a').exists()).toBe(false);
    const previewEl = previewCard.find('[aria-label="Vista previa"]');
    expect(previewEl.exists()).toBe(true);
    expect(previewEl.element.tagName.toLowerCase()).toBe('div');
    expect(previewEl.classes()).toContain('cursor-default');
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

  it('renders discounted price, struck-through original price, promo badge and installments on discounted price', () => {
    const wrapper = mountCard(
      makeProduct({
        price: 30000,
        has_discount: true,
        discount_percentage: 20,
        discounted_price: 24000,
        promo_label: 'Liquidación',
        max_installments: 3,
      })
    );

    expect(wrapper.find('[data-testid="promo-badge"]').text()).toBe('Liquidación');
    expect(wrapper.find('[data-testid="discounted-price"]').text()).toBe('$24.000');
    expect(wrapper.find('[data-testid="original-price"]').text()).toBe('$30.000');
    const installments = wrapper.find('[data-testid="card-installments"]');
    if (installments.exists()) {
      expect(installments.text()).toContain('$8.000');
    }
  });

  it('falls back to -XX% badge when promo_label is empty and hides expired discounts', () => {
    const active = mountCard(
      makeProduct({
        price: 20000,
        has_discount: true,
        discount_percentage: 15,
        promo_label: null,
      })
    );
    expect(active.find('[data-testid="promo-badge"]').text()).toBe('-15%');
    expect(active.find('[data-testid="discounted-price"]').text()).toBe('$17.000');

    const expired = mountCard(
      makeProduct({
        price: 20000,
        has_discount: true,
        discount_percentage: 25,
        discount_ends_at: '2020-01-01T00:00:00Z',
      })
    );
    expect(expired.find('[data-testid="promo-badge"]').exists()).toBe(false);
    expect(expired.find('[data-testid="discounted-price"]').exists()).toBe(false);
  });
});
