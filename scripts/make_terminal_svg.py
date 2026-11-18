"""Generate terminal.svg: a dark terminal card matching the profile README boxes.

Animations use pure CSS (no SMIL) so they render consistently inside a GitHub <img>.

Usage: python scripts/make_terminal_svg.py terminal.svg
"""
import sys
from xml.sax.saxutils import escape

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
WIDTH = 860
PAD = 28
PROMPT = "norman@github ~ $"
PROMPT_SIZE = 16
TEXT_SIZE = 15
CHAR = PROMPT_SIZE * 0.6
TYPE_START = 0.2
TYPE_PER_CHAR = 0.045

STYLE = (
    f".p{{fill:#3fb950;font:{PROMPT_SIZE}px {MONO}}}"
    f".h{{fill:#e6edf3;font:{PROMPT_SIZE}px {MONO}}}"
    f".out{{fill:#c9d1d9;font:{TEXT_SIZE}px {MONO}}}"
    ".hi{fill:#e6edf3;font-weight:700}"
    ".acc{fill:#58a6ff}"
    ".sep{fill:#6e7681}"
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

# Each block: (command, [(segments_list), ...]) where each segment is (css_class_or_None, text).
BLOCKS = [
    (
        "whoami",
        [
            [
                ("hi", "Norman Smith Martínez Acevedo"),
                (None, " "),
                ("acc", "@NormanSMA"),
                ("sep", " · "),
                (None, "Full Stack · Databases · Cloud"),
            ],
        ],
    ),
    (
        "cat status.txt",
        [
            [(None, "Final-year Information Systems Engineering student at UAM (Dec 2026)")],
            [(None, "Managua, Nicaragua "), ("sep", "·"), (None, " open to remote and junior roles")],
        ],
    ),
    (
        "ls open-source/",
        [
            [("acc", "jam  libredb-studio  freeCodeCamp  meshery")],
        ],
    ),
]


def render_segments(segments):
    """Render styled text spans inside a single <text> element."""
    parts = []
    for cls, text in segments:
        escaped = escape(text)
        parts.append(f'<tspan class="{cls}">{escaped}</tspan>' if cls else escaped)
    return "".join(parts)


def main(out):
    body = []
    clock = TYPE_START
    y = 38
    cmd_x = PAD + (len(PROMPT) + 1) * CHAR

    for command, outputs in BLOCKS:
        dur = max(len(command) * TYPE_PER_CHAR, 0.35)
        body.append(
            f'<text x="{PAD}" y="{y}" class="p in" style="--d:{clock:.2f}s">{escape(PROMPT)}</text>'
            f'<text x="{cmd_x:.1f}" y="{y}" class="h ty" '
            f'style="--d:{clock:.2f}s;--dur:{dur:.2f}s;--n:{len(command)}">{escape(command)}</text>'
        )
        clock += dur + 0.22
        y += 30

        for segments in outputs:
            body.append(
                f'<g class="rise" style="--d:{clock:.2f}s">'
                f'<text x="{PAD}" y="{y}" class="out">{render_segments(segments)}</text></g>'
            )
            clock += 0.22
            y += 26

        clock += 0.14
        y += 12

    body.append(
        f'<text x="{PAD}" y="{y}" class="p in" style="--d:{clock:.2f}s">{escape(PROMPT)}</text>'
        f'<rect x="{cmd_x:.1f}" y="{y - 13}" width="9" height="17" class="cur" style="--d:{clock:.2f}s"/>'
    )
    height = y + 26

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}" role="img" '
        'aria-label="Terminal: Norman Smith Martinez Acevedo (@NormanSMA), Full Stack, Databases and Cloud">\n'
        f"<style>{STYLE}</style>\n"
        f'<rect x=".5" y=".5" width="{WIDTH - 1}" height="{height - 1}" rx="12" fill="#0d1117" stroke="#30363d"/>\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg)
    print(f"wrote {out} ({WIDTH}x{height})")


if __name__ == "__main__":
    main(sys.argv[1])
