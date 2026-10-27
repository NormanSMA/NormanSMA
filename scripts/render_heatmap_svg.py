"""Render an animated contribution heatmap SVG from data/contributions.json.

Usage: python scripts/render_heatmap_svg.py data/contributions.json contrib-heatmap.svg

Animation (pure CSS, works inside a GitHub <img>):
  1. The command line types itself.
  2. Cells rise in as a diagonal wave.
  3. A scanner sweeps the grid in a loop and lights each column as it passes.
  4. The best day pulses.
"""
import json
import sys
from datetime import date

CELL = 13
GAP = 4
STEP = CELL + GAP
LEFT = 44
TOP = 70
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS = {1: "Mon", 3: "Wed", 5: "Fri"}
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

COMMAND = "./contributions.sh --last-year"
TYPE_START = 0.2
TYPE_PER_CHAR = 0.035
WAVE_START = TYPE_START + len(COMMAND) * TYPE_PER_CHAR + 0.2
WAVE_COL = 0.028
WAVE_ROW = 0.035
SCAN_PERIOD = 7.0


def streaks(days):
    longest = run = 0
    for day in days:
        run = run + 1 if day["count"] > 0 else 0
        longest = max(longest, run)
    current = 0
    tail = days[:-1] if days and days[-1]["count"] == 0 else days
    for day in reversed(tail):
        if day["count"] == 0:
            break
        current += 1
    return longest, current


def plural(value, word):
    return f"{value} {word}" if value == 1 else f"{value} {word}s"


