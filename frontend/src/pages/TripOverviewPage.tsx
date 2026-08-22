import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  Title,
  Text,
  Grid,
  Stack,
  Accordion,
  List,
  Button,
  Group,
  Loader,
  Alert,
  Card,
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import * as tripsApi from '../api/trips'
import * as attractionsApi from '../api/attractions'
import * as weatherApi from '../api/weather'
import { useTripStore } from '../store/tripStore'
import { ApiError } from '../api/client'
import { ChatPanel } from '../components/chat/ChatPanel'

export function TripOverviewPage() {
  const { place } = useParams<{ place: string }>()
  const navigate = useNavigate()
  const currentTrip = useTripStore((s) => s.currentTrip)

  const tripQuery = useQuery({
    queryKey: ['trip', place],
    queryFn: () => tripsApi.getTrip(place!),
    enabled: !!place,
    initialData: currentTrip?.place_name === place ? currentTrip : undefined,
    retry: false,
  })

  const attractionsQuery = useQuery({
    queryKey: ['attractions', place],
    queryFn: () => attractionsApi.getAttractions(place!),
    enabled: !!place,
  })

  const weatherQuery = useQuery({
    queryKey: ['weather', place],
    queryFn: () => weatherApi.getWeather(place!),
    enabled: !!place,
  })

  const saveMutation = useMutation({
    mutationFn: () => tripsApi.saveTrip(trip!),
    onSuccess: () => {
      notifications.show({ message: 'Trip saved!', color: 'green' })
      navigate('/')
    },
    onError: (e) =>
      notifications.show({
        message: e instanceof ApiError ? e.message : 'Failed to save trip',
        color: 'red',
      }),
  })

  const planMutation = useMutation({
    mutationFn: () => tripsApi.startPlanning(place!),
    onSuccess: () => navigate(`/trips/${encodeURIComponent(place!)}/itinerary`),
    onError: (e) =>
      notifications.show({
        message: e instanceof ApiError ? e.message : 'Failed to start planning',
        color: 'red',
      }),
  })

  const trip = tripQuery.data ?? currentTrip ?? undefined

  if (!place) return <Text c="dimmed">No destination selected.</Text>

  return (
    <Stack>
      <Title order={2}>Trip to {place}</Title>

      {trip && (
        <Card withBorder>
          <List size="sm" spacing="xs">
            <List.Item>Scenario: {trip.scenario}</List.Item>
            <List.Item>Climate: {trip.climate}</List.Item>
            <List.Item>Duration: {trip.duration}</List.Item>
            <List.Item>People: {trip.people}</List.Item>
            <List.Item>Transport: {trip.transport}</List.Item>
            <List.Item>{trip.description}</List.Item>
          </List>
        </Card>
      )}

      <Grid>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <Accordion defaultValue={['attractions', 'weather']} multiple>
            <Accordion.Item value="attractions">
              <Accordion.Control>Things to Do</Accordion.Control>
              <Accordion.Panel>
                {attractionsQuery.isLoading && <Loader size="sm" />}
                {attractionsQuery.error && <Alert color="red">Could not load attractions.</Alert>}
                <List type="ordered" size="sm">
                  {attractionsQuery.data?.places.map((p) => (
                    <List.Item key={p}>{p}</List.Item>
                  ))}
                </List>
              </Accordion.Panel>
            </Accordion.Item>
            <Accordion.Item value="weather">
              <Accordion.Control>Weather Information</Accordion.Control>
              <Accordion.Panel>
                {weatherQuery.isLoading && <Loader size="sm" />}
                {weatherQuery.error && <Alert color="red">Could not load weather.</Alert>}
                {weatherQuery.data && <Text size="sm">{weatherQuery.data.explanation}</Text>}
              </Accordion.Panel>
            </Accordion.Item>
          </Accordion>
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <ChatPanel place={place} />
        </Grid.Col>
      </Grid>

      <Group>
        <Button loading={saveMutation.isPending} onClick={() => saveMutation.mutate()} disabled={!trip}>
          Save Trip
        </Button>
        <Button loading={planMutation.isPending} onClick={() => planMutation.mutate()} variant="light">
          Start Planning
        </Button>
        <Button variant="subtle" onClick={() => navigate('/')}>
          Back to Home
        </Button>
      </Group>
    </Stack>
  )
}
