# Letterboxd Stats Dashboard

A web app that turns your [Letterboxd](https://letterboxd.com) data export into a beautiful, interactive statistics dashboard.

Upload your Letterboxd ZIP file and get instant insights about your film watching habits — genres, actors, directors, decades, ratings, and more.

**Live at**: [letterboxd-stats-two.vercel.app](https://letterboxd-stats-two.vercel.app)

## How It Works

1. Go to [Letterboxd Settings > Import & Export](https://letterboxd.com/settings/data/)
2. Click **Export Your Data** and download the ZIP
3. Upload it on the website
4. Get your personalized dashboard in under 2 minutes

## Dashboard Tabs

- **Overview** — Key stats, genres watched vs liked, activity charts, runtime distribution
- **Journey** — First film, milestones (100th, 500th, 1000th...), personal records, 5-star wall
- **Year Wrap** — Previous year summary with top/bottom rated films, top actor & director
- **Year Live** — Current year stats, updated on each upload
- **Decades** — Films by era, top-rated per decade
- **People/Studios** — Top actors, directors, composers, cinematographers, writers, and studios
- **Insights** — Viewing time, genre distribution, countries, rating trends

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React, TypeScript, Vite, Tailwind CSS v4, Chart.js |
| Backend | Python, FastAPI |
| Metadata | Supabase (primary), TMDB API (fallback) |
| Hosting | Vercel (frontend), Render (backend) |

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- A [TMDB API key](https://www.themoviedb.org/settings/api)

### Backend
```bash
cd backend
cp .env.example .env  # Add your TMDB_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
cp .env.example .env  # Set VITE_API_URL=http://localhost:8000
npm install
npm run dev
```

## Credits

- Film data from [Letterboxd](https://letterboxd.com)
- Metadata from [The Movie Database (TMDB)](https://www.themoviedb.org)
- This product uses the TMDB API but is not endorsed or certified by TMDB

## License

MIT
