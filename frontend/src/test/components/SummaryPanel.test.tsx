import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { SummaryPanel } from '../../components/SummaryPanel'
import type { Document } from '../../types'

const pdfDoc: Document = {
  id: '1',
  filename: 'report.pdf',
  doc_type: 'pdf',
  summary: 'This document covers quarterly results.',
  total_chunks: 12,
  created_at: new Date().toISOString(),
}

describe('SummaryPanel', () => {
  it('renders filename', () => {
    render(<SummaryPanel doc={pdfDoc} />)
    expect(screen.getByText('report.pdf')).toBeInTheDocument()
  })

  it('renders summary when present', () => {
    render(<SummaryPanel doc={pdfDoc} />)
    expect(screen.getByText('This document covers quarterly results.')).toBeInTheDocument()
  })

  it('renders chunk count', () => {
    render(<SummaryPanel doc={pdfDoc} />)
    expect(screen.getByText('12 chunks')).toBeInTheDocument()
  })

  it('renders without summary gracefully', () => {
    render(<SummaryPanel doc={{ ...pdfDoc, summary: null }} />)
    expect(screen.queryByText('AI Summary')).not.toBeInTheDocument()
  })

  it('renders audio doc type', () => {
    render(<SummaryPanel doc={{ ...pdfDoc, doc_type: 'audio', filename: 'podcast.mp3' }} />)
    expect(screen.getByText('podcast.mp3')).toBeInTheDocument()
  })
})
