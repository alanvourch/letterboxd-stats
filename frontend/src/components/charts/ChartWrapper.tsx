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

  // Apply dark theme defaults with glassmorphism-compatible styling
  const darkOptions = {
    ...options,
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: { top: 5, bottom: 5 },
      ...options?.layout,
    },
    plugins: {
      ...options?.plugins,
      legend: {
        ...options?.plugins?.legend,
        labels: {
          color: '#a0a0b0',
          padding: 16,
          font: { size: 12 },
          ...options?.plugins?.legend?.labels,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(13, 13, 20, 0.95)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        titleColor: '#ffffff',
        bodyColor: '#a0a0b0',
        cornerRadius: 8,
        padding: 12,
        displayColors: true,
        boxPadding: 4,
        ...options?.plugins?.tooltip,
      },
    },
    scales: type !== 'doughnut' ? {
      x: {
        ...options?.scales?.x,
        ticks: { color: '#71717a', font: { size: 11 }, ...options?.scales?.x?.ticks },
        grid: { color: 'rgba(255, 255, 255, 0.06)', ...options?.scales?.x?.grid },
      },
      y: {
        ...options?.scales?.y,
        ticks: { color: '#71717a', font: { size: 11 }, ...options?.scales?.y?.ticks },
        grid: { color: 'rgba(255, 255, 255, 0.06)', ...options?.scales?.y?.grid },
      },
    } : undefined,
  }

  const chartProps = { data, options: darkOptions }

  return (
    <div className="h-[300px]">
      {type === 'bar' && <Bar {...chartProps} />}
      {type === 'line' && <Line {...chartProps} />}
      {type === 'doughnut' && <Doughnut {...chartProps} />}
    </div>
  )
}
