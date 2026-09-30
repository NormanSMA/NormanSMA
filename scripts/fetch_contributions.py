"""Scrape the public contribution calendar of a GitHub user. No token needed.

Usage: python scripts/fetch_contributions.py NormanSMA data/contributions.json
"""
import json
import re
import sys
import urllib.request

CELL = re.compile(
    r'<td[^>]*data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="(contribution-day-component-\d+-\d+)"'
    r'[^>]*data-level="(\d)"'
)
TIP = re.compile(r'<tool-tip[^>]*for="(contribution-day-component-\d+-\d+)"[^>]*>([^<]*)</tool-tip>')


def fetch(login):
    request = urllib.request.Request(
        f"https://github.com/users/{login}/contributions",
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-updater)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def parse(html):
    tips = {cell: text.strip() for cell, text in TIP.findall(html)}
    days = []
    for date, cell, level in CELL.findall(html):
        match = re.match(r"(\d+)\s+contribution", tips.get(cell, ""))
        days.append({"date": date, "level": int(level), "count": int(match.group(1)) if match else 0})
    days.sort(key=lambda day: day["date"])
    return days


def main(login, out):
    days = parse(fetch(login))
    if len(days) < 300:
        raise SystemExit(f"unexpected calendar size: {len(days)} days")
    total = sum(day["count"] for day in days)
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump({"login": login, "total": total, "days": days}, handle, indent=1)
    print(f"{login}: {len(days)} days, {total} contributions")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
