import PosterCard from '../ui/PosterCard'

interface JourneyTabProps {
  stats: Record<string, unknown>
}

interface Film {
  title: string
  year: number
  rating?: number
  poster_path?: string
  liked?: boolean
}

export default function JourneyTab({ stats }: JourneyTabProps) {
  const journey = (stats.journey || {}) as Record<string, unknown>
  const milestones = (journey.milestones || []) as Array<{ count: number; film: Film }>
  const rewatches = (journey.most_rewatched || []) as Array<{ film: Film; count: number }>
  const fiveStars = (journey.five_star_films || []) as Film[]

  return (
    <div className="space-y-8">
      {/* Milestones */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Film Milestones</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {milestones.map(m => (
            <div key={m.count} className="bg-bg-card rounded-xl p-4">
              <p className="text-accent-cyan font-bold mb-2">#{m.count}</p>
              <PosterCard film={m.film} size="md" />
            </div>
          ))}
        </div>
      </section>

      {/* Most Rewatched */}
      {rewatches.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold mb-4">Most Rewatched</h2>
          <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
            {rewatches.slice(0, 6).map((r, i) => (
              <div key={i} className="text-center">
                <PosterCard film={r.film} size="md" />
                <p className="text-text-secondary text-sm mt-2">{r.count}x</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 5-Star Wall */}
      {fiveStars.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold mb-4">5-Star Wall</h2>
          <div className="grid grid-cols-4 md:grid-cols-8 gap-2">
            {fiveStars.map((film, i) => (
              <PosterCard key={i} film={film} size="sm" />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
