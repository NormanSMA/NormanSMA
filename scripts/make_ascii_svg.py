"""Turn a cut-out portrait (transparent or light background) into an animated ASCII SVG.

Usage: python scripts/make_ascii_svg.py source.png portrait.svg [cols] [keep_fraction | x0,y0,x1,y1]

The subject mask comes from the alpha channel when present, so bright skin is kept.
Edges are blended into the brightness so dark clothing still shows its outline.
Glyphs are grouped into four tone bands. The SVG decodes top to bottom, then a
scanline loops over it.
"""
import sys
from xml.sax.saxutils import escape

from PIL import Image, ImageFilter, ImageOps

RAMP = " .:-=+*#%@"
CELL_W = 4.0
CELL_H = 7.0
FONT = 6.6
PAD = 16
TONES = ["#0d419d", "#1f6feb", "#58a6ff", "#cae8ff"]
NOISE = "!<>-_\\/[]{}=+*^?#"


def load(path):
    image = Image.open(path).convert("RGBA")
    alpha = image.getchannel("A")
    if alpha.getextrema()[0] == 255:
        # No transparency: treat near-white as background.
        gray = image.convert("L")
        alpha = gray.point(lambda v: 0 if v > 238 else 255)
    return image.convert("RGB"), alpha


def main(source, out, cols=72, keep=1.0, box=None):
    image, alpha = load(source)
    if not box:
        left, top, right, bottom = alpha.point(lambda v: 255 if v > 24 else 0).getbbox()
        box = (left, top, right, top + round((bottom - top) * keep))
    image, alpha = image.crop(box), alpha.crop(box)
    width, height = image.size
    rows = round(cols * (height / width) * (CELL_W / CELL_H))

    gray = image.convert("L")
    gray = ImageOps.equalize(gray, mask=alpha.point(lambda v: 255 if v > 128 else 0))
    edges = gray.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
    small = gray.resize((cols, rows), Image.LANCZOS)
    small_edges = edges.resize((cols, rows), Image.LANCZOS)
    small_alpha = alpha.resize((cols, rows), Image.LANCZOS)

    grid = []
    for y in range(rows):
        row = []
        for x in range(cols):
            if small_alpha.getpixel((x, y)) < 110:
                row.append(None)
                continue
            lum = small.getpixel((x, y)) / 255
            edge = min(small_edges.getpixel((x, y)) / 140, 1.0)
            value = max(0.12 + lum ** 0.85 * 0.88, edge * 0.85)
            row.append(min(value, 1.0))
        grid.append(row)

    body = []
    for index, row in enumerate(grid):
        cells = [(i, v) for i, v in enumerate(row) if v is not None]
        if not cells:
            continue
        start, end = cells[0][0], cells[-1][0]
        y = PAD + (index + 1) * CELL_H - 2
        spans = []
        current_tone, chunk = None, ""
        for value in row[start:end + 1]:
            if value is None:
                char, tone = " ", current_tone if current_tone is not None else 0
            else:
                char = RAMP[min(int(value * (len(RAMP) - 1)) + 1, len(RAMP) - 1)]
                tone = min(int(value * len(TONES)), len(TONES) - 1)
            if tone != current_tone and chunk:
                spans.append(f'<tspan class="t{current_tone}">{escape(chunk)}</tspan>')
                chunk = ""
            current_tone = tone
            chunk += char
        if chunk:
            spans.append(f'<tspan class="t{current_tone}">{escape(chunk)}</tspan>')
        length = end - start + 1
        delay = 0.2 + index * 0.028
        noise = "".join(NOISE[(index * 7 + i * 3) % len(NOISE)] for i in range(length))
        x = PAD + start * CELL_W
        attrs = f'x="{x:.1f}" y="{y:.1f}" textLength="{length * CELL_W:.1f}" lengthAdjust="spacing"'
        body.append(f'<text {attrs} class="n" style="--d:{delay:.2f}s">{escape(noise)}</text>')
        body.append(f'<text {attrs} class="r" style="--d:{delay + 0.12:.2f}s">{"".join(spans)}</text>')

    svg_w = round(cols * CELL_W + PAD * 2)
    svg_h = round(rows * CELL_H + PAD * 2)
    decode_end = 0.2 + rows * 0.028 + 0.4
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" '
        f'height="{svg_h}" role="img" aria-label="Portrait of Norman as ASCII art">\n'
        "<style>"
        f'text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;'
        f"font-size:{FONT}px;white-space:pre}}"
        + "".join(f".t{i}{{fill:{c}}}" for i, c in enumerate(TONES))
        + ".n{fill:#79c0ff;opacity:0;animation:noise .22s steps(1) var(--d) forwards}"
        "@keyframes noise{0%{opacity:.9}50%{opacity:.5}100%{opacity:0}}"
        ".r{opacity:0;animation:on .25s ease-out var(--d) forwards}"
        "@keyframes on{to{opacity:1}}"
        f".scan{{opacity:0;animation:scan 5s linear {decode_end:.2f}s infinite}}"
        f"@keyframes scan{{0%{{opacity:1;transform:translateY(0)}}70%{{opacity:1;transform:translateY({svg_h}px)}}"
        f"70.1%,100%{{opacity:0;transform:translateY({svg_h}px)}}}}"
        ".glow{animation:breathe 4s ease-in-out infinite}"
        "@keyframes breathe{0%,100%{opacity:.35}50%{opacity:.7}}"
        "@media (prefers-reduced-motion:reduce){.r{animation:none;opacity:1}.n,.scan{display:none}.glow{animation:none}}"
        "</style>\n"
        '<defs><linearGradient id="sl" x1="0" x2="0" y1="0" y2="1">'
        '<stop offset="0" stop-color="#388bfd" stop-opacity="0"/>'
        '<stop offset=".9" stop-color="#388bfd" stop-opacity=".18"/>'
        '<stop offset="1" stop-color="#a5d6ff" stop-opacity=".55"/></linearGradient>'
        '<radialGradient id="halo" cx=".5" cy=".38" r=".55">'
        '<stop offset="0" stop-color="#1f6feb" stop-opacity=".45"/>'
        '<stop offset="1" stop-color="#1f6feb" stop-opacity="0"/></radialGradient></defs>\n'
        f'<rect width="{svg_w}" height="{svg_h}" rx="14" fill="#0d1117"/>\n'
        f'<rect width="{svg_w}" height="{svg_h}" rx="14" fill="url(#halo)" class="glow"/>\n'
        + "\n".join(body)
        + f'\n<rect x="0" y="-40" width="{svg_w}" height="40" fill="url(#sl)" class="scan"/>\n'
        f'<rect x=".5" y=".5" width="{svg_w - 1}" height="{svg_h - 1}" rx="14" fill="none" stroke="#30363d"/>\n'
        "</svg>\n"
    )
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg)
    print(f"wrote {out} ({svg_w}x{svg_h}, {rows} rows, {cols} cols)")


if __name__ == "__main__":
    cols = int(sys.argv[3]) if len(sys.argv) > 3 else 72
    extra = sys.argv[4] if len(sys.argv) > 4 else "1.0"
    if "," in extra:
        main(sys.argv[1], sys.argv[2], cols, box=tuple(int(v) for v in extra.split(",")))
    else:
        main(sys.argv[1], sys.argv[2], cols, float(extra))
