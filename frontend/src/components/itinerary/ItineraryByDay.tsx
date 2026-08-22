import { Stack, Title, List, Text, Card } from '@mantine/core'
import type { ItineraryItem } from '../../types/api'

interface Props {
  itineraryByDate: Record<string, ItineraryItem[]>
}

export function ItineraryByDay({ itineraryByDate }: Props) {
  const dates = Object.keys(itineraryByDate)

  if (dates.length === 0) {
    return <Text c="dimmed">No finalized itinerary yet. Chat with the assistant to build one.</Text>
  }

  return (
    <Stack>
      {dates.map((date) => (
        <Card key={date} withBorder padding="md">
          <Title order={5}>{date}</Title>
          <List size="sm" mt="xs">
            {itineraryByDate[date].map((item, idx) => (
              <List.Item key={`${date}-${idx}`}>
                {item.time !== 'unknown' ? `${item.time} — ` : ''}
                {item.location}
              </List.Item>
            ))}
          </List>
        </Card>
      ))}
    </Stack>
  )
}
