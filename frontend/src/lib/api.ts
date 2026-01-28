const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function uploadZip(file: File): Promise<{ job_id: string }> {
  const formData = new FormData()
  formData.append('zip_file', file)

  const response = await fetch(`${API_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Upload failed')
  }

  return response.json()
}

export function getStatusUrl(jobId: string): string {
  return `${API_URL}/api/status/${jobId}`
}

export async function getResultJson(jobId: string): Promise<{ stats: unknown; charts: unknown }> {
  const response = await fetch(`${API_URL}/api/result/${jobId}/json`)
  if (!response.ok) {
    throw new Error('Failed to fetch results')
  }
  return response.json()
}

export function getDownloadUrl(jobId: string): string {
  return `${API_URL}/api/result/${jobId}/html`
}
