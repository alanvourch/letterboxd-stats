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
    <div className="space-y-8">
      {/* First & Recent Film */}
      {(firstFilm || recentFilm) && (
        <section className="grid md:grid-cols-2 gap-6">
          {firstFilm && (
            <div className="bg-bg-card rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-2 text-accent-cyan">First Film Logged</h3>
              <div className="flex gap-4 items-center">
                <PosterCard film={firstFilm} size="md" />
                <div>
                  <p className="font-bold text-lg">{firstFilm.title}</p>
                  <p className="text-text-secondary">{firstFilm.year}</p>
                  <p className="text-text-secondary text-sm mt-1">{firstFilm.date}</p>
                </div>
              </div>
            </div>
          )}
          {recentFilm && (
            <div className="bg-bg-card rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-2 text-accent-purple">Most Recent Film</h3>
              <div className="flex gap-4 items-center">
                <PosterCard film={recentFilm} size="md" />
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
            <div className="bg-bg-card rounded-xl p-6 text-center">
              <p className="text-3xl font-bold text-accent-yellow">{maxDayCount}</p>
              <p className="text-text-secondary text-sm">Most films in a day</p>
              {maxDay && <p className="text-text-secondary text-xs mt-1">{maxDay}</p>}
            </div>
          )}
          {longestStreak && longestStreak > 1 && (
            <div className="bg-bg-card rounded-xl p-6 text-center">
              <p className="text-3xl font-bold text-accent-green">{longestStreak}</p>
              <p className="text-text-secondary text-sm">Day streak</p>
            </div>
          )}
          {daysSinceFirst && daysSinceFirst > 0 && (
            <div className="bg-bg-card rounded-xl p-6 text-center">
              <p className="text-3xl font-bold text-accent-cyan">{daysSinceFirst}</p>
              <p className="text-text-secondary text-sm">Days since first log</p>
            </div>
          )}
        </section>
      )}

      {/* Milestones */}
      {milestones.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold mb-4">Film Milestones</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {milestones.map(m => (
              <div key={m.number} className="bg-bg-card rounded-xl p-4 text-center">
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
          <h2 className="text-2xl font-bold mb-4">Fun Facts</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {funFacts.map((fact, i) => (
              <div key={i} className="bg-bg-card rounded-xl p-5 flex gap-4 items-start">
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
          <h2 className="text-2xl font-bold mb-4">Most Rewatched</h2>
          <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
            {mostRewatched.slice(0, 10).map((film, i) => (
              <div key={i} className="text-center">
                <PosterCard film={film} size="md" />
                <p className="text-sm font-medium mt-2 truncate">{film.title}</p>
                <p className="text-text-secondary text-sm">{film.rewatch_count}x watched</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 5-Star Wall */}
      {fiveStars.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold mb-4">5-Star Wall ({fiveStars.length} films)</h2>
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
