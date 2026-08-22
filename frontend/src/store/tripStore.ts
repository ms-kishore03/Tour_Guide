import { create } from 'zustand'
import type { TripResponse } from '../types/api'

interface TripState {
  currentTrip: TripResponse | null
  setCurrentTrip: (trip: TripResponse | null) => void
}

export const useTripStore = create<TripState>((set) => ({
  currentTrip: null,
  setCurrentTrip: (trip) => set({ currentTrip: trip }),
}))
