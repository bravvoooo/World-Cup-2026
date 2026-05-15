# wc2026

A Python CLI + Telegram bot for tracking the 2026 FIFA World Cup and playing a personal prediction game. Built solo as a learning project focused on dict-native patterns, JSON persistence, and API integration.

## Status

**Phase 1 complete** — group standings and today's matches via CLI, fed by real data from football-data.org with on-disk JSON caching.

Next up: Phase 2 (prediction submission and scoring logic), then Phase 3 (Telegram bot), then Phase 4 (scheduled polling + notifications).

## Setup

Requires Python 3.11+.

```powershell
# Clone
git clone https://github.com/bravvoooo/wc2026.git
cd wc2026

# Create + activate virtual environment (Windows / PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# On macOS/Linux instead:
# python3 -m venv venv
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
FOOTBALL_DATA_API_KEY=your_key_here
```

Get a free API key at [football-data.org/client/register](https://www.football-data.org/client/register). Free tier is 10 requests/minute, which is plenty — the on-disk cache keeps real usage well under that.

Before running for the first time, generate `data/tournament.json`:

```powershell
python src/state.py
```

That calls `regenerate_tournament()`, which hits the API once, parses matches, builds group standings, and writes the tournament dict to disk. After this, the CLI reads from the local JSON and only re-hits the API when the cache expires. Re-run any time you want to refresh state from the API.

## Usage

**Show a group's standings:**

```
python src/main.py standings A
```

Output:
```
Group A
GER Played: 3 W: 2 D: 1 L: 0 GF: 8 GA: 2 GD: +6 PTS: 7
SUI Played: 3 W: 1 D: 2 L: 0 GF: 5 GA: 3 GD: +2 PTS: 5
HUN Played: 3 W: 1 D: 0 L: 2 GF: 2 GA: 5 GD: -3 PTS: 3
SCO Played: 3 W: 0 D: 1 L: 2 GF: 2 GA: 7 GD: -5 PTS: 1
```

Sorted by points → goal difference → goals for, per FIFA group-stage tiebreakers (stops at GF; full H2H tiebreakers deferred to v2).

**Show today's matches:**

```
python src/main.py today
```

Output:
```
Today's matches (America/New_York):
428786  ROU vs NED  12:00 PM  FT 0 : 3  Stage: LAST_16  Matchday: 4
428785  AUT vs TUR  03:00 PM  FT 1 : 2  Stage: LAST_16  Matchday: 4
```

Times converted from UTC to Eastern via `zoneinfo` (DST-aware). Sorted by kickoff.

## Project structure

```
wc2026/
├── .env                     # API key (gitignored)
├── data/
│   ├── tournament.json      # Generated state (gitignored)
│   └── cache/               # Per-endpoint API response cache with TTL
├── src/
│   ├── api_client.py        # football-data.org wrapper + JSON file cache
│   ├── state.py             # Parse matches, build standings, query tournament
│   └── main.py              # CLI entry point
└── requirements.txt
```

Phase 2+ will add `predictions.py`, `scoring.py`, `formatting.py`, `telegram_bot.py`, and `scheduler.py`.

## Goals

Primary: get fluent with nested dicts, JSON persistence, and API integration in a domain I actually care about.

Secondary: build something I'll actually use during the 2026 World Cup, and develop reusable patterns (API clients, cache layers, scheduled jobs) for future projects.

Design constraints:
- **Dict-native.** Everything is a dict that round-trips to JSON. No ORMs, no SQL, no opaque database formats. `cat data/tournament.json` should be readable.
- **No frameworks.** Standard library + `requests` + `python-telegram-bot` + `python-dotenv`. That's it.
- **Solo-first.** Multi-user / friends-mode is optional Phase 5 polish, not a v1 requirement.

## License

Personal learning project — no license. Code is here to read, not necessarily to reuse.

## Questions

Open an issue on this repo for bugs, DM me on GitHub for everything else: [@bravvoooo](https://github.com/bravvoooo)