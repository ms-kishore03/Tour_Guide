import { apiFetch } from './client'
import type { WeatherResponse } from '../types/api'

export function getWeather(place: string) {
  return apiFetch<WeatherResponse>(`/weather/${encodeURIComponent(place)}`)
}
