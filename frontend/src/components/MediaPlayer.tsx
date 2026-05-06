import { forwardRef, useImperativeHandle, useRef } from 'react'
import { getMediaFileUrl } from '../services/api'
import type { DocType } from '../types'

export interface MediaPlayerHandle {
  seekTo: (seconds: number) => void
}

interface Props {
  docId: string
  docType: DocType
  filename: string
}

export const MediaPlayer = forwardRef<MediaPlayerHandle, Props>(
  ({ docId, docType, filename }, ref) => {
    const mediaRef = useRef<HTMLVideoElement | HTMLAudioElement>(null)

    useImperativeHandle(ref, () => ({
      seekTo: (seconds: number) => {
        if (mediaRef.current) {
          mediaRef.current.currentTime = seconds
          mediaRef.current.play().catch(() => {})
        }
      },
    }))

    const src = getMediaFileUrl(docId)

    if (docType === 'video') {
      return (
        <div className="rounded-xl overflow-hidden bg-black">
          <video
            ref={mediaRef as React.RefObject<HTMLVideoElement>}
            src={src}
            controls
            className="w-full max-h-72"
            title={filename}
          />
        </div>
      )
    }

    return (
      <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
        <p className="text-xs text-gray-500 mb-2 truncate">{filename}</p>
        <audio
          ref={mediaRef as React.RefObject<HTMLAudioElement>}
          src={src}
          controls
          className="w-full"
        />
      </div>
    )
  },
)
MediaPlayer.displayName = 'MediaPlayer'
