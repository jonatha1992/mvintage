const arsFormatter = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
  maximumFractionDigits: 0
})

export const formatPrice = (amount?: number | string | null): string =>
  arsFormatter.format(Number(amount ?? 0)).replace(/\s/g, '')
