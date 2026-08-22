import { useState } from 'react'
import { Title, TextInput, Select, NumberInput, Button, Stack, Alert, Group } from '@mantine/core'
import { useForm } from '@mantine/form'
import * as flightsApi from '../api/flights'
import { FlightResultsTable } from '../components/flights/FlightResultsTable'
import { ApiError } from '../api/client'
import type { FlightOption } from '../types/api'

interface FormValues {
  departure: string
  arrival: string
  outbound_date: string
  return_date: string
  currency: string
  travel_class: string
  trip_type: string
  adults: number
  children: number
  infants_in_seat: number
  infants_in_lap: number
}

const CURRENCIES = ['USD', 'EUR', 'GBP', 'INR', 'JPY', 'AUD', 'CAD']
const TRAVEL_CLASSES = [
  { value: '1', label: 'Economy' },
  { value: '2', label: 'Premium Economy' },
  { value: '3', label: 'Business' },
  { value: '4', label: 'First' },
]
const TRIP_TYPES = [
  { value: '1', label: 'Round Trip' },
  { value: '2', label: 'One Way' },
  { value: '3', label: 'Multi City' },
]

export function FlightSearchPage() {
  const [flights, setFlights] = useState<FlightOption[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const form = useForm<FormValues>({
    initialValues: {
      departure: '',
      arrival: '',
      outbound_date: '',
      return_date: '',
      currency: 'USD',
      travel_class: '1',
      trip_type: '1',
      adults: 1,
      children: 0,
      infants_in_seat: 0,
      infants_in_lap: 0,
    },
    validate: {
      departure: (v) => (v.trim() ? null : 'Required'),
      arrival: (v) => (v.trim() ? null : 'Required'),
      outbound_date: (v) => (v.trim() ? null : 'Required'),
    },
  })

  async function handleSubmit(values: FormValues) {
    setError(null)
    setLoading(true)
    setFlights(null)
    try {
      const res = await flightsApi.searchFlights({
        ...values,
        travel_class: Number(values.travel_class),
        trip_type: Number(values.trip_type),
      })
      setFlights(res.flights)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Failed to search flights')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Stack maw={720}>
      <Title order={2}>Flight Search</Title>
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack>
          <Group grow>
            <TextInput label="Departure" {...form.getInputProps('departure')} />
            <TextInput label="Arrival" {...form.getInputProps('arrival')} />
          </Group>
          <Group grow>
            <TextInput label="Outbound date" placeholder="YYYY-MM-DD" {...form.getInputProps('outbound_date')} />
            <TextInput label="Return date" placeholder="YYYY-MM-DD" {...form.getInputProps('return_date')} />
          </Group>
          <Group grow>
            <Select label="Currency" data={CURRENCIES} {...form.getInputProps('currency')} />
            <Select label="Travel class" data={TRAVEL_CLASSES} {...form.getInputProps('travel_class')} />
            <Select label="Trip type" data={TRIP_TYPES} {...form.getInputProps('trip_type')} />
          </Group>
          <Group grow>
            <NumberInput label="Adults" min={1} {...form.getInputProps('adults')} />
            <NumberInput label="Children" min={0} {...form.getInputProps('children')} />
            <NumberInput label="Infants (seat)" min={0} {...form.getInputProps('infants_in_seat')} />
            <NumberInput label="Infants (lap)" min={0} {...form.getInputProps('infants_in_lap')} />
          </Group>
          <Button type="submit" loading={loading}>
            Search Flights
          </Button>
        </Stack>
      </form>
      {error && <Alert color="red">{error}</Alert>}
      {flights && <FlightResultsTable flights={flights} />}
    </Stack>
  )
}
