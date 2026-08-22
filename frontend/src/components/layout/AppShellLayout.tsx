import type { ReactNode } from 'react'
import { AppShell, Group, Button, Title } from '@mantine/core'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

const NAV_LINKS = [
  { to: '/', label: 'Home' },
  { to: '/explore', label: 'Explore' },
  { to: '/accommodations', label: 'Accommodations' },
  { to: '/flights', label: 'Flights' },
  { to: '/ongoing-trip', label: 'Ongoing Trip' },
]

export function AppShellLayout({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  return (
    <AppShell header={{ height: 60 }} padding="md">
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Title order={4}>Tour Guide</Title>
          <Group gap="sm">
            {NAV_LINKS.map((link) => (
              <Button key={link.to} component={Link} to={link.to} variant="subtle" size="sm">
                {link.label}
              </Button>
            ))}
            {user && (
              <Button
                variant="light"
                color="red"
                size="sm"
                onClick={() => {
                  logout()
                  navigate('/login')
                }}
              >
                Logout
              </Button>
            )}
          </Group>
        </Group>
      </AppShell.Header>
      <AppShell.Main>{children}</AppShell.Main>
    </AppShell>
  )
}
