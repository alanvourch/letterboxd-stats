const TMDB_IMG = 'https://image.tmdb.org/t/p/w185'

interface Film {
  title: string
  year: number
  rating?: number
  poster_path?: string
  liked?: boolean
}

interface Person {
  name: string
  count: number
  liked_count: number
  avg_rating: number
  profile_path?: string
  films: Film[]
}

interface PersonCardProps {
  person: Person
  rank: number
  onClick: () => void
}

export default function PersonCard({ person, rank, onClick }: PersonCardProps) {
  const profileUrl = person.profile_path
    ? `${TMDB_IMG}${person.profile_path}`
    : null

  const likeRatio = person.count > 0 ? (person.liked_count / person.count) * 100 : 0

  return (
    <div
      onClick={onClick}
      className="glass-card glass-card-interactive relative overflow-hidden p-5 cursor-pointer group"
    >
      {/* Top gradient strip on hover */}
      <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-accent-cyan to-accent-purple opacity-0 group-hover:opacity-100 transition-opacity" />

      <div className="flex gap-4">
        {/* Rank + Photo */}
        <div className="flex-shrink-0 text-center">
          <span className="text-accent-cyan font-bold text-sm">#{rank}</span>
          <div className="w-[100px] h-[100px] mt-1 rounded-full overflow-hidden ring-2 ring-white/[0.08] group-hover:ring-accent-cyan/40 transition-all">
            {profileUrl ? (
              <img src={profileUrl} alt={person.name} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full bg-gradient-to-br from-accent-purple to-accent-cyan flex items-center justify-center text-white text-2xl font-bold">
                {person.name.charAt(0)}
              </div>
            )}
          </div>
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-base truncate">{person.name}</h3>
          <div className="text-text-secondary text-sm flex gap-3">
            <span>{person.count} films</span>
            <span className="text-accent-yellow">★ {person.avg_rating.toFixed(1)}</span>
          </div>

          {/* Mini poster strip */}
          <div className="flex gap-1.5 mt-2.5">
            {person.films.slice(0, 5).map((film, i) => (
              <div key={i} className="w-[48px] h-[72px] flex-shrink-0 rounded overflow-hidden">
                {film.poster_path ? (
                  <img
                    src={`${TMDB_IMG}${film.poster_path}`}
                    alt={film.title}
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full bg-bg-hover rounded" />
                )}
              </div>
            ))}
          </div>

          {/* Like ratio bar */}
          {person.liked_count > 0 && (
            <div className="mt-2.5">
              <div className="h-1.5 bg-bg-hover rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-accent-cyan to-accent-pink rounded-full" style={{ width: `${likeRatio}%` }} />
              </div>
              <p className="text-xs text-text-secondary mt-0.5">
                {person.liked_count} liked ({likeRatio.toFixed(0)}%)
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
