# COUNT/REACH Review Generator

Upload a QBR, WCSR, or business review deck (.pptx or .pdf). The app extracts
and scores the content using Gemini, then fills in your COUNT/REACH template
with the results — the template's design is never touched, because the fill
happens through code (python-pptx replacing text tokens), not by asking a
chat model to redraw the slide.

## What changed in this version

- Added a worked example (few-shot) inside the AI prompt, based on the
  original reference slide, so the model has a concrete quality bar for
  brevity and specificity instead of guessing at tone.
- Tightened timeouts: Gemini call times out at 45s, gunicorn worker timeout
  raised to 180s, so a slow response gets a clean error instead of a crash.
- If it's still slow: Render's **free tier cold-starts** after ~15 min of
  inactivity, which can add 30-60+ seconds to the first request after a gap.
  That's a hosting-tier limitation, not a bug — upgrading to Render's Starter
  plan ($7/mo) removes cold starts entirely.

## Setup (one time)

1. Get a Gemini key: https://aistudio.google.com/apikey
2. `cp .env.example .env` and fill in `GEMINI_API_KEY` and `APP_PASSWORD`
3. Run locally: `./run.sh` → http://localhost:5000
4. Or deploy on Render:
   - Runtime: **Python 3** (not Docker — check this explicitly when creating the service)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --timeout 180`
   - Env vars: `GEMINI_API_KEY`, `APP_PASSWORD`, `FLASK_SECRET_KEY`

## Files

| File | Purpose |
|---|---|
| `app.py` | Flask app — upload, login gate, processing route |
| `extract.py` | Pulls text out of uploaded PPTX/PDF source decks |
| `summarizer.py` | Calls Gemini, returns structured JSON (scores + evidence) |
| `templatefill.py` | Opens the real template and replaces tokens — no redesign possible |
| `assets/count_template.pptx` | The real, editable COUNT/REACH template |
| `templates/index.html` | Upload page |
| `templates/login.html` | Password gate |

## Notes

- No uploaded file is stored after processing.
- The five REACH category names are hardcoded into the template shapes and
  can never be renamed by the AI.
- If uploads consistently take over a minute even when the service is
  "warm" (recently used), check Render's Logs tab during an upload — that
  will show whether the delay is the Gemini call itself or something else.
