import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Title, Grid, Stack, Button, Group, Loader, Alert, Text } from '@mantine/core'
import { notifications } from '@mantine/notifications'
import * as itineraryApi from '../api/itinerary'
import * as ongoingTripsApi from '../api/ongoingTrips'
import { ItineraryByDay } from '../components/itinerary/ItineraryByDay'
import { TodoList } from '../components/todo/TodoList'
import { ChatPanel } from '../components/chat/ChatPanel'
import { ApiError } from '../api/client'

export function TripItineraryPage() {
  const { place } = useParams<{ place: string }>()
  const navigate = useNavigate()

  const itineraryQuery = useQuery({
    queryKey: ['itinerary', place],
    queryFn: () => itineraryApi.getItinerary(place!),
    enabled: !!place,
  })

  const startTripMutation = useMutation({
    mutationFn: () => ongoingTripsApi.startOngoingTrip(place!),
    onSuccess: () => navigate('/ongoing-trip'),
    onError: (e) =>
      notifications.show({
        message: e instanceof ApiError ? e.message : 'Failed to start trip',
        color: 'red',
      }),
  })

  if (!place) return <Text c="dimmed">No destination selected.</Text>

  return (
    <Stack>
      <Title order={2}>Plan your trip to {place}</Title>

      <Group>
        <Button component={Link} to="/flights" variant="light">
          Search Flights
        </Button>
        <Button component={Link} to="/accommodations" variant="light">
          Search Accommodations
        </Button>
      </Group>

      <TodoList place={place} />

      <Grid>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <ChatPanel place={place} />
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <Title order={4} mb="sm">
            Itinerary
          </Title>
          {itineraryQuery.isLoading && <Loader size="sm" />}
          {itineraryQuery.error && <Alert color="red">Could not load itinerary.</Alert>}
          {itineraryQuery.data && <ItineraryByDay itineraryByDate={itineraryQuery.data.itinerary_by_date} />}
        </Grid.Col>
      </Grid>

      <Button loading={startTripMutation.isPending} onClick={() => startTripMutation.mutate()}>
        Start Trip
      </Button>
    </Stack>
  )
}
