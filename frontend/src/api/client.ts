import { useAuthStore } from '../store/authStore'
import type { TokenResponse } from '../types/api'

export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

let refreshPromise: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  const { refreshToken, setAccessToken, logout } = useAuthStore.getState()
  if (!refreshToken) return null
  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
    if (!res.ok) {
      logout()
      return null
    }
    const data: TokenResponse = await res.json()
    useAuthStore.getState().setSession(data.access_token, data.refresh_token, useAuthStore.getState().user)
    setAccessToken(data.access_token)
    return data.access_token
  } catch {
    logout()
    return null
  }
}

interface RequestOptions extends RequestInit {
  auth?: boolean
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { auth = true, headers, ...rest } = options
  const doFetch = async (token: string | null) => {
    const h: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(headers as Record<string, string> | undefined),
    }
    if (auth && token) h.Authorization = `Bearer ${token}`
    return fetch(`${API_BASE}${path}`, { ...rest, headers: h })
  }

  let token = useAuthStore.getState().accessToken
  let res = await doFetch(token)

  if (res.status === 401 && auth) {
    if (!refreshPromise) refreshPromise = refreshAccessToken().finally(() => (refreshPromise = null))
    token = await refreshPromise
    if (token) res = await doFetch(token)
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new ApiError(res.status, body.detail ?? res.statusText)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}
