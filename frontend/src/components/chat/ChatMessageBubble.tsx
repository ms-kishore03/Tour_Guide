import { Paper, Text, Group, Loader } from '@mantine/core'
import type { ChatMessage } from '../../types/api'

export function ChatMessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user'
  return (
    <Paper
      withBorder
      p="sm"
      radius="md"
      style={{ alignSelf: isUser ? 'flex-end' : 'flex-start', maxWidth: '80%' }}
      bg={isUser ? 'blue.0' : undefined}
    >
      <Group gap="xs" wrap="nowrap">
        <Text size="sm">{message.content}</Text>
        {message.partial && <Loader size="xs" />}
      </Group>
    </Paper>
  )
}
