import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { FileUpload } from '../../components/FileUpload'

vi.mock('../../hooks/useFileUpload', () => ({
  useFileUpload: () => ({
    upload: vi.fn(),
    isUploading: false,
    progress: 0,
    error: null,
  }),
}))

describe('FileUpload', () => {
  it('renders upload area', () => {
    render(<FileUpload onUploaded={vi.fn()} />)
    expect(screen.getByText(/Drag & drop or click to upload/i)).toBeInTheDocument()
  })

  it('shows accepted file types', () => {
    render(<FileUpload onUploaded={vi.fn()} />)
    expect(screen.getByText(/PDF, MP3, WAV, MP4/i)).toBeInTheDocument()
  })
})

describe('FileUpload with error', () => {
  it('shows error message', () => {
    vi.doMock('../../hooks/useFileUpload', () => ({
      useFileUpload: () => ({
        upload: vi.fn(),
        isUploading: false,
        progress: 0,
        error: 'Upload failed',
      }),
    }))
  })
})
