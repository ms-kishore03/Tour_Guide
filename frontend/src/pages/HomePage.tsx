import { Title, Text, Card, Group, Button, Stack, Loader, Alert } from '@mantine/core'
import { useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import * as tripsApi from '../api/trips'
import { useTripStore } from '../store/tripStore'
import type { TripResponse } from '../types/api'

export function HomePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const setCurrentTrip = useTripStore((s) => s.setCurrentTrip)

  const { data: trips, isLoading, error } = useQuery({
    queryKey: ['trips'],
    queryFn: tripsApi.listTrips,
  })

  const deleteMutation = useMutation({
    mutationFn: tripsApi.deleteTrip,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['trips'] }),
  })

  function openTrip(trip: TripResponse) {
    setCurrentTrip(trip)
    navigate(`/trips/${encodeURIComponent(trip.place_name)}`)
  }

  return (
    <Stack>
      <Title order={2}>Saved Trips</Title>
      {isLoading && <Loader />}
      {error && <Alert color="red">Failed to load saved trips.</Alert>}
      {trips && trips.length === 0 && (
        <Text c="dimmed">No saved trips yet. Head to Explore to find your next destination.</Text>
      )}
      {trips?.map((trip) => (
        <Card key={trip.place_name} withBorder padding="lg">
          <Group justify="space-between">
            <div>
              <Text fw={600}>{trip.place_name}</Text>
              <Text size="sm" c="dimmed">
                {trip.description}
              </Text>
            </div>
            <Group>
              <Button variant="light" onClick={() => openTrip(trip)}>
                View
              </Button>
              <Button
                color="red"
                variant="subtle"
                loading={deleteMutation.isPending && deleteMutation.variables === trip.place_name}
                onClick={() => deleteMutation.mutate(trip.place_name)}
              >
                Delete
              </Button>
            </Group>
          </Group>
        </Card>
      ))}
    </Stack>
  )
}
