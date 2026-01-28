import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar, Line, Doughnut } from 'react-chartjs-2'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

interface ChartWrapperProps {
  config: string | undefined
  type: 'bar' | 'line' | 'doughnut'
}

export default function ChartWrapper({ config, type }: ChartWrapperProps) {
  if (!config) {
    return <div className="text-text-secondary text-center py-8">No chart data</div>
  }

  let chartConfig
  try {
    chartConfig = typeof config === 'string' ? JSON.parse(config) : config
  } catch {
    return <div className="text-text-secondary text-center py-8">Invalid chart data</div>
  }

  const { data, options } = chartConfig

  // Apply dark theme defaults
  const darkOptions = {
    ...options,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      ...options?.plugins,
      legend: {
        ...options?.plugins?.legend,
        labels: {
          color: '#a0a0b0',
          ...options?.plugins?.legend?.labels,
        },
      },
    },
    scales: type !== 'doughnut' ? {
      x: {
        ...options?.scales?.x,
        ticks: { color: '#a0a0b0', ...options?.scales?.x?.ticks },
        grid: { color: '#252540', ...options?.scales?.x?.grid },
      },
      y: {
        ...options?.scales?.y,
        ticks: { color: '#a0a0b0', ...options?.scales?.y?.ticks },
        grid: { color: '#252540', ...options?.scales?.y?.grid },
      },
    } : undefined,
  }

  const chartProps = { data, options: darkOptions }

  return (
    <div className="h-64">
      {type === 'bar' && <Bar {...chartProps} />}
      {type === 'line' && <Line {...chartProps} />}
      {type === 'doughnut' && <Doughnut {...chartProps} />}
    </div>
  )
}
