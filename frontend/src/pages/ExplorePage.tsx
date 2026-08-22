import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Title, TextInput, Select, Button, Stack, Card, Text, Alert, Group } from '@mantine/core'
import { useForm } from '@mantine/form'
import * as exploreApi from '../api/explore'
import { useTripStore } from '../store/tripStore'
import { ApiError } from '../api/client'
import type { ExploreSuggestion } from '../types/api'

interface FormValues {
  trip_theme: string
  activity: string
  climate: string
  budget: string
  duration: string
  location: string
  trip_type: string
  transport: string
}

const CLIMATE_OPTIONS = ['Any', 'Tropical', 'Mild', 'Cold', 'Dry']
const TRIP_TYPE_OPTIONS = ['Solo', 'Couple', 'Family', 'Friends']
const TRANSPORT_OPTIONS = ['Flight', 'Train', 'Road Trip', 'Cruise']

export function ExplorePage() {
  const navigate = useNavigate()
  const setCurrentTrip = useTripStore((s) => s.setCurrentTrip)
  const [suggestions, setSuggestions] = useState<ExploreSuggestion[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const form = useForm<FormValues>({
    initialValues: {
      trip_theme: '',
      activity: '',
      climate: 'Any',
      budget: '',
      duration: '',
      location: '',
      trip_type: 'Solo',
      transport: 'Flight',
    },
    validate: {
      trip_theme: (v) => (v.trim() ? null : 'Required'),
      duration: (v) => (v.trim() ? null : 'Required'),
    },
  })

  async function handleSubmit(values: FormValues) {
    setError(null)
    setLoading(true)
    setSuggestions(null)
    try {
      const res = await exploreApi.explore(values)
      setSuggestions(res.places)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Failed to fetch suggestions')
    } finally {
      setLoading(false)
    }
  }

  function selectPlace(suggestion: ExploreSuggestion) {
    const values = form.getValues()
    setCurrentTrip({
      place_name: suggestion.name,
      scenario: values.trip_theme,
      climate: values.climate,
      duration: values.duration,
      people: values.trip_type,
      transport: values.transport,
      description: suggestion.description,
    })
    navigate(`/trips/${encodeURIComponent(suggestion.name)}`)
  }

  return (
    <Stack maw={720}>
      <Title order={2}>Explore Destinations</Title>
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack>
          <TextInput label="Trip theme" placeholder="e.g. Adventure" {...form.getInputProps('trip_theme')} />
          <TextInput label="Specific activity" placeholder="e.g. Hiking" {...form.getInputProps('activity')} />
          <Select label="Climate" data={CLIMATE_OPTIONS} {...form.getInputProps('climate')} />
          <TextInput label="Budget" placeholder="e.g. Medium" {...form.getInputProps('budget')} />
          <TextInput label="Duration" placeholder="e.g. 5 days" {...form.getInputProps('duration')} />
          <TextInput label="Departure location" {...form.getInputProps('location')} />
          <Select label="Trip type" data={TRIP_TYPE_OPTIONS} {...form.getInputProps('trip_type')} />
          <Select label="Transport" data={TRANSPORT_OPTIONS} {...form.getInputProps('transport')} />
          <Button type="submit" loading={loading}>
            Suggest destinations
          </Button>
        </Stack>
      </form>

      {error && <Alert color="red">{error}</Alert>}

      {suggestions && suggestions.length === 0 && <Text c="dimmed">No suggestions found.</Text>}

      {suggestions?.map((s) => (
        <Card key={s.name} withBorder padding="lg" onClick={() => selectPlace(s)} style={{ cursor: 'pointer' }}>
          <Group justify="space-between">
            <Text fw={600}>{s.name}</Text>
          </Group>
          <Text size="sm" c="dimmed" mt="xs">
            {s.description}
          </Text>
        </Card>
      ))}
    </Stack>
  )
}
