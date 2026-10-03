"""Builds assets/tagline-light.svg / tagline-dark.svg: the README tagline in Alro, drawn as paths."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = Path(__file__).parent
OUT = HERE.parent / 'assets'
FONT = Path.home() / 'AppData/Local/Microsoft/Windows/Fonts/alro-alro-regular-400.otf'

# (text, size, delay, GitHub's text colour per theme)
LINES = [
    ('Systems-oriented CS engineer, building robots and the software around them.', 34, 2.2,
     {'light': '#1F2328', 'dark': '#E6EDF3'}),
    ('Perception · sensor fusion · embedded control · backend APIs · mobile apps', 27, 2.45,
     {'light': '#59636E', 'dark': '#9198A1'}),
]
GAP = 10
PAD = 6

font = TTFont(FONT)
glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
upm = font['head'].unitsPerEm
ascent, descent = font['hhea'].ascent, font['hhea'].descent


def line_path(text, size):
    """Returns (path data starting at x=0 on the baseline, advance width)."""
    scale = size / upm
    pen = SVGPathPen(glyphs, ntos=lambda v: f'{v:.1f}'.rstrip('0').rstrip('.'))
    x = 0.0
    for ch in text:
        g = glyphs[cmap[ord(ch)]]
        g.draw(TransformPen(pen, (scale, 0, 0, -scale, x, 0)))
        x += g.width * scale
    return pen.getCommands(), x


rendered = [(line_path(text, size), size, delay, inks) for text, size, delay, inks in LINES]
W = round(max(w for (_, w), *_ in rendered) + PAD * 2)

# Stack the lines, each centred.
placed, y = [], PAD
for (d, w), size, delay, inks in rendered:
    baseline = y + ascent / upm * size
    placed.append((d, (W - w) / 2, baseline, delay, inks))
    y = baseline - descent / upm * size + GAP
H = round(y - GAP + PAD)

label = ' '.join(text for text, *_ in LINES)
for theme in ('light', 'dark'):
    groups = ''.join(
        f'<g transform="translate({x:.1f} {b:.1f})"><path d="{d}" fill="{inks[theme]}" style="animation-delay:{delay}s"/></g>\n'
        for d, x, b, delay, inks in placed
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
<style>
  path {{ animation: rise 1s cubic-bezier(0.16, 1, 0.3, 1) both; }}
  @keyframes rise {{ from {{ transform: translateY(10px); opacity: 0; }} to {{ transform: none; opacity: 1; }} }}
  @media (prefers-reduced-motion: reduce) {{ path {{ animation: none; }} }}
</style>
{groups}</svg>
'''
    (OUT / f'tagline-{theme}.svg').write_text(svg, encoding='utf-8')
print(f'{W}x{H}')
