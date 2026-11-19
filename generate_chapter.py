import json
import os
import random
import urllib.error
from datetime import datetime, timezone
from urllib import request

API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY or DEEPSEEK_API_KEY in environment.")

with open("story_config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
with open("series_state.json", "r", encoding="utf-8") as f:
    state = json.load(f)
with open("stories.json", "r", encoding="utf-8") as f:
    stories = json.load(f)
with open("locations.json", "r", encoding="utf-8") as f:
    locations = json.load(f)["states"]
with open("character_names.json", "r", encoding="utf-8") as f:
    names_db = json.load(f)

max_series = config.get("max_series", 5)
chapters_per_series = config.get("chapters_per_series", 15)
current_series_num = state.get("active_series_number", 1)

if current_series_num > max_series:
    print(f"Reached maximum limit of {max_series} series. Stopping generation.")
    raise SystemExit(0)

chapter_num = state.get("next_chapter", 1)

system_prompt = """
You are a literary serial fiction writer for Akshara Lokam.
Write in rich, rhythmic poetic Telugu prose with natural colloquial regional dialogue—never stiff textbook translations.
Ground scenes in authentic cultural and regional sensory texture specific to the given State and City/Town.
End the chapter with a compelling cliffhanger.
Return ONLY valid UTF-8 JSON matching this exact schema:
{
  "title": "string",
  "excerpt": "string (1-2 sentences)",
  "html_paragraphs": ["<p>...</p>", "<p>...</p>"],
  "next_chapter_summary": "string (concise memory summary for the next chapter)",
  "next_series_title": "string (only needed if starting a new series)"
}
"""

user_prompt = f"""
Series Number: {current_series_num} of {max_series}
Series Title: {state["series_title"]}
Setting: {state["city"]}, {state["state"]}
Characters: {json.dumps(state["characters"], ensure_ascii=False)}
Motifs: {json.dumps(config["motifs"], ensure_ascii=False)}
Chapter Number: {chapter_num} of {chapters_per_series}
Previous Plot Memory: {state["plot_memory"]}

Generate Chapter {chapter_num} now.
"""

payload = {
    "systemInstruction": {"parts": [{"text": system_prompt}]},
    "contents": [{"parts": [{"text": user_prompt}]}],
    "generationConfig": {"responseMimeType": "application/json"}
}

models_to_try = []
if os.environ.get("GEMINI_MODEL"):
    models_to_try.append(os.environ["GEMINI_MODEL"].strip())
models_to_try.extend(["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"])
models_to_try = list(dict.fromkeys(models_to_try))

raw_resp = None
last_error = None

for model_name in models_to_try:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with request.urlopen(req, timeout=60) as resp:
            raw_resp = json.loads(resp.read().decode("utf-8"))
        print(f"Generated chapter using model: {model_name}")
        break
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"Model {model_name} failed with HTTP {e.code}: {err_body}")
        last_error = e
        if e.code != 404:
            raise

if raw_resp is None:
    raise last_error or RuntimeError("All Gemini models returned 404 Not Found.")

chapter_data = json.loads(raw_resp["candidates"][0]["content"]["parts"][0]["text"])

new_entry = {
    "chapter": chapter_num,
    "title": chapter_data["title"],
    "excerpt": chapter_data["excerpt"],
    "html_paragraphs": chapter_data["html_paragraphs"],
    "published_at": datetime.now(timezone.utc).isoformat()
}

stories.setdefault("series", [])
target_series = next(
    (s for s in stories["series"] if s["series_number"] == current_series_num),
    None
)
if target_series is None:
    target_series = {
        "series_number": current_series_num,
        "series_title": state["series_title"],
        "state": state["state"],
        "city": state["city"],
        "chapters": []
    }
    stories["series"].append(target_series)

target_series["chapters"].append(new_entry)

# Check if current series finished and rotate to next series (up to max 5)[cite: 3]
if chapter_num >= chapters_per_series:
    state.setdefault("completed_series", []).append(state["series_title"])
    next_series_num = current_series_num + 1
    state["active_series_number"] = next_series_num

    if next_series_num <= max_series:
        next_state = random.choice(list(locations.keys()))
        next_city = random.choice(locations[next_state])
        male_pick = random.choice(names_db["male"])
        female_pick = random.choice(names_db["female"])

        state["total_series_created"] = next_series_num
        state["series_title"] = chapter_data.get("next_series_title") or f"{next_city} కథలు (Series {next_series_num})"
        state["state"] = next_state
        state["city"] = next_city
        state["characters"] = [
            {"name_en": male_pick["en"], "name_te": male_pick["te"], "gender": "Male", "role": "Lead male protagonist"},
            {"name_en": female_pick["en"], "name_te": female_pick["te"], "gender": "Female", "role": "Lead female protagonist"}
        ]
        state["next_chapter"] = 1
        state["plot_memory"] = f"Series {next_series_num} begins in {next_city}, {next_state} with {male_pick['te']} and {female_pick['te']}."
        stories["series"].append({
            "series_number": next_series_num,
            "series_title": state["series_title"],
            "state": next_state,
            "city": next_city,
            "chapters": []
        })
else:
    state["next_chapter"] = chapter_num + 1
    state["plot_memory"] = chapter_data["next_chapter_summary"]

with open("stories.json", "w", encoding="utf-8") as f:
    json.dump(stories, f, ensure_ascii=False, indent=2)
with open("series_state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
