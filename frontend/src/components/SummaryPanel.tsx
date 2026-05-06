import { FileText, Music, Video, Sparkles } from 'lucide-react'
import type { Document } from '../types'

interface Props {
  doc: Document
}

const icons = {
  pdf: <FileText className="w-5 h-5 text-red-500" />,
  audio: <Music className="w-5 h-5 text-purple-500" />,
  video: <Video className="w-5 h-5 text-blue-500" />,
}

export function SummaryPanel({ doc }: Props) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        {icons[doc.doc_type]}
        <span className="font-medium text-gray-800 truncate">{doc.filename}</span>
        <span className="ml-auto text-xs text-gray-400">{doc.total_chunks} chunks</span>
      </div>

      {doc.summary && (
        <div className="bg-amber-50 border border-amber-100 rounded-lg p-3">
          <div className="flex items-center gap-1.5 mb-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            <span className="text-xs font-semibold text-amber-700 uppercase tracking-wide">
              AI Summary
            </span>
          </div>
          <p className="text-sm text-gray-700 leading-relaxed">{doc.summary}</p>
        </div>
      )}
    </div>
  )
}
