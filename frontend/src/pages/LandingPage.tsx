import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadZip } from '../lib/api'
import UploadZone from '../components/UploadZone'

export default function LandingPage() {
  const navigate = useNavigate()
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
        <div className="bg-bg-card rounded-2xl p-8 mb-12">
          <UploadZone
            onUpload={handleUpload}
            isLoading={isUploading}
            error={error}
          />
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
