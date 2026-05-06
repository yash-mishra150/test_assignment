import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileText, Music, Video, LogOut, Plus } from 'lucide-react'
import { listDocuments, logout, getTranscript } from '../services/api'
import { FileUpload } from '../components/FileUpload'
import { SummaryPanel } from '../components/SummaryPanel'
import { ChatInterface } from '../components/ChatInterface'
import { MediaPlayer, MediaPlayerHandle } from '../components/MediaPlayer'
import { TimestampList } from '../components/TimestampList'
import type { Document, TranscriptSegment } from '../types'

const docIcon = (type: Document['doc_type']) => {
  if (type === 'pdf') return <FileText className="w-4 h-4 text-red-500" />
  if (type === 'audio') return <Music className="w-4 h-4 text-purple-500" />
  return <Video className="w-4 h-4 text-blue-500" />
}

export function Dashboard() {
  const navigate = useNavigate()
  const [documents, setDocuments] = useState<Document[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [activeDoc, setActiveDoc] = useState<Document | null>(null)
  const [segments, setSegments] = useState<TranscriptSegment[]>([])
  const [showUpload, setShowUpload] = useState(false)
  const mediaRef = useRef<MediaPlayerHandle>(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) { navigate('/login'); return }
    listDocuments().then((r) => setDocuments(r.data)).catch(() => navigate('/login'))
  }, [navigate])

  const handleUploaded = (doc: Document) => {
    setDocuments((prev) => [doc, ...prev])
    setActiveDoc(doc)
    setShowUpload(false)
    if (doc.doc_type !== 'pdf') {
      getTranscript(doc.id).then((r) => setSegments(r.data.segments)).catch(() => {})
    } else {
      setSegments([])
    }
  }

  const handleSelectDoc = (doc: Document) => {
    setActiveDoc(doc)
    if (doc.doc_type !== 'pdf') {
      getTranscript(doc.id).then((r) => setSegments(r.data.segments)).catch(() => {})
    } else {
      setSegments([])
    }
  }

  const toggleDocForChat = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const handleSeekTimestamp = (_docId: string, seconds: number) => {
    mediaRef.current?.seekTo(seconds)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Topbar */}
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-primary-600" />
          <span className="font-bold text-gray-900">DocQA</span>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign out
        </button>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-72 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-100">
            <button
              onClick={() => setShowUpload((v) => !v)}
              className="w-full flex items-center justify-center gap-2 bg-primary-600 text-white
                rounded-xl py-2.5 text-sm font-medium hover:bg-primary-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Upload File
            </button>
            {showUpload && (
              <div className="mt-3">
                <FileUpload onUploaded={handleUploaded} />
              </div>
            )}
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-1">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide px-2 mb-2">
              Documents ({documents.length})
            </p>
            {documents.length === 0 && (
              <p className="text-sm text-gray-400 text-center py-8">No files yet</p>
            )}
            {documents.map((doc) => (
              <div
                key={doc.id}
                className={`group flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors
                  ${activeDoc?.id === doc.id ? 'bg-primary-50' : 'hover:bg-gray-50'}`}
                onClick={() => handleSelectDoc(doc)}
              >
                <input
                  type="checkbox"
                  checked={selected.has(doc.id)}
                  onChange={(e) => { e.stopPropagation(); toggleDocForChat(doc.id) }}
                  className="rounded text-primary-600 shrink-0"
                  title="Include in chat context"
                />
                {docIcon(doc.doc_type)}
                <span className="text-sm text-gray-700 truncate flex-1">{doc.filename}</span>
              </div>
            ))}
          </div>

          {selected.size > 0 && (
            <div className="p-3 border-t border-gray-100 bg-primary-50">
              <p className="text-xs text-primary-700 font-medium">
                {selected.size} file{selected.size > 1 ? 's' : ''} selected for chat
              </p>
            </div>
          )}
        </aside>

        {/* Main content */}
        <main className="flex-1 flex overflow-hidden">
          {/* Document detail */}
          <div className="w-80 border-r border-gray-200 bg-white flex flex-col gap-4 p-4 overflow-y-auto">
            {activeDoc ? (
              <>
                <SummaryPanel doc={activeDoc} />
                {activeDoc.doc_type !== 'pdf' && (
                  <MediaPlayer
                    ref={mediaRef}
                    docId={activeDoc.id}
                    docType={activeDoc.doc_type}
                    filename={activeDoc.filename}
                  />
                )}
                {segments.length > 0 && (
                  <TimestampList
                    segments={segments}
                    onSeek={(s) => mediaRef.current?.seekTo(s)}
                  />
                )}
              </>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-center text-gray-400 py-12">
                <FileText className="w-10 h-10 mb-3 opacity-30" />
                <p className="text-sm">Select a document to preview</p>
              </div>
            )}
          </div>

          {/* Chat */}
          <div className="flex-1 p-4">
            <ChatInterface
              docIds={Array.from(selected)}
              onSeekTimestamp={handleSeekTimestamp}
            />
          </div>
        </main>
      </div>
    </div>
  )
}
