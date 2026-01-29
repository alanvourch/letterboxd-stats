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
  size?: 'xs' | 'sm' | 'md' | 'lg'
  showTitle?: boolean
}

const sizes = {
  xs: 'w-[60px] h-[90px]',
  sm: 'w-[90px] h-[135px]',
  md: 'w-[120px] h-[180px]',
  lg: 'w-[150px] h-[225px]',
}

export default function PosterCard({ film, size = 'md', showTitle = false }: PosterCardProps) {
  const posterUrl = film.poster_path
    ? `${TMDB_IMG}${film.poster_path}`
    : null

  return (
    <div className={`relative ${sizes[size]} flex-shrink-0 group`}>
      {posterUrl ? (
        <img
          src={posterUrl}
          alt={film.title}
          className="w-full h-full object-cover rounded-lg shadow-lg group-hover:scale-105 transition-transform duration-200"
          loading="lazy"
        />
      ) : (
        <div className="w-full h-full bg-bg-hover rounded-lg flex items-center justify-center p-1">
          <span className="text-text-secondary text-xs text-center leading-tight">{film.title}</span>
        </div>
      )}

      {/* Liked heart */}
      {film.liked && (
        <div className="absolute top-1 right-1 text-accent-red text-xs drop-shadow-md">❤️</div>
      )}

      {/* Rating badge */}
      {film.rating && (
        <div className="absolute bottom-1 right-1 bg-black/75 px-1.5 py-0.5 rounded text-xs text-accent-yellow font-medium">
          ★{film.rating}
        </div>
      )}

      {/* Hover overlay */}
      <div className="absolute inset-0 bg-black/75 opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-lg flex flex-col justify-end p-2">
        <p className="text-xs font-medium line-clamp-2 leading-tight">{film.title}</p>
        <p className="text-xs text-text-secondary">{film.year}</p>
      </div>

      {/* Title below poster */}
      {showTitle && (
        <p className="text-xs text-text-secondary mt-1 truncate text-center">{film.title}</p>
      )}
    </div>
  )
}
