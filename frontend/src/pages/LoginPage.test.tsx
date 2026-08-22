import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { MantineProvider } from '@mantine/core'
import { LoginPage } from './LoginPage'
import * as authApi from '../api/auth'
import { useAuthStore } from '../store/authStore'

vi.mock('../api/auth')

function renderLoginPage() {
  return render(
    <MantineProvider>
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    </MantineProvider>,
  )
}

describe('LoginPage', () => {
  beforeEach(() => {
    useAuthStore.getState().logout()
    vi.clearAllMocks()
  })

  it('shows validation errors on empty submit', async () => {
    renderLoginPage()
    const user = userEvent.setup()
    await user.click(screen.getByRole('button', { name: /log in/i }))
    expect(await screen.findByText(/username is required/i)).toBeInTheDocument()
  })

  it('logs in successfully and stores the session', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'access-123',
      refresh_token: 'refresh-123',
      token_type: 'bearer',
    })
    vi.mocked(authApi.me).mockResolvedValue({ username: 'alice', email: 'alice@example.com' })

    renderLoginPage()
    const user = userEvent.setup()
    await user.type(screen.getByLabelText(/username/i), 'alice')
    await user.type(screen.getByLabelText(/^password$/i), 'password1')
    await user.click(screen.getByRole('button', { name: /log in/i }))

    await waitFor(() => expect(useAuthStore.getState().accessToken).toBe('access-123'))
    expect(useAuthStore.getState().user?.username).toBe('alice')
  })

  it('shows an error banner on failed login', async () => {
    const { ApiError } = await import('../api/client')
    vi.mocked(authApi.login).mockRejectedValue(new ApiError(401, 'Invalid credentials'))

    renderLoginPage()
    const user = userEvent.setup()
    await user.type(screen.getByLabelText(/username/i), 'alice')
    await user.type(screen.getByLabelText(/^password$/i), 'wrongpass')
    await user.click(screen.getByRole('button', { name: /log in/i }))

    expect(await screen.findByText(/invalid credentials/i)).toBeInTheDocument()
  })
})
