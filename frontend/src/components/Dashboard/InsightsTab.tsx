import ChartWrapper from '../charts/ChartWrapper'

interface InsightsTabProps {
  stats: Record<string, unknown>
  charts: Record<string, unknown>
}

export default function InsightsTab({ stats, charts }: InsightsTabProps) {
  const runtime = (stats.runtime || {}) as Record<string, unknown>
  const shortest = runtime.shortest as Record<string, string | number> | undefined
  const longest = runtime.longest as Record<string, string | number> | undefined

  return (
    <div className="space-y-10">
      {/* Runtime Stats */}
      <section className="glass-card p-6">
        <h2 className="text-2xl font-bold mb-6">Viewing Time</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-3xl font-bold text-accent-cyan">
              <span className="inline-block bg-accent-cyan/10 px-4 py-1.5 rounded-lg">
                {Math.round((runtime.total_minutes as number || 0) / 60)}h
              </span>
            </p>
            <p className="text-text-secondary text-xs uppercase tracking-wider mt-2">Total Watch Time</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-accent-purple">
              <span className="inline-block bg-accent-purple/10 px-4 py-1.5 rounded-lg">
                {String(runtime.average || 0)}
              </span>
            </p>
            <p className="text-text-secondary text-xs uppercase tracking-wider mt-2">Avg Runtime (min)</p>
          </div>
          <div className="text-center">
            <p className="text-xl font-bold text-accent-green truncate px-2">
              {shortest?.title || 'N/A'}
            </p>
            {shortest?.runtime && (
              <p className="text-accent-green/70 text-sm">{String(shortest.runtime)} min</p>
            )}
            <p className="text-text-secondary text-xs uppercase tracking-wider mt-1">Shortest Film</p>
          </div>
          <div className="text-center">
            <p className="text-xl font-bold text-accent-yellow truncate px-2">
              {longest?.title || 'N/A'}
            </p>
            {longest?.runtime && (
              <p className="text-accent-yellow/70 text-sm">{String(longest.runtime)} min</p>
            )}
            <p className="text-text-secondary text-xs uppercase tracking-wider mt-1">Longest Film</p>
          </div>
        </div>
      </section>

      {/* Charts Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Top Genres</h3>
          <ChartWrapper config={charts.genres as string} type="doughnut" />
        </div>
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Top Countries</h3>
          <ChartWrapper config={charts.countries as string} type="bar" />
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Rating Trends</h3>
          <ChartWrapper config={charts.rating_evolution as string} type="line" />
        </div>
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Rating Distribution</h3>
          <ChartWrapper config={charts.ratings as string} type="bar" />
        </div>
      </div>
    </div>
  )
}
