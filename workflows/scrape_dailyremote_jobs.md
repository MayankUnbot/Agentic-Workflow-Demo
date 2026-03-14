# Scrape DailyRemote Jobs

## Objective
Scrape remote software development job listings from dailyremote.com and export to an Excel spreadsheet.

## Required Inputs
- **Search terms**: e.g., "backend", "full stack", "python", "node.js"
- **Max pages per search** (optional): Default 10. Each page has ~20-23 listings.
- **Delay between requests** (optional): Default 2 seconds.

## Tools
1. `tools/scrape_dailyremote.py` — Multi-page scraper
2. `tools/parse_dailyremote.py` — Markdown-to-JSON parser
3. `tools/export_to_excel.py` — JSON-to-Excel exporter

## Step-by-Step

### 1. Scrape
```bash
python tools/scrape_dailyremote.py --search backend --max-pages 10 --delay 2
python tools/scrape_dailyremote.py --search "full stack" --max-pages 10 --delay 2
```
Raw markdown saved to `.tmp/dailyremote/raw/`.

### 2. Parse
```bash
python tools/parse_dailyremote.py
```
Deduplicates across searches. Outputs `.tmp/dailyremote/parsed_jobs.json`.

### 3. Export
```bash
python tools/export_to_excel.py
```
Creates `.tmp/dailyremote/dailyremote_jobs.xlsx` with formatted headers, auto-filter, and frozen header row.

## Output Columns
| Column | Description |
|--------|-------------|
| Job Title | Role name |
| Company | Extracted from title when available (e.g., "Role at Company") |
| Employment Type | Full Time / Part Time / Contract |
| Location | Country/region |
| Salary | Pay range (blank if not listed) |
| Experience | Years required |
| Category | Role subcategory (e.g., Backend Engineer, Full Stack Developer) |
| Description | Summary excerpt |
| Posted | Relative time (e.g., "3 hours ago") |
| Job URL | Direct link to the listing |
| Search Term | Which search query found the job |

## Credit Cost
- ~20-23 jobs per page
- 1 FireCrawl credit per page
- 10 pages × 2 searches = 20 credits for ~450 jobs

## Edge Cases & Notes
- **Company names**: Most listings don't show company name on the listing page. Only "Role at Company" patterns are extracted.
- **Salary**: ~30% of listings include salary info.
- **Duplicates**: Jobs appearing in multiple searches are deduplicated by URL.
- **Ads/promotions**: Bootcamp ads and promotional blocks are filtered out during parsing.
- **Rate limits**: 2-second delay between requests prevents rate limiting. Increase if you hit 429 errors.
- **Pagination**: If a page returns no job listings, the scraper stops early.