def main(source, out):
    with open(source, encoding="utf-8") as handle:
        data = json.load(handle)
    days = data["days"]
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # Sunday = 0
    weeks = (len(days) + offset + 6) // 7
    width = LEFT + weeks * STEP + 24
    grid_bottom = TOP + 7 * STEP
    height = grid_bottom + 64
    wave_end = WAVE_START + weeks * WAVE_COL + 7 * WAVE_ROW + 0.5
    scan_start = wave_end + 0.3
    best = max(days, key=lambda d: d["count"])
    longest, current = streaks(days)

    body = []
    last_month = None
    last_label_col = -10
    for index, day in enumerate(days):
        col, row = divmod(index + offset, 7)
        x = LEFT + col * STEP
        y = TOP + row * STEP
        current_date = date.fromisoformat(day["date"])
        if row == 0 and current_date.month != last_month and col < weeks - 2:
            if col - last_label_col >= 3:
                body.append(f'<text x="{x}" y="{TOP - 10}" class="m">{MONTHS[current_date.month - 1]}</text>')
                last_label_col = col
            last_month = current_date.month
        wave = WAVE_START + col * WAVE_COL + row * WAVE_ROW
        scan = scan_start + col / weeks * SCAN_PERIOD * 0.8
        body.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[day["level"]]}" '
            f'class="c" style="animation-delay:{wave:.2f}s,{scan:.2f}s">'
            f'<title>{day["count"]} contributions on {day["date"]}</title></rect>'
        )
        if day is best and best["count"] > 0:
            body.append(
                f'<rect x="{x - 2}" y="{y - 2}" width="{CELL + 4}" height="{CELL + 4}" rx="4" class="best" '
                f'style="animation-delay:{wave + 0.4:.2f}s"/>'
            )

    for row, label in DAYS.items():
        body.append(f'<text x="8" y="{TOP + row * STEP + 11}" class="m">{label}</text>')

    # Scanner band that sweeps the grid in sync with the per-cell flash.
    band_w = STEP * 3
    body.append(
        f'<rect x="{LEFT - band_w}" y="{TOP - 4}" width="{band_w}" height="{7 * STEP + 4}" '
        f'fill="url(#band)" class="band" style="animation-delay:{scan_start:.2f}s"/>'
    )

    legend_y = grid_bottom + 12
    legend_x = width - 24 - 5 * STEP - 34
    body.append(f'<text x="{legend_x - 34}" y="{legend_y + 11}" class="m">Less</text>')
    for level, color in enumerate(PALETTE):
        body.append(f'<rect x="{legend_x + level * STEP}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="3" fill="{color}"/>')
    body.append(f'<text x="{legend_x + 5 * STEP + 4}" y="{legend_y + 11}" class="m">More</text>')

    stats = [
        (f'{data["total"]}', "contributions"),
        (plural(longest, "day"), "longest streak"),
        (plural(current, "day"), "current streak"),
        (f'{best["count"]}', f'best day · {best["date"]}'),
    ]
    stat_y = grid_bottom + 46
    stat_x = LEFT
    for index, (value, label) in enumerate(stats):
        delay = wave_end + index * 0.15
        body.append(
            f'<text x="{stat_x}" y="{stat_y}" class="s" style="animation-delay:{delay:.2f}s">'
            f'<tspan class="v">{value}</tspan> {label}</text>'
        )
        stat_x += (len(value) + len(label) + 1) * 8.4 + 30

    type_dur = len(COMMAND) * TYPE_PER_CHAR
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" '
        f'aria-label="Contribution graph: {data["total"]} contributions in the last year">\n'
        "<style>"
        ".c{opacity:0;transform-box:fill-box;transform-origin:center;"
        f"animation:rise .45s cubic-bezier(.2,.8,.2,1.2) forwards,scan {SCAN_PERIOD}s linear infinite}}"
        "@keyframes rise{0%{opacity:0;transform:translateY(6px) scale(.3)}100%{opacity:1;transform:none}}"
        "@keyframes scan{0%,100%{filter:none}3%{filter:brightness(1.9) drop-shadow(0 0 3px #39d353)}9%{filter:none}}"
        ".band{opacity:0;animation:sweep "
        f"{SCAN_PERIOD}s linear infinite}}"
        f"@keyframes sweep{{0%{{opacity:.9;transform:translateX(0)}}80%{{opacity:.9;transform:translateX({weeks * STEP + band_w}px)}}"
        f"80.1%,100%{{opacity:0;transform:translateX({weeks * STEP + band_w}px)}}}}"
        ".best{fill:none;stroke:#7ee787;stroke-width:1.5;opacity:0;transform-box:fill-box;transform-origin:center;"
        "animation:ring 2.4s ease-in-out infinite}"
        "@keyframes ring{0%{opacity:0;transform:scale(.8)}30%{opacity:1;transform:scale(1)}100%{opacity:0;transform:scale(1.9)}}"
        f".m{{fill:#8b949e;font:12px {MONO}}}"
        f".p{{fill:#3fb950;font:16px {MONO}}}"
        f".h{{fill:#e6edf3;font:16px {MONO}}}"
        ".t{clip-path:inset(0 100% 0 0);"
        f"animation:type {type_dur:.2f}s steps({len(COMMAND)},end) {TYPE_START}s forwards}}"
        "@keyframes type{to{clip-path:inset(0 0 0 0)}}"
        ".cur{fill:#e6edf3;animation:blink 1s steps(1) infinite}"
        "@keyframes blink{50%{opacity:0}}"
        f".s{{fill:#8b949e;font:14px {MONO};opacity:0;animation:fade .5s ease-out forwards}}"
        ".v{fill:#e6edf3;font-weight:700}"
        "@keyframes fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}"
        "@media (prefers-reduced-motion:reduce){.c,.s{animation:none;opacity:1}.t{animation:none;clip-path:none}"
        ".band,.best,.cur{animation:none;opacity:0}}"
        "</style>\n"
        '<defs><linearGradient id="band" x1="0" x2="1" y1="0" y2="0">'
        '<stop offset="0" stop-color="#39d353" stop-opacity="0"/>'
        '<stop offset=".85" stop-color="#39d353" stop-opacity=".16"/>'
        '<stop offset="1" stop-color="#7ee787" stop-opacity=".5"/></linearGradient></defs>\n'
        f'<rect width="{width}" height="{height}" rx="12" fill="#0d1117" stroke="#30363d"/>\n'
        f'<text x="{LEFT}" y="32" class="p">norman@github ~ $</text>\n'
        f'<text x="{LEFT + 173}" y="32" class="h t">{COMMAND}</text>\n'
        f'<rect x="{LEFT + 173 + len(COMMAND) * 9.6 + 4}" y="20" width="8" height="15" class="cur"/>\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg)
    print(f"wrote {out} ({width}x{height}, {len(days)} days, longest {longest}, current {current})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
