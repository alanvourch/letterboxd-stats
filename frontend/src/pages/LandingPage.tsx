import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadZip, pingHealth } from '../lib/api'
import UploadZone from '../components/UploadZone'

export default function LandingPage() {
  const navigate = useNavigate()
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [serverReady, setServerReady] = useState<boolean | null>(null)

  // Warm up backend on page load
  useEffect(() => {
    const start = Date.now()
    const controller = new AbortController()
    fetch(
      `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/health`,
      { signal: controller.signal }
    )
      .then(() => setServerReady(true))
      .catch(() => {
        // If it took a while and failed, server might be waking up
        if (Date.now() - start > 5000) setServerReady(false)
      })
    return () => controller.abort()
  }, [])

  const handleUpload = async (file: File) => {
    setIsUploading(true)
    setError(null)

    try {
      const { job_id } = await uploadZip(file)
      navigate(`/dashboard/${job_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
      setIsUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Hero Section */}
      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-accent-cyan via-accent-purple to-accent-pink bg-clip-text text-transparent">
            Letterboxd Stats
          </h1>
          <p className="text-xl text-text-secondary">
            Generate beautiful visualizations of your movie watching journey
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-bg-card rounded-2xl p-8 mb-8">
          <UploadZone
            onUpload={handleUpload}
            isLoading={isUploading}
            error={error}
          />
          {serverReady === false && (
            <p className="text-center text-accent-yellow text-sm mt-4">
              Server is waking up... this may take up to 30 seconds on first visit.
            </p>
          )}
          <p className="text-center text-text-secondary text-xs mt-3">
            Processing typically takes 1-2 minutes for large libraries.
          </p>
        </div>

        {/* Privacy Notice */}
        <div className="text-center mb-8">
          <p className="text-text-secondary text-sm">
            Your data is processed in memory and deleted immediately. We don't store your films.
          </p>
        </div>

        {/* Instructions */}
        <div className="bg-bg-secondary rounded-2xl p-8">
          <h2 className="text-2xl font-semibold mb-6">How to get your data</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="flex flex-col items-center text-center p-4">
              <div className="w-12 h-12 rounded-full bg-accent-cyan/20 flex items-center justify-center mb-4">
                <span className="text-accent-cyan font-bold">1</span>
              </div>
              <h3 className="font-semibold mb-2">Go to Letterboxd</h3>
              <p className="text-text-secondary text-sm">
                Visit{' '}
                <a
                  href="https://letterboxd.com/settings/data/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent-cyan hover:underline"
                >
                  letterboxd.com/settings/data
                </a>
              </p>
            </div>
            <div className="flex flex-col items-center text-center p-4">
              <div className="w-12 h-12 rounded-full bg-accent-purple/20 flex items-center justify-center mb-4">
                <span className="text-accent-purple font-bold">2</span>
              </div>
              <h3 className="font-semibold mb-2">Export Your Data</h3>
              <p className="text-text-secondary text-sm">
                Click "Export Your Data" and download the ZIP file
              </p>
            </div>
            <div className="flex flex-col items-center text-center p-4">
              <div className="w-12 h-12 rounded-full bg-accent-pink/20 flex items-center justify-center mb-4">
                <span className="text-accent-pink font-bold">3</span>
              </div>
              <h3 className="font-semibold mb-2">Upload Here</h3>
              <p className="text-text-secondary text-sm">
                Drag and drop or click to upload your ZIP file
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
