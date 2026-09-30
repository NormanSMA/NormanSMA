"""Render an animated contribution heatmap SVG from data/contributions.json.

Usage: python scripts/render_heatmap_svg.py data/contributions.json contrib-heatmap.svg
"""
import json
import sys
from datetime import date

CELL = 13
GAP = 4
LEFT = 44
TOP = 52
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS = {1: "Mon", 3: "Wed", 5: "Fri"}


def main(source, out):
    with open(source, encoding="utf-8") as handle:
        data = json.load(handle)
    days = data["days"]
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # Sunday = 0
    weeks = (len(days) + offset + 6) // 7
    width = LEFT + weeks * (CELL + GAP) + 24
    height = TOP + 7 * (CELL + GAP) + 44
    body = []
    last_month = None
    last_label_col = -10
    for index, day in enumerate(days):
        slot = index + offset
        col, row = divmod(slot, 7)
        x = LEFT + col * (CELL + GAP)
        y = TOP + row * (CELL + GAP)
        current = date.fromisoformat(day["date"])
        if row == 0 and current.month != last_month and col < weeks - 2:
            if col - last_label_col >= 3:
                body.append(f'<text x="{x}" y="{TOP - 10}" class="m">{MONTHS[current.month - 1]}</text>')
                last_label_col = col
            last_month = current.month
        delay = (col * 0.045) + (row * 0.012)
        body.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
            f'fill="{PALETTE[day["level"]]}" class="c" style="animation-delay:{delay:.2f}s">'
            f'<title>{day["count"]} contributions on {day["date"]}</title></rect>'
        )
    for row, label in DAYS.items():
        body.append(f'<text x="8" y="{TOP + row * (CELL + GAP) + 11}" class="m">{label}</text>')
    legend_x = width - 24 - 5 * (CELL + GAP) - 60
    legend_y = TOP + 7 * (CELL + GAP) + 14
    body.append(f'<text x="{legend_x - 34}" y="{legend_y + 11}" class="m">Less</text>')
    for level, color in enumerate(PALETTE):
        body.append(
            f'<rect x="{legend_x + level * (CELL + GAP)}" y="{legend_y}" width="{CELL}" '
            f'height="{CELL}" rx="3" fill="{color}"/>'
        )
    body.append(f'<text x="{legend_x + 5 * (CELL + GAP) + 4}" y="{legend_y + 11}" class="m">More</text>')
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="Contribution graph">\n'
        "<style>"
        ".c{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .5s ease-out forwards}"
        "@keyframes pop{0%{opacity:0;transform:scale(.2)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:scale(1)}}"
        '.m{fill:#8b949e;font:11px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}'
        '.h{fill:#e6edf3;font:14px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}'
        "</style>\n"
        f'<rect width="{width}" height="{height}" rx="12" fill="#0d1117" stroke="#30363d"/>\n'
        f'<text x="{LEFT}" y="26" class="h">{data["total"]} contributions in the last year</text>\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg)
    print(f"wrote {out} ({width}x{height}, {len(days)} days)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
