# WC 2026 Tracker + Prediction Bot
 
A dictionary-heavy Python project that tracks the 2026 World Cup and runs a prediction game over Telegram. Live data comes from [Football-Data.org](https://www.football-data.org/). Standings update automatically, predictions are scored after each match, and a Telegram bot delivers reminders and digests.
 
Built solo as a learning project — no web UI, no database, no ORM. Just dicts, JSON files, and HTTP.
 
---
 
## Features
 
- **Live group standings** — points, goal difference, goals for/against, played
- **Match results** auto-pulled from the API on a 30-minute polling cycle
- **Predictions** — submit a scoreline per match before kickoff
- **Auto-scoring** — predictions are scored after the final whistle (exact / goal difference / correct result / nothing)
- **Pre-match reminders** — nudges you ~1 hour before kickoff if you haven't predicted
- **Post-match scoring messages** — tells you how your prediction did
- **Daily digest** — yesterday's results, today's fixtures, and updated standings every morning at 8am ET
---
 
## Tech stack
 
| Layer | Choice |
|---|---|
| Language | Python 3.14 |
| HTTP | `requests` |
| Storage | JSON files on disk |
| Telegram | `python-telegram-bot` |
| Scheduling | `python-telegram-bot` job queue |
| Config | `.env` via `python-dotenv` |
| Testing | `pytest` |
 
---
 
## Setup
 
### 1. Clone and create a virtual environment
 
```powershell
git clone <your-repo-url>
cd wc2026
python -m venv venv
venv\Scripts\Activate.ps1
```
 
> On macOS/Linux, activate with `source venv/bin/activate` instead.
 
### 2. Install dependencies
 
```powershell
pip install -r requirements.txt
```
 
### 3. Get a Football-Data.org API key
 
1. Register for a free account at [football-data.org/client/register](https://www.football-data.org/client/register).
2. Copy the API token from your account page.
> The free tier allows 10 requests per minute and covers the current season only. This project caches responses to disk to stay well under that limit.
 
### 4. Create your own Telegram bot
 
Each person running this needs their own bot and token — you can't share one.
 
1. Open Telegram and search for **@BotFather** (the official account has a blue checkmark).
2. Send `/newbot`.
3. Choose a display name when prompted (e.g. `My WC 2026 Bot`).
4. Choose a username — it must be unique and end in `bot` (e.g. `my_wc2026_bot`).
5. BotFather replies with an access token. Copy it and keep it secret — treat it like a password.
### 5. Create your `.env` file
 
In the project root, create a file named `.env`:
 
```
FOOTBALL_DATA_API_KEY=your_football_data_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```
 
 
### 6. Generate the tournament data
 
Pull the latest fixtures and standings from the API into `data/tournament.json`:
 
```powershell
python -m src.state
```
 
### 7. Run the bot
 
```powershell
python -m src.bot
```
 
Then open Telegram, find your bot by its username, and send `/start` to register.
 
---
 
## Bot commands
 
| Command | What it does |
|---|---|
| `/start` | Register and get the command list |
| `/standings <group_letter>` | Show a group table, e.g. `/standings A` |
| `/today` | Today's matches (America/New_York) with kickoff times |
| `/predict <match_id> <score>` | Submit a prediction, e.g. `/predict 537327 2-1` |
| `/team <country_code>` | Show a team's record, e.g. `/team MEX` |
| `/mypicks` | List your submitted predictions |
 
Match IDs are shown in the output of `/today`.
 
---
 
## How scoring works
 
When a match finishes, each prediction is scored on a tier system (highest applicable tier wins):
 
| Tier | Condition | Points |
|---|---|---|
| Exact score | You nailed the exact scoreline | 5 |
| Correct goal difference | Right margin, wrong scoreline | 3 |
| Correct result | Right winner (or draw), wrong margin | 2 |
| Nothing | Wrong result | 0 |
 
Predictions lock 5 minutes before kickoff. After that, the match no longer accepts submissions.
 
---
 
## Project structure
 
```
wc2026/
├── .env                  # Your API key and bot token (gitignored)
├── data/                 # Generated JSON (gitignored)
│   ├── tournament.json   # Fixtures, standings, match results
│   ├── predictions.json  # User predictions and points
│   └── cache/            # Cached API responses with TTL
├── src/
│   ├── api_client.py     # Football-Data.org wrapper (rate limit, cache, retry)
│   ├── state.py          # Load/save tournament, build standings
│   ├── predictions.py    # Submit, lock, score predictions
│   ├── scoring.py        # Pure scoring logic
│   ├── formatting.py     # Render dicts as Telegram-friendly strings
│   ├── scheduler.py      # Polling, scoring messages, reminders, digest
│   └── bot.py            # Telegram bot entry point
└── tests/                # pytest unit tests
```
 
---
 
## Running tests
 
```powershell
pytest
```
 
---
 
## Known limitations / roadmap
 
- `/leaderboard` and `/summary` exist in the codebase but aren't wired up yet — coming in a future version.
- Free-tier API only covers the current season, with delayed (not real-time) scores. This project polls every 30 minutes; it isn't built for live goal alerts.
- Tiebreakers stop at goals-for (`pts → GD → GF`). Head-to-head and below aren't implemented.
- Knockout bracket tracking and pre-tournament bracket picks are planned but not yet built.
---
 
## A note on data files
 
`tournament.json` and `predictions.json` live in `data/`, which is gitignored. They're generated and updated at runtime — never committed. A fresh clone has no `data/` directory; it gets created the first time you run `python -m src.state`.


## License

Personal learning project — no license. Code is here to read, not necessarily to reuse.

## Questions

Open an issue on this repo for bugs, DM me on GitHub for everything else: [@bravvoooo](https://github.com/bravvoooo)