import { List, Text } from '@mantine/core'

export function AccommodationResults({ results }: { results: string[] }) {
  if (results.length === 0) return <Text c="dimmed">No accommodations found.</Text>
  return (
    <List type="ordered">
      {results.map((r) => (
        <List.Item key={r}>{r}</List.Item>
      ))}
    </List>
  )
}
