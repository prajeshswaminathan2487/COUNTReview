"""Send extracted report text to Azure OpenAI and get back structured COUNT/REACH data.

Azure OpenAI needs three things (all set as env vars, see .env.example):
  AZURE_OPENAI_API_KEY      - your key
  AZURE_OPENAI_ENDPOINT     - e.g. https://your-resource-name.openai.azure.com
  AZURE_OPENAI_DEPLOYMENT   - the deployment name you created in Azure AI Foundry
                              (NOT the base model name - Azure uses your own
                              deployment name, which you choose when you deploy
                              a model like gpt-4o in the Azure AI Foundry portal)
"""

import json
import os
import requests

API_VERSION = "2024-08-01-preview"

SYSTEM_PROMPT = """You are a COUNT/REACH Review Analyst. Your job is EXTRACTION, not summarization.

Read every uploaded file completely. Extract specific, named details — customer names, dollar
figures, dates, percentages, contract terms. Do not write generic statements that could apply to
any account.

RULES
- Every bullet must contain at least one specific fact from the source documents (a name, number,
  date, or direct reference). If you cannot find a specific fact for a section, write
  "Not Available" — never write a vague placeholder bullet just to fill space.
- Never invent, estimate, or infer a number that isn't stated in the documents.
- When multiple reporting periods are provided, use the most recent as primary and call out
  specific changes from the prior period.
- Match the terminology used in the source documents rather than paraphrasing into generic
  business language.
- The five REACH category names are FIXED: Return on Assets, SI Value to Customer, AR & Contracts,
  Customer Stage & Crisis, High Performers. Never rename or reinterpret these labels.

SCORING RUBRIC — use this exactly, do not deviate:
  5 = Clearly exceeding target/expectation, documented evidence of strong result
  4 = Meeting target/expectation, no notable concerns
  3 = Mixed — meeting in some areas, gaps or risks in others
  2 = Below target/expectation, active concern requiring attention
  1 = Critical — significant failure, escalation, or crisis documented
If the documents don't contain enough information to justify a score, use null instead of guessing.

Produce ONLY a JSON object (no markdown fences, no commentary) with this exact structure:

{
  "review_date": "short date or period label, e.g. 'Q3 2026' or 'Oct 14, 2026'",
  "subheader": "one short line: account name + period + review type, e.g. 'Meridian Outfitters Q3 2026 Business Review'",
  "account_snapshot": "one line after 'ACCOUNT SNAPSHOT | ': account name, status, and one key figure, e.g. 'Meridian Outfitters | Healthy Growth | Revenue $4.82M'",
  "reach": {
    "return_on_assets": {"score": 1-5 or null, "evidence": "specific fact(s), under 12 words"},
    "si_value_to_customer": {"score": 1-5 or null, "evidence": "specific fact(s), under 12 words"},
    "ar_contracts": {"score": 1-5 or null, "evidence": "specific fact(s), under 12 words"},
    "customer_stage_crisis": {"score": 1-5 or null, "evidence": "specific fact(s), under 12 words"},
    "high_performers": {"score": 1-5 or null, "evidence": "specific fact(s), under 12 words"}
  },
  "total_score": "sum of the five scores as an integer, or best estimate if some are null",
  "classification": "one of: High Performer / Strategic, Healthy Growth, Needs Attention, At Risk / Crisis — based on total_score bands: 21-25, 16-20, 11-15, 5-10"
}

Keep every evidence string SHORT — it must fit in a small card on a one-page slide, so aim for
under 12 words, specific and numeric wherever possible."""


def summarize_report(raw_text, api_key=None, endpoint=None, deployment=None):
    """Call Azure OpenAI and return a parsed dict matching the structure in SYSTEM_PROMPT."""
    key = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
    deployment = deployment or os.environ.get("AZURE_OPENAI_DEPLOYMENT")

    if not key or not endpoint or not deployment:
        raise RuntimeError(
            "Azure OpenAI is not fully configured. Need AZURE_OPENAI_API_KEY, "
            "AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT."
        )

    url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/chat/completions?api-version={API_VERSION}"

    res = requests.post(
        url,
        headers={"Content-Type": "application/json", "api-key": key},
        json={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Here is the extracted report/slide content:\n\n" + raw_text +
                 "\n\nProduce the JSON now."},
            ],
            "temperature": 0.3,
            "max_tokens": 1200,
            "response_format": {"type": "json_object"},
        },
        timeout=60,
    )
    data = res.json()

    try:
        text_block = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError("Azure OpenAI returned no usable text: " + json.dumps(data)[:500])

    cleaned = text_block.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            "Azure OpenAI's response wasn't valid JSON (rare, try again). Details: " + str(e)
        )
