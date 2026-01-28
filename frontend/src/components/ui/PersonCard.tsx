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
      className="bg-bg-card rounded-xl p-4 cursor-pointer hover:bg-bg-hover transition-colors"
    >
      <div className="flex gap-4">
        {/* Rank + Photo */}
        <div className="flex-shrink-0">
          <span className="text-accent-cyan font-bold text-lg">#{rank}</span>
          <div className="w-20 h-20 mt-2 rounded-full overflow-hidden bg-bg-hover">
            {profileUrl ? (
              <img
                src={profileUrl}
                alt={person.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-text-secondary">
                👤
              </div>
            )}
          </div>
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-lg truncate">{person.name}</h3>
          <div className="text-text-secondary text-sm space-y-1">
            <p>{person.count} films</p>
            <p>★ {person.avg_rating.toFixed(1)} avg</p>
          </div>

          {/* Mini poster strip */}
          <div className="flex gap-1 mt-2">
            {person.films.slice(0, 5).map((film, i) => (
              <div key={i} className="w-12 h-18 flex-shrink-0">
                {film.poster_path ? (
                  <img
                    src={`${TMDB_IMG}${film.poster_path}`}
                    alt={film.title}
                    className="w-full h-full object-cover rounded"
                  />
                ) : (
                  <div className="w-full h-full bg-bg-hover rounded" />
                )}
              </div>
            ))}
          </div>

          {/* Like ratio bar */}
          <div className="mt-2">
            <div className="h-1 bg-bg-hover rounded-full overflow-hidden">
              <div
                className="h-full bg-accent-pink"
                style={{ width: `${likeRatio}%` }}
              />
            </div>
            <p className="text-xs text-text-secondary mt-1">
              {person.liked_count} liked ({likeRatio.toFixed(0)}%)
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
