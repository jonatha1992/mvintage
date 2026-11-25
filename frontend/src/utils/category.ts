const labels: Record<string, string> = {
  SHOE: 'Calzado', BASICA: 'Básica', PANTALON: 'Pantalón',
}

export function categoryLabel(name: string | undefined): string {
  if (!name) return ''
  return labels[name.toUpperCase()] ?? name.charAt(0).toLocaleUpperCase('es-AR') + name.slice(1).toLocaleLowerCase('es-AR')
}
