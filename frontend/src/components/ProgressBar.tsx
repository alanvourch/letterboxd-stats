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
  { key: 'calculating', label: 'Calculating' },
  { key: 'generating', label: 'Generating' },
]

export default function ProgressBar({ progress }: ProgressBarProps) {
  const percent = progress?.percent ?? 0
  const currentStep = progress?.step ?? 'loading'

  return (
    <div className="w-full">
      {/* Step indicators */}
      <div className="flex justify-between mb-4">
        {STEPS.map((step, index) => {
          const stepIndex = STEPS.findIndex(s => s.key === currentStep)
          const isActive = index <= stepIndex
          const isCurrent = step.key === currentStep

          return (
            <div key={step.key} className="flex flex-col items-center">
              <div
                className={`
                  w-8 h-8 rounded-full flex items-center justify-center mb-2 transition-all
                  ${isCurrent ? 'bg-accent-cyan text-bg-primary' : isActive ? 'bg-accent-cyan/30 text-accent-cyan' : 'bg-bg-hover text-text-secondary'}
                `}
              >
                {index + 1}
              </div>
              <span className={`text-xs ${isActive ? 'text-text-primary' : 'text-text-secondary'}`}>
                {step.label}
              </span>
            </div>
          )
        })}
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
        {progress?.message ?? 'Connecting...'}
      </p>
    </div>
  )
}
