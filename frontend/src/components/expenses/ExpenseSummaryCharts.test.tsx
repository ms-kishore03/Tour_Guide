import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MantineProvider } from '@mantine/core'
import { ExpenseSummaryCharts } from './ExpenseSummaryCharts'

describe('ExpenseSummaryCharts', () => {
  it('sums total and groups amounts by category', () => {
    render(
      <MantineProvider>
        <ExpenseSummaryCharts
          expenses={[
            { amount: 10, category: 'Food', date: '01/01/2026' },
            { amount: 5, category: 'Food', date: '01/02/2026' },
            { amount: 20, category: 'Transport', date: '01/01/2026' },
          ]}
        />
      </MantineProvider>,
    )

    expect(screen.getByText('Total: 35.00')).toBeInTheDocument()
    expect(screen.getByText('Food: 15.00')).toBeInTheDocument()
    expect(screen.getByText('Transport: 20.00')).toBeInTheDocument()
  })

  it('shows a zero total for no expenses', () => {
    render(
      <MantineProvider>
        <ExpenseSummaryCharts expenses={[]} />
      </MantineProvider>,
    )
    expect(screen.getByText('Total: 0.00')).toBeInTheDocument()
  })
})
