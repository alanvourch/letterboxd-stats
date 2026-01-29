import ChartWrapper from '../charts/ChartWrapper'

interface OverviewTabProps {
  stats: Record<string, unknown>
  charts: Record<string, unknown>
}

export default function OverviewTab({ stats, charts }: OverviewTabProps) {
  const basic = (stats.basic || {}) as Record<string, number>

  return (
    <div className="space-y-8">
      {/* Key Stats */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Overview</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="Films Watched" value={basic.total_watched || 0} color="cyan" />
          <StatCard label="Films Rated" value={basic.total_rated || 0} color="purple" />
          <StatCard label="Average Rating" value={(basic.avg_rating || 0).toFixed(1)} color="yellow" />
          <StatCard label="Films Liked" value={basic.total_liked || 0} color="pink" />
        </div>
      </section>

      {/* Charts */}
      <section className="grid md:grid-cols-2 gap-6">
        <div className="bg-bg-card rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Films Per Year</h3>
          <ChartWrapper config={charts.yearly as string} type="bar" />
        </div>
        <div className="bg-bg-card rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Monthly Activity</h3>
          <ChartWrapper config={charts.monthly as string} type="line" />
        </div>
      </section>

      <section className="grid md:grid-cols-2 gap-6">
        <div className="bg-bg-card rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Genres: Watched vs Liked</h3>
          <ChartWrapper config={(charts.genres_watched_vs_liked || charts.genres) as string} type="bar" />
        </div>
        <div className="bg-bg-card rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Runtime Distribution</h3>
          <ChartWrapper config={charts.runtime as string} type="bar" />
        </div>
      </section>
    </div>
  )
}

function StatCard({ label, value, color }: { label: string; value: number | string; color: string }) {
  const colorClasses: Record<string, string> = {
    cyan: 'text-accent-cyan',
    purple: 'text-accent-purple',
    pink: 'text-accent-pink',
    yellow: 'text-accent-yellow',
  }

  return (
    <div className="bg-bg-card rounded-xl p-6">
      <p className="text-text-secondary text-sm mb-1">{label}</p>
      <p className={`text-3xl font-bold ${colorClasses[color]}`}>{value}</p>
    </div>
  )
}
