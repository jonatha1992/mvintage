import { describe, it, expect } from 'vitest';
import { buildImageVariantUrl, buildImageSrcset } from '../imageUrl';

describe('imageUrl', () => {
  const sample = 'https://img.tecnofusion.dev/showroomisabella/image/upload/productos/abc123.webp';

  it('builds 400w and 800w WebP variant URLs for img-server uploads', () => {
    expect(buildImageVariantUrl(sample, 400)).toBe(
      'https://img.tecnofusion.dev/showroomisabella/image/upload/w_400,q_80,f_webp/productos/abc123.webp'
    );
    expect(buildImageVariantUrl(sample, 800)).toBe(
      'https://img.tecnofusion.dev/showroomisabella/image/upload/w_800,q_80,f_webp/productos/abc123.webp'
    );
  });

  it('builds srcset with 400w and 800w', () => {
    expect(buildImageSrcset(sample)).toBe(
      'https://img.tecnofusion.dev/showroomisabella/image/upload/w_400,q_80,f_webp/productos/abc123.webp 400w, ' +
        'https://img.tecnofusion.dev/showroomisabella/image/upload/w_800,q_80,f_webp/productos/abc123.webp 800w'
    );
  });

  it('leaves non-img-server and already-transformed URLs untouched', () => {
    expect(buildImageVariantUrl('/logo_redondo.jpg', 400)).toBe('/logo_redondo.jpg');
    expect(buildImageSrcset('/logo_redondo.jpg')).toBeUndefined();
    expect(buildImageSrcset('https://example.com/1.jpg')).toBeUndefined();
    const already = 'https://img.tecnofusion.dev/showroomisabella/image/upload/w_400,q_80,f_webp/productos/abc123.webp';
    expect(buildImageVariantUrl(already, 800)).toBe(already);
    expect(buildImageSrcset(already)).toBeUndefined();
  });
});
