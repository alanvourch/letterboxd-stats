import ChartWrapper from '../charts/ChartWrapper'
import PosterCard from '../ui/PosterCard'

interface DecadesTabProps {
  stats: Record<string, unknown>
  charts: Record<string, unknown>
}

interface Film {
  title: string
  year: number
  rating?: number
  poster_path?: string
  liked?: boolean
}

interface DecadeInfo {
  films: Film[]
  total: number
  avg_rating: number
}

export default function DecadesTab({ stats, charts }: DecadesTabProps) {
  const decades = (stats.decades || {}) as Record<string, unknown>
  const topPerDecade = (decades.top_per_decade || {}) as Record<string, DecadeInfo>
  const favoriteDecade = decades.favorite_decade as string | undefined
  const favoriteDecadeAvg = decades.favorite_decade_avg as number | undefined

  // Sort decades for display
  const sortedDecades = Object.entries(topPerDecade).sort(([a], [b]) => {
    const numA = parseInt(a)
    const numB = parseInt(b)
    return numA - numB
  })

  return (
    <div className="space-y-8">
      {/* Favorite Decade */}
      {favoriteDecade && (
        <section className="bg-bg-card rounded-xl p-6 text-center">
          <p className="text-text-secondary mb-2">Your Favorite Decade</p>
          <p className="text-4xl font-bold bg-gradient-to-r from-accent-cyan to-accent-purple bg-clip-text text-transparent">
            {favoriteDecade}
          </p>
          {favoriteDecadeAvg && (
            <p className="text-text-secondary mt-1">Average rating: {favoriteDecadeAvg.toFixed(2)}</p>
          )}
        </section>
      )}

      {/* Decades Chart */}
      <section className="bg-bg-card rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-4">Films by Decade</h2>
        <ChartWrapper config={charts.decades as string} type="bar" />
      </section>

      {/* Decade Cards */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Top Films by Era</h2>
        <div className="space-y-6">
          {sortedDecades.map(([decade, info]) => (
            <div key={decade} className="bg-bg-card rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-accent-cyan">{decade}</h3>
                <div className="flex gap-4 text-text-secondary text-sm">
                  <span>{info.total} films</span>
                  {info.avg_rating > 0 && <span>Avg: {info.avg_rating.toFixed(1)}</span>}
                </div>
              </div>
              <div className="flex gap-3 overflow-x-auto pb-2">
                {info.films.slice(0, 8).map((film, i) => (
                  <div key={i} className="flex-shrink-0 text-center">
                    <PosterCard film={film} size="md" />
                    <p className="text-xs mt-1 text-text-secondary max-w-[100px] truncate">{film.title}</p>
                    {film.rating && <p className="text-xs text-accent-yellow">{'★'.repeat(Math.floor(film.rating))}{film.rating % 1 >= 0.5 ? '½' : ''}</p>}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
