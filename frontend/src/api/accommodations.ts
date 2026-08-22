import { apiFetch } from './client'
import type { AccommodationSearchResponse } from '../types/api'

export function searchAccommodations(location: string, checkin: string, checkout: string) {
  return apiFetch<AccommodationSearchResponse>('/accommodations/search', {
    method: 'POST',
    body: JSON.stringify({ location, checkin, checkout }),
    auth: false,
  })
}
