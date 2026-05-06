import { useEffect, useRef, useState } from 'react'
import { Send, Square, FileText, Clock } from 'lucide-react'
import { useChat } from '../hooks/useChat'
import type { ChatMessage, SourceRef } from '../types'

interface Props {
  docIds: string[]
  onSeekTimestamp?: (docId: string, seconds: number) => void
}

function SourceBadge({
  source,
  onSeek,
}: {
  source: SourceRef
  onSeek?: (docId: string, seconds: number) => void
}) {
  const hasTimestamp = source.start_sec !== null && source.start_sec !== undefined

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60)
    const sec = Math.floor(s % 60)
    return `${m}:${sec.toString().padStart(2, '0')}`
  }

  return (
    <button
      onClick={() =>
        hasTimestamp && onSeek
          ? onSeek(source.doc_id, source.start_sec!)
          : undefined
      }
      className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border
        ${hasTimestamp
          ? 'bg-purple-50 border-purple-200 text-purple-700 hover:bg-purple-100 cursor-pointer'
          : 'bg-gray-50 border-gray-200 text-gray-600 cursor-default'
        }`}
    >
      {hasTimestamp ? <Clock className="w-3 h-3" /> : <FileText className="w-3 h-3" />}
      <span className="truncate max-w-[120px]">{source.filename}</span>
      {source.page && <span>p.{source.page}</span>}
      {hasTimestamp && <span>{formatTime(source.start_sec!)}</span>}
    </button>
  )
}

function MessageBubble({
  message,
  onSeek,
}: {
  message: ChatMessage
  onSeek?: (docId: string, seconds: number) => void
}) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed
            ${isUser
              ? 'bg-primary-600 text-white rounded-br-sm'
              : 'bg-white border border-gray-200 text-gray-800 rounded-bl-sm shadow-sm'
            }`}
        >
          {message.content}
          {message.isStreaming && (
            <span className="inline-block w-1.5 h-4 bg-current animate-pulse ml-0.5 align-text-bottom" />
          )}
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap gap-1 px-1">
            {message.sources.map((s, i) => (
              <SourceBadge key={i} source={s} onSeek={onSeek} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export function ChatInterface({ docIds, onSeekTimestamp }: Props) {
  const [input, setInput] = useState('')
  const { messages, isStreaming, sendMessage, abort } = useChat(docIds)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = () => {
    const q = input.trim()
    if (!q || isStreaming) return
    setInput('')
    sendMessage(q)
    inputRef.current?.focus()
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="flex flex-col h-full bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
      {/* Message list */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center text-gray-400 py-12">
            <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center mb-3">
              <Send className="w-5 h-5 text-primary-500" />
            </div>
            <p className="font-medium text-gray-600">Ask anything about your documents</p>
            <p className="text-sm mt-1">Upload files and start asking questions</p>
          </div>
        )}
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} onSeek={onSeekTimestamp} />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 bg-white p-3 flex items-end gap-2">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question… (Enter to send)"
          rows={1}
          className="flex-1 resize-none rounded-xl border border-gray-300 px-3 py-2.5 text-sm
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
            max-h-32 overflow-y-auto"
          style={{ minHeight: '42px' }}
        />
        {isStreaming ? (
          <button
            onClick={abort}
            className="p-2.5 rounded-xl bg-red-100 text-red-600 hover:bg-red-200 transition-colors"
            title="Stop"
          >
            <Square className="w-4 h-4" />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!input.trim()}
            className="p-2.5 rounded-xl bg-primary-600 text-white hover:bg-primary-700
              disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            title="Send"
          >
            <Send className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  )
}
