"""Turn a cut-out portrait (light background) into an animated ASCII SVG.

Usage: python scripts/make_ascii_svg.py source.png portrait.svg [cols] [keep_fraction | x0,y0,x1,y1]
"""
import sys
from xml.sax.saxutils import escape

from PIL import Image, ImageOps

RAMP = " .,:;-=+*#%@"
CELL_W = 5.2
CELL_H = 9.4
FONT = 8.6
PAD = 14
COLOR = "#7ee7ff"


def load(path):
    image = Image.open(path).convert("RGBA")
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    background.alpha_composite(image)
    return background.convert("RGB")


def subject_box(image):
    gray = image.convert("L")
    mask = gray.point(lambda v: 255 if v < 238 else 0)
    return mask.getbbox()


def main(source, out, cols=56, keep=1.0, box=None):
    image = load(source)
    if box:
        image = image.crop(box)
    else:
        image = image.crop(subject_box(image))
        image = image.crop((0, 0, image.width, round(image.height * keep)))
    width, height = image.size
    rows = round(cols * (height / width) * (CELL_W / CELL_H))
    small = image.resize((cols, rows), Image.LANCZOS)
    gray = ImageOps.autocontrast(small.convert("L"), cutoff=2)
    gray = ImageOps.equalize(gray)
    lines = []
    for y in range(rows):
        row = ""
        for x in range(cols):
            r, g, b = small.getpixel((x, y))
            if min(r, g, b) > 232:
                row += " "
                continue
            level = gray.getpixel((x, y))
            row += RAMP[min(int(level / 256 * (len(RAMP) - 1)) + 1, len(RAMP) - 1)]
        lines.append(row.rstrip())
    svg_w = round(cols * CELL_W + PAD * 2)
    svg_h = round(rows * CELL_H + PAD * 2)
    body = []
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        y = PAD + (index + 1) * CELL_H - 2
        body.append(
            f'<text x="{PAD}" y="{y:.1f}" textLength="{len(line) * CELL_W:.1f}" lengthAdjust="spacing" '
            f'style="--d:{0.15 + index * 0.05:.2f}s">{escape(line)}</text>'
        )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" '
        f'height="{svg_h}" role="img" aria-label="Portrait of Norman as ASCII art">\n'
        "<style>"
        f'text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;'
        f"font-size:{FONT}px;white-space:pre;fill:{COLOR};opacity:0;animation:on .4s ease-out var(--d) forwards}}"
        "@keyframes on{to{opacity:1}}"
        "</style>\n"
        f'<rect width="{svg_w}" height="{svg_h}" rx="14" fill="#0d1117"/>\n' + "\n".join(body) + "\n</svg>\n"
    )
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg)
    print(f"wrote {out} ({svg_w}x{svg_h}, {rows} rows, {cols} cols)")


if __name__ == "__main__":
    cols = int(sys.argv[3]) if len(sys.argv) > 3 else 56
    extra = sys.argv[4] if len(sys.argv) > 4 else "1.0"
    if "," in extra:
        main(sys.argv[1], sys.argv[2], cols, box=tuple(int(v) for v in extra.split(",")))
    else:
        main(sys.argv[1], sys.argv[2], cols, float(extra))
