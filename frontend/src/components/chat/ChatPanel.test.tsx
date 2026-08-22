import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MantineProvider } from '@mantine/core'
import { ChatPanel } from './ChatPanel'
import * as chatApi from '../../api/chat'
import type { SseEvent } from '../../api/chat'

vi.mock('../../api/chat')

function renderPanel() {
  return render(
    <MantineProvider>
      <ChatPanel place="Kyoto" />
    </MantineProvider>,
  )
}

describe('ChatPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(chatApi.getChatHistory).mockResolvedValue([])
  })

  it('appends incremental token events to the streaming assistant message', async () => {
    vi.mocked(chatApi.streamChat).mockImplementation(async (_place, _message, onEvent) => {
      const events: SseEvent[] = [
        { type: 'tool_call', tool: 'WEATHER' },
        { type: 'token', data: 'It' },
        { type: 'token', data: 's sunny.' },
        { type: 'final', data: { message: "It's sunny." } },
      ]
      for (const event of events) onEvent(event)
    })

    renderPanel()
    const user = userEvent.setup()
    await user.type(screen.getByPlaceholderText(/ask anything/i), 'weather?')
    await user.click(screen.getByRole('button', { name: /send/i }))

    await waitFor(() => expect(screen.getByText("It's sunny.")).toBeInTheDocument())
  })

  it('shows a reconnect banner when the stream errors', async () => {
    vi.mocked(chatApi.streamChat).mockRejectedValue(new Error('network down'))

    renderPanel()
    const user = userEvent.setup()
    await user.type(screen.getByPlaceholderText(/ask anything/i), 'hello')
    await user.click(screen.getByRole('button', { name: /send/i }))

    expect(await screen.findByTestId('chat-reconnect-banner')).toBeInTheDocument()
  })
})
