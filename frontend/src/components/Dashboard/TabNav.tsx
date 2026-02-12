interface TabNavProps {
  tabs: string[]
  activeTab: string
  onTabChange: (tab: string) => void
}

export default function TabNav({ tabs, activeTab, onTabChange }: TabNavProps) {
  return (
    <nav className="flex gap-1 overflow-x-auto scrollbar-hide bg-bg-card/50 rounded-xl p-1.5 mb-2">
      {tabs.map(tab => (
        <button
          key={tab}
          onClick={() => onTabChange(tab)}
          className={`
            px-5 py-2.5 rounded-lg font-medium whitespace-nowrap transition-all text-sm
            ${activeTab === tab
              ? 'bg-gradient-to-r from-accent-cyan to-accent-purple text-white font-semibold shadow-lg shadow-accent-purple/20'
              : 'text-text-secondary hover:text-text-primary hover:bg-white/[0.05]'}
          `}
        >
          {tab}
        </button>
      ))}
    </nav>
  )
}
