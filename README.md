# COUNT/REACH Review Generator (Gemini version)

Upload a QBR, WCSR, or business review deck (.pptx or .pdf). The app extracts
and scores the content using Gemini, then fills in your COUNT/REACH template
with the results — the template's design, colors, and layout are never
touched, because the fill happens through code (python-pptx), not by asking a
chat model to redraw the slide.

## Why this exists

Asking a chat assistant (like Copilot) to both extract content AND redesign a
slide to match a template reliably fails — it tends to invent a simplified
layout, rename fixed category labels, or mismatch content to the wrong section.
This app splits the job:
- The AI's job: read the source deck, extract facts, score the five REACH
  categories according to a fixed rubric. Text only, structured JSON.
- The code's job: take that JSON and drop it into the exact right spot in the
  real .pptx template. No redesign possible, because no redesign happens —
  and the five REACH titles are hardcoded into the template shapes, so they
  can never be renamed.

## Setup (one time)

### 1. Get a Gemini key
Go to https://aistudio.google.com/apikey → sign in → **Create API key**. Free,
no card needed.

**Privacy note:** a free AI Studio key is used by Google to improve their
products by default — fine for testing with sample/fake data, not for real
company reports. For real data, use a paid Vertex AI key instead (same code
works — just generate the key from a billing-enabled Google Cloud project
instead of AI Studio). Paid tiers do not train on your data.

### 2. Add your key
```
cp .env.example .env
```
Open `.env` and fill in `GEMINI_API_KEY` and `APP_PASSWORD`.

### 3. Run it locally
```
./run.sh
```
Open http://localhost:5000

### Or deploy on Render
1. Push this whole folder to a GitHub repo
2. Render dashboard → New + → Web Service → connect the repo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app --timeout 120`
5. Environment variables: `GEMINI_API_KEY`, `APP_PASSWORD`, `FLASK_SECRET_KEY`
6. Create Web Service. Once "Live," visit the URL and log in.

## Files

| File | Purpose |
|---|---|
| `app.py` | Flask web app — upload, login gate, processing route |
| `extract.py` | Pulls text out of uploaded PPTX/PDF source decks |
| `summarizer.py` | Calls Gemini, returns structured JSON (scores + evidence) |
| `templatefill.py` | Opens the real template and replaces tokens — no redesign possible |
| `assets/count_template.pptx` | The real, editable COUNT/REACH template |
| `templates/index.html` | Upload page |
| `templates/login.html` | Password gate |

## Switching to Anthropic or Azure OpenAI later

Only `summarizer.py` needs to change — it just needs to accept `raw_text` and
return the same JSON structure. `app.py`, `extract.py`, and `templatefill.py`
don't need to know or care which API is behind `summarize_report()`.

## Editing the template itself

Open `assets/count_template.pptx` directly in PowerPoint to restyle colors,
fonts, or layout — just don't delete or retype the `{{TOKEN}}` placeholders
(e.g. `{{R_SCORE}}`, `{{R_EVIDENCE}}`), since `templatefill.py` looks for
those exact strings.

## Notes

- No uploaded file is stored after processing.
- The five REACH category names are fixed in the template and can never be
  renamed by the AI — this was the main failure mode with chat-based
  generation.
