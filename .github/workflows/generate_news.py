import os
import json
import requests
import feedparser

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

RSS_FEEDS = [
    "https://www.thehindu.com/news/national/feeder/default.rss",
    "https://indianexpress.com/section/explained/feed/",
    "https://pib.gov.in/RssMain.aspx?ModId=6&LangId=1"
]

def get_feed_headlines():
    articles = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                articles.append(f"Title: {entry.title}\nSummary: {getattr(entry, 'summary', '')}\n")
        except Exception as e:
            print(f"Error fetching feed {url}: {e}")
    return "\n---\n".join(articles[:25])

def fetch_upsc_json():
    headlines_text = get_feed_headlines()
    prompt = f"""
You are an expert UPSC Civil Services examination mentor and evaluator.
Analyze these raw headlines from today's Hindu, Indian Express Explained, and PIB feeds:

{headlines_text}

Select the 5 MOST CRITICAL news items strictly relevant to UPSC CSE (GS-1, GS-2, GS-3, GS-4).
Filter out sensational politics, state-specific crime, and petty administrative transfers.

For each item, output valid JSON adhering strictly to this schema:
[
  {{
    "id": 1,
    "title": "Clear headline with constitutional/legal concept",
    "paper": "GS-1" | "GS-2" | "GS-3" | "GS-4",
    "keywords": ["5-6 single-word or short statutory/case keywords for automated diffing"],
    "newsContext": "2-line summary of what happened.",
    "prelimsTraps": [
      "Trap 1: Constitutional vs Statutory distinction",
      "Trap 2: Ministry, reporting body, or IUCN status",
      "Trap 3: Precise numbers, limits, or exceptions"
    ],
    "staticAnchors": [
      "Constitutional Articles or Statutory Sections involved",
      "Key Landmark Supreme Court Judgments or Law Commission/Administrative Commissions",
      "Baseline facts, constitutional provisions, or international conventions"
    ],
    "mainsSnippet": {{
      "intro": "A 1-line crisp definition/context sentence.",
      "keywords": ["Three", "High-Impact", "Phrases"],
      "wayForward": "A balanced, reformative closing sentence."
    }}
  }}
]

Return ONLY raw JSON. Do NOT wrap in markdown backticks. Do not include introductory text.
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2}
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json()
    raw_text = response_json['candidates'][0]['content']['parts'][0]['text'].strip()
    
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
        if raw_text.endswith("```"):
            raw_text = raw_text.rsplit("\n", 1)[0]
    
    data = json.loads(raw_text)
    
    os.makedirs("data", exist_ok=True)
    with open("data/today.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Successfully generated data/today.json")

if __name__ == "__main__":
    fetch_upsc_json()
  
