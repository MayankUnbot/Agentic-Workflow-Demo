"""
DailyRemote Job Listing Parser
Parses scraped markdown from dailyremote.com into structured job data.

Usage:
    python tools/parse_dailyremote.py [--input-dir .tmp/dailyremote/raw] [--output .tmp/dailyremote/parsed_jobs.json]

Reads raw scraped JSON files and extracts job listings into structured format.
"""

import argparse
import json
import os
import re
import sys

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DEFAULT_INPUT = os.path.join(BASE_DIR, ".tmp", "dailyremote", "raw")
DEFAULT_OUTPUT = os.path.join(BASE_DIR, ".tmp", "dailyremote", "parsed_jobs.json")


def parse_jobs_from_markdown(markdown: str, search_term: str) -> list[dict]:
    """Extract job listings from a page's markdown content."""
    jobs = []

    # Split on job headings: ## [Title](url)
    # Match pattern: ## [Job Title](https://dailyremote.com/remote-job/...)
    pattern = r'## \[([^\]]+)\]\((https://dailyremote\.com/remote-job/[^\)]+)\)'
    matches = list(re.finditer(pattern, markdown))

    for i, match in enumerate(matches):
        title = match.group(1)
        url = match.group(2)

        # Get the text block between this match and the next one (or end)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        block = markdown[start:end]

        # Skip ad blocks (they contain image links, not job data)
        if "metana.io" in block or "bootcamp" in block.lower():
            continue
        # Skip blocks that are just promotional content
        if "Unlock Hidden Remote Jobs" in block:
            continue

        job = parse_job_block(title, url, block, search_term)
        if job:
            jobs.append(job)

    return jobs


def parse_job_block(title: str, url: str, block: str, search_term: str) -> dict:
    """Parse a single job listing block into structured data."""

    # Employment type: first non-empty line, typically "Full Time", "Part Time", "Contract"
    emp_type = ""
    emp_match = re.search(r'(Full Time|Part Time|Contract|Internship|Freelance)', block)
    if emp_match:
        emp_type = emp_match.group(1)

    # Posted time: ·3 hours ago, ·52 mins ago, ·2 days ago
    posted = ""
    posted_match = re.search(r'·\s*(.+?ago)', block)
    if posted_match:
        posted = posted_match.group(1).strip()

    # Location: text after 🌎 emoji, before 💵 or ⭐ or [
    location = ""
    # The location line looks like: Location💵 or Location⭐ or Location[
    loc_match = re.search(r'🌎\s*\n?\s*\n?\s*(.+?)(?:💵|⭐|\[)', block)
    if loc_match:
        location = loc_match.group(1).strip()

    # Salary: text after 💵, before ⭐ or [
    salary = ""
    salary_match = re.search(r'💵\s*(.+?)(?:⭐|\[)', block)
    if salary_match:
        salary = salary_match.group(1).strip()

    # Experience: text after ⭐, before [
    experience = ""
    exp_match = re.search(r'⭐\s*(.+?)(?:\[|$)', block)
    if exp_match:
        experience = exp_match.group(1).strip()

    # Category: text in [💼 Category](url) link
    category = ""
    cat_match = re.search(r'\[💼\s*([^\]]+)\]', block)
    if cat_match:
        category = cat_match.group(1).strip()

    # Subcategory/role type: second link after category, like [Backend Engineer](url)
    subcategory = ""
    subcat_match = re.findall(r'\[([^\]💼]+)\]\(https://dailyremote\.com/remote-[^\)]+\)', block)
    if subcat_match:
        # Last match is usually the role subcategory (skip "APPLY" links)
        for sc in subcat_match:
            if sc != "APPLY" and "Software Development" not in sc:
                subcategory = sc.strip()
                break

    # Description: the paragraph after the metadata line, before [APPLY]
    description = ""
    # Find text that's not part of links or emojis
    lines = block.split('\n')
    for line in lines:
        line = line.strip()
        # Skip empty lines, metadata lines, links
        if not line or line.startswith('[') or line.startswith('🌎') or line.startswith('#'):
            continue
        if '💵' in line or '⭐' in line or '💼' in line:
            continue
        if 'Full Time' in line or 'Part Time' in line or 'Contract' in line:
            continue
        if line.startswith('·'):
            continue
        if 'Unlock Hidden' in line or 'Create Alert' in line or 'notify you' in line:
            continue
        # This should be the description
        if len(line) > 30:
            description = line
            break

    # Try to extract company from title patterns like "Role at Company"
    company = ""
    # Only match explicit "at Company" pattern — avoids false positives
    cm = re.search(r'\bat\s+([A-Z][A-Za-z0-9\s&\.\-]+?)$', title)
    if cm:
        company = cm.group(1).strip()

    return {
        "title": title,
        "company": company,
        "employment_type": emp_type,
        "location": location,
        "salary": salary,
        "experience": experience,
        "category": category,
        "subcategory": subcategory,
        "description": description,
        "posted": posted,
        "url": url,
        "search_term": search_term,
    }


def main():
    parser = argparse.ArgumentParser(description="Parse DailyRemote scraped data")
    parser.add_argument("--input-dir", default=DEFAULT_INPUT, help="Directory with raw scraped JSON files")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT, help="Output path for parsed JSON")
    args = parser.parse_args()

    if not os.path.exists(args.input_dir):
        print(f"ERROR: Input directory not found: {args.input_dir}", file=sys.stderr)
        sys.exit(1)

    all_jobs = []
    seen_urls = set()
    files = sorted(f for f in os.listdir(args.input_dir) if f.endswith(".json"))

    print(f"Found {len(files)} raw files to parse")

    for filename in files:
        filepath = os.path.join(args.input_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        search_term = data.get("search_term", "unknown")
        markdown = data.get("markdown", "")
        jobs = parse_jobs_from_markdown(markdown, search_term)

        # Deduplicate by URL
        new_jobs = 0
        for job in jobs:
            if job["url"] not in seen_urls:
                seen_urls.add(job["url"])
                all_jobs.append(job)
                new_jobs += 1

        print(f"  {filename}: {len(jobs)} jobs found, {new_jobs} new (after dedup)")

    # Save output
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)

    # Stats
    with_salary = sum(1 for j in all_jobs if j["salary"])
    with_company = sum(1 for j in all_jobs if j["company"])
    print(f"\nTotal unique jobs: {len(all_jobs)}")
    print(f"With salary info: {with_salary}")
    print(f"With company name: {with_company}")
    print(f"Saved to: {args.output}")


if __name__ == "__main__":
    main()
