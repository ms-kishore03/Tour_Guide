import { apiFetch } from './client'
import type { FlightSearchResponse } from '../types/api'

export interface FlightSearchRequest {
  departure: string
  arrival: string
  outbound_date: string
  return_date?: string
  currency: string
  travel_class: number
  trip_type: number
  adults: number
  children: number
  infants_in_seat: number
  infants_in_lap: number
}

export function searchFlights(payload: FlightSearchRequest) {
  return apiFetch<FlightSearchResponse>('/flights/search', {
    method: 'POST',
    body: JSON.stringify(payload),
    auth: false,
  })
}
