"""Builds skills-marquee.svg: an endlessly scrolling line of category + skill pills."""
import re
from pathlib import Path
from PIL import ImageFont

HERE = Path(__file__).parent
INK = '#20201E'
TONES = {'coral': 'F28482', 'teal': '84A59D', 'bronze': 'F6BD60', 'rose': 'F5CAC3'}

CATEGORIES = [
    ('ROBOTICS & VISION', 'coral', [
        ('OpenCV', 'opencv'), ('YOLOv8', 'yolo'), ('Pixhawk', None), ('PyMAVLink', None),
        ('Raspberry Pi', 'raspberrypi'), ('Arduino', 'arduino'), ('OAK-D Lite', None), ('Fusion 360', 'autodesk'),
    ]),
    ('APPS & BACKEND', 'teal', [
        ('Flutter', 'flutter'), ('React', 'react'), ('React Native', 'react'), ('FastAPI', 'fastapi'), ('MQTT', 'mqtt'),
        ('PostgreSQL', 'postgresql'), ('Supabase', 'supabase'), ('Firebase', 'firebase'), ('Docker', 'docker'),
    ]),
    ('LANGUAGES', 'bronze', [
        ('Python', 'python'), ('TypeScript', 'typescript'), ('JavaScript', 'javascript'),
        ('Dart', 'dart'), ('C', 'c'), ('Java', 'openjdk'),
    ]),
    ('DESIGN & TOOLS', 'rose', [
        ('Figma', 'figma'), ('Photoshop', 'adobephotoshop'), ('Illustrator', 'adobeillustrator'),
        ('Git', 'git'), ('GitHub', 'github'), ('Linux', 'linux'),
    ]),
]

FONT_SIZE = 15
H, PILL_H, GAP, CAT_GAP = 64, 38, 10, 28
VIEW_W = 900
SPEED = 45  # px per second

regular = ImageFont.truetype('arial.ttf', FONT_SIZE)
bold = ImageFont.truetype('arialbd.ttf', FONT_SIZE)


def tint(hex_, amount):
    r, g, b = (int(hex_[i:i + 2], 16) for i in (0, 2, 4))
    mix = lambda c: round(c + (255 - c) * amount)
    return f'#{mix(r):02X}{mix(g):02X}{mix(b):02X}'


def icon_path(slug):
    if not slug:
        return None
    return re.search(r'<path d="([^"]+)"', (HERE / 'icons' / f'{slug}.svg').read_text()).group(1)


def pill(x, label, tone, category):
    font = bold if category else regular
    text_w = font.getlength(label if category else label[1]) * 1.06  # headroom for font differences across OSes
    y = (H - PILL_H) / 2
    tone_hex = TONES[tone]
    parts, pad = [], 16
    if category:
        w = text_w + pad * 2
        parts.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{PILL_H}" rx="{PILL_H / 2}" fill="#{tone_hex}"/>')
        parts.append(f'<text x="{x + pad:.1f}" y="{H / 2 + 5}" class="cat">{label.replace("&", "&amp;")}</text>')
        return parts, w
    path, label_text = label
    icon_w = 18 if path else 0
    w = text_w + pad * 2 + (icon_w + 8 if path else 0)
    parts.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{PILL_H}" rx="{PILL_H / 2}" '
                 f'fill="{tint(tone_hex, 0.72)}" stroke="#{tone_hex}" stroke-width="1.5"/>')
    tx = x + pad
    if path:
        s = icon_w / 24
        parts.append(f'<path transform="translate({tx:.1f} {H / 2 - icon_w / 2}) scale({s:.3f})" d="{path}" fill="{INK}"/>')
        tx += icon_w + 8
    parts.append(f'<text x="{tx:.1f}" y="{H / 2 + 5}" class="skill">{label_text}</text>')
    return parts, w


def build_row():
    parts, x = [], 0.0
    for name, tone, skills in CATEGORIES:
        p, w = pill(x, name, tone, True)
        parts += p
        x += w + GAP
        for label, slug in skills:
            p, w = pill(x, (icon_path(slug), label), tone, False)
            parts += p
            x += w + GAP
        x += CAT_GAP - GAP
    return parts, x


row, row_w = build_row()
duration = row_w / SPEED

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{VIEW_W}" height="{H}" viewBox="0 0 {VIEW_W} {H}" role="img" aria-label="Skills: {", ".join(s for _, _, sk in CATEGORIES for s, _ in sk)}">
<style>
  text {{ font-family: Arial, Helvetica, sans-serif; font-size: {FONT_SIZE}px; fill: {INK}; }}
  .cat {{ font-weight: 700; letter-spacing: .02em; }}
  .track {{ animation: scroll {duration:.1f}s linear infinite; }}
  @keyframes scroll {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-{row_w:.1f}px); }} }}
  @media (prefers-reduced-motion: reduce) {{ .track {{ animation: none; }} }}
</style>
<defs>
  <linearGradient id="fade" x1="0" x2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".07" stop-color="#fff"/>
    <stop offset=".93" stop-color="#fff"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="edges"><rect width="{VIEW_W}" height="{H}" fill="url(#fade)"/></mask>
  <g id="row">{"".join(row)}</g>
</defs>
<g mask="url(#edges)">
  <g class="track"><use href="#row"/><use href="#row" x="{row_w:.1f}"/></g>
</g>
</svg>
'''
(HERE / 'skills-marquee.svg').write_text(svg, encoding='utf-8')
print(f'row width {row_w:.0f}px, loop {duration:.0f}s, {len(svg) / 1024:.1f} KB')
