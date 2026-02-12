import { useEffect } from 'react'
import PosterCard from './PosterCard'

interface Film {
  title: string
  year: number
  rating?: number
  poster_path?: string
  liked?: boolean
}

interface FilmModalProps {
  title: string
  films: Film[]
  onClose: () => void
}

export default function FilmModal({ title, films, onClose }: FilmModalProps) {
  // Close on ESC
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleEsc)
    return () => window.removeEventListener('keydown', handleEsc)
  }, [onClose])

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

      {/* Modal */}
      <div
        className="relative bg-bg-secondary/95 backdrop-blur-xl border border-white/[0.08] rounded-2xl max-w-5xl w-full max-h-[85vh] overflow-hidden shadow-2xl"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/[0.08]">
          <h2 className="text-2xl font-bold">
            {title}
            <span className="text-text-secondary text-base font-normal ml-3">
              {films.length} films
            </span>
          </h2>
          <button
            onClick={onClose}
            className="w-10 h-10 rounded-full bg-white/[0.06] hover:bg-white/[0.12] flex items-center justify-center transition-colors text-text-secondary hover:text-text-primary"
          >
            <span className="text-xl leading-none">&times;</span>
          </button>
        </div>

        {/* Film Grid */}
        <div className="p-6 overflow-y-auto max-h-[65vh]">
          <div className="grid grid-cols-3 md:grid-cols-5 lg:grid-cols-7 gap-4">
            {films.map((film, i) => (
              <PosterCard key={i} film={film} size="md" />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
