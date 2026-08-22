import { Table, Text } from '@mantine/core'
import type { FlightOption } from '../../types/api'

export function FlightResultsTable({ flights }: { flights: FlightOption[] }) {
  if (flights.length === 0) return <Text c="dimmed">No flights found.</Text>
  return (
    <Table>
      <Table.Thead>
        <Table.Tr>
          <Table.Th>Departure</Table.Th>
          <Table.Th>Arrival</Table.Th>
          <Table.Th>Airlines</Table.Th>
          <Table.Th>Duration</Table.Th>
          <Table.Th>Layovers</Table.Th>
          <Table.Th>Price</Table.Th>
          <Table.Th>Carbon</Table.Th>
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>
        {flights.map((f, i) => (
          <Table.Tr key={i}>
            <Table.Td>{f.departure_time}</Table.Td>
            <Table.Td>{f.arrival_time}</Table.Td>
            <Table.Td>{f.airlines}</Table.Td>
            <Table.Td>{f.duration}</Table.Td>
            <Table.Td>{f.layovers}</Table.Td>
            <Table.Td>{f.price}</Table.Td>
            <Table.Td>{f.carbon_emission}</Table.Td>
          </Table.Tr>
        ))}
      </Table.Tbody>
    </Table>
  )
}
