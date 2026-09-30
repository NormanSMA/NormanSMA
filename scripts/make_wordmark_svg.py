"""Generate wordmark.svg: a 3D extruded pixel wordmark that wipes in left to right.

Usage: python scripts/make_wordmark_svg.py NORMAN wordmark.svg
"""
import sys

FONT = {
    "N": ["X...X", "XX..X", "X.X.X", "X..XX", "X...X"],
    "O": [".XXX.", "X...X", "X...X", "X...X", ".XXX."],
    "R": ["XXXX.", "X...X", "XXXX.", "X..X.", "X...X"],
    "M": ["X...X", "XX.XX", "X.X.X", "X...X", "X...X"],
    "A": [".XXX.", "X...X", "XXXXX", "X...X", "X...X"],
    "S": [".XXXX", "X....", ".XXX.", "....X", "XXXX."],
}

PITCH = 16
SIZE = 14
PAD_X = 28
PAD_Y = 18
DEPTH = 7
FRONT = "#22d3ee"
SIDE_FROM = (14, 116, 144)
SIDE_TO = (8, 47, 73)


def shade(step, total):
    t = step / max(total - 1, 1)
    return "#%02x%02x%02x" % tuple(
        round(a + (b - a) * t) for a, b in zip(SIDE_FROM, SIDE_TO)
    )


def pixels(word):
    cells = []
    for index, char in enumerate(word):
        glyph = FONT[char]
        for row, line in enumerate(glyph):
            for col, flag in enumerate(line):
                if flag == "X":
                    cells.append(((index * 6 + col) * PITCH, row * PITCH))
    return cells


def main(word, out):
    cells = pixels(word)
    width = (len(word) * 6 - 1) * PITCH + PAD_X * 2 + DEPTH * 2
    height = 5 * PITCH + PAD_Y * 2 + DEPTH * 2
    parts = []
    for layer in range(DEPTH, 0, -1):
        color = shade(DEPTH - layer, DEPTH)
        offset = layer * 1.6
        rects = "".join(
            f'<rect x="{x + PAD_X + offset:.1f}" y="{y + PAD_Y + offset:.1f}" '
            f'width="{SIZE}" height="{SIZE}" rx="2"/>'
            for x, y in cells
        )
        parts.append(f'<g fill="{color}">{rects}</g>')
    front = "".join(
        f'<rect x="{x + PAD_X}" y="{y + PAD_Y}" width="{SIZE}" height="{SIZE}" rx="2"/>'
        for x, y in cells
    )
    parts.append(f'<g fill="{FRONT}">{front}</g>')
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{word}">\n'
        "<style>.w{clip-path:inset(0 100% 0 0);animation:wipe 1.8s cubic-bezier(.4,0,.2,1) .2s forwards}"
        "@keyframes wipe{to{clip-path:inset(0 0 0 0)}}</style>\n"
        f'<rect width="{width}" height="{height}" rx="14" fill="#0d1117"/>\n'
        f'<g class="w">\n' + "\n".join(parts) + "\n</g>\n</svg>\n"
    )
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg)
    print(f"wrote {out} ({width}x{height}, {len(cells)} pixels)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
