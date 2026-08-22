import { apiFetch } from './client'
import type { ItineraryResponse } from '../types/api'

export function getItinerary(place: string) {
  return apiFetch<ItineraryResponse>(`/trips/${encodeURIComponent(place)}/itinerary`)
}

export function getTodos(place: string) {
  return apiFetch<string[]>(`/trips/${encodeURIComponent(place)}/itinerary/todo`)
}

export function addTodo(place: string, task: string) {
  return apiFetch<string[]>(`/trips/${encodeURIComponent(place)}/itinerary/todo`, {
    method: 'POST',
    body: JSON.stringify({ task }),
  })
}
