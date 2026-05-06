import axios from 'axios'
import type { Document, TokenPair, TranscriptSegment, User } from '../types'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({ baseURL: BASE_URL })

// Attach JWT on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post<TokenPair>(`${BASE_URL}/auth/refresh`, {
            refresh_token: refresh,
          })
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)
          original.headers.Authorization = `Bearer ${data.access_token}`
          return api(original)
        } catch {
          localStorage.clear()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  },
)

// ─── Auth ─────────────────────────────────────────────────────────────────

export const register = (email: string, password: string, full_name: string) =>
  api.post<User>('/auth/register', { email, password, full_name })

export const login = async (email: string, password: string): Promise<TokenPair> => {
  const { data } = await api.post<TokenPair>('/auth/login', { email, password })
  localStorage.setItem('access_token', data.access_token)
  localStorage.setItem('refresh_token', data.refresh_token)
  return data
}

export const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

// ─── Documents ────────────────────────────────────────────────────────────

export const uploadDocument = (file: File, onProgress?: (pct: number) => void) => {
  const form = new FormData()
  form.append('file', file)
  return api.post<Document>('/documents/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total) onProgress?.(Math.round((e.loaded * 100) / e.total))
    },
  })
}

export const listDocuments = () => api.get<Document[]>('/documents/')

export const getDocument = (id: string) => api.get<Document>(`/documents/${id}`)

// ─── Media ────────────────────────────────────────────────────────────────

export const uploadMedia = (file: File, onProgress?: (pct: number) => void) => {
  const form = new FormData()
  form.append('file', file)
  return api.post<Document>('/media/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total) onProgress?.(Math.round((e.loaded * 100) / e.total))
    },
  })
}

export const getTranscript = (docId: string) =>
  api.get<{ doc_id: string; segments: TranscriptSegment[] }>(`/media/${docId}/transcript`)

export const getMediaFileUrl = (docId: string) => `${BASE_URL}/media/${docId}/file`

// ─── Chat (SSE) ───────────────────────────────────────────────────────────

export const streamChat = (
  query: string,
  docIds: string[],
  onToken: (token: string) => void,
  onSources: (sources: unknown[]) => void,
  onDone: () => void,
  onError: (err: Error) => void,
): (() => void) => {
  const token = localStorage.getItem('access_token')
  const controller = new AbortController()

  fetch(`${BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({ query, doc_ids: docIds }),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (line.startsWith('event: token')) continue
          if (line.startsWith('event: sources')) continue
          if (line.startsWith('event: done')) { onDone(); return }
          if (line.startsWith('data: ')) {
            const raw = line.slice(6)
            // Try parse as sources array first
            try {
              const parsed = JSON.parse(raw)
              if (Array.isArray(parsed)) { onSources(parsed); continue }
            } catch { /* not JSON */ }
            if (raw !== '') onToken(raw)
          }
        }
      }
      onDone()
    })
    .catch((err) => {
      if (err.name !== 'AbortError') onError(err)
    })

  return () => controller.abort()
}
