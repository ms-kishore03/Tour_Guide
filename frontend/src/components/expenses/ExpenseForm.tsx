import { useState } from 'react'
import { NumberInput, TextInput, Button, Group } from '@mantine/core'

export interface ExpenseFormValues {
  amount: number
  category: string
  date: string
}

export function ExpenseForm({ onAdd, loading }: { onAdd: (values: ExpenseFormValues) => void; loading?: boolean }) {
  const [amount, setAmount] = useState<number | string>('')
  const [category, setCategory] = useState('')
  const [date, setDate] = useState('')

  function handleSubmit() {
    if (!amount || !category || !date) return
    onAdd({ amount: Number(amount), category, date })
    setAmount('')
    setCategory('')
    setDate('')
  }

  return (
    <Group align="flex-end">
      <NumberInput label="Amount" value={amount} onChange={setAmount} min={0} />
      <TextInput label="Category" value={category} onChange={(e) => setCategory(e.currentTarget.value)} />
      <TextInput label="Date" placeholder="MM/DD/YYYY" value={date} onChange={(e) => setDate(e.currentTarget.value)} />
      <Button onClick={handleSubmit} loading={loading}>
        Add Expense
      </Button>
    </Group>
  )
}
