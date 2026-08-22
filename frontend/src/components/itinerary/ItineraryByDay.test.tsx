import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MantineProvider } from '@mantine/core'
import { ItineraryByDay } from './ItineraryByDay'

describe('ItineraryByDay', () => {
  it('renders every item for a day with multiple stops (regression: old Streamlit UI only showed the last one)', () => {
    render(
      <MantineProvider>
        <ItineraryByDay
          itineraryByDate={{
            '01/01/2026': [
              { location: 'Fushimi Inari', time: '09:00 AM' },
              { location: 'Kiyomizu-dera', time: '01:00 PM' },
              { location: 'Gion District', time: '06:00 PM' },
            ],
          }}
        />
      </MantineProvider>,
    )

    expect(screen.getByText(/Fushimi Inari/)).toBeInTheDocument()
    expect(screen.getByText(/Kiyomizu-dera/)).toBeInTheDocument()
    expect(screen.getByText(/Gion District/)).toBeInTheDocument()
  })

  it('renders multiple days each with their own items', () => {
    render(
      <MantineProvider>
        <ItineraryByDay
          itineraryByDate={{
            '01/01/2026': [{ location: 'Fushimi Inari', time: '09:00 AM' }],
            '01/02/2026': [{ location: 'Arashiyama', time: '10:00 AM' }],
          }}
        />
      </MantineProvider>,
    )

    expect(screen.getByText('01/01/2026')).toBeInTheDocument()
    expect(screen.getByText('01/02/2026')).toBeInTheDocument()
  })

  it('shows an empty state when there is no itinerary', () => {
    render(
      <MantineProvider>
        <ItineraryByDay itineraryByDate={{}} />
      </MantineProvider>,
    )
    expect(screen.getByText(/no finalized itinerary yet/i)).toBeInTheDocument()
  })
})
