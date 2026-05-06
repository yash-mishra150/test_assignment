import { Clock, Play } from 'lucide-react'
import type { TranscriptSegment } from '../types'

interface Props {
  segments: TranscriptSegment[]
  onSeek: (seconds: number) => void
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

export function TimestampList({ segments, onSeek }: Props) {
  if (segments.length === 0) return null

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 bg-gray-50 border-b border-gray-100">
        <Clock className="w-4 h-4 text-gray-500" />
        <span className="text-sm font-semibold text-gray-700">Transcript Timestamps</span>
      </div>
      <ul className="divide-y divide-gray-50 max-h-60 overflow-y-auto">
        {segments.map((seg, i) => (
          <li key={i}>
            <button
              onClick={() => onSeek(seg.start)}
              className="w-full text-left px-4 py-2.5 hover:bg-primary-50 transition-colors flex items-start gap-3 group"
            >
              <span className="flex items-center gap-1 text-xs font-mono font-semibold text-primary-600 shrink-0 mt-0.5 group-hover:text-primary-700">
                <Play className="w-3 h-3" />
                {formatTime(seg.start)}
              </span>
              <span className="text-sm text-gray-700 leading-snug line-clamp-2">{seg.text}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
