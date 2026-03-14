"""
FireCrawl Web Scraping Tool
Scrapes a single URL and returns its content as markdown.

Usage:
    python tools/scrape_single_site.py <url> [--formats markdown,html] [--output <file>]

Requires:
    FIRECRAWL_API_KEY in .env
"""

import argparse
import json
import os
import sys
from dotenv import load_dotenv
from firecrawl import FirecrawlApp


def scrape(url: str, formats: list[str] = None) -> dict:
    """Scrape a single URL and return its content."""
    load_dotenv()
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("ERROR: FIRECRAWL_API_KEY not found in .env", file=sys.stderr)
        sys.exit(1)

    app = FirecrawlApp(api_key=api_key)
    result = app.scrape(url, formats=formats or ["markdown"])
    return result


def main():
    parser = argparse.ArgumentParser(description="Scrape a website using FireCrawl")
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument(
        "--formats",
        default="markdown",
        help="Comma-separated output formats (default: markdown)",
    )
    parser.add_argument("--output", "-o", help="Save output to file")
    args = parser.parse_args()

    formats = [f.strip() for f in args.formats.split(",")]
    result = scrape(args.url, formats=formats)

    result_dict = {
        "markdown": result.markdown,
        "html": result.html,
        "metadata": {
            "title": result.metadata.title,
            "description": result.metadata.description,
            "url": result.metadata.url,
            "language": result.metadata.language,
            "status_code": result.metadata.status_code,
        },
    }
    output = json.dumps(result_dict, indent=2, default=str)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Output saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
