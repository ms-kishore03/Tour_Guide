import { apiFetch } from './client'
import type { MessageResponse, TripResponse } from '../types/api'

export function saveTrip(trip: TripResponse) {
  return apiFetch<TripResponse>('/trips', { method: 'POST', body: JSON.stringify(trip) })
}

export function listTrips() {
  return apiFetch<TripResponse[]>('/trips')
}

export function getTrip(placeName: string) {
  return apiFetch<TripResponse>(`/trips/${encodeURIComponent(placeName)}`)
}

export function deleteTrip(placeName: string) {
  return apiFetch<MessageResponse>(`/trips/${encodeURIComponent(placeName)}`, { method: 'DELETE' })
}

export function startPlanning(placeName: string) {
  return apiFetch<MessageResponse>(`/trips/${encodeURIComponent(placeName)}/plan`, { method: 'POST' })
}
