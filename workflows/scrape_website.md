# Scrape Website

## Objective
Extract content from a web page and return it as structured data (markdown by default).

## Required Inputs
- **URL**: The web page to scrape
- **Formats** (optional): Output formats — `markdown` (default), `html`, or both

## Tool
`tools/scrape_single_site.py`

## Usage

```bash
# Basic scrape (returns markdown)
python tools/scrape_single_site.py <url>

# Specify formats
python tools/scrape_single_site.py <url> --formats markdown,html

# Save to file
python tools/scrape_single_site.py <url> --output .tmp/scraped.json
```

## Output
JSON with:
- `markdown`: Page content as markdown
- `html`: Page content as HTML (if requested)
- `metadata`: Title, description, URL, language, status code

## Edge Cases
- **Rate limits**: FireCrawl API has rate limits. If hit, wait and retry.
- **Missing API key**: Script exits with error if `FIRECRAWL_API_KEY` not in `.env`.
- **Dynamic pages**: FireCrawl handles JS-rendered pages by default.

## Credits
Each scrape uses 1 FireCrawl API credit.
