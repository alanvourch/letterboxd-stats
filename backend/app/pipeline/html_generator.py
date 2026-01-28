"""
Generate HTML dashboard with modern tabbed layout, modals, and movie posters
Dashboard v5.4 - Optimized TMDB fetching, enhanced People/Studios tab, sub-tabs navigation
"""
from typing import Dict
import json
from app import config


class HTMLGenerator:
    """Generate interactive HTML dashboard with tabs, modals, and posters"""

    POSTER_BASE_URL = f"{config.TMDB_IMAGE_BASE_URL}/{config.POSTER_SIZE}"
    POSTER_PLACEHOLDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='185' height='278' viewBox='0 0 185 278'%3E%3Crect fill='%231a1a2e' width='185' height='278'/%3E%3Ctext fill='%234a4a5a' font-family='sans-serif' font-size='14' x='50%25' y='50%25' text-anchor='middle'%3ENo Poster%3C/text%3E%3C/svg%3E"

    def __init__(self, stats: Dict, charts: Dict):
        self.stats = stats
        self.charts = charts

    def generate(self) -> str:
        """Generate complete HTML page"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Letterboxd Stats Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    {self._generate_styles()}
</head>
<body>
    <div class="app">
        {self._generate_header()}
        {self._generate_nav()}
        <main class="main-content">
            {self._generate_overview_tab()}
            {self._generate_journey_tab()}
            {self._generate_year_tab('last_full_year')}
            {self._generate_year_tab('current_year')}
            {self._generate_decades_tab()}
            {self._generate_people_tab()}
            {self._generate_insights_tab()}
        </main>
        {self._generate_footer()}
    </div>
    {self._generate_modal()}
    {self._generate_scripts()}
</body>
</html>'''

    def _generate_styles(self) -> str:
        """Generate modern CSS styles"""
        return '''<style>
:root {
    --bg-primary: #0d0d14;
    --bg-secondary: #14141f;
    --bg-tertiary: #1a1a2e;
    --bg-card: rgba(255, 255, 255, 0.03);
    --bg-card-hover: rgba(255, 255, 255, 0.06);
    --border-color: rgba(255, 255, 255, 0.08);
    --border-color-light: rgba(255, 255, 255, 0.12);
    --text-primary: #f4f4f5;
    --text-secondary: #a1a1aa;
    --text-muted: #71717a;
    --accent-cyan: #00d4ff;
    --accent-purple: #7c3aed;
    --accent-pink: #f472b6;
    --accent-yellow: #fbbf24;
    --accent-green: #34d399;
    --accent-orange: #fb923c;
    --accent-red: #ef4444;
    --liked-color: #ef4444;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
    line-height: 1.5;
}

.app {
    max-width: 1400px;
    margin: 0 auto;
    padding: 1.5rem;
}

/* Header */
.header {
    text-align: center;
    padding: 2rem 1rem;
    margin-bottom: 1rem;
}

.header h1 {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple), var(--accent-pink));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}

.header .subtitle {
    color: var(--text-secondary);
    font-size: 1rem;
}

/* Navigation */
.nav {
    display: flex;
    gap: 0.5rem;
    padding: 0.5rem;
    background: var(--bg-secondary);
    border-radius: var(--radius-lg);
    margin-bottom: 2rem;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

.nav-btn {
    flex: 1;
    min-width: fit-content;
    padding: 0.75rem 1.25rem;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    font-family: inherit;
    font-size: 0.9rem;
    font-weight: 500;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}

.nav-btn:hover {
    background: var(--bg-card-hover);
    color: var(--text-primary);
}

.nav-btn.active {
    background: var(--accent-purple);
    color: white;
}

.nav-btn .year-badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    background: rgba(255,255,255,0.15);
    border-radius: 9999px;
    font-size: 0.75rem;
    margin-left: 0.5rem;
}

/* Tab content */
.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Stats Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    text-align: center;
    transition: all 0.2s;
}

.stat-card:hover {
    background: var(--bg-card-hover);
    transform: translateY(-2px);
}

.stat-number {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.stat-label {
    color: var(--text-secondary);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stat-card.cyan .stat-number { color: var(--accent-cyan); }
.stat-card.purple .stat-number { color: var(--accent-purple); }
.stat-card.pink .stat-number { color: var(--accent-pink); }
.stat-card.yellow .stat-number { color: var(--accent-yellow); }
.stat-card.green .stat-number { color: var(--accent-green); }
.stat-card.orange .stat-number { color: var(--accent-orange); }
.stat-card.red .stat-number { color: var(--liked-color); }

/* Section */
.section {
    margin-bottom: 2.5rem;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
}

.section-subtitle {
    color: var(--text-secondary);
    font-size: 0.85rem;
}

/* Charts Grid */
.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

@media (max-width: 500px) {
    .charts-grid {
        grid-template-columns: 1fr;
    }
}

.chart-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
}

.chart-card h3 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--text-primary);
}

.chart-container {
    position: relative;
    height: 280px;
}

.chart-container-pie {
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* People Sub-Tab Navigation */
.people-subtabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
    overflow-x: auto;
    padding-bottom: 0.25rem;
}

.people-subtab {
    padding: 0.5rem 1.25rem;
    border-radius: 999px;
    border: 1px solid var(--border-color);
    background: var(--bg-card);
    color: var(--text-secondary);
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
    font-family: inherit;
}

.people-subtab:hover {
    border-color: var(--accent-purple);
    color: var(--text-primary);
}

.people-subtab.active {
    background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan));
    border-color: transparent;
    color: white;
    font-weight: 600;
}

.people-subcontent {
    display: none;
}

.people-subcontent.active {
    display: block;
}

/* People Grid (Actors/Directors) - Enhanced v5.0 */
.people-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 1.25rem;
}

.person-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    cursor: pointer;
    transition: all 0.25s ease;
    display: flex;
    gap: 1.25rem;
    align-items: flex-start;
    position: relative;
    overflow: hidden;
}

.person-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
    opacity: 0;
    transition: opacity 0.25s;
}

.person-card:hover {
    background: var(--bg-card-hover);
    border-color: var(--accent-purple);
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.15);
}

.person-card:hover::before {
    opacity: 1;
}

.person-card .person-photo {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
    border: 3px solid var(--border-color);
    background: var(--bg-secondary);
}

.person-card .person-photo-placeholder {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    flex-shrink: 0;
    background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.2rem;
    font-weight: 700;
    color: white;
}

.person-card .person-info {
    flex: 1;
    min-width: 0;
}

.person-card .person-rank {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.2rem;
}

.person-card .name {
    font-weight: 600;
    font-size: 1.2rem;
    margin-bottom: 0.4rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.person-card .person-stats {
    display: flex;
    gap: 1rem;
    font-size: 0.85rem;
    margin-bottom: 0.6rem;
}

.person-card .person-stat {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.person-card .person-stat .stat-value {
    font-weight: 600;
}

.person-card .person-stat.watched { color: var(--accent-cyan); }
.person-card .person-stat.liked { color: var(--liked-color); }
.person-card .person-stat.rating { color: var(--accent-yellow); }

.person-card .like-ratio {
    height: 3px;
    background: var(--bg-secondary);
    border-radius: 2px;
    overflow: hidden;
}

.person-card .like-ratio-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-cyan), var(--liked-color));
    border-radius: 2px;
    transition: width 0.5s ease;
}

.person-card .person-posters {
    display: flex;
    gap: 0.4rem;
    margin-top: 0.6rem;
    overflow: hidden;
}

.person-card .person-mini-poster {
    width: 48px;
    height: 72px;
    border-radius: 4px;
    object-fit: cover;
    opacity: 0.85;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
}

/* Crew grid (composers, cinematographers, writers) - same size as person cards */
.crew-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 1.25rem;
}

.crew-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    display: flex;
    gap: 1.25rem;
    align-items: flex-start;
    cursor: pointer;
    transition: all 0.25s;
    position: relative;
    overflow: hidden;
}

.crew-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-pink), var(--accent-purple));
    opacity: 0;
    transition: opacity 0.25s;
}

.crew-card:hover {
    background: var(--bg-card-hover);
    border-color: var(--accent-purple);
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.15);
}

.crew-card:hover::before {
    opacity: 1;
}

.crew-card .crew-photo {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
    border: 3px solid var(--border-color);
    background: var(--bg-secondary);
}

.crew-card .crew-photo-placeholder {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    flex-shrink: 0;
    background: linear-gradient(135deg, var(--accent-pink), var(--accent-purple));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.2rem;
    font-weight: 700;
    color: white;
}

.crew-card .crew-info {
    flex: 1;
    min-width: 0;
}

.crew-card .crew-name {
    font-weight: 600;
    font-size: 1.2rem;
    margin-bottom: 0.4rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.crew-card .crew-meta {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-bottom: 0.6rem;
}

.crew-card .crew-posters {
    display: flex;
    gap: 0.4rem;
}

.crew-card .crew-mini-poster {
    width: 48px;
    height: 72px;
    border-radius: 4px;
    object-fit: cover;
    opacity: 0.85;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
}

/* Studios section */
.studio-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 1.25rem;
}

.studio-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    cursor: pointer;
    transition: all 0.25s;
    display: flex;
    gap: 1.25rem;
    align-items: center;
}

.studio-card:hover {
    border-color: var(--accent-cyan);
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0, 188, 212, 0.15);
}

.studio-card .studio-logo {
    width: 80px;
    height: 80px;
    object-fit: contain;
    flex-shrink: 0;
    background: white;
    border-radius: var(--radius-md);
    padding: 8px;
}

.studio-card .studio-logo-placeholder {
    width: 80px;
    height: 80px;
    flex-shrink: 0;
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    font-weight: 700;
    color: white;
}

.studio-card .studio-info {
    flex: 1;
    min-width: 0;
}

.studio-card .studio-name {
    font-weight: 600;
    font-size: 1.1rem;
    margin-bottom: 0.4rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.studio-card .studio-meta {
    font-size: 0.85rem;
    color: var(--text-secondary);
    display: flex;
    gap: 1rem;
}

.studio-card .studio-meta .stat-value {
    font-weight: 600;
    color: var(--accent-cyan);
}

/* Film Posters Grid - Fixed 4 per row layout for year wrap */
.posters-grid-adaptive {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
}

.posters-grid-adaptive .poster-card {
    min-height: 150px;
}

.posters-grid-adaptive .poster-card img {
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
}

@media (max-width: 768px) {
    .posters-grid-adaptive {
        grid-template-columns: repeat(4, 1fr);
        gap: 0.5rem;
    }
}

@media (max-width: 500px) {
    .posters-grid-adaptive {
        grid-template-columns: repeat(2, 1fr);
        gap: 0.5rem;
    }
}

/* Auto-fill poster grid */
.posters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 0.75rem;
}

.poster-card {
    position: relative;
    border-radius: var(--radius-md);
    overflow: hidden;
    aspect-ratio: 2/3;
    background: var(--bg-secondary);
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.poster-card:hover {
    transform: scale(1.05);
    z-index: 1;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
}

.poster-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.poster-card .overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 2.5rem 0.5rem 0.5rem;
    background: linear-gradient(transparent, rgba(0,0,0,0.95));
}

.poster-card .title {
    font-size: 0.8rem;
    font-weight: 600;
    line-height: 1.25;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

.poster-card .year {
    font-size: 0.7rem;
    color: var(--text-secondary);
    margin-top: 0.15rem;
}

.poster-card .rating {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background: rgba(0,0,0,0.8);
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    backdrop-filter: blur(4px);
}

.poster-card .rating.high { color: var(--accent-green); }
.poster-card .rating.mid { color: var(--accent-yellow); }
.poster-card .rating.low { color: var(--liked-color); }

.poster-card .liked-badge {
    position: absolute;
    top: 0.5rem;
    left: 0.5rem;
    color: var(--liked-color);
    font-size: 1rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.7);
    filter: drop-shadow(0 0 3px rgba(239, 68, 68, 0.5));
}

/* Year Wrap Section */
.year-wrap {
    background: linear-gradient(145deg, rgba(124, 58, 237, 0.08), rgba(244, 114, 182, 0.08), rgba(0, 212, 255, 0.05));
    border: 1px solid var(--border-color);
    border-radius: var(--radius-xl);
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.year-wrap::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-purple), var(--accent-pink), var(--accent-cyan));
}

.year-wrap .year-header {
    text-align: center;
    margin-bottom: 2rem;
}

.year-wrap .year-number {
    font-size: 5rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink), var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin-bottom: 0.25rem;
}

.year-wrap .year-label {
    color: var(--text-secondary);
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.year-highlight {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}

@media (max-width: 900px) {
    .year-highlight {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 500px) {
    .year-highlight {
        grid-template-columns: 1fr;
    }
}

.highlight-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1rem 1.25rem;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 100px;
}

.highlight-card .icon {
    font-size: 1.5rem;
    margin-bottom: 0.25rem;
    line-height: 1;
}

.highlight-card .icon.heart-icon {
    color: var(--liked-color);
}

.highlight-card .value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--accent-cyan);
    line-height: 1.1;
}

.highlight-card .value.liked-value {
    color: var(--liked-color);
}

.highlight-card .label {
    color: var(--text-secondary);
    font-size: 0.8rem;
    margin-top: 0.15rem;
}

.highlight-card .sub-value {
    color: var(--text-muted);
    font-size: 0.75rem;
    margin-top: 0.1rem;
}

.top-person-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.top-person-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    transition: all 0.2s;
}

.top-person-card:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-color-light);
}

.top-person-card h4 {
    color: var(--text-secondary);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
}

.top-person-card .person-name {
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
    background: linear-gradient(135deg, var(--text-primary), var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.top-person-card .person-count {
    color: var(--text-muted);
    font-size: 0.85rem;
    margin-bottom: 1rem;
}

.top-person-card .mini-posters {
    display: flex;
    gap: 0.75rem;
    overflow-x: auto;
    padding-bottom: 0.5rem;
    scrollbar-width: thin;
    scrollbar-color: var(--bg-tertiary) transparent;
}

.top-person-card .mini-posters::-webkit-scrollbar {
    height: 4px;
}

.top-person-card .mini-posters::-webkit-scrollbar-thumb {
    background: var(--bg-tertiary);
    border-radius: 2px;
}

.top-person-card .mini-poster-wrapper {
    position: relative;
    flex-shrink: 0;
}

.top-person-card .mini-poster {
    width: 90px;
    height: 135px;
    border-radius: var(--radius-sm);
    object-fit: cover;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    transition: transform 0.2s;
}

.top-person-card .mini-poster:hover {
    transform: scale(1.05);
}

.top-person-card .mini-poster-wrapper .mini-liked {
    position: absolute;
    top: 6px;
    left: 6px;
    font-size: 0.85rem;
    color: var(--liked-color);
    text-shadow: 0 1px 4px rgba(0,0,0,0.9);
    filter: drop-shadow(0 0 2px rgba(239, 68, 68, 0.5));
}

/* Insights Section Cards */
.insights-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.insight-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
}

.insight-card .insight-label {
    color: var(--text-muted);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
}

.insight-card .insight-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}

.insight-card .insight-sub {
    color: var(--text-secondary);
    font-size: 0.85rem;
    word-break: break-word;
    overflow-wrap: break-word;
}

.insight-card.accent-cyan .insight-value { color: var(--accent-cyan); }
.insight-card.accent-purple .insight-value { color: var(--accent-purple); }
.insight-card.accent-pink .insight-value { color: var(--accent-pink); }
.insight-card.accent-yellow .insight-value { color: var(--accent-yellow); }
.insight-card.accent-green .insight-value { color: var(--accent-green); }
.insight-card.accent-orange .insight-value { color: var(--accent-orange); }

/* Modal */
.modal-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.85);
    z-index: 1000;
    align-items: center;
    justify-content: center;
    padding: 1rem;
}

.modal-overlay.active {
    display: flex;
}

.modal {
    background: var(--bg-secondary);
    border-radius: var(--radius-xl);
    max-width: 900px;
    max-height: 85vh;
    width: 100%;
    overflow: hidden;
    animation: modalIn 0.3s ease;
}

@keyframes modalIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
}

.modal-header .meta {
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.modal-close {
    background: var(--bg-card);
    border: none;
    color: var(--text-primary);
    width: 40px;
    height: 40px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 1.25rem;
    transition: background 0.2s;
}

.modal-close:hover {
    background: var(--bg-card-hover);
}

.modal-body {
    padding: 1.5rem;
    overflow-y: auto;
    max-height: calc(85vh - 100px);
}

.modal-films-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 1rem;
}

.modal-film {
    text-align: center;
    position: relative;
}

.modal-film .poster-wrapper {
    position: relative;
    margin-bottom: 0.5rem;
}

.modal-film img {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    border-radius: var(--radius-sm);
}

.modal-film .film-liked {
    position: absolute;
    top: 6px;
    left: 6px;
    color: var(--liked-color);
    font-size: 1rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.9);
    filter: drop-shadow(0 0 3px rgba(239, 68, 68, 0.5));
}

.modal-film .film-title {
    font-size: 0.75rem;
    font-weight: 500;
    line-height: 1.2;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.modal-film .film-year {
    font-size: 0.65rem;
    color: var(--text-secondary);
}

.modal-film .film-rating {
    font-size: 0.7rem;
    color: var(--accent-yellow);
    margin-top: 0.25rem;
}

/* Footer */
.footer {
    text-align: center;
    padding: 2rem;
    color: var(--text-muted);
    font-size: 0.85rem;
}

.footer a {
    color: var(--accent-cyan);
    text-decoration: none;
}

.footer a:hover {
    text-decoration: underline;
}

/* Utility classes */
.two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

@media (max-width: 768px) {
    .two-col {
        grid-template-columns: 1fr;
    }
}

.empty-state {
    text-align: center;
    padding: 3rem;
    color: var(--text-secondary);
}

/* Top rated section in year wrap */
.rated-section {
    margin-bottom: 1.5rem;
    background: var(--bg-card);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    border: 1px solid var(--border-color);
}

.rated-section h3 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.rated-section h3 .icon {
    font-size: 1.25rem;
}

/* V5.0: Journey Section */
.journey-hero {
    background: linear-gradient(145deg, rgba(124, 58, 237, 0.15), rgba(0, 212, 255, 0.1));
    border: 1px solid var(--border-color);
    border-radius: var(--radius-xl);
    padding: 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.journey-hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple), var(--accent-pink));
}

.milestone-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
}

.milestone-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.milestone-card:hover {
    transform: translateY(-4px);
    border-color: var(--accent-purple);
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.2);
}

.milestone-card .milestone-number {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.milestone-card .milestone-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.75rem;
}

.milestone-card .film-title {
    font-weight: 600;
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}

.milestone-card .film-date {
    font-size: 0.75rem;
    color: var(--text-secondary);
}

.milestone-card .milestone-poster {
    width: 80px;
    height: 120px;
    border-radius: var(--radius-sm);
    object-fit: cover;
    margin: 0.75rem auto;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}

/* Fun Facts */
.fun-facts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
}

.fun-fact-card {
    background: linear-gradient(145deg, var(--bg-card), rgba(124, 58, 237, 0.05));
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    transition: all 0.2s;
}

.fun-fact-card:hover {
    border-color: var(--accent-purple);
    transform: translateY(-2px);
}

.fun-fact-card .fact-icon {
    font-size: 2rem;
    line-height: 1;
}

.fun-fact-card .fact-text {
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 0.25rem;
}

.fun-fact-card .fact-subtext {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

/* 5-Star Poster Wall */
.poster-wall {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
    gap: 0.5rem;
}

.poster-wall .wall-poster {
    aspect-ratio: 2/3;
    border-radius: var(--radius-sm);
    object-fit: cover;
    transition: all 0.2s;
    cursor: pointer;
}

.poster-wall .wall-poster:hover {
    transform: scale(1.1);
    z-index: 10;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
}

/* Record Stats */
.record-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
}

.record-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    text-align: center;
}

.record-card .record-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent-cyan);
}

.record-card .record-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 0.25rem;
}

.record-card .record-detail {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
}

/* V5.0: Decades Section */
.decade-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.decade-card .decade-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.decade-card .decade-name {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.decade-card .decade-stats {
    display: flex;
    gap: 1rem;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.decade-card .decade-films {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    padding-bottom: 0.5rem;
}

.decade-card .decade-poster {
    width: 70px;
    height: 105px;
    border-radius: var(--radius-sm);
    object-fit: cover;
    flex-shrink: 0;
    transition: transform 0.2s;
}

.decade-card .decade-poster:hover {
    transform: scale(1.08);
}

/* Rewatch Section */
.rewatch-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 1rem;
}

.rewatch-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 0.75rem;
    text-align: center;
    position: relative;
}

.rewatch-card .rewatch-badge {
    position: absolute;
    top: -8px;
    right: -8px;
    background: var(--accent-purple);
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.25rem 0.5rem;
    border-radius: 9999px;
}

.rewatch-card img {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    border-radius: var(--radius-sm);
    margin-bottom: 0.5rem;
}

.rewatch-card .rewatch-title {
    font-size: 0.8rem;
    font-weight: 500;
    line-height: 1.2;
}

/* Animated Stats */
.stat-number {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

@keyframes countUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-in {
    animation: countUp 0.5s ease-out forwards;
}

/* First/Last Film Cards */
.journey-film-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    display: flex;
    gap: 1.5rem;
    align-items: center;
}

.journey-film-card img {
    width: 100px;
    height: 150px;
    border-radius: var(--radius-md);
    object-fit: cover;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
}

.journey-film-card .film-info h4 {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}

.journey-film-card .film-info .title {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.journey-film-card .film-info .date {
    color: var(--text-secondary);
    font-size: 0.9rem;
}
</style>'''

    def _generate_header(self) -> str:
        """Generate header"""
        basic = self.stats.get('basic', {})
        return f'''
<header class="header">
    <h1>Letterboxd Stats</h1>
    <p class="subtitle">{basic.get('total_watched', 0):,} films watched</p>
</header>'''

    def _generate_nav(self) -> str:
        """Generate navigation tabs"""
        yearly = self.stats.get('yearly_breakdown', {})
        last_year = yearly.get('last_full_year_value', 2025)
        current_year = yearly.get('current_year_value', 2026)

        return f'''
<nav class="nav">
    <button class="nav-btn active" data-tab="overview">Overview</button>
    <button class="nav-btn" data-tab="journey">🎯 Journey</button>
    <button class="nav-btn" data-tab="year-last">{last_year}<span class="year-badge">Wrap</span></button>
    <button class="nav-btn" data-tab="year-current">{current_year}<span class="year-badge">Live</span></button>
    <button class="nav-btn" data-tab="decades">📅 Decades</button>
    <button class="nav-btn" data-tab="people">People/Studios</button>
    <button class="nav-btn" data-tab="insights">Insights</button>
</nav>'''

    def _generate_overview_tab(self) -> str:
        """Generate overview tab content"""
        basic = self.stats.get('basic', {})

        # Calculate like ratio
        watched = basic.get('total_watched', 0)
        liked = basic.get('total_liked', 0)
        like_ratio = round(liked / watched * 100, 1) if watched > 0 else 0

        return f'''
<div id="overview" class="tab-content active">
    <div class="stats-grid">
        <div class="stat-card cyan">
            <div class="stat-number">{basic.get('total_watched', 0):,}</div>
            <div class="stat-label">Films Watched</div>
        </div>
        <div class="stat-card red">
            <div class="stat-number">{basic.get('total_liked', 0):,}</div>
            <div class="stat-label">Films Liked</div>
        </div>
        <div class="stat-card pink">
            <div class="stat-number">{like_ratio}%</div>
            <div class="stat-label">Like Ratio</div>
        </div>
        <div class="stat-card yellow">
            <div class="stat-number">{basic.get('avg_rating', 0)}</div>
            <div class="stat-label">Avg Rating</div>
        </div>
        <div class="stat-card green">
            <div class="stat-number">{basic.get('total_rated', 0):,}</div>
            <div class="stat-label">Rated</div>
        </div>
        <div class="stat-card orange">
            <div class="stat-number">{basic.get('total_watchlist', 0):,}</div>
            <div class="stat-label">Watchlist</div>
        </div>
    </div>

    <section class="section">
        <div class="section-header">
            <h2 class="section-title">❤️ Watched vs Liked</h2>
            <span class="section-subtitle">How much do you really love what you watch?</span>
        </div>
        <div class="charts-grid">
            <div class="chart-card">
                <h3>Genres: Watched vs Liked</h3>
                <div class="chart-container">
                    <canvas id="genresWatchedLikedChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3>Actors: Watched vs Liked</h3>
                <div class="chart-container">
                    <canvas id="actorsWatchedLikedChart"></canvas>
                </div>
            </div>
        </div>
    </section>

    <section class="section">
        <div class="section-header">
            <h2 class="section-title">📊 Activity</h2>
        </div>
        <div class="charts-grid">
            <div class="chart-card">
                <h3>Films Per Year</h3>
                <div class="chart-container">
                    <canvas id="yearlyChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3>Monthly Activity (Last 24 Months)</h3>
                <div class="chart-container">
                    <canvas id="monthlyChart"></canvas>
                </div>
            </div>
        </div>
    </section>

    <section class="section">
        <div class="section-header">
            <h2 class="section-title">🎬 Directors & Runtime</h2>
        </div>
        <div class="charts-grid">
            <div class="chart-card">
                <h3>Directors: Watched vs Liked</h3>
                <div class="chart-container">
                    <canvas id="directorsWatchedLikedChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3>Runtime Distribution</h3>
                <div class="chart-container">
                    <canvas id="runtimeChart"></canvas>
                </div>
            </div>
        </div>
    </section>
</div>'''

    def _generate_year_tab(self, year_key: str) -> str:
        """Generate year wrap-up or current year tab"""
        yearly = self.stats.get('yearly_breakdown', {})
        year_stats = yearly.get(year_key, {})
        year_value = yearly.get(f'{year_key}_value', 0)

        is_wrap = year_key == 'last_full_year'
        tab_id = 'year-last' if is_wrap else 'year-current'
        label = 'Year in Review' if is_wrap else 'Year in Progress'

        if not year_stats or year_stats.get('total_films', 0) == 0:
            return f'''
<div id="{tab_id}" class="tab-content">
    <div class="year-wrap">
        <div class="year-header">
            <div class="year-number">{year_value}</div>
            <div class="year-label">{label}</div>
        </div>
        <div class="empty-state">
            <p>No films logged for {year_value} yet.</p>
        </div>
    </div>
</div>'''

        # Month name mapping - full names for better readability
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        most_active_month = year_stats.get('most_active_month', 0)
        most_active_month_name = month_names[most_active_month] if most_active_month else 'N/A'
        most_active_month_count = year_stats.get('most_active_month_count', 0)

        # Generate top rated posters (4 per row, 2 rows = 8 movies)
        top_rated_html = self._generate_rated_poster_grid(year_stats.get('top_rated', []), 'Highest Rated', 'trophy')
        bottom_rated_html = self._generate_rated_poster_grid(year_stats.get('bottom_rated', []), 'Lowest Rated', 'thumbs-down')

        # Top actor section - show ALL films
        top_actor = year_stats.get('top_actor')
        top_actor_html = ''
        if top_actor:
            actor_films = top_actor.get('films', [])
            actor_posters = ''.join([
                f'''<div class="mini-poster-wrapper">
                    <img class="mini-poster" src="{self._poster_url(f.get("poster_path"))}" alt="{f.get("title")}" loading="lazy">
                    {('<span class="mini-liked">❤️</span>' if f.get("liked") else '')}
                </div>'''
                for f in actor_films
            ])
            top_actor_html = f'''
<div class="top-person-card">
    <h4>🎭 Most Watched Actor</h4>
    <div class="person-name">{top_actor.get('name', 'N/A')}</div>
    <div class="person-count">{top_actor.get('count', 0)} films this year</div>
    <div class="mini-posters">{actor_posters}</div>
</div>'''

        # Top director section - show ALL films
        top_director = year_stats.get('top_director')
        top_director_html = ''
        if top_director:
            director_films = top_director.get('films', [])
            director_posters = ''.join([
                f'''<div class="mini-poster-wrapper">
                    <img class="mini-poster" src="{self._poster_url(f.get("poster_path"))}" alt="{f.get("title")}" loading="lazy">
                    {('<span class="mini-liked">❤️</span>' if f.get("liked") else '')}
                </div>'''
                for f in director_films
            ])
            top_director_html = f'''
<div class="top-person-card">
    <h4>🎬 Most Watched Director</h4>
    <div class="person-name">{top_director.get('name', 'N/A')}</div>
    <div class="person-count">{top_director.get('count', 0)} films this year</div>
    <div class="mini-posters">{director_posters}</div>
</div>'''

        return f'''
<div id="{tab_id}" class="tab-content">
    <div class="year-wrap">
        <div class="year-header">
            <div class="year-number">{year_value}</div>
            <div class="year-label">{label}</div>
        </div>

        <div class="year-highlight">
            <div class="highlight-card">
                <div class="icon">🎬</div>
                <div class="value">{year_stats.get('total_films', 0)}</div>
                <div class="label">Films Logged</div>
            </div>
            <div class="highlight-card">
                <div class="icon heart-icon">❤️</div>
                <div class="value liked-value">{year_stats.get('total_liked', 0)}</div>
                <div class="label">Films Liked</div>
            </div>
            <div class="highlight-card">
                <div class="icon">⭐</div>
                <div class="value">{year_stats.get('avg_rating', 0)}</div>
                <div class="label">Avg Rating</div>
            </div>
            <div class="highlight-card">
                <div class="icon">📅</div>
                <div class="value">{most_active_month_name}</div>
                <div class="label">Most Active</div>
                <div class="sub-value">{most_active_month_count} films</div>
            </div>
        </div>

        <div class="top-person-section">
            {top_actor_html}
            {top_director_html}
        </div>

        <div class="two-col">
            {top_rated_html}
            {bottom_rated_html}
        </div>
    </div>
</div>'''

    def _generate_rated_poster_grid(self, films: list, title: str, icon: str) -> str:
        """Generate a grid of movie posters for top/bottom rated - adaptive layout"""
        if not films:
            return f'<div class="rated-section"><h3>{title}</h3><p class="empty-state">No films</p></div>'

        icon_html = '🏆' if icon == 'trophy' else '👎'

        posters_html = ''
        for film in films:
            rating = film.get('rating', 0)
            rating_class = 'high' if rating >= 4 else 'mid' if rating >= 3 else 'low'
            liked_badge = '<span class="liked-badge">❤️</span>' if film.get('liked') else ''
            rating_stars = ''
            if rating:
                full_stars = int(rating)
                half_star = rating % 1 >= 0.5
                rating_stars = '★' * full_stars + ('½' if half_star else '')

            posters_html += f'''
<div class="poster-card">
    <img src="{self._poster_url(film.get('poster_path'))}" alt="{film.get('title')}" loading="lazy">
    {liked_badge}
    <span class="rating {rating_class}">{rating_stars}</span>
    <div class="overlay">
        <div class="title">{film.get('title', 'Unknown')}</div>
        <div class="year">{film.get('year', '')}</div>
    </div>
</div>'''

        return f'''
<div class="rated-section">
    <h3><span class="icon">{icon_html}</span> {title}</h3>
    <div class="posters-grid-adaptive">{posters_html}</div>
</div>'''

    def _generate_person_card(self, person: dict, person_type: str, index: int) -> str:
        """Generate an enhanced person card with photo and stats"""
        name = person.get('name', 'Unknown')
        profile_path = person.get('profile_path')
        like_ratio = person.get('like_ratio', 0)
        avg_rating = person.get('avg_rating', 0)
        initial = name[0] if name else '?'

        # Profile photo or placeholder
        if profile_path:
            photo_html = f'<img class="person-photo" src="{self.POSTER_BASE_URL.replace(config.POSTER_SIZE, "w185")}/{profile_path}" alt="{name}" loading="lazy">'
        else:
            photo_html = f'<div class="person-photo-placeholder">{initial}</div>'

        # Mini poster strip (first 5 films)
        films = person.get('films', [])[:5]
        posters_html = ''
        for f in films:
            posters_html += f'<img class="person-mini-poster" src="{self._poster_url(f.get("poster_path"))}" alt="{f.get("title")}" loading="lazy">'

        return f'''
<div class="person-card" data-person-type="{person_type}" data-person-index="{index}">
    {photo_html}
    <div class="person-info">
        <div class="person-rank">#{index + 1}</div>
        <div class="name">{name}</div>
        <div class="person-stats">
            <span class="person-stat watched"><span class="stat-value">{person.get('count', 0)}</span> films</span>
            <span class="person-stat liked">❤️ <span class="stat-value">{person.get('liked_count', 0)}</span></span>
            <span class="person-stat rating">★ <span class="stat-value">{avg_rating}</span></span>
        </div>
        <div class="like-ratio">
            <div class="like-ratio-fill" style="width: {like_ratio}%"></div>
        </div>
        <div class="person-posters">{posters_html}</div>
    </div>
</div>'''

    def _generate_crew_card(self, person: dict, person_type: str, index: int) -> str:
        """Generate a crew card with photo and poster strip"""
        name = person.get('name', 'Unknown')
        profile_path = person.get('profile_path')
        initial = name[0] if name else '?'

        if profile_path:
            photo_html = f'<img class="crew-photo" src="{self.POSTER_BASE_URL.replace(config.POSTER_SIZE, "w185")}/{profile_path}" alt="{name}" loading="lazy">'
        else:
            photo_html = f'<div class="crew-photo-placeholder">{initial}</div>'

        # Mini poster strip (first 3 films)
        films = person.get('films', [])[:3]
        posters_html = ''
        for f in films:
            posters_html += f'<img class="crew-mini-poster" src="{self._poster_url(f.get("poster_path"))}" alt="{f.get("title")}" loading="lazy">'

        return f'''
<div class="crew-card" data-person-type="{person_type}" data-person-index="{index}">
    {photo_html}
    <div class="crew-info">
        <div class="crew-name">{name}</div>
        <div class="crew-meta">{person.get('count', 0)} films · ★ {person.get('avg_rating', 0)} · ❤️ {person.get('liked_count', 0)}</div>
        <div class="crew-posters">{posters_html}</div>
    </div>
</div>'''

    def _generate_people_tab(self) -> str:
        """Generate enhanced people tab with sub-tabs, photos, crew, and studios"""
        actors = self.stats.get('actors', {}).get('top_by_count', [])[:15]
        directors = self.stats.get('directors', {}).get('top_by_count', [])[:15]
        composers = self.stats.get('composers', {}).get('top_by_count', [])[:6]
        cinematographers = self.stats.get('cinematographers', {}).get('top_by_count', [])[:6]
        writers = self.stats.get('writers', {}).get('top_by_count', [])[:6]
        studios = self.stats.get('studios', {}).get('top_by_count', [])[:8]

        # Actor cards
        actors_html = ''
        for i, actor in enumerate(actors):
            actors_html += self._generate_person_card(actor, 'actor', i)

        # Director cards
        directors_html = ''
        for i, director in enumerate(directors):
            directors_html += self._generate_person_card(director, 'director', i)

        # Crew cards
        composers_html = ''
        for i, person in enumerate(composers):
            composers_html += self._generate_crew_card(person, 'composer', i)

        cinematographers_html = ''
        for i, person in enumerate(cinematographers):
            cinematographers_html += self._generate_crew_card(person, 'cinematographer', i)

        writers_html = ''
        for i, person in enumerate(writers):
            writers_html += self._generate_crew_card(person, 'writer', i)

        # Studio cards
        studios_html = ''
        for i, studio in enumerate(studios):
            logo_path = studio.get('logo_path')
            if logo_path:
                logo_html = f'<img class="studio-logo" src="{self.POSTER_BASE_URL.replace(config.POSTER_SIZE, "w185")}/{logo_path}" alt="{studio.get("name", "")}" loading="lazy">'
            else:
                initial = studio.get('name', '?')[0]
                logo_html = f'<div class="studio-logo-placeholder">{initial}</div>'
            studios_html += f'''
<div class="studio-card" data-person-type="studio" data-person-index="{i}">
    {logo_html}
    <div class="studio-info">
        <div class="studio-name">{studio.get('name', 'Unknown')}</div>
        <div class="studio-meta">
            <span><span class="stat-value">{studio.get('count', 0)}</span> films</span>
            <span>★ {studio.get('avg_rating', 0)}</span>
            <span>❤️ {studio.get('liked_count', 0)}</span>
        </div>
    </div>
</div>'''

        # Build sub-tab buttons (only show tabs that have data)
        subtabs = []
        subtabs.append(('actors', '🎭 Actors', True))
        subtabs.append(('directors', '🎬 Directors', True))
        if composers:
            subtabs.append(('composers', '🎵 Composers', False))
        if cinematographers:
            subtabs.append(('cinematographers', '📸 Cinematographers', False))
        if writers:
            subtabs.append(('writers', '✍️ Writers', False))
        if studios:
            subtabs.append(('studios', '🏢 Studios', False))

        subtab_buttons = ''
        for key, label, is_first in subtabs:
            active = ' active' if key == 'actors' else ''
            subtab_buttons += f'<button class="people-subtab{active}" data-people-tab="{key}">{label}</button>'

        return f'''
<div id="people" class="tab-content">
    <div class="people-subtabs">{subtab_buttons}</div>

    <div class="people-subcontent active" data-people-content="actors">
        <div class="section-header">
            <h2 class="section-title">🎭 Top Actors</h2>
            <span class="section-subtitle">{self.stats.get('actors', {}).get('total_unique', 0):,} unique actors — click to see films</span>
        </div>
        <div class="people-grid">{actors_html}</div>
    </div>

    <div class="people-subcontent" data-people-content="directors">
        <div class="section-header">
            <h2 class="section-title">🎬 Top Directors</h2>
            <span class="section-subtitle">{self.stats.get('directors', {}).get('total_unique', 0):,} unique directors — click to see films</span>
        </div>
        <div class="people-grid">{directors_html}</div>
    </div>

    {f"""<div class="people-subcontent" data-people-content="composers">
        <div class="section-header">
            <h2 class="section-title">🎵 Top Composers</h2>
            <span class="section-subtitle">Click to see their filmography</span>
        </div>
        <div class="crew-grid">{composers_html}</div>
    </div>""" if composers else ""}

    {f"""<div class="people-subcontent" data-people-content="cinematographers">
        <div class="section-header">
            <h2 class="section-title">📸 Top Cinematographers</h2>
            <span class="section-subtitle">Click to see their filmography</span>
        </div>
        <div class="crew-grid">{cinematographers_html}</div>
    </div>""" if cinematographers else ""}

    {f"""<div class="people-subcontent" data-people-content="writers">
        <div class="section-header">
            <h2 class="section-title">✍️ Top Writers</h2>
            <span class="section-subtitle">Click to see their filmography</span>
        </div>
        <div class="crew-grid">{writers_html}</div>
    </div>""" if writers else ""}

    {f"""<div class="people-subcontent" data-people-content="studios">
        <div class="section-header">
            <h2 class="section-title">🏢 Top Studios</h2>
            <span class="section-subtitle">Production companies behind your films — click to see their catalog</span>
        </div>
        <div class="studio-grid">{studios_html}</div>
    </div>""" if studios else ""}
</div>'''

    def _generate_insights_tab(self) -> str:
        """Generate insights tab with runtime, genres, countries, rating trends"""
        runtime = self.stats.get('runtime', {})
        basic = self.stats.get('basic', {})
        geography = self.stats.get('geography', {})

        # Runtime stats
        avg_runtime = runtime.get('average', 0)
        total_hours = runtime.get('total_hours', 0)
        shortest = runtime.get('shortest', {})
        longest = runtime.get('longest', {})

        # Calculate additional fun stats
        total_watched = basic.get('total_watched', 0)
        total_liked = basic.get('total_liked', 0)

        # Get top language
        top_languages = geography.get('top_languages', [])
        top_language = top_languages[0] if top_languages else {'language': 'N/A', 'count': 0}

        return f'''
<div id="insights" class="tab-content">
    <section class="section">
        <div class="section-header">
            <h2 class="section-title">⏱️ Viewing Time</h2>
        </div>
        <div class="insights-grid">
            <div class="insight-card accent-cyan">
                <div class="insight-label">Average Runtime</div>
                <div class="insight-value">{avg_runtime} min</div>
                <div class="insight-sub">{round(avg_runtime/60, 1) if avg_runtime else 0}h per film</div>
            </div>
            <div class="insight-card accent-purple">
                <div class="insight-label">Total Watch Time</div>
                <div class="insight-value">{total_hours:,}h</div>
                <div class="insight-sub">{round(total_hours/24, 1) if total_hours else 0} days</div>
            </div>
            <div class="insight-card accent-green">
                <div class="insight-label">Shortest Film</div>
                <div class="insight-value">{shortest.get('runtime', 0)} min</div>
                <div class="insight-sub">{shortest.get('title', 'N/A')}</div>
            </div>
            <div class="insight-card accent-orange">
                <div class="insight-label">Longest Film</div>
                <div class="insight-value">{longest.get('runtime', 0)} min</div>
                <div class="insight-sub">{longest.get('title', 'N/A')}</div>
            </div>
        </div>
    </section>

    <section class="section">
        <div class="section-header">
            <h2 class="section-title">🌍 Geography & Genres</h2>
        </div>
        <div class="charts-grid">
            <div class="chart-card">
                <h3>Top Genres</h3>
                <div class="chart-container chart-container-pie">
                    <canvas id="genresChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3>Top Countries</h3>
                <div class="chart-container">
                    <canvas id="countriesChart"></canvas>
                </div>
            </div>
        </div>
    </section>

    <section class="section">
        <div class="section-header">
            <h2 class="section-title">📈 Rating Analysis</h2>
        </div>
        <div class="charts-grid">
            <div class="chart-card">
                <h3>Your Ratings Over Time</h3>
                <div class="chart-container">
                    <canvas id="ratingEvolutionChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3>Rating Distribution</h3>
                <div class="chart-container">
                    <canvas id="ratingDistributionChart"></canvas>
                </div>
            </div>
        </div>
    </section>
</div>'''

    def _generate_journey_tab(self) -> str:
        """Generate journey tab with milestones, records, and fun facts"""
        journey = self.stats.get('journey', {})
        fun_facts = self.stats.get('fun_facts', [])
        rewatches = self.stats.get('rewatches', {})
        five_stars = self.stats.get('five_star_films', [])

        # First and recent film cards
        first_film = journey.get('first_film', {})
        recent_film = journey.get('recent_film', {})

        first_film_html = f'''
<div class="journey-film-card">
    <img src="{self._poster_url(first_film.get('poster_path'))}" alt="{first_film.get('title')}" loading="lazy">
    <div class="film-info">
        <h4>🎬 Your First Film</h4>
        <div class="title">{first_film.get('title', 'Unknown')}</div>
        <div class="date">{first_film.get('date', '')}</div>
    </div>
</div>''' if first_film else ''

        recent_film_html = f'''
<div class="journey-film-card">
    <img src="{self._poster_url(recent_film.get('poster_path'))}" alt="{recent_film.get('title')}" loading="lazy">
    <div class="film-info">
        <h4>🆕 Most Recent Film</h4>
        <div class="title">{recent_film.get('title', 'Unknown')}</div>
        <div class="date">{recent_film.get('date', '')}</div>
    </div>
</div>''' if recent_film else ''

        # Milestones
        milestones = journey.get('milestones', [])
        milestones_html = ''
        for m in milestones:
            milestones_html += f'''
<div class="milestone-card">
    <div class="milestone-label">Film #{m['number']}</div>
    <img class="milestone-poster" src="{self._poster_url(m.get('poster_path'))}" alt="{m.get('title')}" loading="lazy">
    <div class="film-title">{m.get('title', 'Unknown')}</div>
    <div class="film-date">{m.get('date', '')}</div>
</div>'''

        # Records
        max_day_count = journey.get('max_day_count', 0)
        max_month = journey.get('max_month', '')
        max_month_count = journey.get('max_month_count', 0)
        longest_streak = journey.get('longest_streak', 0)
        days_active = journey.get('days_since_first', 0)

        # Fun facts HTML
        fun_facts_html = ''
        for fact in fun_facts[:6]:  # Limit to 6 facts
            fun_facts_html += f'''
<div class="fun-fact-card">
    <div class="fact-icon">{fact.get('icon', '📊')}</div>
    <div>
        <div class="fact-text">{fact.get('text', '')}</div>
        <div class="fact-subtext">{fact.get('subtext', '')}</div>
    </div>
</div>'''

        # Most rewatched films
        most_rewatched = rewatches.get('most_rewatched', [])[:8]
        rewatches_html = ''
        for film in most_rewatched:
            rewatches_html += f'''
<div class="rewatch-card">
    <span class="rewatch-badge">×{film.get('rewatch_count', 1)}</span>
    <img src="{self._poster_url(film.get('poster_path'))}" alt="{film.get('title')}" loading="lazy">
    <div class="rewatch-title">{film.get('title', 'Unknown')}</div>
</div>'''

        # 5-star poster wall (first 30)
        wall_html = ''
        for film in five_stars[:30]:
            wall_html += f'<img class="wall-poster" src="{self._poster_url(film.get("poster_path"))}" alt="{film.get("title")}" title="{film.get("title")} ({film.get("year")})" loading="lazy">'

        return f'''
<div id="journey" class="tab-content">
    <div class="journey-hero">
        <div class="section-header">
            <h2 class="section-title">🎯 Your Film Journey</h2>
            <span class="section-subtitle">{journey.get('total_diary_entries', 0):,} diary entries over {days_active:,} days</span>
        </div>

        <div class="two-col" style="margin-top: 1.5rem;">
            {first_film_html}
            {recent_film_html}
        </div>
    </div>

    <section class="section">
        <div class="section-header">
            <h2 class="section-title">🏆 Milestones</h2>
            <span class="section-subtitle">Films that marked your journey</span>
        </div>
        <div class="milestone-grid">
            {milestones_html if milestones_html else '<p class="empty-state">Keep watching to reach milestones!</p>'}
        </div>
    </section>

    <section class="section">
        <div class="section-header">
            <h2 class="section-title">📊 Personal Records</h2>
        </div>
        <div class="record-grid">
            <div class="record-card">
                <div class="record-value">{max_day_count}</div>
                <div class="record-label">Films in One Day</div>
                <div class="record-detail">Your movie marathon record</div>
            </div>
            <div class="record-card">
                <div class="record-value">{max_month_count}</div>
                <div class="record-label">Films in One Month</div>
                <div class="record-detail">{max_month if max_month else 'N/A'}</div>
            </div>
            <div class="record-card">
                <div class="record-value">{longest_streak}</div>
                <div class="record-label">Day Streak</div>
                <div class="record-detail">Consecutive days watching</div>
            </div>
            <div class="record-card">
                <div class="record-value">{rewatches.get('total', 0)}</div>
                <div class="record-label">Total Rewatches</div>
                <div class="record-detail">{rewatches.get('unique_films', 0)} unique films</div>
            </div>
        </div>
    </section>

    <section class="section">
        <div class="section-header">
            <h2 class="section-title">✨ Fun Facts</h2>
            <span class="section-subtitle">Personalized insights about your viewing habits</span>
        </div>
        <div class="fun-facts-grid">
            {fun_facts_html if fun_facts_html else '<p class="empty-state">Not enough data for fun facts yet!</p>'}
        </div>
    </section>

    {f'''<section class="section">
        <div class="section-header">
            <h2 class="section-title">🔄 Most Rewatched</h2>
            <span class="section-subtitle">Films you keep coming back to</span>
        </div>
        <div class="rewatch-grid">
            {rewatches_html}
        </div>
    </section>''' if rewatches_html else ''}

    {f'''<section class="section">
        <div class="section-header">
            <h2 class="section-title">⭐ 5-Star Wall</h2>
            <span class="section-subtitle">{len(five_stars)} perfect films</span>
        </div>
        <div class="poster-wall">
            {wall_html}
        </div>
    </section>''' if wall_html else ''}
</div>'''

    def _generate_decades_tab(self) -> str:
        """Generate decades analysis tab"""
        decades = self.stats.get('decades', {})
        distribution = decades.get('distribution', [])
        top_per_decade = decades.get('top_per_decade', {})
        favorite_decade = decades.get('favorite_decade', 'N/A')
        favorite_avg = decades.get('favorite_decade_avg', 0)

        # Decades cards with top films
        decades_html = ''
        for decade_info in sorted(distribution, key=lambda x: x['decade_num'], reverse=True):
            decade = decade_info['decade']
            count = decade_info['count']
            decade_data = top_per_decade.get(decade, {})
            films = decade_data.get('films', [])
            avg_rating = decade_data.get('avg_rating', 0)

            films_html = ''
            for film in films[:6]:
                films_html += f'<img class="decade-poster" src="{self._poster_url(film.get("poster_path"))}" alt="{film.get("title")}" title="{film.get("title")} ({film.get("year")}) - {film.get("rating")}★" loading="lazy">'

            decades_html += f'''
<div class="decade-card">
    <div class="decade-header">
        <span class="decade-name">{decade}</span>
        <div class="decade-stats">
            <span>{count} films</span>
            <span>★ {avg_rating}</span>
        </div>
    </div>
    <div class="decade-films">
        {films_html if films_html else '<span class="empty-state">No rated films</span>'}
    </div>
</div>'''

        return f'''
<div id="decades" class="tab-content">
    <section class="section">
        <div class="section-header">
            <h2 class="section-title">📅 Decades Distribution</h2>
            <span class="section-subtitle">Your favorite decade: {favorite_decade} (★ {favorite_avg} avg)</span>
        </div>
        <div class="chart-card" style="margin-bottom: 2rem;">
            <h3>Films by Decade</h3>
            <div class="chart-container">
                <canvas id="decadesChart"></canvas>
            </div>
        </div>
    </section>

    <section class="section">
        <div class="section-header">
            <h2 class="section-title">🎬 Top Films by Decade</h2>
            <span class="section-subtitle">Your highest rated films from each era</span>
        </div>
        {decades_html}
    </section>
</div>'''

    def _generate_modal(self) -> str:
        """Generate modal structure for film lists"""
        return '''
<div class="modal-overlay" id="filmModal">
    <div class="modal">
        <div class="modal-header">
            <div>
                <h2 id="modalTitle">Person Name</h2>
                <span class="meta" id="modalMeta">X films</span>
            </div>
            <button class="modal-close" onclick="closeModal()">&#10005;</button>
        </div>
        <div class="modal-body">
            <div class="modal-films-grid" id="modalFilmsGrid"></div>
        </div>
    </div>
</div>'''

    def _generate_footer(self) -> str:
        """Generate footer"""
        return '''
<footer class="footer">
    <p>Data from <a href="https://letterboxd.com" target="_blank">Letterboxd</a> |
       Enhanced with <a href="https://www.themoviedb.org" target="_blank">TMDB</a></p>
    <p>Letterboxd Stats v5.4</p>
</footer>'''

    def _generate_scripts(self) -> str:
        """Generate JavaScript for interactivity and charts"""
        # Prepare data for JavaScript
        actors_data = json.dumps(self.stats.get('actors', {}).get('top_by_count', []))
        directors_data = json.dumps(self.stats.get('directors', {}).get('top_by_count', []))
        composers_data = json.dumps(self.stats.get('composers', {}).get('top_by_count', []))
        cinematographers_data = json.dumps(self.stats.get('cinematographers', {}).get('top_by_count', []))
        writers_data = json.dumps(self.stats.get('writers', {}).get('top_by_count', []))
        studios_data = json.dumps(self.stats.get('studios', {}).get('top_by_count', []))

        return f'''
<script>
// Data for modals
const actorsData = {actors_data};
const directorsData = {directors_data};
const composersData = {composers_data};
const cinematographersData = {cinematographers_data};
const writersData = {writers_data};
const studiosData = {studios_data};
const POSTER_BASE = "{self.POSTER_BASE_URL}";
const POSTER_PLACEHOLDER = "{self.POSTER_PLACEHOLDER}";

// Tab navigation
document.querySelectorAll('.nav-btn').forEach(btn => {{
    btn.addEventListener('click', () => {{
        // Update buttons
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
        document.getElementById(btn.dataset.tab).classList.add('active');
    }});
}});

// People sub-tab navigation
document.querySelectorAll('.people-subtab').forEach(btn => {{
    btn.addEventListener('click', () => {{
        document.querySelectorAll('.people-subtab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.querySelectorAll('.people-subcontent').forEach(c => c.classList.remove('active'));
        const target = document.querySelector(`.people-subcontent[data-people-content="${{btn.dataset.peopleTab}}"]`);
        if (target) target.classList.add('active');
    }});
}});

// Person/crew/studio card clicks (open modal)
const dataMap = {{
    actor: actorsData,
    director: directorsData,
    composer: composersData,
    cinematographer: cinematographersData,
    writer: writersData,
    studio: studiosData
}};
document.querySelectorAll('.person-card, .crew-card, .studio-card').forEach(card => {{
    card.addEventListener('click', () => {{
        const type = card.dataset.personType;
        const index = parseInt(card.dataset.personIndex);
        const data = dataMap[type] ? dataMap[type][index] : null;
        if (data) openModal(data, type);
    }});
}});

function openModal(person, type) {{
    document.getElementById('modalTitle').textContent = person.name;
    document.getElementById('modalMeta').textContent = `${{person.count}} films watched | ${{person.liked_count || 0}} liked`;

    const grid = document.getElementById('modalFilmsGrid');
    grid.innerHTML = '';

    (person.films || []).forEach(film => {{
        const posterUrl = film.poster_path ? POSTER_BASE + film.poster_path : POSTER_PLACEHOLDER;
        const ratingStars = film.rating ? '★'.repeat(Math.floor(film.rating)) + (film.rating % 1 >= 0.5 ? '½' : '') : '';
        const likedBadge = film.liked ? '<span class="film-liked">❤️</span>' : '';

        const filmEl = document.createElement('div');
        filmEl.className = 'modal-film';
        filmEl.innerHTML = `
            <div class="poster-wrapper">
                <img src="${{posterUrl}}" alt="${{film.title}}" loading="lazy">
                ${{likedBadge}}
            </div>
            <div class="film-title">${{film.title}}</div>
            <div class="film-year">${{film.year}}</div>
            ${{ratingStars ? `<div class="film-rating">${{ratingStars}}</div>` : ''}}
        `;
        grid.appendChild(filmEl);
    }});

    document.getElementById('filmModal').classList.add('active');
    document.body.style.overflow = 'hidden';
}}

function closeModal() {{
    document.getElementById('filmModal').classList.remove('active');
    document.body.style.overflow = '';
}}

// Close modal on overlay click
document.getElementById('filmModal').addEventListener('click', (e) => {{
    if (e.target.classList.contains('modal-overlay')) closeModal();
}});

// Close modal on escape
document.addEventListener('keydown', (e) => {{
    if (e.key === 'Escape') closeModal();
}});

// Chart.js configuration
Chart.defaults.color = '#a1a1aa';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.08)';
Chart.defaults.font.family = "'Inter', sans-serif";

// Initialize charts
const charts = {{
    genresWatchedLikedChart: {self.charts.get('genres_watched_vs_liked', '{}')},
    actorsWatchedLikedChart: {self.charts.get('actors_watched_vs_liked', '{}')},
    directorsWatchedLikedChart: {self.charts.get('directors_watched_vs_liked', '{}')},
    yearlyChart: {self.charts.get('yearly', '{}')},
    monthlyChart: {self.charts.get('monthly', '{}')},
    runtimeChart: {self.charts.get('runtime', '{}')},
    genresChart: {self.charts.get('genres', '{}')},
    countriesChart: {self.charts.get('countries', '{}')},
    ratingEvolutionChart: {self.charts.get('rating_evolution', '{}')},
    ratingDistributionChart: {self.charts.get('ratings', '{}')},
    decadesChart: {self.charts.get('decades_distribution', '{}')}
}};

// Create charts when tab becomes visible
function initCharts() {{
    Object.entries(charts).forEach(([id, config]) => {{
        const canvas = document.getElementById(id);
        if (canvas && !canvas.chart) {{
            canvas.chart = new Chart(canvas, config);
        }}
    }});
}}

// Initialize visible charts
initCharts();

// Reinitialize when tab changes (for proper sizing)
document.querySelectorAll('.nav-btn').forEach(btn => {{
    btn.addEventListener('click', () => {{
        setTimeout(initCharts, 100);
    }});
}});
</script>'''

    def _poster_url(self, poster_path: str) -> str:
        """Get full poster URL or placeholder"""
        if poster_path:
            return f"{self.POSTER_BASE_URL}{poster_path}"
        return self.POSTER_PLACEHOLDER

    def _is_film_liked_by_key(self, title: str, year: int) -> bool:
        """Check if a film is liked using the liked stats"""
        # This is a helper for year wrap-up sections
        # We check against the liked films data
        liked_films = self.stats.get('basic', {})
        # For simplicity, we'll check the film's liked flag if available
        # This is handled at the data level now
        return False  # Fallback - actual check is done at template level
