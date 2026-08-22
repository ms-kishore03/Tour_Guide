import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MantineProvider } from '@mantine/core'
import { ExpenseForm } from './ExpenseForm'

function renderForm(onAdd = vi.fn()) {
  render(
    <MantineProvider>
      <ExpenseForm onAdd={onAdd} />
    </MantineProvider>,
  )
  return onAdd
}

describe('ExpenseForm', () => {
  it('does not call onAdd when required fields are missing', async () => {
    const onAdd = renderForm()
    const user = userEvent.setup()
    await user.click(screen.getByRole('button', { name: /add expense/i }))
    expect(onAdd).not.toHaveBeenCalled()
  })

  it('calls onAdd with parsed values and clears the form', async () => {
    const onAdd = renderForm()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/amount/i), '25')
    await user.type(screen.getByLabelText(/category/i), 'Food')
    await user.type(screen.getByLabelText(/date/i), '01/01/2026')
    await user.click(screen.getByRole('button', { name: /add expense/i }))

    expect(onAdd).toHaveBeenCalledWith({ amount: 25, category: 'Food', date: '01/01/2026' })
    expect(screen.getByLabelText(/category/i)).toHaveValue('')
  })
})
