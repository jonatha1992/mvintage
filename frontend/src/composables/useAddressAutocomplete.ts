import { ref, readonly } from 'vue'

export interface AddressSuggestion {
  place_id: number
  display_name: string
  address: {
    house_number?: string
    road?: string
    neighbourhood?: string
    city?: string
    town?: string
    village?: string
    municipality?: string
    state?: string
    province?: string
    postcode?: string
    country?: string
    country_code?: string
  }
  lat: string
  lon: string
}

export interface ParsedAddress {
  fullAddress: string
  street: string
  city: string
  postalCode: string
  province: string
  country: string
}

export function useAddressAutocomplete() {
  const suggestions = ref<AddressSuggestion[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Rate limiting - máximo 1 consulta por segundo según términos de Nominatim
  let lastRequestTime = 0
  const MIN_REQUEST_INTERVAL = 1000

  const searchAddresses = async (query: string, countryCode: string = 'AR'): Promise<AddressSuggestion[]> => {
    if (query.length < 3) {
      suggestions.value = []
      return []
    }

    // Rate limiting
    const now = Date.now()
    const timeSinceLastRequest = now - lastRequestTime
    if (timeSinceLastRequest < MIN_REQUEST_INTERVAL) {
      await new Promise(resolve => setTimeout(resolve, MIN_REQUEST_INTERVAL - timeSinceLastRequest))
    }

    loading.value = true
    error.value = null

    try {
      const countryCodes = countryCode === 'AR' ? 'ar' : countryCode === 'UY' ? 'uy' : countryCode === 'CL' ? 'cl' : 'ar'

      const url = new URL('https://nominatim.openstreetmap.org/search')
      url.searchParams.set('q', query)
      url.searchParams.set('format', 'json')
      url.searchParams.set('countrycodes', countryCodes)
      url.searchParams.set('limit', '5')
      url.searchParams.set('addressdetails', '1')
      url.searchParams.set('extratags', '1')

      lastRequestTime = Date.now()

      const response = await fetch(url.toString(), {
        headers: {
          'User-Agent': 'M-VINTAGE-App/1.0 (mvintageapp@gmail.com)'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      suggestions.value = data
      return data

    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error al buscar direcciones'
      suggestions.value = []
      return []

    } finally {
      loading.value = false
    }
  }

  const parseAddress = (suggestion: AddressSuggestion): ParsedAddress => {
    const { address } = suggestion

    // Construir direccin completa
    let street = ''
    if (address.road) {
      street = address.road
      if (address.house_number) {
        street += ` ${address.house_number}`
      }
    }

    // Determinar ciudad
    let city = address.city || address.town || address.village || address.municipality || ''
    if (!city && address.neighbourhood) {
      city = address.neighbourhood
    }

    // Determinar provincia/estado
    let province = address.state || address.province || ''

    // Determinar país
    let country = address.country_code?.toUpperCase() || 'AR'

    return {
      fullAddress: suggestion.display_name,
      street: street || suggestion.display_name.split(',')[0],
      city: city,
      postalCode: address.postcode || '',
      province: province,
      country: country
    }
  }

  const clearSuggestions = () => {
    suggestions.value = []
    error.value = null
  }

  return {
    suggestions: readonly(suggestions),
    loading: readonly(loading),
    error: readonly(error),
    searchAddresses,
    parseAddress,
    clearSuggestions
  }
}

