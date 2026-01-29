import ChartWrapper from '../charts/ChartWrapper'

interface InsightsTabProps {
  stats: Record<string, unknown>
  charts: Record<string, unknown>
}

export default function InsightsTab({ stats, charts }: InsightsTabProps) {
  const runtime = (stats.runtime || {}) as Record<string, unknown>
  const geography = (stats.geography || {}) as Record<string, unknown>

  return (
    <div className="space-y-8">
      {/* Runtime Stats */}
      <section className="bg-bg-card rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-4">Viewing Time</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-3xl font-bold text-accent-cyan">
              {Math.round((runtime.total_minutes as number || 0) / 60)}h
            </p>
            <p className="text-text-secondary">Total Watch Time</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-accent-purple">
              {String(runtime.average || 0)}
            </p>
            <p className="text-text-secondary">Avg Runtime (min)</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-accent-green">
              {(runtime.shortest as Record<string, string>)?.title || 'N/A'}
            </p>
            <p className="text-text-secondary">Shortest Film</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-accent-yellow">
              {(runtime.longest as Record<string, string>)?.title || 'N/A'}
            </p>
            <p className="text-text-secondary">Longest Film</p>
          </div>
        </div>
      </section>

      {/* Charts Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-bg-card rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Top Genres</h3>
          <ChartWrapper config={charts.genres as string} type="doughnut" />
        </div>
        <div className="bg-bg-card rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Top Countries</h3>
          <ChartWrapper config={charts.countries as string} type="bar" />
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-bg-card rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Rating Trends</h3>
          <ChartWrapper config={charts.rating_evolution as string} type="line" />
        </div>
        <div className="bg-bg-card rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Rating Distribution</h3>
          <ChartWrapper config={charts.ratings as string} type="bar" />
        </div>
      </div>

      {/* Top Languages */}
      <section className="bg-bg-card rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Top Languages</h2>
        <div className="flex flex-wrap gap-2">
          {((geography.top_languages || []) as Array<{ language: string; count: number }>)
            .slice(0, 10)
            .map((lang) => (
              <span
                key={lang.language}
                className="px-3 py-1 bg-bg-hover rounded-full text-sm"
              >
                {lang.language}: {lang.count}
              </span>
            ))}
        </div>
      </section>
    </div>
  )
}
