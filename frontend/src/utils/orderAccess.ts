export function orderAccessToken(orderId: number, token?: unknown): string | undefined {
  const key = `order_access_${orderId}`
  if (typeof token === 'string' && token) {
    localStorage.setItem(key, token)
    return token
  }
  return localStorage.getItem(key) || undefined
}

export function orderLink(orderId: number): string {
  const token = orderAccessToken(orderId)
  return `/orders/${orderId}${token ? `?access_token=${encodeURIComponent(token)}` : ''}`
}
