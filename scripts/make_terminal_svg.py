"""Generate terminal.svg: a terminal card whose lines type in one after another.

Animations use CSS only (no SMIL), which renders the same in every browser.

Usage: python scripts/make_terminal_svg.py terminal.svg
"""
import sys
from xml.sax.saxutils import escape

FONT_SIZE = 15
CHAR_W = 9.0
LINE_H = 26
LEFT = 28
TOP = 64
WIDTH = 760
PROMPT = "norman@github ~ $ "

# (kind, text): "cmd" lines are typed after the prompt, "out" lines are output.
LINES = [
    ("cmd", "whoami"),
    ("out", "Norman Smith Martínez Acevedo - Full Stack | Databases | Cloud"),
    ("cmd", "cat status.txt"),
    ("out", "Final-year Information Systems Engineering student at UAM (Dec 2026)"),
    ("out", "Managua, Nicaragua - open to remote and junior roles"),
    ("cmd", "ls open-source/"),
    ("out", "jam  libredb-studio  freeCodeCamp  meshery"),
]

STYLE = (
    'text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;'
    f"font-size:{FONT_SIZE}px;white-space:pre}}"
    ".l{opacity:0;animation:on 0s linear var(--d) forwards}"
    ".t{clip-path:inset(0 100% 0 0);"
    "animation:on 0s linear var(--d) forwards,type var(--dur) steps(var(--n),end) var(--d) forwards}"
    ".cur{opacity:0;animation:on 0s linear var(--d) forwards,blink 1.1s steps(1) calc(var(--d) + .1s) infinite}"
    "@keyframes on{to{opacity:1}}"
    "@keyframes type{to{clip-path:inset(0 0 0 0)}}"
    "@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}"
)


def main(out):
    height = TOP + LINE_H * len(LINES) + 28
    body = []
    clock = 0.6
    prompt_w = len(PROMPT) * CHAR_W
    for index, (kind, text) in enumerate(LINES):
        y = TOP + index * LINE_H
        if kind == "cmd":
            duration = max(len(text) * 0.07, 0.4)
            body.append(
                f'<text class="l" x="{LEFT}" y="{y}" fill="#7ee787" textLength="{prompt_w}" lengthAdjust="spacing" style="--d:{clock:.2f}s">{escape(PROMPT)}</text>'
            )
            body.append(
                f'<text class="t" x="{LEFT + prompt_w}" y="{y}" fill="#e6edf3" textLength="{len(text) * CHAR_W}" lengthAdjust="spacing" '
                f'style="--d:{clock:.2f}s;--dur:{duration:.2f}s;--n:{len(text)}">{escape(text)}</text>'
            )
            clock += duration + 0.25
        else:
            body.append(
                f'<text class="l" x="{LEFT}" y="{y}" fill="#8b949e" textLength="{len(text) * CHAR_W}" lengthAdjust="spacing" style="--d:{clock:.2f}s">{escape(text)}</text>'
            )
            clock += 0.35
    cursor_y = TOP + len(LINES) * LINE_H
    body.append(
        f'<text class="l" x="{LEFT}" y="{cursor_y}" fill="#7ee787" textLength="{prompt_w}" lengthAdjust="spacing" style="--d:{clock:.2f}s">{escape(PROMPT)}</text>'
    )
    body.append(
        f'<rect class="cur" x="{LEFT + prompt_w}" y="{cursor_y - 13}" width="9" height="17" '
        f'fill="#e6edf3" style="--d:{clock:.2f}s"/>'
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}" role="img" aria-label="Terminal: whoami">\n'
        f"<style>{STYLE}</style>\n"
        f'<rect width="{WIDTH}" height="{height}" rx="12" fill="#0d1117" stroke="#30363d"/>\n'
        f'<path d="M0 12a12 12 0 0 1 12-12h{WIDTH - 24}a12 12 0 0 1 12 12v24H0z" fill="#161b22"/>\n'
        f'<circle cx="26" cy="18" r="6" fill="#ff5f56"/><circle cx="48" cy="18" r="6" fill="#ffbd2e"/>'
        f'<circle cx="70" cy="18" r="6" fill="#27c93f"/>\n'
        f'<text x="{WIDTH / 2}" y="23" text-anchor="middle" fill="#8b949e" style="font-size:13px">'
        f"norman -- zsh -- 80x24</text>\n" + "\n".join(body) + "\n</svg>\n"
    )
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg)
    print(f"wrote {out} ({WIDTH}x{height})")


if __name__ == "__main__":
    main(sys.argv[1])
