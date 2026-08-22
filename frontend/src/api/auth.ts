import { apiFetch } from './client'
import type { MessageResponse, TokenResponse, UserResponse } from '../types/api'

export function register(payload: {
  username: string
  password: string
  confirm_password: string
  email: string
}) {
  return apiFetch<MessageResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
    auth: false,
  })
}

export function login(username: string, password: string) {
  return apiFetch<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
    auth: false,
  })
}

export function me() {
  return apiFetch<UserResponse>('/auth/me')
}

export function logout() {
  return apiFetch<MessageResponse>('/auth/logout', { method: 'POST' })
}
