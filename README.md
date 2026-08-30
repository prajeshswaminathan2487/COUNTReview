# COUNT/REACH Review Generator

Upload a QBR, WCSR, or business review deck (.pptx or .pdf). The app extracts
and scores the content using Azure OpenAI, then fills in your COUNT/REACH
template with the results — the template's design, colors, and layout are
never touched, because the fill happens through code (python-pptx), not by
asking a chat model to redraw the slide.

## Why this exists

Asking a chat assistant (like Copilot) to both extract content AND redesign a
slide to match a template reliably fails — it tends to invent a simplified
layout instead of populating the real one. This app splits the job:
- The AI's job: read the source deck, extract facts, score the five REACH
  categories according to a fixed rubric. Text only.
- The code's job: take that text and drop it into the exact right spot in the
  real .pptx template. No redesign possible, because no redesign happens.

## Setup (one time)

### 1. Set up Azure OpenAI
Azure OpenAI needs three pieces of information (unlike most APIs, which just
need one key):

1. Go to https://ai.azure.com (Azure AI Foundry) and create/open a resource.
2. Under **Deployments**, deploy a chat model (gpt-4o or similar) and give it
   a deployment name — remember this name, you'll need it.
3. Under **Keys and Endpoint**, copy your API key and endpoint URL.

### 2. Add your credentials
```
cp .env.example .env
```
Open `.env` and fill in:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT` (the deployment name you chose, not the model name)
- `APP_PASSWORD` (a password to lock the site if you deploy it publicly)

### 3. Run it locally
```
./run.sh
```
Open http://localhost:5000

### Or deploy on Render (recommended for sharing with a team)
1. Push this whole folder to a GitHub repo
2. Render dashboard → New + → Web Service → connect the repo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app --timeout 120`
5. Environment variables: same four as above (`AZURE_OPENAI_API_KEY`,
   `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `APP_PASSWORD`,
   `FLASK_SECRET_KEY`)
6. Create Web Service. Once "Live," visit the URL and log in.

## Files

| File | Purpose |
|---|---|
| `app.py` | Flask web app — upload, login gate, processing route |
| `extract.py` | Pulls text out of uploaded PPTX/PDF source decks |
| `summarizer.py` | Calls Azure OpenAI, returns structured JSON (scores + evidence) |
| `templatefill.py` | Opens the real template and replaces tokens — no redesign possible |
| `assets/count_template.pptx` | The real, editable COUNT/REACH template |
| `templates/index.html` | Upload page |
| `templates/login.html` | Password gate |

## Editing the template itself

If you want to change colors, fonts, or layout, open `assets/count_template.pptx`
directly in PowerPoint and edit it — just don't delete or retype the `{{TOKEN}}`
placeholders (e.g. `{{R_SCORE}}`, `{{R_EVIDENCE}}`), since `templatefill.py`
looks for those exact strings. Everything else about the template is yours to
restyle freely.

## Notes

- No uploaded file is stored after processing.
- The five REACH category names (Return on Assets, SI Value to Customer, etc.)
  are fixed in the template and can never be renamed by the AI — this was the
  main failure mode with chat-based generation.
