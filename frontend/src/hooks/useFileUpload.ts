import { useState } from 'react'
import { uploadDocument, uploadMedia } from '../services/api'
import type { Document } from '../types'

interface UploadState {
  progress: number
  isUploading: boolean
  error: string | null
}

export function useFileUpload(onSuccess: (doc: Document) => void) {
  const [state, setState] = useState<UploadState>({
    progress: 0,
    isUploading: false,
    error: null,
  })

  const upload = async (file: File) => {
    setState({ progress: 0, isUploading: true, error: null })

    const isMedia = file.type.startsWith('audio/') || file.type.startsWith('video/')
    const fn = isMedia ? uploadMedia : uploadDocument

    try {
      const { data } = await fn(file, (pct) =>
        setState((s) => ({ ...s, progress: pct })),
      )
      setState({ progress: 100, isUploading: false, error: null })
      onSuccess(data)
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Upload failed. Please try again.'
      setState({ progress: 0, isUploading: false, error: msg })
    }
  }

  return { ...state, upload }
}
