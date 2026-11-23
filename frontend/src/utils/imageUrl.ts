const IMG_UPLOAD_SEGMENT = '/image/upload/';
const HAS_TRANSFORM_RE = /\/image\/upload\/(?:[a-z]+_[^/]+,)*[a-z]+_[^/]+\//;

export function buildImageVariantUrl(url: string, width: number, quality = 80): string {
  if (!url || !url.includes(IMG_UPLOAD_SEGMENT) || HAS_TRANSFORM_RE.test(url)) {
    return url;
  }
  return url.replace(IMG_UPLOAD_SEGMENT, `${IMG_UPLOAD_SEGMENT}w_${width},q_${quality},f_webp/`);
}

export function buildImageSrcset(url: string, widths: number[] = [400, 800], quality = 80): string | undefined {
  if (!url || !url.includes(IMG_UPLOAD_SEGMENT) || HAS_TRANSFORM_RE.test(url)) {
    return undefined;
  }
  return widths.map((w) => `${buildImageVariantUrl(url, w, quality)} ${w}w`).join(', ');
}
