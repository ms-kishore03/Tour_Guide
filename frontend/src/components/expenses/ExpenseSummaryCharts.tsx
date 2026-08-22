import { Stack, Text, Group, Badge } from '@mantine/core'
import type { ExpenseResponse } from '../../types/api'

export function ExpenseSummaryCharts({ expenses }: { expenses: ExpenseResponse[] }) {
  const byCategory = new Map<string, number>()
  for (const e of expenses) {
    byCategory.set(e.category, (byCategory.get(e.category) ?? 0) + e.amount)
  }
  const total = expenses.reduce((sum, e) => sum + e.amount, 0)

  return (
    <Stack gap="xs">
      <Text fw={600}>Total: {total.toFixed(2)}</Text>
      <Group gap="xs">
        {[...byCategory.entries()].map(([category, amount]) => (
          <Badge key={category} variant="light">
            {category}: {amount.toFixed(2)}
          </Badge>
        ))}
      </Group>
    </Stack>
  )
}
