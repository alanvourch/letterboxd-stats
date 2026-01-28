import { useState, useEffect } from 'react'
import { getStatusUrl } from '../lib/api'

interface JobProgress {
  step: string
  message: string
  percent: number
}

interface UseJobStatusResult {
  status: 'connecting' | 'progress' | 'complete' | 'error'
  progress: JobProgress | null
  error: string | null
}

export function useJobStatus(jobId: string | null): UseJobStatusResult {
  const [status, setStatus] = useState<UseJobStatusResult['status']>('connecting')
  const [progress, setProgress] = useState<JobProgress | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!jobId) return

    const eventSource = new EventSource(getStatusUrl(jobId))

    eventSource.addEventListener('progress', (e) => {
      const data = JSON.parse(e.data)
      setProgress(data)
      setStatus('progress')
    })

    eventSource.addEventListener('complete', () => {
      setStatus('complete')
      eventSource.close()
    })

    eventSource.addEventListener('error', (e) => {
      if (e instanceof MessageEvent) {
        const data = JSON.parse(e.data)
        setError(data.error)
      }
      setStatus('error')
      eventSource.close()
    })

    eventSource.onerror = () => {
      setError('Connection lost')
      setStatus('error')
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [jobId])

  return { status, progress, error }
}
