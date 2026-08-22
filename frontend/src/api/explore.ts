import { apiFetch } from './client'
import type { ExploreResponse } from '../types/api'

export interface ExploreRequest {
  trip_theme: string
  activity: string
  climate: string
  budget: string
  duration: string
  location: string
  trip_type: string
  transport: string
}

export function explore(payload: ExploreRequest) {
  return apiFetch<ExploreResponse>('/explore', { method: 'POST', body: JSON.stringify(payload) })
}
