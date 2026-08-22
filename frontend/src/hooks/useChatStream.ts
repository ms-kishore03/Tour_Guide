import { useCallback, useRef, useState } from 'react'
import { streamChat, getChatHistory, type SseEvent } from '../api/chat'
import type { ChatMessage } from '../types/api'

export type ConnectionState = 'idle' | 'connecting' | 'streaming' | 'error'

export function useChatStream(place: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [connectionState, setConnectionState] = useState<ConnectionState>('idle')
  const [activeTool, setActiveTool] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const loadHistory = useCallback(async () => {
    try {
      const history = await getChatHistory(place)
      setMessages(history)
    } catch {
      // no history yet, or backend unreachable — leave the panel empty
    }
  }, [place])

  const sendMessage = useCallback(
    async (text: string) => {
      setMessages((prev) => [...prev, { role: 'user', content: text, ts: new Date().toISOString() }])
      setMessages((prev) => [...prev, { role: 'assistant', content: '', ts: new Date().toISOString(), partial: true }])
      setConnectionState('connecting')
      setActiveTool(null)

      const controller = new AbortController()
      abortRef.current = controller

      let assistantText = ''

      function applyEvent(event: SseEvent) {
        if (event.type === 'tool_call') {
          setActiveTool(event.tool ?? null)
          setConnectionState('streaming')
        } else if (event.type === 'tool_result') {
          setActiveTool(null)
        } else if (event.type === 'token') {
          assistantText += (event.data as string) ?? ''
          setConnectionState('streaming')
          setMessages((prev) => {
            const next = [...prev]
            next[next.length - 1] = { ...next[next.length - 1], content: assistantText, partial: true }
            return next
          })
        } else if (event.type === 'final') {
          const finalData = event.data as { message?: string } | undefined
          const finalMessage = finalData?.message ?? assistantText
          setActiveTool(null)
          setMessages((prev) => {
            const next = [...prev]
            next[next.length - 1] = { ...next[next.length - 1], content: finalMessage, partial: false }
            return next
          })
        } else if (event.type === 'error') {
          setConnectionState('error')
        }
      }

      try {
        await streamChat(place, text, applyEvent, controller.signal)
        setConnectionState('idle')
      } catch {
        setConnectionState('error')
      }
    },
    [place],
  )

  const cancel = useCallback(() => {
    abortRef.current?.abort()
  }, [])

  return { messages, connectionState, activeTool, sendMessage, loadHistory, cancel }
}
