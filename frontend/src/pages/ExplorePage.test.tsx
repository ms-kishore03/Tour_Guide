import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { MantineProvider } from '@mantine/core'
import { ExplorePage } from './ExplorePage'
import * as exploreApi from '../api/explore'
import { useTripStore } from '../store/tripStore'

vi.mock('../api/explore')

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => mockNavigate }
})

function renderPage() {
  return render(
    <MantineProvider>
      <MemoryRouter>
        <ExplorePage />
      </MemoryRouter>
    </MantineProvider>,
  )
}

describe('ExplorePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    useTripStore.setState({ currentTrip: null })
  })

  it('shows a validation error when trip theme is empty', async () => {
    renderPage()
    const user = userEvent.setup()
    await user.click(screen.getByRole('button', { name: /suggest destinations/i }))
    expect(await screen.findAllByText(/required/i)).not.toHaveLength(0)
  })

  it('renders suggestions returned by the API and selecting one sets the trip store', async () => {
    vi.mocked(exploreApi.explore).mockResolvedValue({
      places: [{ name: 'Kyoto', description: 'Historic temples.' }],
    })

    renderPage()
    const user = userEvent.setup()
    await user.type(screen.getByLabelText(/trip theme/i), 'Cultural')
    await user.type(screen.getByLabelText(/duration/i), '5 days')
    await user.click(screen.getByRole('button', { name: /suggest destinations/i }))

    const card = await screen.findByText('Kyoto')
    await user.click(card)

    expect(useTripStore.getState().currentTrip?.place_name).toBe('Kyoto')
    expect(mockNavigate).toHaveBeenCalledWith('/trips/Kyoto')
  })
})
