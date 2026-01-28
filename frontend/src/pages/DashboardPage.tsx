import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useJobStatus } from '../hooks/useJobStatus'
import { getResultJson, getDownloadUrl } from '../lib/api'
import ProgressBar from '../components/ProgressBar'
import DownloadButton from '../components/DownloadButton'
import TabNav from '../components/Dashboard/TabNav'
import OverviewTab from '../components/Dashboard/OverviewTab'
import JourneyTab from '../components/Dashboard/JourneyTab'
import WrapTab from '../components/Dashboard/WrapTab'
import DecadesTab from '../components/Dashboard/DecadesTab'
import PeopleTab from '../components/Dashboard/PeopleTab'
import InsightsTab from '../components/Dashboard/InsightsTab'

const TABS = ['Overview', 'Journey', 'Wrap', 'Live', 'Decades', 'People', 'Insights']

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
    switch (activeTab) {
      case 'Overview':
        return <OverviewTab stats={data.stats} charts={data.charts} />
      case 'Journey':
        return <JourneyTab stats={data.stats} />
      case 'Wrap':
        return <WrapTab stats={data.stats} year="previous" />
      case 'Live':
        return <WrapTab stats={data.stats} year="current" />
      case 'Decades':
        return <DecadesTab stats={data.stats} charts={data.charts} />
      case 'People':
        return <PeopleTab stats={data.stats} />
      case 'Insights':
        return <InsightsTab stats={data.stats} charts={data.charts} />
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-bg-secondary/95 backdrop-blur border-b border-bg-hover">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-accent-cyan to-accent-purple bg-clip-text text-transparent">
            Your Letterboxd Stats
          </h1>
          <DownloadButton url={getDownloadUrl(jobId!)} />
        </div>
        <TabNav tabs={TABS} activeTab={activeTab} onTabChange={setActiveTab} />
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {renderTab()}
      </main>
    </div>
  )
}
