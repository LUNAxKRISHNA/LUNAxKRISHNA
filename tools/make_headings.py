"""Builds assets/heading-<name>-<theme>.svg: the README section headings in Alro caps, drawn as paths."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = Path(__file__).parent
OUT = HERE.parent / 'assets'
FONT = Path.home() / 'AppData/Local/Microsoft/Windows/Fonts/alro-alro-regular-400.otf'

HEADINGS = {'now': 'RIGHT NOW', 'work': 'SELECTED WORK', 'toolkit': 'TOOLKIT', 'activity': 'ACTIVITY'}
SIZE = 30
TRACKING = 0.14  # letter spacing, in em
PAD = 4
INK = {'light': '#1F2328', 'dark': '#E6EDF3'}  # GitHub's own text colours

font = TTFont(FONT)
glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
upm = font['head'].unitsPerEm
scale = SIZE / upm
cap = font['OS/2'].sCapHeight * scale

for name, text in HEADINGS.items():
    pen = SVGPathPen(glyphs, ntos=lambda v: f'{v:.1f}'.rstrip('0').rstrip('.'))
    x = 0.0
    for i, ch in enumerate(text):
        g = glyphs[cmap[ord(ch)]]
        g.draw(TransformPen(pen, (scale, 0, 0, -scale, x, 0)))
        x += g.width * scale + (TRACKING * SIZE if i < len(text) - 1 else 0)
    W, H = round(x + PAD * 2), round(cap + PAD * 2)
    for theme, ink in INK.items():
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
               f'role="img" aria-label="{text}">\n'
               f'<g transform="translate({PAD} {PAD + cap:.1f})"><path d="{pen.getCommands()}" fill="{ink}"/></g>\n</svg>\n')
        (OUT / f'heading-{name}-{theme}.svg').write_text(svg, encoding='utf-8')
    print(f'{name}: {W}x{H}')
