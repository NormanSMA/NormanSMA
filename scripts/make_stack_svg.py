"""Render the tech stack as an animated icon grid SVG.

Usage: python scripts/make_stack_svg.py data/skillicons.svg stack.svg

data/skillicons.svg is the sprite from https://skillicons.dev (MIT), fetched with:
  https://skillicons.dev/icons?i=<ids>&theme=dark&perline=<count>
Each icon is inlined so the SVG works inside a GitHub <img>.

Animation (pure CSS):
  1. The command line types itself.
  2. Icons pop in left to right.
  3. A wave travels across the icons in a loop.
"""
import re
import sys

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
NAMES = ["JavaScript", "TypeScript", "PHP", "React", "Next.js", "Astro", "Vue.js", "Tailwind", "Node.js", "Laravel",
         "PostgreSQL", "MySQL", "Supabase", "Docker", "AWS", "Vercel", "Cloudflare", "Git", "pnpm"]
COMMAND = "./stack.sh"
WIDTH = 860
PER_LINE = 10
ICON = 52
GAP = 22
LABEL_H = 18
TOP = 66
TYPE_START = 0.2
TYPE_PER_CHAR = 0.05
WAVE_PERIOD = 4.5


def icons(sprite):
    text = open(sprite, encoding="utf-8").read()
    parts = re.split(r'<g transform="translate\(\d+, 0\)">', text)[1:]
    # Each part ends with the icon's closing </g>; the last one also carries the sprite's </svg>.
    return [re.sub(r"</g>\s*(</svg>\s*)?$", "", part.strip()) for part in parts]


def main(sprite, out):
    tiles = icons(sprite)
    if len(tiles) != len(NAMES):
        sys.exit(f"sprite has {len(tiles)} icons, expected {len(NAMES)}")
    rows = (len(tiles) + PER_LINE - 1) // PER_LINE
    cell_h = ICON + LABEL_H + 14
    height = TOP + rows * cell_h + 12
    type_end = TYPE_START + len(COMMAND) * TYPE_PER_CHAR
    scale = ICON / 256
    body = []
    for index, (tile, name) in enumerate(zip(tiles, NAMES)):
        row, col = divmod(index, PER_LINE)
        in_row = min(PER_LINE, len(tiles) - row * PER_LINE)
        row_w = in_row * ICON + (in_row - 1) * GAP
        x = (WIDTH - row_w) / 2 + col * (ICON + GAP)
        y = TOP + row * cell_h
        pop = type_end + 0.15 + index * 0.06
        wave = pop + 0.8 + (col + row * 0.5) * 0.12
        body.append(
            f'<g transform="translate({x:.1f},{y})"><g class="i" style="animation-delay:{pop:.2f}s,{wave:.2f}s">'
            f"<title>{name}</title>"
            f'<g transform="scale({scale:.4f})">{tile}</g>'
            f'<text x="{ICON / 2}" y="{ICON + 15}" class="n">{name}</text></g></g>'
        )
    type_dur = len(COMMAND) * TYPE_PER_CHAR
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}" '
        f'role="img" aria-label="Tech stack: {", ".join(NAMES)}">\n<style>'
        f".p{{fill:#3fb950;font:16px {MONO}}}"
        f".h{{fill:#e6edf3;font:16px {MONO}}}"
        ".t{clip-path:inset(0 100% 0 0);"
        f"animation:type {type_dur:.2f}s steps({len(COMMAND)},end) {TYPE_START}s forwards}}"
        "@keyframes type{to{clip-path:inset(0 0 0 0)}}"
        ".cur{fill:#e6edf3;animation:blink 1s steps(1) infinite}"
        "@keyframes blink{50%{opacity:0}}"
        ".i{opacity:0;transform-box:fill-box;transform-origin:center;"
        f"animation:pop .45s cubic-bezier(.2,.8,.2,1.3) forwards,wave {WAVE_PERIOD}s ease-in-out infinite}}"
        "@keyframes pop{0%{opacity:0;transform:translateY(10px) scale(.6)}100%{opacity:1;transform:none}}"
        "@keyframes wave{0%,16%,100%{transform:none;filter:none}"
        "8%{transform:translateY(-6px);filter:brightness(1.18) drop-shadow(0 4px 6px rgba(88,166,255,.25))}}"
        f".n{{fill:#8b949e;font:12px {MONO};text-anchor:middle}}"
        "@media (prefers-reduced-motion:reduce){.i{animation:none;opacity:1}.t{animation:none;clip-path:none}}"
        "</style>\n"
        f'<rect width="{WIDTH}" height="{height}" rx="12" fill="#0d1117" stroke="#30363d"/>\n'
        f'<text x="28" y="34" class="p">norman@github ~ $</text>\n'
        f'<text x="201" y="34" class="h t">{COMMAND}</text>\n'
        f'<rect x="{201 + len(COMMAND) * 9.6 + 4}" y="22" width="8" height="15" class="cur"/>\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg)
    print(f"wrote {out} ({WIDTH}x{height}, {len(tiles)} icons)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
