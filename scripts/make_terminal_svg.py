"""Generate terminal.svg: a Windows 98 style console window whose lines type in.

Animations use CSS only (no SMIL), which renders the same in every browser.

Usage: python scripts/make_terminal_svg.py terminal.svg
"""
import sys
from xml.sax.saxutils import escape

FONT_SIZE = 15
CHAR_W = 9.0
LINE_H = 25
LEFT = 20
TOP = 64
WIDTH = 760
PROMPT = "C:\\Users\\norman> "

# (kind, text): "cmd" lines are typed after the prompt, "out" lines are output.
LINES = [
    ("cmd", "whoami"),
    ("out", "Norman Smith Martínez Acevedo - Full Stack | Databases | Cloud"),
    ("cmd", "type status.txt"),
    ("out", "Final-year Information Systems Engineering student at UAM (Dec 2026)"),
    ("out", "Managua, Nicaragua - open to remote and junior roles"),
    ("cmd", "dir open-source"),
    ("out", "jam  libredb-studio  freeCodeCamp  meshery"),
]

STYLE = (
    "text.c{font-family:'Lucida Console','Courier New',ui-monospace,Consolas,monospace;"
    f"font-size:{FONT_SIZE}px;white-space:pre}}"
    "text.ui{font-family:Tahoma,'MS Sans Serif',Verdana,Arial,sans-serif;font-size:13px;font-weight:700}"
    ".l{opacity:0;animation:on 0s linear var(--d) forwards}"
    ".t{clip-path:inset(0 100% 0 0);"
    "animation:on 0s linear var(--d) forwards,type var(--dur) steps(var(--n),end) var(--d) forwards}"
    ".cur{opacity:0;animation:on 0s linear var(--d) forwards,blink 1.1s steps(1) calc(var(--d) + .1s) infinite}"
    "@keyframes on{to{opacity:1}}"
    "@keyframes type{to{clip-path:inset(0 0 0 0)}}"
    "@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}"
)


def bevel(x, y, w, h, raised=True):
    """Win9x 3D border drawn with four lines. Raised: light top/left, dark bottom/right."""
    light, dark = ("#ffffff", "#404040") if raised else ("#404040", "#ffffff")
    mid_light, mid_dark = ("#dfdfdf", "#808080") if raised else ("#808080", "#dfdfdf")
    return (
        f'<path d="M{x} {y + h - 1}V{y}H{x + w - 1}" fill="none" stroke="{light}"/>'
        f'<path d="M{x + w - 1} {y}V{y + h - 1}H{x}" fill="none" stroke="{dark}"/>'
        f'<path d="M{x + 1} {y + h - 2}V{y + 1}H{x + w - 2}" fill="none" stroke="{mid_light}"/>'
        f'<path d="M{x + w - 2} {y + 1}V{y + h - 2}H{x + 1}" fill="none" stroke="{mid_dark}"/>'
    )


def button(x, y, glyph):
    w, h = 18, 16
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#c0c0c0"/>'
        + bevel(x, y, w, h)
        + glyph(x, y)
    )


def g_min(x, y):
    return f'<rect x="{x + 5}" y="{y + 10}" width="7" height="2" fill="#000"/>'


def g_max(x, y):
    return (
        f'<rect x="{x + 4}" y="{y + 3}" width="9" height="9" fill="none" stroke="#000"/>'
        f'<rect x="{x + 4}" y="{y + 3}" width="9" height="2" fill="#000"/>'
    )


def g_close(x, y):
    return (
        f'<path d="M{x + 5} {y + 4}L{x + 12} {y + 11}M{x + 12} {y + 4}L{x + 5} {y + 11}" '
        'stroke="#000" stroke-width="2" fill="none"/>'
    )


def main(out):
    height = TOP + LINE_H * len(LINES) + 26
    body = []
    clock = 0.6
    prompt_w = len(PROMPT) * CHAR_W
    for index, (kind, text) in enumerate(LINES):
        y = TOP + index * LINE_H
        if kind == "cmd":
            duration = max(len(text) * 0.07, 0.4)
            body.append(
                f'<text class="c l" x="{LEFT}" y="{y}" fill="#c0c0c0" textLength="{prompt_w}" '
                f'lengthAdjust="spacing" style="--d:{clock:.2f}s">{escape(PROMPT)}</text>'
            )
            body.append(
                f'<text class="c t" x="{LEFT + prompt_w}" y="{y}" fill="#ffffff" '
                f'textLength="{len(text) * CHAR_W}" lengthAdjust="spacing" '
                f'style="--d:{clock:.2f}s;--dur:{duration:.2f}s;--n:{len(text)}">{escape(text)}</text>'
            )
            clock += duration + 0.25
        else:
            body.append(
                f'<text class="c l" x="{LEFT}" y="{y}" fill="#c0c0c0" textLength="{len(text) * CHAR_W}" '
                f'lengthAdjust="spacing" style="--d:{clock:.2f}s">{escape(text)}</text>'
            )
            clock += 0.35
    cursor_y = TOP + len(LINES) * LINE_H
    body.append(
        f'<text class="c l" x="{LEFT}" y="{cursor_y}" fill="#c0c0c0" textLength="{prompt_w}" '
        f'lengthAdjust="spacing" style="--d:{clock:.2f}s">{escape(PROMPT)}</text>'
    )
    body.append(
        f'<rect class="cur" x="{LEFT + prompt_w}" y="{cursor_y - 13}" width="9" height="16" '
        f'fill="#c0c0c0" style="--d:{clock:.2f}s"/>'
    )
    buttons = (
        button(WIDTH - 4 - 18 - 2 - 18 - 18, 7, g_min)
        + button(WIDTH - 4 - 18 - 2 - 18, 7, g_max)
        + button(WIDTH - 4 - 18, 7, g_close)
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}" role="img" aria-label="Console window: whoami">\n'
        f"<style>{STYLE}</style>\n"
        '<defs><linearGradient id="tb" x1="0" x2="1" y1="0" y2="0">'
        '<stop offset="0" stop-color="#000080"/><stop offset="1" stop-color="#1084d0"/></linearGradient></defs>\n'
        f'<rect width="{WIDTH}" height="{height}" fill="#c0c0c0"/>\n'
        + bevel(0, 0, WIDTH, height)
        + f'\n<rect x="4" y="4" width="{WIDTH - 8}" height="22" fill="url(#tb)"/>\n'
        '<rect x="8" y="8" width="14" height="14" fill="#000"/>'
        '<rect x="10" y="10" width="10" height="2" fill="#c0c0c0"/>'
        '<text class="ui" x="28" y="20" fill="#ffffff">C:\\WINDOWS\\system32\\cmd.exe - norman</text>\n'
        + buttons
        + f'\n<rect x="6" y="30" width="{WIDTH - 12}" height="{height - 36}" fill="#000000"/>\n'
        + bevel(5, 29, WIDTH - 10, height - 34, raised=False)
        + "\n"
        + "\n".join(body)
        + "\n</svg>\n"
    )
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg)
    print(f"wrote {out} ({WIDTH}x{height})")


if __name__ == "__main__":
    main(sys.argv[1])
