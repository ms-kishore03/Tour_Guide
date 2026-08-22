export interface UserResponse {
  username: string
  email: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface MessageResponse {
  message: string
}

export interface TripResponse {
  place_name: string
  scenario: string
  climate: string
  duration: string
  people: string
  transport: string
  description: string
}

export interface ExploreSuggestion {
  name: string
  description: string
}

export interface ExploreResponse {
  places: ExploreSuggestion[]
}

export interface AttractionsResponse {
  status: string
  places: string[]
}

export interface WeatherResponse {
  explanation: string
  current: string
  forecast: Record<string, unknown>[]
}

export interface ItineraryItem {
  location: string
  time: string
}

export interface ItineraryResponse {
  itinerary_by_date: Record<string, ItineraryItem[]>
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  ts: string
  partial?: boolean
}

export interface ExpenseResponse {
  amount: number
  category: string
  date: string
}

export interface OngoingTripResponse {
  username: string
  place: string
  trip_details: Record<string, unknown>
  expenses: ExpenseResponse[]
}

export interface FlightOption {
  departure_time: string
  arrival_time: string
  airlines: string
  duration: string
  layovers: string
  price: string
  carbon_emission: string
}

export interface FlightSearchResponse {
  flights: FlightOption[]
}

export interface AccommodationSearchResponse {
  results: string[]
}
