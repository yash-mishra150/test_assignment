export interface User {
  id: string
  email: string
  full_name: string
  created_at: string
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
}

export type DocType = 'pdf' | 'audio' | 'video'

export interface Document {
  id: string
  filename: string
  doc_type: DocType
  summary: string | null
  total_chunks: number
  created_at: string
}

export interface TranscriptSegment {
  start: number
  end: number
  text: string
}

export interface SourceRef {
  doc_id: string
  filename: string
  page: number | null
  start_sec: number | null
  end_sec: number | null
  score: number
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: SourceRef[]
  isStreaming?: boolean
}
