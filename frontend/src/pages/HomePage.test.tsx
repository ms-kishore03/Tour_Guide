import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { MantineProvider } from '@mantine/core'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { HomePage } from './HomePage'
import * as tripsApi from '../api/trips'

vi.mock('../api/trips')

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <MantineProvider>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <HomePage />
        </MemoryRouter>
      </QueryClientProvider>
    </MantineProvider>,
  )
}

describe('HomePage', () => {
  beforeEach(() => vi.clearAllMocks())

  it('shows an empty state when there are no saved trips', async () => {
    vi.mocked(tripsApi.listTrips).mockResolvedValue([])
    renderPage()
    expect(await screen.findByText(/no saved trips yet/i)).toBeInTheDocument()
  })

  it('renders saved trips and deletes one on click', async () => {
    vi.mocked(tripsApi.listTrips).mockResolvedValue([
      {
        place_name: 'Kyoto',
        scenario: 'Cultural',
        climate: 'Mild',
        duration: '5 days',
        people: '2',
        transport: 'Flight',
        description: 'Historic temples.',
      },
    ])
    vi.mocked(tripsApi.deleteTrip).mockResolvedValue({ message: 'Trip deleted' })

    renderPage()
    expect(await screen.findByText('Kyoto')).toBeInTheDocument()

    const user = userEvent.setup()
    await user.click(screen.getByRole('button', { name: /delete/i }))

    await waitFor(() => expect(tripsApi.deleteTrip).toHaveBeenCalledWith('Kyoto', expect.anything()))
  })
})
