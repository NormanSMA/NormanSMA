"""Generate wordmark.svg: figlet "bloody" letters leaned left with a larry3d-style side extrusion.

Usage: python scripts/make_wordmark_svg.py "NORMAN/SMA" wordmark.svg
Requires: pip install pyfiglet

Words are separated by "/" and stacked on separate lines, centered.
Letter rows are bright blue, drips and extrusion are darker blue.
Rows decode with a noise flash, the same entrance as the portrait.
"""
import sys
from xml.sax.saxutils import escape

import pyfiglet

FONT = "bloody"
W, H, PAD = 529, 257, 14
LEAN = 0.5  # columns shifted per row; positive leans the letters to the left
DEPTH = 1  # extrusion cells down and to the right
DRIPS = 2  # stain-only rows kept under each word
COLORS = {"f": "#79c0ff", "s": "#1f6feb", "e": "#0d419d"}
SOLID = set("█▄▀▐▌▓")
NOISE = "!<>-_\\/[]{}=+*^?#"
MONO = 'ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace'


def figlet(words):
    blocks = []
    for word in words:
        lines = pyfiglet.figlet_format(word, font=FONT, width=400).split("\n")
        while lines and not lines[-1].strip():
            lines.pop()
        blocks.append(lines)
    widest = max(len(line) for block in blocks for line in block)
    out = []
    for index, block in enumerate(blocks):
        shift = (widest - max(len(line) for line in block)) // 2
        out += [" " * shift + line.rstrip() for line in block]
        if index < len(blocks) - 1:
            out.append("")
    return out


def build(words):
    lines = figlet(words)
    rows = len(lines)
    width = int(max(len(line) for line in lines) + rows * LEAN + DEPTH * 2 + 4)
    grid = [[" "] * width for _ in range(rows + DEPTH)]
    blank = [i for i, line in enumerate(lines) if not line.strip()]
    for r, line in enumerate(lines):
        block_start = max([b + 1 for b in blank if b < r], default=0)
        shift = DEPTH + int((r - block_start) * LEAN)
        for c, ch in enumerate(line):
            if ch != " ":
                grid[r][c + shift] = ch
    # Letter rows are bright; rows with only stain glyphs are drips.
    cls = []
    for row in grid:
        letter_row = any(ch in SOLID for ch in row)
        cls.append(["" if ch == " " else ("f" if letter_row else "s") for ch in row])
    for r in range(rows - 1, -1, -1):
        for c in range(width):
            if grid[r][c] in SOLID:
                for k in range(1, DEPTH + 1):
                    rr, cc = r + k, c + k
                    if cc < width and grid[rr][cc] == " ":
                        grid[rr][cc] = "\\"
                        cls[rr][cc] = "e"
    kept_g, kept_c, run = [], [], 0
    for row, crow in zip(grid, cls):
        letter_row = any(ch in SOLID for ch in row)
        empty = all(ch == " " for ch in row)
        run = 0 if letter_row else run + (0 if empty else 1)
        if letter_row or empty or run <= DRIPS:
            kept_g.append(row)
            kept_c.append(crow)
    while kept_g and all(ch == " " for ch in kept_g[-1]):
        kept_g.pop()
        kept_c.pop()
    left = min(next((i for i, ch in enumerate(row) if ch != " "), width) for row in kept_g)
    return [row[left:] for row in kept_g], [row[left:] for row in kept_c]


def main(text, out):
    grid, cls = build(text.split("/"))
    texts = ["".join(row).rstrip() for row in grid]
    cols, rows = max(len(t) for t in texts), len(texts)
    size = min((W - PAD * 2) / (cols * 0.6), (H - PAD * 2) / rows)
    cw = size * 0.6
    x0, y0 = (W - cols * cw) / 2, (H - rows * size) / 2
    body = []
    for i, text_row in enumerate(texts):
        if not text_row.strip():
            continue
        start = len(text_row) - len(text_row.lstrip())
        seg = text_row[start:]
        spans, cur, chunk = [], None, ""
        for k in range(start, len(text_row)):
            c = cls[i][k] or cur or "f"
            if c != cur and chunk:
                spans.append(f'<tspan class="{cur}">{escape(chunk)}</tspan>')
                chunk = ""
            cur = c
            chunk += text_row[k]
        spans.append(f'<tspan class="{cur}">{escape(chunk)}</tspan>')
        y, x, d = y0 + (i + 0.8) * size, x0 + start * cw, 0.2 + i * 0.06
        attrs = f'x="{x:.1f}" y="{y:.1f}" textLength="{len(seg) * cw:.1f}" lengthAdjust="spacingAndGlyphs"'
        noise = "".join(NOISE[(i * 7 + k * 3) % len(NOISE)] if ch != " " else " " for k, ch in enumerate(seg))
        body.append(f'<text {attrs} class="wn" style="--d:{d:.2f}s">{escape(noise)}</text>')
        body.append(f'<text {attrs} class="wr" style="--d:{d + 0.14:.2f}s">{"".join(spans)}</text>')
    css = (f".wn,.wr{{font-family:{MONO};font-size:{size:.2f}px;white-space:pre}}"
           + "".join(f".{k}{{fill:{v}}}" for k, v in COLORS.items())
           + f".wn{{fill:{COLORS['f']};opacity:0;animation:wnoise .24s steps(1) var(--d) forwards}}"
           "@keyframes wnoise{0%{opacity:.8}50%{opacity:.4}100%{opacity:0}}"
           ".wr{opacity:0;animation:won .25s ease-out var(--d) forwards}@keyframes won{to{opacity:1}}"
           "@media (prefers-reduced-motion:reduce){.wr{animation:none;opacity:1}.wn{display:none}}")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
           f'aria-label="{" ".join(text.split("/"))}">\n<style>{css}</style>\n'
           f'<rect width="{W}" height="{H}" rx="14" fill="#0d1117"/>\n' + "\n".join(body) + "\n</svg>\n")
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg)
    print(f"wrote {out} ({cols}x{rows} glyphs at {size:.1f}px)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
