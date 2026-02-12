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
      className="glass-card glass-card-interactive p-5 cursor-pointer"
    >
      <div className="flex gap-4 items-center">
        {/* Rank */}
        <span className="text-accent-cyan font-bold text-lg">#{rank}</span>

        {/* Logo */}
        <div className="w-20 h-20 rounded-xl overflow-hidden flex items-center justify-center">
          {logoUrl ? (
            <div className="w-full h-full bg-white p-2 flex items-center justify-center">
              <img
                src={logoUrl}
                alt={studio.name}
                className="max-w-full max-h-full object-contain"
              />
            </div>
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center text-white text-2xl font-bold rounded-xl">
              {studio.name.charAt(0)}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold truncate">{studio.name}</h3>
          <div className="text-text-secondary text-sm">
            <p>{studio.count} films</p>
            <p className="text-accent-yellow">★ {studio.avg_rating.toFixed(1)} avg</p>
          </div>
        </div>
      </div>
    </div>
  )
}
