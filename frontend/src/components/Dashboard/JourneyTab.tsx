import PosterCard from '../ui/PosterCard'

interface JourneyTabProps {
  stats: Record<string, unknown>
}

interface Milestone {
  number: number
  title: string
  year: number
  date: string
  poster_path?: string
}

interface RewatchedFilm {
  title: string
  year: number
  rewatch_count: number
  rating?: number
  liked?: boolean
  poster_path?: string
}

interface Film {
  title: string
  year: number
  poster_path?: string
  liked?: boolean
}

const FACT_BORDER_COLORS = [
  'border-l-accent-cyan',
  'border-l-accent-purple',
  'border-l-accent-pink',
  'border-l-accent-yellow',
  'border-l-accent-green',
  'border-l-accent-red',
]

export default function JourneyTab({ stats }: JourneyTabProps) {
  const journey = (stats.journey || {}) as Record<string, unknown>
  const milestones = (journey.milestones || []) as Milestone[]
  const firstFilm = journey.first_film as Milestone | undefined
  const recentFilm = journey.recent_film as Milestone | undefined
  const rewatchData = (stats.rewatches || {}) as Record<string, unknown>
  const mostRewatched = (rewatchData.most_rewatched || []) as RewatchedFilm[]
  const fiveStars = (stats.five_star_films || []) as Film[]
  const funFacts = (stats.fun_facts || []) as Array<{ icon: string; text: string; subtext: string }>

  const longestStreak = journey.longest_streak as number | undefined
  const maxDayCount = journey.max_day_count as number | undefined
  const maxDay = journey.max_day as string | undefined
  const daysSinceFirst = journey.days_since_first as number | undefined

  return (
    <div className="space-y-10">
      {/* First & Recent Film */}
      {(firstFilm || recentFilm) && (
        <section className="grid md:grid-cols-2 gap-6">
          {firstFilm && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-3 text-accent-cyan">First Film Logged</h3>
              <div className="flex gap-5 items-center">
                <PosterCard film={firstFilm} size="lg" />
                <div>
                  <p className="font-bold text-lg">{firstFilm.title}</p>
                  <p className="text-text-secondary">{firstFilm.year}</p>
                  <p className="text-text-secondary text-sm mt-1">{firstFilm.date}</p>
                </div>
              </div>
            </div>
          )}
          {recentFilm && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-3 text-accent-purple">Most Recent Film</h3>
              <div className="flex gap-5 items-center">
                <PosterCard film={recentFilm} size="lg" />
                <div>
                  <p className="font-bold text-lg">{recentFilm.title}</p>
                  <p className="text-text-secondary">{recentFilm.year}</p>
                  <p className="text-text-secondary text-sm mt-1">{recentFilm.date}</p>
                </div>
              </div>
            </div>
          )}
        </section>
      )}

      {/* Personal Records */}
      {(longestStreak || maxDayCount) && (
        <section className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {maxDayCount && maxDayCount > 1 && (
            <div className="glass-card p-6 text-center">
              <p className="text-3xl font-bold text-accent-yellow">{maxDayCount}</p>
              <p className="text-text-secondary text-sm mt-1">Most films in a day</p>
              {maxDay && <p className="text-text-secondary text-xs mt-1">{maxDay}</p>}
            </div>
          )}
          {longestStreak && longestStreak > 1 && (
            <div className="glass-card p-6 text-center">
              <p className="text-3xl font-bold text-accent-green">{longestStreak}</p>
              <p className="text-text-secondary text-sm mt-1">Day streak</p>
            </div>
          )}
          {daysSinceFirst && daysSinceFirst > 0 && (
            <div className="glass-card p-6 text-center">
              <p className="text-3xl font-bold text-accent-cyan">{daysSinceFirst}</p>
              <p className="text-text-secondary text-sm mt-1">Days since first log</p>
            </div>
          )}
        </section>
      )}

      {/* Milestones */}
      {milestones.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold mb-6">Film Milestones</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {milestones.map(m => (
              <div key={m.number} className="glass-card p-4 text-center">
                <p className="text-accent-cyan font-bold mb-2">#{m.number}</p>
                <PosterCard film={m} size="md" />
                <p className="text-sm font-medium mt-2">{m.title}</p>
                <p className="text-text-secondary text-xs">{m.date}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Fun Facts */}
      {funFacts.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold mb-6">Fun Facts</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {funFacts.map((fact, i) => (
              <div key={i} className={`glass-card p-5 flex gap-4 items-start border-l-4 ${FACT_BORDER_COLORS[i % FACT_BORDER_COLORS.length]}`}>
                <span className="text-2xl">{fact.icon}</span>
                <div>
                  <p className="font-medium">{fact.text}</p>
                  <p className="text-text-secondary text-sm">{fact.subtext}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Most Rewatched */}
      {mostRewatched.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold mb-6">Most Rewatched</h2>
          <div className="flex flex-wrap gap-4">
            {mostRewatched.slice(0, 10).map((film, i) => (
              <div key={i} className="text-center w-[110px]">
                <PosterCard film={film} size="sm" />
                <p className="text-xs font-medium mt-1.5 truncate">{film.title}</p>
                <p className="text-text-secondary text-xs">{film.rewatch_count}x</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 5-Star Wall */}
      {fiveStars.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold mb-6">5-Star Wall ({fiveStars.length} films)</h2>
          <div className="grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(110px, 1fr))' }}>
            {fiveStars.map((film, i) => (
              <PosterCard key={i} film={film} size="sm" />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
