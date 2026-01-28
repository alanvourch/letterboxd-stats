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

  const actors = (stats.actors || []) as Person[]
  const directors = (stats.directors || []) as Person[]
  const composers = ((stats as Record<string, unknown>).composers || []) as Person[]
  const cinematographers = ((stats as Record<string, unknown>).cinematographers || []) as Person[]
  const writers = ((stats as Record<string, unknown>).writers || []) as Person[]
  const studios = ((stats as Record<string, unknown>).studios || []) as Studio[]

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
    <div className="space-y-6">
      {/* Sub-tab navigation */}
      <div className="flex gap-2 flex-wrap">
        {TABS.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-full font-medium transition-all ${
              activeTab === tab
                ? 'bg-accent-cyan text-bg-primary'
                : 'bg-bg-card text-text-secondary hover:text-text-primary'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
