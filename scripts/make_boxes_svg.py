"""Render the terminal boxes of the profile README.

Usage: python scripts/make_boxes_svg.py

Every box follows the same rule as the heatmap and stack:
dark card, green prompt, typed command, blinking cursor.

Outputs:
  whoami.svg          prompt + ASCII portrait + wordmark (inlines portrait.svg and wordmark.svg)
  links/<n>.svg       one box split in three clickable segments
  now.svg             now.sh as a log with a progress bar
"""
import os
import re
from xml.sax.saxutils import escape

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
WIDTH = 860
PAD = 28
PROMPT = "norman@github ~ $"
PROMPT_SIZE = 16
TEXT_SIZE = 15
CHAR = PROMPT_SIZE * 0.6
TEXT_CHAR = TEXT_SIZE * 0.6
TYPE_START = 0.2
TYPE_PER_CHAR = 0.045

BASE_CSS = (
    f".p{{fill:#3fb950;font:{PROMPT_SIZE}px {MONO}}}"
    f".h{{fill:#e6edf3;font:{PROMPT_SIZE}px {MONO}}}"
    ".ty{clip-path:inset(0 100% 0 0);animation:type var(--dur) steps(var(--n),end) var(--d) forwards}"
    "@keyframes type{to{clip-path:inset(0 0 0 0)}}"
    ".cur{fill:#e6edf3;opacity:0;animation:show 0s linear var(--d) forwards,blink 1s steps(1) var(--d) infinite}"
    "@keyframes blink{50%{opacity:0}}"
    ".in{opacity:0;animation:show .3s ease-out var(--d) forwards}"
    "@keyframes show{to{opacity:1}}"
    ".rise{opacity:0;animation:rise .5s cubic-bezier(.2,.8,.2,1) var(--d) forwards}"
    "@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}"
    "@media (prefers-reduced-motion:reduce){.ty{animation:none;clip-path:none}.in,.rise{animation:none;opacity:1}}"
)


def prompt(y, command, start, x=PAD):
    """Return (svg, end_time, cursor_x) for one typed prompt line."""
    dur = len(command) * TYPE_PER_CHAR
    cmd_x = x + (len(PROMPT) + 1) * CHAR
    svg = (
        f'<text x="{x}" y="{y}" class="p in" style="--d:{start:.2f}s">{PROMPT}</text>'
        f'<text x="{cmd_x:.1f}" y="{y}" class="h ty" '
        f'style="--d:{start:.2f}s;--dur:{dur:.2f}s;--n:{len(command)}">{escape(command)}</text>'
    )
    return svg, start + dur, cmd_x + len(command) * CHAR + 4


def cursor(x, y, start):
    return f'<rect x="{x:.1f}" y="{y - 13}" width="9" height="17" class="cur" style="--d:{start:.2f}s"/>'


def frame(width, height, body, css="", label="", shift=0, view_w=None):
    view_w = view_w or width
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {height}" width="{view_w}" '
        f'height="{height}" role="img" aria-label="{escape(label)}">\n'
        f"<style>{BASE_CSS}{css}</style>\n"
        f'<g transform="translate({-shift},0)">\n'
        f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="#0d1117" stroke="#30363d"/>\n'
        f"{body}\n</g>\n</svg>\n"
    )


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print(f"wrote {path}")


def inner(path):
    """Split an SVG file into (viewBox w, h, style, inner markup)."""
    text = open(path, encoding="utf-8").read()
    w, h = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', text).groups()
    style = re.search(r"<style>(.*?)</style>", text, re.S).group(1)
    body = re.sub(r"^.*?</style>\s*", "", text, flags=re.S)
    body = re.sub(r"</svg>\s*$", "", body)
    return float(w), float(h), style, body


def whoami():
    line, end, cur_x = prompt(36, "whoami", TYPE_START)
    pw, ph, pstyle, pbody = inner("portrait.svg")
    ww, wh, wstyle, wbody = inner("wordmark.svg")
    target_h = 250
    p_w = pw * target_h / ph
    w_w = ww * target_h / wh
    gap = 24
    x0 = (WIDTH - p_w - w_w - gap) / 2
    y0 = 58
    height = y0 + target_h + 24
    body = (
        line
        + cursor(cur_x, 36, end)
        + f'<svg x="{x0:.1f}" y="{y0}" width="{p_w:.1f}" height="{target_h}" viewBox="0 0 {pw:g} {ph:g}">{pbody}</svg>'
        + f'<svg x="{x0 + p_w + gap:.1f}" y="{y0}" width="{w_w:.1f}" height="{target_h}" viewBox="0 0 {ww:g} {wh:g}">'
        f"{wbody}</svg>"
    )
    write("whoami.svg", frame(WIDTH, height, body, pstyle + wstyle, "whoami: ASCII portrait of Norman and NORMAN SMA"))


