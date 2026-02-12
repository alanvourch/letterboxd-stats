import PosterCard from '../ui/PosterCard'

interface WrapTabProps {
  stats: Record<string, unknown>
  year: 'previous' | 'current'
}

interface Film {
  title: string
  year: number
  rating?: number
  poster_path?: string
  liked?: boolean
}

const MONTH_NAMES = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

export default function WrapTab({ stats, year }: WrapTabProps) {
  const breakdown = (stats.yearly_breakdown || {}) as Record<string, unknown>
  const dataKey = year === 'previous' ? 'last_full_year' : 'current_year'
  const yearValue = year === 'previous'
    ? breakdown.last_full_year_value as number
    : breakdown.current_year_value as number
  const yearStats = (breakdown[dataKey] || {}) as Record<string, unknown>

  if (!yearStats.total_films || (yearStats.total_films as number) === 0) {
    return (
      <div className="text-center text-text-secondary py-12">
        No data available for {yearValue || 'this year'}
      </div>
    )
  }

  const topRated = (yearStats.top_rated || []) as Film[]
  const bottomRated = (yearStats.bottom_rated || []) as Film[]
  const topActor = yearStats.top_actor as { name: string; count: number; films: Film[] } | null
  const topDirector = yearStats.top_director as { name: string; count: number; films: Film[] } | null
  const mostActiveMonth = yearStats.most_active_month as number
  const monthName = MONTH_NAMES[mostActiveMonth] || ''

  return (
    <div className="space-y-10">
      {/* Wrap container with subtle gradient bg */}
      <div className="glass-card bg-gradient-to-br from-accent-purple/[0.06] via-accent-pink/[0.04] to-accent-cyan/[0.04] p-8 md:p-10">
        {/* Year Header */}
        <div className="text-center mb-10">
          <h2 className="text-7xl font-extrabold bg-gradient-to-r from-accent-cyan via-accent-purple to-accent-pink bg-clip-text text-transparent">
            {yearValue}
          </h2>
          <p className="text-text-secondary uppercase tracking-[3px] mt-2 text-sm">
            Your Year in Film
          </p>
        </div>

        {/* Key Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="glass-card p-6 text-center">
            <p className="text-4xl font-bold text-accent-cyan">{String(yearStats.total_films)}</p>
            <p className="text-text-secondary text-xs uppercase tracking-wider mt-1">Films</p>
          </div>
          <div className="glass-card p-6 text-center">
            <p className="text-4xl font-bold text-accent-pink">{String(yearStats.total_liked)}</p>
            <p className="text-text-secondary text-xs uppercase tracking-wider mt-1">Liked</p>
          </div>
          <div className="glass-card p-6 text-center">
            <p className="text-4xl font-bold text-accent-yellow">{(yearStats.avg_rating as number)?.toFixed(1)}</p>
            <p className="text-text-secondary text-xs uppercase tracking-wider mt-1">Avg Rating</p>
          </div>
          <div className="glass-card p-6 text-center">
            <p className="text-2xl font-bold text-accent-purple">{monthName}</p>
            <p className="text-text-secondary text-xs uppercase tracking-wider mt-1">Best Month</p>
          </div>
        </div>
      </div>

      {/* Top Person Sections */}
      <div className="grid md:grid-cols-2 gap-6">
        {topActor && (
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Top Actor</h3>
            <p className="text-2xl font-bold text-accent-cyan mb-1">{topActor.name}</p>
            <p className="text-text-secondary text-sm mb-4">{topActor.count} films</p>
            <div className="flex gap-3 overflow-x-auto pb-1">
              {topActor.films.slice(0, 5).map((film, i) => (
                <PosterCard key={i} film={film} size="md" />
              ))}
            </div>
          </div>
        )}
        {topDirector && (
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Top Director</h3>
            <p className="text-2xl font-bold text-accent-purple mb-1">{topDirector.name}</p>
            <p className="text-text-secondary text-sm mb-4">{topDirector.count} films</p>
            <div className="flex gap-3 overflow-x-auto pb-1">
              {topDirector.films.slice(0, 5).map((film, i) => (
                <PosterCard key={i} film={film} size="md" />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Highest/Lowest Rated */}
      <div className="grid md:grid-cols-2 gap-6">
        {topRated.length > 0 && (
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Highest Rated</h3>
            <div className="flex flex-wrap gap-4">
              {topRated.slice(0, 8).map((film, i) => (
                <div key={i} className="text-center w-[110px]">
                  <PosterCard film={film} size="sm" />
                  <p className="text-xs text-text-secondary mt-1.5 truncate">{film.title}</p>
                </div>
              ))}
            </div>
          </div>
        )}
        {bottomRated.length > 0 && (
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Lowest Rated</h3>
            <div className="flex flex-wrap gap-4">
              {bottomRated.slice(0, 8).map((film, i) => (
                <div key={i} className="text-center w-[110px]">
                  <PosterCard film={film} size="sm" />
                  <p className="text-xs text-text-secondary mt-1.5 truncate">{film.title}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
