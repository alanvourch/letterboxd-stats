import { useState, useEffect } from 'react'

interface ProgressBarProps {
  progress: {
    step: string
    message: string
    percent: number
  } | null
}

const STEPS = [
  { key: 'loading', label: 'Loading' },
  { key: 'enriching', label: 'Enriching' },
  { key: 'calculating', label: 'Stats' },
  { key: 'generating', label: 'Dashboard' },
]

export default function ProgressBar({ progress }: ProgressBarProps) {
  const percent = progress?.percent ?? 0
  const currentStep = progress?.step ?? 'loading'
  const [waitingLong, setWaitingLong] = useState(false)

  // If no progress after 10 seconds, show cold start message
  useEffect(() => {
    if (progress) {
      setWaitingLong(false)
      return
    }
    const timer = setTimeout(() => setWaitingLong(true), 10000)
    return () => clearTimeout(timer)
  }, [progress])

  const stepIndex = STEPS.findIndex(s => s.key === currentStep)

  return (
    <div className="w-full">
      {/* Step indicators with connecting lines */}
      <div className="flex items-start justify-between mb-6 relative">
        {STEPS.map((step, index) => {
          const isActive = index <= stepIndex
          const isCurrent = step.key === currentStep
          const isComplete = index < stepIndex

          return (
            <div key={step.key} className="flex flex-col items-center relative z-10 flex-1">
              <div
                className={`
                  w-9 h-9 rounded-full flex items-center justify-center mb-2 transition-all duration-300 text-sm font-medium
                  ${isCurrent ? 'bg-accent-cyan text-bg-primary scale-110' : isComplete ? 'bg-accent-cyan/40 text-accent-cyan' : 'bg-bg-hover text-text-secondary'}
                `}
              >
                {isComplete ? '\u2713' : index + 1}
              </div>
              <span className={`text-xs transition-colors ${isCurrent ? 'text-accent-cyan font-medium' : isActive ? 'text-text-primary' : 'text-text-secondary'}`}>
                {step.label}
              </span>
            </div>
          )
        })}
        {/* Connecting line */}
        <div className="absolute top-4 left-[12.5%] right-[12.5%] h-0.5 bg-bg-hover -z-0">
          <div
            className="h-full bg-accent-cyan/40 transition-all duration-500"
            style={{ width: `${Math.max(0, stepIndex / (STEPS.length - 1)) * 100}%` }}
          />
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-bg-hover rounded-full overflow-hidden mb-4">
        <div
          className="h-full bg-gradient-to-r from-accent-cyan to-accent-purple transition-all duration-300"
          style={{ width: `${percent}%` }}
        />
      </div>

      {/* Message */}
      <p className="text-center text-text-secondary">
        {progress?.message ?? (waitingLong
          ? 'Waking up server... this can take up to 30 seconds on first visit.'
          : 'Connecting...'
        )}
      </p>
      {percent > 0 && (
        <p className="text-center text-text-secondary text-xs mt-1">
          {percent}%
        </p>
      )}
    </div>
  )
}
