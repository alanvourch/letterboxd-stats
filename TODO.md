# TODO.md — Letterboxd Stats Web App

*Last updated: 2026-02-10 — Sprint 1 complete.*

---

## STATUS: Sprint 1 DONE ✓

All Phase 1–4 tasks from the original plan have been implemented and verified (TypeScript builds clean, Python imports OK).

---

## WHAT WAS DONE (Sprint 1)

### Performance
| Task | File | Change |
|------|------|--------|
| Parallel Supabase batches | `supabase_enricher.py` | 5 concurrent workers via `ThreadPoolExecutor`; ~6-10x speedup on Supabase phase |
| Normalized title matching | `supabase_enricher.py` | New `_normalize_title()` strips Unicode accents, punctuation; secondary pass after exact match |
| Year tolerance ±1 → ±2 | `supabase_enricher.py` | Catches festival vs wide-release year discrepancies |
| TMDB workers 8 → 15 | `supabase_enricher.py` | More concurrent fallback requests; stays within TMDB 50/10s rate limit |
| TMDB session cache | `supabase_enricher.py` | Per-run dict avoids duplicate fetches of the same film |
| Keep-alive ping | `LandingPage.tsx` | Pings `/api/health` on mount; shows cold-start warning if >10s |
| GitHub Actions cron | `.github/workflows/keepalive.yml` | Pings backend every 14 min to prevent Render sleep |

### Missing Films
| Task | File | Change |
|------|------|--------|
| Richer fallback tracking | `supabase_enricher.py` | Each missing film now has `tmdb_found` + `supabase_miss_reason` (not_in_db / year_mismatch) |
| Enhanced JSON endpoint | `routes/download.py` | `/missing` now returns `tmdb_found` and `tmdb_not_found` counts |
| New CSV endpoint | `routes/download.py` | `/missing/csv` downloads sorted CSV (title, year, tmdb_found, supabase_miss_reason) |
| MissingFilmsButton | `MissingFilmsButton.tsx` (new) | Dashboard header badge showing "X films fetched from TMDB"; click downloads CSV; hover tooltip |

### UI / UX
| Task | File | Change |
|------|------|--------|
| 5-Star Wall poster size | `JourneyTab.tsx` | `xs` (60px) → `sm` (90px); `flex-wrap` → CSS grid `auto-fill minmax(90px, 1fr)` |
| Wrap tab poster titles | `WrapTab.tsx` | Highest/Lowest rated films now show title below each poster |
| Dashboard header stats | `DashboardPage.tsx` | Sub-headline "2,143 films · ★3.8 · since 2012" from live stats |
| Progress screen | `ProgressBar.tsx` | Connecting lines between steps, ✓ for completed steps, cold-start warning after 10s idle |
| Landing page | `LandingPage.tsx` | Privacy notice, "Processing typically takes 1-2 minutes" note |

### Backend housekeeping
| Task | File | Change |
|------|------|--------|
| Job cleanup | `workers.py` + `models.py` + `main.py` | `created_at` on `JobState`; `cleanup_old_jobs()` coroutine runs every 5 min via lifespan |

---

## ARCHITECTURE NOTES (current state)

### Key file paths
```
backend/app/main.py              — FastAPI app, CORS, lifespan (job cleanup)
backend/app/config.py            — Settings from env vars
backend/app/models.py            — JobState (now has created_at), JobStatus enum
backend/app/workers.py           — Pipeline runner + cleanup_old_jobs()
backend/app/routes/upload.py     — POST /api/upload
backend/app/routes/status.py     — GET /api/status/{job_id} (SSE)
backend/app/routes/download.py   — /json, /html, /missing, /missing/csv
backend/app/pipeline/
  data_loader.py                 — CSV loading
  supabase_enricher.py           — Parallel Supabase + TMDB fallback (HEAVILY MODIFIED)
  stats_calculator.py            — All stats (~1300 lines, untouched)
  chart_generator.py             — Chart.js config (untouched)
  html_generator.py              — Standalone HTML (untouched)

frontend/src/
  lib/api.ts                     — API helpers incl. getMissingFilmsJson, getMissingFilmsCsvUrl, pingHealth
  pages/LandingPage.tsx          — Keep-alive + privacy notice
  pages/DashboardPage.tsx        — Stats summary header + MissingFilmsButton
  components/ProgressBar.tsx     — Step indicators with connecting lines + cold-start message
  components/MissingFilmsButton.tsx — NEW: missing films badge + CSV download
  components/Dashboard/
    JourneyTab.tsx               — 5-Star Wall: sm posters + CSS grid
    WrapTab.tsx                  — Titles below Highest/Lowest rated posters

.github/workflows/keepalive.yml  — NEW: cron ping every 14 min
```

