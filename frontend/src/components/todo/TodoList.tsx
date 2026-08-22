import { useState } from 'react'
import { Stack, TextInput, Button, Checkbox, Group, Title } from '@mantine/core'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as itineraryApi from '../../api/itinerary'

export function TodoList({ place }: { place: string }) {
  const queryClient = useQueryClient()
  const [task, setTask] = useState('')

  const { data: todos } = useQuery({
    queryKey: ['todos', place],
    queryFn: () => itineraryApi.getTodos(place),
  })

  const addMutation = useMutation({
    mutationFn: (t: string) => itineraryApi.addTodo(place, t),
    onSuccess: (updated) => queryClient.setQueryData(['todos', place], updated),
  })

  function handleAdd() {
    if (!task.trim()) return
    addMutation.mutate(task)
    setTask('')
  }

  return (
    <Stack gap="xs">
      <Title order={5}>To-do</Title>
      {todos?.map((t, i) => (
        <Checkbox key={i} label={t} readOnly checked={false} />
      ))}
      <Group>
        <TextInput
          flex={1}
          placeholder="Add a task"
          value={task}
          onChange={(e) => setTask(e.currentTarget.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
        />
        <Button onClick={handleAdd} loading={addMutation.isPending}>
          Add
        </Button>
      </Group>
    </Stack>
  )
}
