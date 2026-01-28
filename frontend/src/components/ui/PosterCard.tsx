const TMDB_IMG = 'https://image.tmdb.org/t/p/w185'

interface Film {
  title: string
  year: number
  rating?: number
  poster_path?: string
  liked?: boolean
}

interface PosterCardProps {
  film: Film
  size?: 'sm' | 'md' | 'lg'
}

const sizes = {
  sm: 'w-16 h-24',
  md: 'w-24 h-36',
  lg: 'w-32 h-48',
}

export default function PosterCard({ film, size = 'md' }: PosterCardProps) {
  const posterUrl = film.poster_path
    ? `${TMDB_IMG}${film.poster_path}`
    : null

  return (
    <div className={`relative ${sizes[size]} flex-shrink-0 group`}>
      {posterUrl ? (
        <img
          src={posterUrl}
          alt={film.title}
          className="w-full h-full object-cover rounded-lg shadow-lg group-hover:scale-105 transition-transform"
          loading="lazy"
        />
      ) : (
        <div className="w-full h-full bg-bg-hover rounded-lg flex items-center justify-center">
          <span className="text-text-secondary text-xs text-center px-1">{film.title}</span>
        </div>
      )}

      {/* Liked heart */}
      {film.liked && (
        <div className="absolute top-1 right-1 text-accent-red text-sm">❤️</div>
      )}

      {/* Rating */}
      {film.rating && (
        <div className="absolute bottom-1 right-1 bg-black/70 px-1 rounded text-xs text-accent-yellow">
          ★ {film.rating}
        </div>
      )}

      {/* Hover overlay */}
      <div className="absolute inset-0 bg-black/70 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex flex-col justify-end p-2">
        <p className="text-xs font-medium line-clamp-2">{film.title}</p>
        <p className="text-xs text-text-secondary">{film.year}</p>
      </div>
    </div>
  )
}
