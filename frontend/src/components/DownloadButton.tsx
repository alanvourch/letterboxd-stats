interface DownloadButtonProps {
  url: string
}

export default function DownloadButton({ url }: DownloadButtonProps) {
  return (
    <a
      href={url}
      download="letterboxd_stats.html"
      className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-accent-cyan to-accent-purple rounded-lg font-medium hover:opacity-90 transition-opacity"
    >
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
      Download HTML
    </a>
  )
}
