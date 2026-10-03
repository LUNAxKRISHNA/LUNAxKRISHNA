"""Builds hero.svg: KRISHNA in the portfolio's hero style, with the character leaning his elbow on the A."""
import base64
import io
from pathlib import Path
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

HERE = Path(__file__).parent
PORTFOLIO = Path('D:/Works/portfolio')

font = TTFont(PORTFOLIO / 'src/assets/fonts/SixCaps.woff2')
glyphs, cmap = font.getGlyphSet(), font.getBestCmap()

COLORS = ['#F28482', '#84A59D', '#F6BD60']  # DisplayWord's coral -> teal -> bronze cycle
EASE = 'cubic-bezier(0.16, 1, 0.3, 1)'      # EASE_EDITORIAL
NAME = 'KRISHNA'
STRETCH = 1.3
LETTER_DELAY, LETTER_DUR = 0.15, 1.5

# Points measured on standing.webp (pixels): top of the hair, bottom of the shoes,
# the underside of the elbow that rests on the A, and the first/last solid columns.
IMG_TOP, IMG_FEET = 33, 1491
ELBOW_X, ELBOW_Y = 228, 390
SOLID_L, SOLID_R = 179, 841

H = 720
BASELINE = H - 28  # room below for the ground shadow
HEAD_ROOM = 12

# Size the letters so that, with the elbow on the A's apex and the shoes on the baseline,
# the head still fits inside the canvas.
bp = BoundsPen(glyphs)
glyphs[cmap[ord('A')]].draw(bp)
a_xmin, _, a_xmax, a_top = bp.bounds
cap_px = (BASELINE - HEAD_ROOM) * (IMG_FEET - ELBOW_Y) / (IMG_FEET - IMG_TOP)
scale = cap_px / a_top
img_scale = cap_px / (IMG_FEET - ELBOW_Y)

advances = [glyphs[cmap[ord(c)]].width * scale * STRETCH for c in NAME]
text_w = sum(advances)
apex_x = sum(advances[:-1]) + (a_xmin + a_xmax) / 2 * scale * STRETCH  # from the text start

img = Image.open(HERE / 'standing.webp').convert('RGBA')
fig_left = apex_x - ELBOW_X * img_scale  # image's left edge, from the text start
content_l = min(0, fig_left + SOLID_L * img_scale)
content_r = max(text_w, fig_left + SOLID_R * img_scale)
W = round(content_r - content_l + 60)
x0 = (W - (content_r - content_l)) / 2 - content_l  # text start, so the whole group is centred

# Embedded, since SVGs shown through <img> can't load other files.
small = img.resize((round(img.width * 900 / img.height), 900), Image.LANCZOS)
buf = io.BytesIO()
small.save(buf, 'WEBP', quality=82, method=6)
data = base64.b64encode(buf.getvalue()).decode()

letters, x = [], x0
for i, (ch, adv) in enumerate(zip(NAME, advances)):
    pen = SVGPathPen(glyphs)
    glyphs[cmap[ord(ch)]].draw(TransformPen(pen, (scale * STRETCH, 0, 0, -scale, 0, 0)))
    d = -250 if i % 2 == 0 else 250
    letters.append(
        f'<g transform="translate({x:.1f} {BASELINE})">'
        f'<g class="l" style="--d:{d}px;animation-delay:{LETTER_DELAY * i:.2f}s">'
        f'<path d="{pen.getCommands()}" fill="{COLORS[i % 3]}"/></g></g>'
    )
    x += adv

img_x = x0 + fig_left
img_y = BASELINE - IMG_FEET * img_scale
feet_cx = img_x + 690 * img_scale  # between the two shoes
char_delay = LETTER_DELAY * (len(NAME) - 1) + 0.6  # once the A has landed

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Krishna K">
<style>
  .l {{ animation: drop {LETTER_DUR}s {EASE} both; }}
  @keyframes drop {{ from {{ transform: translateY(var(--d)); opacity: 0; }} to {{ transform: none; opacity: 1; }} }}
  .lean {{ animation: lean 1.1s {EASE} {char_delay:.2f}s both; }}
  @keyframes lean {{ from {{ transform: translateX(90px); opacity: 0; }} to {{ transform: none; opacity: 1; }} }}
  @media (prefers-reduced-motion: reduce) {{ .l, .lean {{ animation: none; }} }}
</style>
<defs>
  <filter id="shadow" x="-20%" y="-10%" width="140%" height="130%">
    <feDropShadow dx="0" dy="18" stdDeviation="14" flood-color="#20201E" flood-opacity=".22"/>
  </filter>
  <filter id="blur" x="-50%" y="-300%" width="200%" height="700%"><feGaussianBlur stdDeviation="8"/></filter>
</defs>
{"".join(letters)}
<g class="lean">
  <ellipse cx="{feet_cx:.1f}" cy="{BASELINE - 4}" rx="{240 * img_scale:.0f}" ry="10" fill="#20201E" fill-opacity=".35" filter="url(#blur)"/>
  <image href="data:image/webp;base64,{data}" x="{img_x:.1f}" y="{img_y:.1f}" width="{img.width * img_scale:.1f}" height="{img.height * img_scale:.1f}" filter="url(#shadow)"/>
</g>
</svg>
'''
(HERE / 'hero.svg').write_text(svg, encoding='utf-8')
print(f'{W}x{H}, {len(svg) / 1024:.0f} KB, cap {cap_px:.0f}px')
