# Tech Stack

## Runtime
- Python 3.10+
- `anthropic >= 0.39.0` — Claude API client
- `python-dotenv >= 1.0.0` — `.env` file loading

## AI Model
- Default: `claude-haiku-4-5-20251001`
- `MAX_TOKENS = 4096`
- API key via `ANTHROPIC_API_KEY` env var or `.env` file

## Web Demo (separate app)
- React 18 + Vite 5 (located in `web-demo/`)
- Node.js / npm for build tooling

## Common Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
pip install -r requirements.txt

# Run
python orchestrator.py --list              # list projects
python orchestrator.py --project 1         # build project 1
python orchestrator.py --project 1,2,3     # build multiple
python orchestrator.py --all               # build all 5
python orchestrator.py --all --demo        # demo mode (no API key)
python orchestrator.py --status            # view previous build results

# Web demo
cd web-demo
npm install
npm run dev
npm run build
```

## Claude API Usage Pattern

All agents use `utils/claude_api.py` → `call_claude()` which handles:
- Automatic retries (3 attempts) with exponential backoff on rate limits
- Optional `expect_json=True` to auto-parse and strip markdown fences
- Singleton client via `get_client()`

Agents can also call `client.messages.create()` directly using the shared `context["client"]`.
