import { Routes, Route } from 'react-router-dom'
import { AppShellLayout } from './components/layout/AppShellLayout'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { LoginPage } from './pages/LoginPage'
import { HomePage } from './pages/HomePage'
import { ExplorePage } from './pages/ExplorePage'
import { TripOverviewPage } from './pages/TripOverviewPage'
import { TripItineraryPage } from './pages/TripItineraryPage'
import { OngoingTripsPage } from './pages/OngoingTripsPage'
import { AccommodationsPage } from './pages/AccommodationsPage'
import { FlightSearchPage } from './pages/FlightSearchPage'

function Protected({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <AppShellLayout>{children}</AppShellLayout>
    </ProtectedRoute>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Protected><HomePage /></Protected>} />
      <Route path="/explore" element={<Protected><ExplorePage /></Protected>} />
      <Route path="/trips/:place" element={<Protected><TripOverviewPage /></Protected>} />
      <Route path="/trips/:place/itinerary" element={<Protected><TripItineraryPage /></Protected>} />
      <Route path="/ongoing-trip" element={<Protected><OngoingTripsPage /></Protected>} />
      <Route path="/accommodations" element={<Protected><AccommodationsPage /></Protected>} />
      <Route path="/flights" element={<Protected><FlightSearchPage /></Protected>} />
    </Routes>
  )
}
