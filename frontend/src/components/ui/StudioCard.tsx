const TMDB_IMG = 'https://image.tmdb.org/t/p/w185'

interface Film {
  title: string
  year: number
  rating?: number
  poster_path?: string
  liked?: boolean
}

interface Studio {
  name: string
  count: number
  avg_rating: number
  logo_path?: string
  films: Film[]
}

interface StudioCardProps {
  studio: Studio
  rank: number
  onClick: () => void
}

export default function StudioCard({ studio, rank, onClick }: StudioCardProps) {
  const logoUrl = studio.logo_path
    ? `${TMDB_IMG}${studio.logo_path}`
    : null

  return (
    <div
      onClick={onClick}
      className="bg-bg-card rounded-xl p-4 cursor-pointer hover:bg-bg-hover transition-colors"
    >
      <div className="flex gap-4 items-center">
        {/* Rank */}
        <span className="text-accent-cyan font-bold text-lg">#{rank}</span>

        {/* Logo */}
        <div className="w-16 h-16 rounded-lg overflow-hidden bg-white flex items-center justify-center p-2">
          {logoUrl ? (
            <img
              src={logoUrl}
              alt={studio.name}
              className="max-w-full max-h-full object-contain"
            />
          ) : (
            <span className="text-bg-primary text-xs text-center">{studio.name.slice(0, 10)}</span>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold truncate">{studio.name}</h3>
          <div className="text-text-secondary text-sm">
            <p>{studio.count} films</p>
            <p>★ {studio.avg_rating.toFixed(1)} avg</p>
          </div>
        </div>
      </div>
    </div>
  )
}
