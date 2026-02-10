import { useState, useEffect } from 'react'
import { getMissingFilmsJson, getMissingFilmsCsvUrl } from '../lib/api'

interface MissingFilmsButtonProps {
  jobId: string
}

export default function MissingFilmsButton({ jobId }: MissingFilmsButtonProps) {
  const [count, setCount] = useState<number | null>(null)
  const [showTooltip, setShowTooltip] = useState(false)

  useEffect(() => {
    getMissingFilmsJson(jobId)
      .then(data => setCount(data.count))
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
        <span className="text-accent-yellow">{count}</span> entries not in database
      </a>
      {showTooltip && (
        <div className="absolute top-full right-0 mt-2 w-80 bg-bg-card border border-bg-hover rounded-lg p-3 shadow-xl z-50 text-sm">
          <p className="text-text-primary mb-2">
            {count} Letterboxd entries weren't found in our film database.
          </p>
          <p className="text-text-secondary text-xs mb-1">Most common reasons:</p>
          <ul className="text-text-secondary text-xs space-y-0.5 list-disc list-inside mb-2">
            <li>TV shows &amp; limited series (e.g. Band of Brothers, Beef)</li>
            <li>Films with fewer than 1,000 IMDb votes</li>
            <li>Short films (runtime &lt; 60 min)</li>
          </ul>
          <p className="text-text-secondary text-xs">
            Click to download the full list as CSV.
          </p>
        </div>
      )}
    </div>
  )
}
