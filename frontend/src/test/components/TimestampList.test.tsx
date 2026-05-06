import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { TimestampList } from '../../components/TimestampList'
import type { TranscriptSegment } from '../../types'

const segments: TranscriptSegment[] = [
  { start: 0, end: 10, text: 'Welcome to the show' },
  { start: 65, end: 80, text: 'Main topic discussion' },
  { start: 125, end: 140, text: 'Closing remarks' },
]

describe('TimestampList', () => {
  it('renders all segments', () => {
    render(<TimestampList segments={segments} onSeek={vi.fn()} />)
    expect(screen.getByText('Welcome to the show')).toBeInTheDocument()
    expect(screen.getByText('Main topic discussion')).toBeInTheDocument()
    expect(screen.getByText('Closing remarks')).toBeInTheDocument()
  })

  it('formats timestamps correctly', () => {
    render(<TimestampList segments={segments} onSeek={vi.fn()} />)
    expect(screen.getByText('0:00')).toBeInTheDocument()
    expect(screen.getByText('1:05')).toBeInTheDocument()
    expect(screen.getByText('2:05')).toBeInTheDocument()
  })

  it('calls onSeek with correct time when clicked', () => {
    const onSeek = vi.fn()
    render(<TimestampList segments={segments} onSeek={onSeek} />)
    fireEvent.click(screen.getByText('Welcome to the show'))
    expect(onSeek).toHaveBeenCalledWith(0)
  })

  it('renders nothing when no segments', () => {
    const { container } = render(<TimestampList segments={[]} onSeek={vi.fn()} />)
    expect(container.firstChild).toBeNull()
  })
})
