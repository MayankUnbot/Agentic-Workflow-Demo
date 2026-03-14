"""
DailyRemote Multi-Page Scraper
Scrapes multiple pages of job listings from dailyremote.com.

Usage:
    python tools/scrape_dailyremote.py --search backend --max-pages 10 --delay 2

Requires:
    FIRECRAWL_API_KEY in .env
"""

import argparse
import json
import os
import sys
import time

# Add tools/ to path so we can import scrape_single_site
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scrape_single_site import scrape


BASE_URL = "https://dailyremote.com/remote-software-development-jobs"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".tmp", "dailyremote", "raw")


def scrape_pages(search_term: str, max_pages: int = 10, delay: float = 2.0):
    """Scrape multiple pages from dailyremote.com."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe_search = search_term.replace(" ", "_")
    credits_used = 0

    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}?page={page}&search={search_term.replace(' ', '+')}"
        output_file = os.path.join(OUTPUT_DIR, f"{safe_search}_page_{page}.json")

        print(f"[{page}/{max_pages}] Scraping: {url}")

        try:
            result = scrape(url, formats=["markdown"])
            result_dict = {
                "markdown": result.markdown,
                "metadata": {
                    "title": result.metadata.title,
                    "url": result.metadata.url,
                    "status_code": result.metadata.status_code,
                },
                "search_term": search_term,
                "page": page,
            }

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result_dict, f, indent=2, default=str)

            credits_used += 1
            print(f"  -> Saved to {output_file}")

            # Check if page has no job listings (end of results)
            if not result.markdown or "No jobs found" in (result.markdown or ""):
                print(f"  -> No more listings found. Stopping.")
                break

        except Exception as e:
            print(f"  -> ERROR on page {page}: {e}", file=sys.stderr)
            continue

        if page < max_pages:
            print(f"  -> Waiting {delay}s...")
            time.sleep(delay)

    print(f"\nDone! Scraped {credits_used} pages for '{search_term}'. Credits used: {credits_used}")
    return credits_used


def main():
    parser = argparse.ArgumentParser(description="Scrape DailyRemote job listings")
    parser.add_argument("--search", default="backend", help="Search term (default: backend)")
    parser.add_argument("--max-pages", type=int, default=10, help="Max pages to scrape (default: 10)")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between requests in seconds (default: 2)")
    args = parser.parse_args()

    total = scrape_pages(args.search, args.max_pages, args.delay)
    print(f"Total credits used: {total}")


if __name__ == "__main__":
    main()
