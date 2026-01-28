interface TabNavProps {
  tabs: string[]
  activeTab: string
  onTabChange: (tab: string) => void
}

export default function TabNav({ tabs, activeTab, onTabChange }: TabNavProps) {
  return (
    <nav className="flex gap-1 px-4 overflow-x-auto scrollbar-hide">
      {tabs.map(tab => (
        <button
          key={tab}
          onClick={() => onTabChange(tab)}
          className={`
            px-4 py-2 rounded-t-lg font-medium whitespace-nowrap transition-all
            ${activeTab === tab
              ? 'bg-bg-card text-accent-cyan'
              : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'}
          `}
        >
          {tab}
        </button>
      ))}
    </nav>
  )
}