ICONS = {
    "portfolio": '<path d="M0 16L9 0L18 16Z" fill="#58a6ff"/>',
    "linkedin": ('<rect width="18" height="18" rx="3" fill="#58a6ff"/><g fill="#0d1117">'
                 '<circle cx="5.2" cy="4.8" r="1.6"/><rect x="3.8" y="7.2" width="2.8" height="7.2"/>'
                 '<path d="M8.2 7.2h2.6v1.1c.5-.8 1.5-1.3 2.6-1.3 2 0 3 1.2 3 3.5v3.9h-2.7v-3.6c0-1-.4-1.6-1.2-1.6s-1.4.7-1.4 1.6v3.6H8.2z"/></g>'),
    "email": ('<rect y="1.5" width="18" height="14" rx="2" fill="none" stroke="#58a6ff" stroke-width="1.8"/>'
              '<path d="M1 3L9 9.5L17 3" fill="none" stroke="#58a6ff" stroke-width="1.8"/>'),
}
LINKS = [
    ("portfolio", "open", "portafolio-nsma-dev.vercel.app"),
    ("linkedin", "connect", "in/norman-martinez"),
    ("email", "mail", "norman.martinez003@gmail.com"),
]
SEGMENTS = [0, 287, 574, WIDTH]


def links():
    height = 120
    line, end, cur_x = prompt(36, "./links.sh", TYPE_START)
    shared = [line, cursor(cur_x, 36, end)]
    for index, (name, verb, target) in enumerate(LINKS):
        x = SEGMENTS[index] + PAD
        d = end + 0.25 + index * 0.2
        shared.append(
            f'<g class="rise" style="--d:{d:.2f}s">'
            f'<g transform="translate({x},60)">{ICONS[name]}</g>'
            f'<text x="{x + 30}" y="75"><tspan class="v">$ {verb} </tspan><tspan class="k">{name}</tspan></text>'
            f'<text x="{x}" y="100" class="u">{escape(target)}</text></g>'
        )
        if index:
            shared.append(f'<line x1="{SEGMENTS[index]}" y1="60" x2="{SEGMENTS[index]}" y2="100" class="sep in" '
                          f'style="--d:{d:.2f}s"/>')
    css = (
        f".k{{fill:#58a6ff;font:700 {TEXT_SIZE}px {MONO}}}.v{{fill:#8b949e;font:{TEXT_SIZE}px {MONO}}}"
        f".u{{fill:#c9d1d9;font:13px {MONO};text-decoration:underline;text-decoration-color:#30363d}}"
        ".sep{stroke:#30363d}"
    )
    for index, (name, _, target) in enumerate(LINKS):
        left, right = SEGMENTS[index], SEGMENTS[index + 1]
        write(f"links/{name}.svg", frame(WIDTH, height, "".join(shared), css, f"{name}: {target}",
                                         shift=left, view_w=right - left))


BAR_CELLS = 16
BAR_FILLED = 15
NOW_LOG = [
    ("2026-12", "graduating", None, "Information Systems Engineering · UAM"),
    ("now", "looking for", "#3fb950", "junior or internship roles · full stack · cloud · devops"),
    ("now", "based in", None, "Managua, Nicaragua · remote or on site"),
    ("now", "contributing", None, "CNCF Meshery · LibreDB Studio · freeCodeCamp"),
    ("always", "speaking", None, "Spanish (native) · English (B2)"),
]


def now():
    line, end, _ = prompt(36, "tail -f now.log", TYPE_START)
    body = [line]
    y = 74
    t = end + 0.25
    verb_x = PAD + 11 * TEXT_CHAR
    value_x = verb_x + 14 * TEXT_CHAR
    for stamp, verb, dot, text in NOW_LOG:
        parts = [f'<text x="{PAD}" y="{y}" class="ts">[{stamp}]</text>',
                 f'<text x="{verb_x:.1f}" y="{y}" class="vb">{verb}</text>']
        x = value_x
        if stamp == "2026-12":
            bar = "█" * BAR_FILLED + "░" * (BAR_CELLS - BAR_FILLED)
            parts.append(
                f'<text x="{x:.1f}" y="{y}" class="bar ty" '
                f'style="--d:{t + 0.2:.2f}s;--dur:1.2s;--n:{BAR_CELLS}">{bar}</text>'
            )
            x += (BAR_CELLS + 2) * TEXT_CHAR
        if dot:
            parts.append(f'<circle cx="{x + 4:.1f}" cy="{y - 5}" r="4.5" fill="{dot}" class="live"/>')
            x += 18
        parts.append(f'<text x="{x:.1f}" y="{y}" class="val">{escape(text)}</text>')
        body.append(f'<g class="rise" style="--d:{t:.2f}s">{"".join(parts)}</g>')
        y += 30
        t += 0.22
    y += 8
    body.append(f'<text x="{PAD}" y="{y}" class="wait in" style="--d:{t:.2f}s">waiting for the next opportunity…</text>')
    body.append(cursor(PAD + 34 * TEXT_CHAR, y, t))
    css = (
        f".ts{{fill:#6e7681;font:{TEXT_SIZE}px {MONO}}}"
        f".vb{{fill:#58a6ff;font:{TEXT_SIZE}px {MONO}}}"
        f".val{{fill:#e6edf3;font:{TEXT_SIZE}px {MONO}}}"
        f".bar{{fill:#388bfd;font:{TEXT_SIZE}px {MONO}}}"
        f".wait{{fill:#8b949e;font:italic {TEXT_SIZE}px {MONO}}}"
        ".live{animation:pulse 1.6s ease-in-out infinite}"
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}"
    )
    label = "now: " + "; ".join(f"{verb} {text}" for _, verb, _, text in NOW_LOG)
    write("now.svg", frame(WIDTH, y + 26, "".join(body), css, label))


if __name__ == "__main__":
    whoami()
    links()
    now()
