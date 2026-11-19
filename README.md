# Telugu-stories
# Akshara Lokam

**Akshara Lokam** is a daily serialized Telugu fiction website hosted on GitHub Pages and automated with GitHub Actions[cite: 1, 2]. It publishes continuing story chapters set across towns and cities of Andhra Pradesh and Telangana, with poetic prose, recurring motifs, and a distraction-free reader interface[cite: 1, 2].

## How It Works
- **Hosting:** Serverless static hosting via GitHub Pages from the `main` branch (`/ (root)`)[cite: 1, 2].
- **Automation:** A scheduled GitHub Actions workflow (`.github/workflows/daily_story.yml`) runs daily at **7:00 AM IST** (`30 1 * * *` UTC) and also supports manual runs (`workflow_dispatch`)[cite: 1, 2].
- **Story Generation:** `generate_chapter.py` calls the Gemini API (`GEMINI_API_KEY`), appends new chapters to `stories.json`, and updates `series_state.json`[cite: 1, 2].
- **Series & World Seeds:** Tracks up to 5 series (`max_series: 5`) using `story_config.json`, `series_state.json`, `locations.json`, and `character_names.json`.

## Repository Structure
- `index.html` — Chapter list, series info, navigation, and Sepia/Dark theme toggle[cite: 2].
- `story.html` — Chapter reader view with Previous/Next chapter navigation[cite: 2].
- `about.html`, `contact.html`, `privacy.html` — Project info, contact details, and privacy/cookie/AdSense disclosures[cite: 1, 2].
- `generate_chapter.py` — Chapter generation and series-rotation script[cite: 2].
- `.github/workflows/daily_story.yml` — Scheduled and manual GitHub Actions runner[cite: 2].
- `story_config.json`, `series_state.json`, `stories.json`, `locations.json`, `character_names.json` — Configuration, narrative memory, published chapters, and regional/character seed data[cite: 2].

## Setup & Testing
1. Add `GEMINI_API_KEY` under **Settings → Secrets and variables → Actions**[cite: 2].
2. Enable GitHub Pages under **Settings → Pages** using the `main` branch and `/ (root)` folder[cite: 2].
3. Go to **Actions → Daily Story Generator** and click **Run workflow** to generate and publish a chapter[cite: 2].
