"""Send extracted report text to Gemini and get back structured COUNT/REACH data.
 
Only needs one env var: GEMINI_API_KEY (get a free one at https://aistudio.google.com/apikey,
or use a paid Vertex AI key for stronger privacy guarantees on real company data).
"""
 
import json
import os
import requests
 
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
 
CATEGORY DEFINITIONS — each category gets ONLY its own type of content, never cross-fill:
  R | Return on Assets -> utilization, productivity, revenue efficiency, burn rate.
      NOT customer counts, NOT profit margin, NOT AR.
  E | SI Value to Customer -> outcomes delivered TO the customer, value realized, completed
      initiatives. NOT revenue figures, NOT churn.
  A | AR & Contracts -> accounts receivable status, contract/renewal health, commercial deals.
      NOT profit, NOT revenue growth.
  C | Customer Stage & Crisis -> customer health, churn, escalations, AND any active operational
      crisis threatening the customer relationship. If source documents flag ANY item as a top
      risk or crisis, it must appear here even if another category also touches it.
  H | High Performers -> NAMED individuals, teams, or departments and what they specifically did.
      NOT headcount numbers, NOT open roles, NOT attrition.
 
SCORING RUBRIC — use this exactly, do not deviate:
  5 = Clearly exceeding target/expectation, documented evidence of strong result
  4 = Meeting target/expectation, no notable concerns
  3 = Mixed — meeting in some areas, gaps or risks in others
  2 = Below target/expectation, active concern requiring attention
  1 = Critical — significant failure, escalation, or crisis documented
If the documents don't contain enough information to justify a score, use null instead of guessing.
 
SCORE MATH MUST BE INTERNALLY CONSISTENT: after assigning the five scores, add them together
yourself. total_score must exactly equal the sum of the five individual scores. Double check this
before responding.
 
DO NOT DROP THE MOST SEVERE ISSUE: scan the source documents for anything explicitly flagged as a
risk, concern, crisis, or the single biggest problem facing the account. That issue MUST appear
somewhere on the slide (most likely Customer Stage & Crisis) even if a milder, more positive
metric would otherwise fill that box.
 
Produce ONLY a JSON object (no markdown fences, no commentary) with this exact structure:
 
{
  "review_date": "short date or period label, e.g. 'Q3 2026' or 'Oct 14, 2026'",
  "subheader": "one short line: account name + period + review type",
  "account_snapshot": "one line after 'ACCOUNT SNAPSHOT | ': account name, status, and one key figure",
  "reach": {
    "return_on_assets": {"score": 1-5 or null, "evidence": "specific fact(s), under 12 words"},
    "si_value_to_customer": {"score": 1-5 or null, "evidence": "specific fact(s), under 12 words"},
    "ar_contracts": {"score": 1-5 or null, "evidence": "specific fact(s), under 12 words"},
    "customer_stage_crisis": {"score": 1-5 or null, "evidence": "specific fact(s), under 12 words"},
    "high_performers": {"score": 1-5 or null, "evidence": "specific fact(s), under 12 words"}
  },
  "total_score": "sum of the five scores as an integer",
  "classification": "one of: High Performer / Strategic, Healthy Growth, Needs Attention, At Risk / Crisis — based on total_score bands: 21-25, 16-20, 11-15, 5-10"
}
 
Keep every evidence string SHORT, under 12 words, specific and numeric wherever possible."""
 
 
def summarize_report(raw_text, api_key=None, **kwargs):
    """Call Gemini and return a parsed dict matching the structure in SYSTEM_PROMPT.
 
    Extra **kwargs (endpoint, deployment) are accepted and ignored, so this can be
    swapped in as a drop-in replacement for the Azure version without changing app.py.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set.")
 
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key=" + key
 
    prompt_text = "Here is the extracted report/slide content:\n\n" + raw_text + "\n\nProduce the JSON now."
 
    res = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": prompt_text}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1500,
                "response_mime_type": "application/json",
            },
        },
        timeout=60,
    )
    data = res.json()
 
    try:
        text_block = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("Gemini returned no usable text: " + json.dumps(data)[:500])
 
    cleaned = text_block.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()
 
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Repair attempt: isolate just the {...} object, in case Gemini added
        # any stray text before/after it despite JSON mode being requested.
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            repaired = cleaned[start:end + 1]
            try:
                return json.loads(repaired)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    "Gemini's response wasn't valid JSON even after repair attempt "
                    "(try uploading again). Details: " + str(e)
                )
        raise RuntimeError(
            "Gemini's response wasn't valid JSON (this can happen occasionally — "
            "try uploading again)."
        )
