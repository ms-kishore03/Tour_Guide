import { useEffect, useState } from 'react'
import { Stack, TextInput, Button, Text, Alert, Group, Badge } from '@mantine/core'
import { useChatStream } from '../../hooks/useChatStream'
import { ChatMessageBubble } from './ChatMessageBubble'

export function ChatPanel({ place }: { place: string }) {
  const { messages, connectionState, activeTool, sendMessage, loadHistory } = useChatStream(place)
  const [input, setInput] = useState('')

  useEffect(() => {
    loadHistory()
  }, [loadHistory])

  async function handleSend() {
    if (!input.trim()) return
    const text = input
    setInput('')
    await sendMessage(text)
  }

  return (
    <Stack gap="sm">
      <Text fw={600}>Trip Assistant</Text>
      {connectionState === 'error' && (
        <Alert color="red" data-testid="chat-reconnect-banner">
          Connection lost. Try sending your message again.
        </Alert>
      )}
      {activeTool && (
        <Badge variant="light" color="grape">
          Using {activeTool.toLowerCase()}…
        </Badge>
      )}
      <Stack gap="xs" style={{ minHeight: 200 }}>
        {messages.map((m, i) => (
          <ChatMessageBubble key={i} message={m} />
        ))}
      </Stack>
      <Group>
        <TextInput
          flex={1}
          placeholder="Ask anything about your destination…"
          value={input}
          onChange={(e) => setInput(e.currentTarget.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <Button onClick={handleSend} loading={connectionState === 'connecting' || connectionState === 'streaming'}>
          Send
        </Button>
      </Group>
    </Stack>
  )
}
