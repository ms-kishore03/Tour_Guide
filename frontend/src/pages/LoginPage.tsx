import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Tabs, TextInput, PasswordInput, Button, Paper, Title, Stack, Alert, Container } from '@mantine/core'
import { useForm } from '@mantine/form'
import * as authApi from '../api/auth'
import { useAuthStore } from '../store/authStore'
import { ApiError } from '../api/client'

interface LoginValues {
  username: string
  password: string
}

interface RegisterValues {
  username: string
  email: string
  password: string
  confirm_password: string
}

export function LoginPage() {
  const navigate = useNavigate()
  const setSession = useAuthStore((s) => s.setSession)
  const [tab, setTab] = useState<string | null>('login')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const loginForm = useForm<LoginValues>({
    initialValues: { username: '', password: '' },
    validate: {
      username: (v) => (v.trim() ? null : 'Username is required'),
      password: (v) => (v ? null : 'Password is required'),
    },
  })

  const registerForm = useForm<RegisterValues>({
    initialValues: { username: '', email: '', password: '', confirm_password: '' },
    validate: {
      username: (v) => (v.trim() ? null : 'Username is required'),
      email: (v) => (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? null : 'Invalid email'),
      password: (v) => (v.length >= 6 ? null : 'Password must be at least 6 characters'),
      confirm_password: (v, values) => (v === values.password ? null : 'Passwords do not match'),
    },
  })

  async function handleLogin(values: LoginValues) {
    setError(null)
    setSubmitting(true)
    try {
      const tokens = await authApi.login(values.username, values.password)
      setSession(tokens.access_token, tokens.refresh_token, null)
      const user = await authApi.me()
      setSession(tokens.access_token, tokens.refresh_token, user)
      navigate('/')
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Login failed')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleRegister(values: RegisterValues) {
    setError(null)
    setSuccess(null)
    setSubmitting(true)
    try {
      await authApi.register(values)
      setSuccess('Registered successfully. You can now log in.')
      setTab('login')
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Registration failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Container size={420} my={80}>
      <Title order={2} ta="center" mb="md">
        Tour Guide
      </Title>
      <Paper withBorder shadow="md" p="xl" radius="md">
        <Tabs value={tab} onChange={setTab} keepMounted={false}>
          <Tabs.List grow>
            <Tabs.Tab value="login">Login</Tabs.Tab>
            <Tabs.Tab value="register">Register</Tabs.Tab>
          </Tabs.List>

          <Tabs.Panel value="login" pt="md">
            <form onSubmit={loginForm.onSubmit(handleLogin)}>
              <Stack>
                {error && tab === 'login' && <Alert color="red">{error}</Alert>}
                <TextInput label="Username" {...loginForm.getInputProps('username')} />
                <PasswordInput label="Password" {...loginForm.getInputProps('password')} />
                <Button type="submit" loading={submitting} fullWidth>
                  Log in
                </Button>
              </Stack>
            </form>
          </Tabs.Panel>

          <Tabs.Panel value="register" pt="md">
            <form onSubmit={registerForm.onSubmit(handleRegister)}>
              <Stack>
                {error && tab === 'register' && <Alert color="red">{error}</Alert>}
                {success && <Alert color="green">{success}</Alert>}
                <TextInput label="Username" {...registerForm.getInputProps('username')} />
                <TextInput label="Email" {...registerForm.getInputProps('email')} />
                <PasswordInput label="Password" {...registerForm.getInputProps('password')} />
                <PasswordInput label="Confirm password" {...registerForm.getInputProps('confirm_password')} />
                <Button type="submit" loading={submitting} fullWidth>
                  Register
                </Button>
              </Stack>
            </form>
          </Tabs.Panel>
        </Tabs>
      </Paper>
    </Container>
  )
}
