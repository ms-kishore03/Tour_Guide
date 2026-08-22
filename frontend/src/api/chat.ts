import { API_BASE } from './client'
import { useAuthStore } from '../store/authStore'
import type { ChatMessage } from '../types/api'

export interface SseEvent {
  type: 'tool_call' | 'tool_result' | 'token' | 'final' | 'error'
  tool?: string
  data?: unknown
}

export function getChatHistory(place: string): Promise<ChatMessage[]> {
  const token = useAuthStore.getState().accessToken
  return fetch(`${API_BASE}/chat/${encodeURIComponent(place)}/history`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  }).then((res) => {
    if (!res.ok) throw new Error('Failed to load chat history')
    return res.json()
  })
}

/**
 * Opens the SSE chat stream via fetch + a manual ReadableStream reader (not
 * EventSource, which can't attach an Authorization header) and invokes
 * onEvent for each parsed SSE frame as it arrives.
 */
export async function streamChat(
  place: string,
  message: string,
  onEvent: (event: SseEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const token = useAuthStore.getState().accessToken
  const res = await fetch(`${API_BASE}/chat/${encodeURIComponent(place)}/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ message }),
    signal,
  })

  if (!res.ok || !res.body) {
    throw new Error(`Chat stream failed: ${res.status}`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    let boundary: number
    while ((boundary = buffer.indexOf('\n\n')) !== -1) {
      const rawFrame = buffer.slice(0, boundary)
      buffer = buffer.slice(boundary + 2)
      const event = parseFrame(rawFrame)
      if (event) onEvent(event)
    }
  }
}

function parseFrame(rawFrame: string): SseEvent | null {
  let eventType = 'message'
  let dataLine = ''
  for (const line of rawFrame.split('\n')) {
    if (line.startsWith('event:')) eventType = line.slice('event:'.length).trim()
    else if (line.startsWith('data:')) dataLine += line.slice('data:'.length).trim()
  }
  if (!dataLine) return null
  try {
    const parsed = JSON.parse(dataLine)
    return { type: (parsed.type ?? eventType) as SseEvent['type'], tool: parsed.tool, data: parsed.data }
  } catch {
    return null
  }
}
