import { useState } from 'react'
import { Title, TextInput, Button, Stack, Alert } from '@mantine/core'
import { useForm } from '@mantine/form'
import * as accommodationsApi from '../api/accommodations'
import { AccommodationResults } from '../components/accommodations/AccommodationResults'
import { ApiError } from '../api/client'

interface FormValues {
  location: string
  checkin: string
  checkout: string
}

export function AccommodationsPage() {
  const [results, setResults] = useState<string[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const form = useForm<FormValues>({
    initialValues: { location: '', checkin: '', checkout: '' },
    validate: {
      location: (v) => (v.trim() ? null : 'Required'),
      checkin: (v) => (v.trim() ? null : 'Required'),
      checkout: (v) => (v.trim() ? null : 'Required'),
    },
  })

  async function handleSubmit(values: FormValues) {
    setError(null)
    setLoading(true)
    setResults(null)
    try {
      const res = await accommodationsApi.searchAccommodations(values.location, values.checkin, values.checkout)
      setResults(res.results)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Failed to search accommodations')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Stack maw={480}>
      <Title order={2}>Accommodations</Title>
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack>
          <TextInput label="Location" {...form.getInputProps('location')} />
          <TextInput label="Check-in" placeholder="YYYY-MM-DD" {...form.getInputProps('checkin')} />
          <TextInput label="Check-out" placeholder="YYYY-MM-DD" {...form.getInputProps('checkout')} />
          <Button type="submit" loading={loading}>
            Search
          </Button>
        </Stack>
      </form>
      {error && <Alert color="red">{error}</Alert>}
      {results && <AccommodationResults results={results} />}
    </Stack>
  )
}
