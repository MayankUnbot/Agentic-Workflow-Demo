# Agentic Workflow Demo

A practical implementation of the **WAT Framework** (Workflows, Agents, Tools) — an architecture that separates AI reasoning from deterministic execution to build reliable agentic automation pipelines.

## How It Works

```
workflows/   →   Agent (Claude)   →   tools/
(instructions)    (orchestration)      (execution)
```

- **Workflows**: Markdown SOPs that define what to do, which tools to use, and how to handle edge cases
- **Agent**: Reads workflows, makes decisions, calls tools in the right order, recovers from errors
- **Tools**: Python scripts that do the actual work — API calls, data parsing, file operations

## Current Pipeline: Remote Job Scraper

Scrapes remote Backend and Full-stack software development jobs from [DailyRemote](https://dailyremote.com) and exports them to a formatted Excel spreadsheet.

### Quick Start

```bash
# 1. Set up your API key
cp .env.example .env
# Add your FIRECRAWL_API_KEY to .env

# 2. Install dependencies
pip install firecrawl-py openpyxl python-dotenv

# 3. Scrape jobs
python tools/scrape_dailyremote.py --search backend --max-pages 10
python tools/scrape_dailyremote.py --search "full stack" --max-pages 10

# 4. Parse into structured data
python tools/parse_dailyremote.py

# 5. Export to Excel
python tools/export_to_excel.py
# Output: .tmp/dailyremote/dailyremote_jobs.xlsx
```

### Output

The Excel file includes these columns:

| Column | Description |
|--------|-------------|
| Job Title | Role name |
| Company | Extracted from title when available |
| Employment Type | Full Time / Part Time / Contract |
| Location | Country/region |
| Salary | Pay range (when listed) |
| Experience | Years required |
| Category | Role subcategory |
| Description | Summary excerpt |
| Posted | When it was listed |
| Job URL | Direct link to apply |
| Search Term | Which query found the job |

## Project Structure

```
tools/              # Python scripts for deterministic execution
  scrape_single_site.py    # FireCrawl-based single URL scraper
  scrape_dailyremote.py    # Multi-page DailyRemote scraper
  parse_dailyremote.py     # Markdown-to-JSON parser
  export_to_excel.py       # JSON-to-Excel exporter
workflows/          # Markdown SOPs
  scrape_website.md        # Generic web scraping workflow
  scrape_dailyremote_jobs.md  # DailyRemote job pipeline workflow
.tmp/               # Temporary/intermediate files (gitignored)
.env                # API keys (gitignored)
CLAUDE.md           # Agent instructions
```

## Requirements

- Python 3.10+
- [FireCrawl API key](https://firecrawl.dev)
- Dependencies: `firecrawl-py`, `openpyxl`, `python-dotenv`
