import { apiFetch } from './client'
import type { ExpenseResponse, MessageResponse, OngoingTripResponse } from '../types/api'

export function startOngoingTrip(place: string) {
  return apiFetch<MessageResponse>(`/ongoing-trips/${encodeURIComponent(place)}/start`, { method: 'POST' })
}

export function getOngoingTrip() {
  return apiFetch<OngoingTripResponse | null>('/ongoing-trips')
}

export function endOngoingTrip(place: string) {
  return apiFetch<MessageResponse>(`/ongoing-trips/${encodeURIComponent(place)}/end`, { method: 'POST' })
}

export function listExpenses(place: string) {
  return apiFetch<ExpenseResponse[]>(`/ongoing-trips/${encodeURIComponent(place)}/expenses`)
}

export function addExpense(place: string, expense: ExpenseResponse) {
  return apiFetch<ExpenseResponse[]>(`/ongoing-trips/${encodeURIComponent(place)}/expenses`, {
    method: 'POST',
    body: JSON.stringify(expense),
  })
}
