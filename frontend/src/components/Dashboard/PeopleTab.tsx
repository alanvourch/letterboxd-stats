import { useState } from 'react'
import PersonCard from '../ui/PersonCard'
import StudioCard from '../ui/StudioCard'
import FilmModal from '../ui/FilmModal'

interface PeopleTabProps {
  stats: Record<string, unknown>
}

interface Film {
  title: string
  year: number
  rating?: number
  poster_path?: string
  liked?: boolean
}

interface Person {
  name: string
  count: number
  liked_count: number
  avg_rating: number
  profile_path?: string
  films: Film[]
}

interface Studio {
  name: string
  count: number
  avg_rating: number
  logo_path?: string
  films: Film[]
}

const TABS = ['Actors', 'Directors', 'Composers', 'Cinematographers', 'Writers', 'Studios']

export default function PeopleTab({ stats }: PeopleTabProps) {
  const [activeTab, setActiveTab] = useState('Actors')
  const [selectedPerson, setSelectedPerson] = useState<Person | Studio | null>(null)

  const actors = ((stats.actors as Record<string, unknown>)?.top_by_count || []) as Person[]
  const directors = ((stats.directors as Record<string, unknown>)?.top_by_count || []) as Person[]
  const composers = ((stats.composers as Record<string, unknown>)?.top_by_count || []) as Person[]
  const cinematographers = ((stats.cinematographers as Record<string, unknown>)?.top_by_count || []) as Person[]
  const writers = ((stats.writers as Record<string, unknown>)?.top_by_count || []) as Person[]
  const studios = ((stats.studios as Record<string, unknown>)?.top_by_count || []) as Studio[]

  const getData = () => {
    switch (activeTab) {
      case 'Actors': return actors
      case 'Directors': return directors
      case 'Composers': return composers
      case 'Cinematographers': return cinematographers
      case 'Writers': return writers
      case 'Studios': return studios
      default: return []
    }
  }

  const data = getData()

  return (
    <div className="space-y-8">
      {/* Sub-tab navigation */}
      <div className="flex gap-2 flex-wrap">
        {TABS.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-5 py-2.5 rounded-full font-medium transition-all text-sm ${
              activeTab === tab
                ? 'bg-gradient-to-r from-accent-purple to-accent-cyan text-white font-semibold border border-transparent'
                : 'border border-white/[0.08] text-text-secondary hover:text-text-primary hover:border-white/[0.16]'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {activeTab === 'Studios' ? (
          (data as Studio[]).map((studio, i) => (
            <StudioCard
              key={studio.name}
              studio={studio}
              rank={i + 1}
              onClick={() => setSelectedPerson(studio)}
            />
          ))
        ) : (
          (data as Person[]).map((person, i) => (
            <PersonCard
              key={person.name}
              person={person}
              rank={i + 1}
              onClick={() => setSelectedPerson(person)}
            />
          ))
        )}
      </div>

      {/* Film Modal */}
      {selectedPerson && (
        <FilmModal
          title={selectedPerson.name}
          films={selectedPerson.films}
          onClose={() => setSelectedPerson(null)}
        />
      )}
    </div>
  )
}
