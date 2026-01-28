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

interface DecadeData {
  decade: string
  count: number
  top_films: Film[]
}

export default function DecadesTab({ stats, charts }: DecadesTabProps) {
  const decades = (stats.decades || []) as DecadeData[]

  return (
    <div className="space-y-8">
      {/* Decades Chart */}
      <section className="bg-bg-card rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-4">Films by Decade</h2>
        <ChartWrapper config={charts.decades as string} type="bar" />
      </section>

      {/* Decade Cards */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Top Films by Era</h2>
        <div className="space-y-6">
          {decades.map(decade => (
            <div key={decade.decade} className="bg-bg-card rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-accent-cyan">{decade.decade}</h3>
                <span className="text-text-secondary">{decade.count} films</span>
              </div>
              <div className="flex gap-3 overflow-x-auto pb-2">
                {decade.top_films.slice(0, 8).map((film, i) => (
                  <PosterCard key={i} film={film} size="md" />
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
