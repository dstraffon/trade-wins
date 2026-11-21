# Trade Winds

An interactive map of every NBA trade from the 1996–97 season through the February 2026 trade deadline: 1,343 trades and 3,736 player moves, drawn as a chord diagram on center court.

## What you can do

- **Scrub time.** Drag across the season bars, pick a decade, or press **Play** to step through the league one season at a time. Ribbons morph as the trade network changes.
- **Pick a team.** Click an arc (or its label) to see the team's busiest partners and every trade it made in the selected seasons.
- **Pick a ribbon.** Click the band between two teams to list every deal between them.
- **Follow a player.** Search any traded player (try Trevor Ariza, Chris Paul or James Harden) and their path is drawn across the court, stop by stop. Dashed hops mean they changed teams without a trade.
- **Blockbusters.** Twenty curated deals, from Kobe's draft-night trade to the 2025 seven-team Durant deal, each jumps to its season and lists who went where.
- **Trade calendar.** Trades by month and the busiest single days, for whatever seasons are selected.

## Files

```
index.html            the whole app (HTML, CSS and JS in one file)
data/trades.json      the trade data (~200 KB), loaded at runtime
data/build_trades.py  script that builds trades.json from the source CSVs
```

The page loads D3 v7.9.0 from cdnjs and its fonts from Google Fonts. Everything else is local.

## Deploy

It's a static site, so any static host works. Upload the folder as-is.

- **GitHub Pages (this repo):** in Settings → Pages, set the source to "Deploy from a branch", branch `main`, folder `/ (root)`. The site will be at `https://dstraffon.github.io/trade-wins/`.
- **Netlify / Vercel / Cloudflare Pages:** drag the folder into the dashboard, or point a project at the repo with no build command.
- **Inside an existing portfolio site:** copy the folder to something like `/projects/trade-winds/` and link to it.

The data is fetched with a relative URL, so `index.html` and `data/` must stay side by side. Opening `index.html` directly from disk (`file://`) won't load the data; run a local server instead:

```
cd trade-wins
python3 -m http.server 8000   # then open http://localhost:8000
```

## Embed

Drop it into any page with an iframe:

```html
<iframe src="https://dstraffon.github.io/trade-wins/"
        title="Trade Winds: 30 years of NBA trades"
        style="width:100%;height:1400px;border:0;border-radius:12px"
        loading="lazy"></iframe>
```

The layout is responsive down to phone width (the court crops to the circle and the panel stacks below it), so a full-width iframe works well. On a portfolio card, a screenshot of the court linking to the full page usually looks better than a small iframe.

To run fully offline, download `d3.min.js` (v7.9.0) next to `index.html` and change the script `src` to `d3.min.js`.

## Data

**Source:** the open [nba-trades-database](https://github.com/brucegav/nba-trades-database) project (commit `f852052`), which scraped player and draft-pick trade legs from Basketball-Reference. That repo doesn't state a license, so credit it and Basketball-Reference wherever you show this.

**How it's counted:** a ribbon's thickness is the number of trades in which two teams exchanged at least one player or draft pick. A three-team deal adds a link for each pair that swapped something. "Players moved" counts each player leg once.

**Franchises:** relocated and renamed teams are drawn under their current franchise, and trade details show the name used at the time.
- Seattle SuperSonics → Oklahoma City Thunder
- Vancouver Grizzlies → Memphis
- New Jersey Nets → Brooklyn
- Washington Bullets → Wizards
- Charlotte Hornets (1996–2002) and Charlotte Bobcats → today's Charlotte Hornets
- New Orleans Hornets (2002–13) → New Orleans Pelicans

**Known gaps:**
- Trades that moved only cash, trade exceptions, or picks that never turned into a player may be missing, or may show only part of the deal.
- Draft-pick details come from free-text notes in the source and are shown as written.
- Some legs in the source were clearly mis-scraped and were fixed by hand in `build_trades.py`: Anthony Davis's 2019 leg (Pelicans → Lakers), and Jalen Green, Dillon Brooks and Khaman Maluach going to Phoenix in the 2025 Durant trade. Other small errors may remain.
- Player names are lowercase in the source. They're title-cased with a list of exceptions (LeBron, O'Neal, Dončić…), so a few may still be cased wrong.

## Rebuilding the data

```
git clone https://github.com/brucegav/nba-trades-database
# from the repo root (adjust SRC at the top of the script if you cloned elsewhere):
python3 data/build_trades.py
```

Requires pandas. Not affiliated with the NBA.
