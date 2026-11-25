# CLAUDE.md — torrent-bot

## Overview

Discord bot that searches torrent indexers via Prowlarr and posts results with magnet links. Uses Claude Haiku to parse natural language queries into structured search parameters.

**Repo**: `yiangwow/torrent-bot` (public GitHub)
**Deploy path**: `/home/tt/is-infra/repos/torrent-bot`
**Docker network**: `self-hosted` (alongside Prowlarr, homepage, dozzle, etc.)

---

## Architecture

```
Discord /search command
  → commands/search.js       (orchestrates the full flow)
  → services/parser.js       (Claude Haiku: natural language → JSON params)
  → services/prowlarr.js     (Prowlarr API: search + filter + sort)
  → utils/embed.js           (format Discord embed + chunked magnet links)
  → Discord reply
```

---

## Project Structure

```
torrent-bot/
├── CLAUDE.md
├── README.md
├── ARCHITECTURE.md
├── Dockerfile               # Alpine Node 20, runs npm ci --omit=dev
├── package.json             # discord.js ^14, @anthropic-ai/sdk ^0.39, express, sharp
├── .env.example             # Template for required env vars
├── .gitignore               # Ignores node_modules/, .env
├── archive/
│   └── discord_bot_prototype.py  # first Python prototype, not run
├── scripts/                 # one-off Prowlarr setup, need PROWLARR_API_KEY in the environment
│   ├── add-indexers.py      # adds every public torrent indexer
│   └── add-cf-indexers.py   # adds the Cloudflare-blocked ones (via FlareSolverr)
└── src/
    ├── index.js             # Discord client setup, command registration, starts the dashboard
    ├── dashboard.js         # express stats page + GET /api/stats, port 8083 (hardcoded)
    ├── stats.js             # usage counters, kept in a file
    ├── commands/
    │   ├── search.js        # /search slash command handler + error handling
    │   ├── ascii.js         # /ascii: image (URL or upload) to ASCII art
    │   └── ping.js          # /ping: bot status and debug info
    ├── services/
    │   ├── parser.js        # Claude Haiku query parser → {title, quality, language, type, ...}
    │   ├── prowlarr.js      # Prowlarr API client, category mapping, seeder filtering
    │   └── ascii.js         # image → ASCII (sharp)
    └── utils/
        └── embed.js         # EmbedBuilder, magnet chunking, size formatting
```

---

## Key Implementation Details

### parser.js
- Model: `claude-haiku-4-5-20251001`, max_tokens: 256
- Extracts: title, quality (normalises 4k→2160p), language, subtitles, type, season, episode
- Falls back to `{ title: query }` on any error

### prowlarr.js
- Endpoint: `GET /api/v1/search?query=...&categories[]=...`
- Auth: `X-Api-Key` header
- Category mapping: movie→2000, tv→5000, game/software→4000, music→3000
- Filters: seeders > 0, has magnetUrl or downloadUrl
- Sorts by seeders desc, returns top 10

### embed.js
- Discord 2000 char limit handled by `splitMessage()`
- Magnet links sent as plain text follow-up messages
- `formatSize(bytes)` → human readable (B/KB/MB/GB/TB)

### index.js
- If DISCORD_CHANNEL_ID set: guild-specific command registration (instant)
- Otherwise: global registration (up to 1h propagation)

---

## Environment Variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| DISCORD_BOT_TOKEN | Yes | — | Discord bot auth |
| DISCORD_CHANNEL_ID | No | — | Restrict to channel (guild-scope registration) |
| PROWLARR_URL | Yes | http://prowlarr:9696 | Prowlarr instance |
| PROWLARR_API_KEY | Yes | — | Prowlarr API key |
| ANTHROPIC_API_KEY | Yes | — | Claude Haiku for parsing |

---

## Running Locally

```bash
npm install
cp .env.example .env   # fill in values
npm run dev            # --watch auto-reload
```

## Production (Docker via is-infra)

Managed by `/home/tt/is-infra/projects/self-hosted/docker-compose.yml`.

```bash
cd /home/tt/is-infra/projects/self-hosted
docker compose up -d --build torrent-bot
docker logs torrent-bot -f
```

---

## Bot Usage

```
/search terminator 2 4k
/search breaking bad s03e05 1080p english subtitles
/search ubuntu 24.04 iso
```

---

## Git Rules

- **Author**: the owner's git identity
- Feature branches + PRs only, never push directly to main
- Conventional commits preferred