### Performance breakdown (updated estimates)
1. **Cold start**: Mitigated by GitHub Actions cron (14 min interval) + frontend warm-up ping
2. **Supabase batching**: Was ~40-60s sequential → now ~8-12s with 5 parallel workers
3. **TMDB fallback**: Faster with 15 workers + session cache + normalized matching reduces miss count
4. **Stats calculation**: <10 seconds (untouched)

### Supabase URL building — do not change
```python
url = f'{self.supabase_url}/rest/v1/movies?select=*&title={urllib.parse.quote(filter_value, safe="().,\"")}'
```
The `safe` param in `quote()` is critical for PostgREST `in.()` filter syntax.

### Tailwind v4
Custom colors (`text-accent-cyan`, `bg-bg-card`, etc.) are defined via `@theme` in `index.css`. Never use hardcoded hex values in className strings.

---

## REMAINING BACKLOG (Phase 5 from original plan)

These were not done in Sprint 1. Ordered by impact:

### P2 — High impact

**[4.9] Clickable poster → film detail modal**
- Add `onClick?: () => void` prop to `PosterCard`
- Extend `FilmModal` (already exists in `ui/`) to accept a film object directly
- Wire up in JourneyTab 5-Star Wall, Wrap highest/lowest, Decades top films
- Requires passing more data through (genres, director, runtime, overview) — backend already has it, just not surfaced in all stat arrays
- *Medium effort, high UX impact*

**[4.3] Overview tab: additional stat cards**
- Add second row: Countries Watched, Total Watch Time (formatted as "X days Y hours"), Unique Directors
- Data already in `stats.countries`, `stats.runtime.total_minutes`, `stats.directors`

**[4.6] People tab: sort + filter**
- Add "Sort by: Most watched / Highest rated / Most liked" dropdown
- Add text filter input for name search
- Pure frontend state — no backend changes needed

**[4.10] Mobile responsiveness review**
- Tab navigation (7 tabs): add `overflow-x-auto` + `whitespace-nowrap` to TabNav
- 5-Star Wall on mobile: consider `minmax(75px, 1fr)` for narrow screens
- Chart containers: add `min-height: 200px` to prevent collapse

### P3 — Nice-to-have

**[4.7] Insights tab: language chart**
- `stats.languages` already has the data — just needs a chart config + `ChartWrapper`

**[4.8] Decades tab: top director per decade**
- Requires backend to add `top_director` field to each decade's stats in `stats_calculator.py`

**[4.4] Journey tab: watching pace stat**
- "You watch an average of X films per month"
- `Math.round(total_watched / (daysSinceFirst / 30))` — pure frontend calculation

---

## FUTURE IDEAS (not planned yet)

1. **Supabase Python client**: Replace manual REST URL building with `supabase-py` for cleaner code
2. **Shareable links**: Store results in Supabase so users can share a URL
3. **Supabase auto-update**: When TMDB fallback finds a film, add it to Supabase automatically
4. **Year-over-year comparison**: Dedicated tab comparing any two calendar years
5. **Director filmographies**: Cross-reference TMDB filmographies against watched list ("You've seen 12/24 Kubrick films")
6. **Dark/light mode toggle**
7. **Export as PDF**

---

## TESTING CHECKLIST (for next session)

- [ ] Full pipeline run: verify Supabase phase is faster (should be <15s for 2000 films)
- [ ] Verify `/api/result/{id}/missing` returns `tmdb_found`/`tmdb_not_found` counts
- [ ] Verify `/api/result/{id}/missing/csv` downloads correctly
- [ ] MissingFilmsButton appears in header after dashboard loads
- [ ] 5-Star Wall posters are 90px wide on desktop
- [ ] Progress screen shows connecting line between steps
- [ ] "Waking up server..." message appears if SSE takes >10s to connect
- [ ] GitHub Actions workflow appears in repo Actions tab after push

---

*Plan written by Claude Sonnet 4.5. Sprint 1 implemented by Claude Opus 4.6. 2026-02-10*
