import { useState, useEffect, useMemo } from 'react'
import { useParams } from 'react-router-dom'
import { useJobStatus } from '../hooks/useJobStatus'
import { getResultJson, getDownloadUrl } from '../lib/api'
import ProgressBar from '../components/ProgressBar'
import DownloadButton from '../components/DownloadButton'
import MissingFilmsButton from '../components/MissingFilmsButton'
import TabNav from '../components/Dashboard/TabNav'
import OverviewTab from '../components/Dashboard/OverviewTab'
import JourneyTab from '../components/Dashboard/JourneyTab'
import WrapTab from '../components/Dashboard/WrapTab'
import DecadesTab from '../components/Dashboard/DecadesTab'
import PeopleTab from '../components/Dashboard/PeopleTab'
import InsightsTab from '../components/Dashboard/InsightsTab'

export default function DashboardPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const { status, progress, error } = useJobStatus(jobId || null)
  const [activeTab, setActiveTab] = useState('Overview')
  const [data, setData] = useState<{ stats: Record<string, unknown>; charts: Record<string, unknown> } | null>(null)

  useEffect(() => {
    if (status === 'complete' && jobId) {
      getResultJson(jobId).then(result => {
        setData({
          stats: result.stats as Record<string, unknown>,
          charts: result.charts as Record<string, unknown>
        })
      })
    }
  }, [status, jobId])

  // Build dynamic tab labels from data
  const tabs = useMemo(() => {
    if (!data) return ['Overview', 'Journey', 'Wrap', 'Live', 'Decades', 'People', 'Insights']
    const breakdown = (data.stats.yearly_breakdown || {}) as Record<string, unknown>
    const lastYear = breakdown.last_full_year_value as number
    const currentYear = breakdown.current_year_value as number
    return [
      'Overview',
      'Journey',
      lastYear ? `${lastYear} Wrap` : 'Wrap',
      currentYear ? `${currentYear} Live` : 'Live',
      'Decades',
      'People',
      'Insights'
    ]
  }, [data])

  // Show progress while processing
  if (status !== 'complete') {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="max-w-md w-full p-8">
          {error ? (
            <div className="text-center">
              <div className="text-accent-red text-xl mb-4">Error</div>
              <p className="text-text-secondary">{error}</p>
            </div>
          ) : (
            <ProgressBar progress={progress} />
          )}
        </div>
      </div>
    )
  }

  // Show dashboard when complete
  if (!data) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="text-text-secondary">Loading results...</div>
      </div>
    )
  }

  const renderTab = () => {
    if (activeTab === 'Overview') return <OverviewTab stats={data.stats} charts={data.charts} />
    if (activeTab === 'Journey') return <JourneyTab stats={data.stats} />
    if (activeTab.includes('Wrap')) return <WrapTab stats={data.stats} year="previous" />
    if (activeTab.includes('Live')) return <WrapTab stats={data.stats} year="current" />
    if (activeTab === 'Decades') return <DecadesTab stats={data.stats} charts={data.charts} />
    if (activeTab === 'People') return <PeopleTab stats={data.stats} />
    if (activeTab === 'Insights') return <InsightsTab stats={data.stats} charts={data.charts} />
    return null
  }

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-bg-secondary/95 backdrop-blur border-b border-bg-hover">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-accent-cyan to-accent-purple bg-clip-text text-transparent">
              Your Letterboxd Stats
            </h1>
            {data && (() => {
              const basic = (data.stats.basic || {}) as Record<string, number>
              const journey = (data.stats.journey || {}) as Record<string, unknown>
              const firstFilm = journey.first_film as { date?: string } | undefined
              const sinceYear = firstFilm?.date ? new Date(firstFilm.date).getFullYear() : null
              return (
                <p className="text-text-secondary text-sm mt-0.5">
                  {basic.total_watched?.toLocaleString() || 0} films
                  {basic.avg_rating ? ` · ★${basic.avg_rating.toFixed(1)}` : ''}
                  {sinceYear ? ` · since ${sinceYear}` : ''}
                </p>
              )
            })()}
          </div>
          <div className="flex items-center gap-4">
            <MissingFilmsButton jobId={jobId!} />
            <DownloadButton url={getDownloadUrl(jobId!)} />
          </div>
        </div>
        <TabNav tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {renderTab()}
      </main>
    </div>
  )
}
