import { useState, useEffect } from 'react'
import { getMissingFilmsJson, getMissingFilmsCsvUrl } from '../lib/api'

interface MissingFilmsButtonProps {
  jobId: string
}

export default function MissingFilmsButton({ jobId }: MissingFilmsButtonProps) {
  const [count, setCount] = useState<number | null>(null)
  const [tmdbFound, setTmdbFound] = useState(0)
  const [tmdbNotFound, setTmdbNotFound] = useState(0)
  const [showTooltip, setShowTooltip] = useState(false)

  useEffect(() => {
    getMissingFilmsJson(jobId)
      .then(data => {
        setCount(data.count)
        setTmdbFound(data.tmdb_found)
        setTmdbNotFound(data.tmdb_not_found)
      })
      .catch(() => {})
  }, [jobId])

  if (count === null || count === 0) return null

  return (
    <div className="relative">
      <a
        href={getMissingFilmsCsvUrl(jobId)}
        download
        className="text-sm text-text-secondary hover:text-text-primary transition-colors flex items-center gap-1.5"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <span className="text-accent-yellow">{count}</span> films fetched from TMDB
      </a>
      {showTooltip && (
        <div className="absolute top-full right-0 mt-2 w-72 bg-bg-card border border-bg-hover rounded-lg p-3 shadow-xl z-50 text-sm">
          <p className="text-text-primary mb-1">
            {count} films weren't found in our database.
          </p>
          <p className="text-text-secondary text-xs">
            {tmdbFound} found via TMDB, {tmdbNotFound} not found anywhere.
          </p>
          <p className="text-text-secondary text-xs mt-1">
            Click to download the full list as CSV.
          </p>
        </div>
      )}
    </div>
  )
}
