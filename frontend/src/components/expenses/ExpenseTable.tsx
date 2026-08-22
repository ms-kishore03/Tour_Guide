import { Table } from '@mantine/core'
import type { ExpenseResponse } from '../../types/api'

export function ExpenseTable({ expenses }: { expenses: ExpenseResponse[] }) {
  return (
    <Table>
      <Table.Thead>
        <Table.Tr>
          <Table.Th>Date</Table.Th>
          <Table.Th>Category</Table.Th>
          <Table.Th>Amount</Table.Th>
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>
        {expenses.map((e, i) => (
          <Table.Tr key={i}>
            <Table.Td>{e.date}</Table.Td>
            <Table.Td>{e.category}</Table.Td>
            <Table.Td>{e.amount.toFixed(2)}</Table.Td>
          </Table.Tr>
        ))}
      </Table.Tbody>
    </Table>
  )
}
