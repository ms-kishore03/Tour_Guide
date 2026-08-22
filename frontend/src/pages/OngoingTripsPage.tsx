import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Title, Stack, Text, Button, Loader } from '@mantine/core'
import * as ongoingTripsApi from '../api/ongoingTrips'
import { ExpenseForm, type ExpenseFormValues } from '../components/expenses/ExpenseForm'
import { ExpenseTable } from '../components/expenses/ExpenseTable'
import { ExpenseSummaryCharts } from '../components/expenses/ExpenseSummaryCharts'
import { ItineraryByDay } from '../components/itinerary/ItineraryByDay'
import * as itineraryApi from '../api/itinerary'

export function OngoingTripsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: trip, isLoading } = useQuery({
    queryKey: ['ongoing-trip'],
    queryFn: ongoingTripsApi.getOngoingTrip,
  })

  const place = trip?.place

  const itineraryQuery = useQuery({
    queryKey: ['itinerary', place],
    queryFn: () => itineraryApi.getItinerary(place!),
    enabled: !!place,
  })

  const addExpenseMutation = useMutation({
    mutationFn: (values: ExpenseFormValues) => ongoingTripsApi.addExpense(place!, values),
    onSuccess: (expenses) =>
      queryClient.setQueryData(['ongoing-trip'], (prev: typeof trip) => (prev ? { ...prev, expenses } : prev)),
  })

  const endTripMutation = useMutation({
    mutationFn: () => ongoingTripsApi.endOngoingTrip(place!),
    onSuccess: () => {
      queryClient.setQueryData(['ongoing-trip'], null)
      navigate('/')
    },
  })

  if (isLoading) return <Loader />
  if (!trip) return <Text c="dimmed">No ongoing trip. Start planning a trip first.</Text>

  return (
    <Stack>
      <Title order={2}>Ongoing Trip: {trip.place}</Title>

      {itineraryQuery.data && <ItineraryByDay itineraryByDate={itineraryQuery.data.itinerary_by_date} />}

      <Title order={4}>Expenses</Title>
      <ExpenseForm onAdd={(v) => addExpenseMutation.mutate(v)} loading={addExpenseMutation.isPending} />
      <ExpenseTable expenses={trip.expenses} />
      <ExpenseSummaryCharts expenses={trip.expenses} />

      <Button color="red" loading={endTripMutation.isPending} onClick={() => endTripMutation.mutate()}>
        End Trip
      </Button>
    </Stack>
  )
}
