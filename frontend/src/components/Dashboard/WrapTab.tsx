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

interface YearStats {
  year: number
  total_films: number
  total_liked: number
  average_rating: number
  most_active_month: string
  top_actor?: { name: string; count: number; films: Film[] }
  top_director?: { name: string; count: number; films: Film[] }
  highest_rated: Film[]
  lowest_rated: Film[]
}

export default function WrapTab({ stats, year }: WrapTabProps) {
  const key = year === 'previous' ? 'year_wrap' : 'year_live'
  const yearStats = (stats[key] || {}) as YearStats

  if (!yearStats.year) {
    return (
      <div className="text-center text-text-secondary py-12">
        No data available for this year
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Year Header */}
      <div className="text-center">
        <h2 className="text-5xl font-bold bg-gradient-to-r from-accent-cyan to-accent-purple bg-clip-text text-transparent">
          {yearStats.year}
        </h2>
      </div>

      {/* Key Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-bg-card rounded-xl p-6 text-center">
          <p className="text-4xl font-bold text-accent-cyan">{yearStats.total_films}</p>
          <p className="text-text-secondary">Films</p>
        </div>
        <div className="bg-bg-card rounded-xl p-6 text-center">
          <p className="text-4xl font-bold text-accent-pink">{yearStats.total_liked}</p>
          <p className="text-text-secondary">Liked</p>
        </div>
        <div className="bg-bg-card rounded-xl p-6 text-center">
          <p className="text-4xl font-bold text-accent-yellow">{yearStats.average_rating?.toFixed(1)}</p>
          <p className="text-text-secondary">Avg Rating</p>
        </div>
        <div className="bg-bg-card rounded-xl p-6 text-center">
          <p className="text-2xl font-bold text-accent-purple">{yearStats.most_active_month}</p>
          <p className="text-text-secondary">Best Month</p>
        </div>
      </div>

      {/* Top Person Sections */}
      <div className="grid md:grid-cols-2 gap-6">
        {yearStats.top_actor && (
          <div className="bg-bg-card rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">Top Actor</h3>
            <p className="text-2xl font-bold text-accent-cyan mb-4">{yearStats.top_actor.name}</p>
            <div className="flex gap-2 overflow-x-auto">
              {yearStats.top_actor.films.slice(0, 5).map((film, i) => (
                <PosterCard key={i} film={film} size="sm" />
              ))}
            </div>
          </div>
        )}
        {yearStats.top_director && (
          <div className="bg-bg-card rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">Top Director</h3>
            <p className="text-2xl font-bold text-accent-purple mb-4">{yearStats.top_director.name}</p>
            <div className="flex gap-2 overflow-x-auto">
              {yearStats.top_director.films.slice(0, 5).map((film, i) => (
                <PosterCard key={i} film={film} size="sm" />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Highest/Lowest Rated */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-bg-card rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Highest Rated</h3>
          <div className="grid grid-cols-4 gap-2">
            {yearStats.highest_rated?.slice(0, 8).map((film, i) => (
              <PosterCard key={i} film={film} size="sm" />
            ))}
          </div>
        </div>
        <div className="bg-bg-card rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Lowest Rated</h3>
          <div className="grid grid-cols-4 gap-2">
            {yearStats.lowest_rated?.slice(0, 8).map((film, i) => (
              <PosterCard key={i} film={film} size="sm" />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
