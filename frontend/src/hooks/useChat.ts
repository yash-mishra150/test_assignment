import { useCallback, useRef, useState } from 'react'
import { streamChat } from '../services/api'
import type { ChatMessage, SourceRef } from '../types'

export function useChat(docIds: string[]) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const abortRef = useRef<(() => void) | null>(null)

  const sendMessage = useCallback(
    (query: string) => {
      if (!query.trim() || isStreaming) return

      const userMsg: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: query,
      }
      const assistantId = (Date.now() + 1).toString()
      const assistantMsg: ChatMessage = {
        id: assistantId,
        role: 'assistant',
        content: '',
        isStreaming: true,
      }

      setMessages((prev) => [...prev, userMsg, assistantMsg])
      setIsStreaming(true)

      abortRef.current = streamChat(
        query,
        docIds,
        (token) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: m.content + token } : m,
            ),
          )
        },
        (sources) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, sources: sources as SourceRef[] } : m,
            ),
          )
        },
        () => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, isStreaming: false } : m,
            ),
          )
          setIsStreaming(false)
        },
        (err) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: `Error: ${err.message}`, isStreaming: false }
                : m,
            ),
          )
          setIsStreaming(false)
        },
      )
    },
    [docIds, isStreaming],
  )

  const abort = useCallback(() => {
    abortRef.current?.()
    setIsStreaming(false)
    setMessages((prev) =>
      prev.map((m) => (m.isStreaming ? { ...m, isStreaming: false } : m)),
    )
  }, [])

  const clearMessages = useCallback(() => setMessages([]), [])

  return { messages, isStreaming, sendMessage, abort, clearMessages }
}
