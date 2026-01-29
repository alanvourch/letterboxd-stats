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
      className="bg-bg-card rounded-xl p-4 cursor-pointer hover:bg-bg-hover transition-colors group"
    >
      <div className="flex gap-3">
        {/* Rank + Photo */}
        <div className="flex-shrink-0 text-center">
          <span className="text-accent-cyan font-bold text-sm">#{rank}</span>
          <div className="w-[80px] h-[80px] mt-1 rounded-full overflow-hidden bg-bg-hover ring-2 ring-bg-hover group-hover:ring-accent-cyan/30 transition-all">
            {profileUrl ? (
              <img src={profileUrl} alt={person.name} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-text-secondary text-2xl">👤</div>
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
          <div className="flex gap-1 mt-2">
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
                  <div className="w-full h-full bg-bg-hover" />
                )}
              </div>
            ))}
          </div>

          {/* Like ratio bar */}
          {person.liked_count > 0 && (
            <div className="mt-2">
              <div className="h-1.5 bg-bg-hover rounded-full overflow-hidden">
                <div className="h-full bg-accent-pink rounded-full" style={{ width: `${likeRatio}%` }} />
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
