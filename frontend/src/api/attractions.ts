import { apiFetch } from './client'
import type { AttractionsResponse } from '../types/api'

export function getAttractions(place: string) {
  return apiFetch<AttractionsResponse>(`/attractions/${encodeURIComponent(place)}`)
}
