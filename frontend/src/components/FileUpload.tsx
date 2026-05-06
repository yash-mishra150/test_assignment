import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Music, Video, Loader2 } from 'lucide-react'
import { useFileUpload } from '../hooks/useFileUpload'
import type { Document } from '../types'

interface Props {
  onUploaded: (doc: Document) => void
}

const ACCEPTED = {
  'application/pdf': ['.pdf'],
  'audio/mpeg': ['.mp3'],
  'audio/wav': ['.wav'],
  'audio/ogg': ['.ogg'],
  'video/mp4': ['.mp4'],
  'video/webm': ['.webm'],
  'video/quicktime': ['.mov'],
}

function FileIcon({ type }: { type: string }) {
  if (type === 'application/pdf') return <FileText className="w-8 h-8 text-red-500" />
  if (type.startsWith('audio/')) return <Music className="w-8 h-8 text-purple-500" />
  return <Video className="w-8 h-8 text-blue-500" />
}

export function FileUpload({ onUploaded }: Props) {
  const { upload, isUploading, progress, error } = useFileUpload(onUploaded)

  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted[0]) upload(accepted[0])
    },
    [upload],
  )

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: ACCEPTED,
    maxFiles: 1,
    disabled: isUploading,
  })

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'}
          ${isUploading ? 'opacity-60 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        <Upload className="w-10 h-10 mx-auto mb-3 text-gray-400" />
        <p className="text-sm font-medium text-gray-700">
          {isDragActive ? 'Drop file here…' : 'Drag & drop or click to upload'}
        </p>
        <p className="text-xs text-gray-500 mt-1">PDF, MP3, WAV, MP4, WebM, MOV</p>
      </div>

      {isUploading && (
        <div className="mt-3">
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-1">
            <Loader2 className="w-4 h-4 animate-spin" />
            {acceptedFiles[0] && (
              <FileIcon type={acceptedFiles[0].type} />
            )}
            <span className="truncate">{acceptedFiles[0]?.name}</span>
            <span className="ml-auto font-medium">{progress}%</span>
          </div>
          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {error && (
        <p className="mt-2 text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{error}</p>
      )}
    </div>
  )
}
