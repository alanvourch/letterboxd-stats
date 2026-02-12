const TMDB_IMG = 'https://image.tmdb.org/t/p/w342'

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
  xs: 'w-[80px] h-[120px]',
  sm: 'w-[110px] h-[165px]',
  md: 'w-[140px] h-[210px]',
  lg: 'w-[170px] h-[255px]',
}

function ratingColor(rating: number) {
  if (rating >= 4) return 'text-accent-green'
  if (rating >= 3) return 'text-accent-yellow'
  return 'text-accent-red'
}

export default function PosterCard({ film, size = 'md', showTitle = false }: PosterCardProps) {
  const posterUrl = film.poster_path
    ? `${TMDB_IMG}${film.poster_path}`
    : null

  return (
    <div className={`relative ${sizes[size]} flex-shrink-0 group cursor-pointer`}>
      {posterUrl ? (
        <img
          src={posterUrl}
          alt={film.title}
          className="w-full h-full object-cover rounded-lg shadow-lg group-hover:scale-[1.07] group-hover:shadow-xl group-hover:shadow-black/50 transition-all duration-300"
          loading="lazy"
        />
      ) : (
        <div className="w-full h-full bg-gradient-to-br from-bg-hover to-bg-secondary rounded-lg flex items-center justify-center p-2 border border-white/[0.06]">
          <span className="text-text-secondary text-xs text-center leading-tight">{film.title}</span>
        </div>
      )}

      {/* Bottom gradient overlay */}
      {posterUrl && (
        <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-black/60 to-transparent rounded-b-lg pointer-events-none" />
      )}

      {/* Liked heart */}
      {film.liked && (
        <div className="absolute top-1.5 right-1.5 text-accent-red text-xs drop-shadow-[0_0_4px_rgba(239,68,68,0.6)]">❤️</div>
      )}

      {/* Rating badge */}
      {film.rating && (
        <div className={`absolute bottom-1.5 right-1.5 bg-black/70 backdrop-blur-sm px-2 py-0.5 rounded-md text-xs font-semibold ${ratingColor(film.rating)}`}>
          ★{film.rating}
        </div>
      )}

      {/* Hover overlay */}
      <div className="absolute inset-0 bg-black/80 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-lg flex flex-col justify-end p-2.5">
        <p className="text-xs font-semibold line-clamp-2 leading-tight">{film.title}</p>
        <p className="text-xs text-text-secondary mt-0.5">{film.year}</p>
      </div>

      {/* Title below poster */}
      {showTitle && (
        <p className="text-xs text-text-secondary mt-1.5 truncate text-center">{film.title}</p>
      )}
    </div>
  )
}
