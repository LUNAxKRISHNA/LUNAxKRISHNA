"""Builds survey-light.svg / survey-dark.svg: Dhruva surveys the contribution grid.

Only the busiest stretch of the year is shown (WEEKS consecutive weeks with the most
contributions). The AUV sweeps it in a lawnmower pattern, row by row, the way an AUV surveys a seabed,
and each day's square lights up as its sonar passes over it. Then the survey loops.

Usage: python make_survey.py <github-user> <output-dir>
Runs daily in GitHub Actions (.github/workflows/survey.yml); needs only the standard library.
"""
import math
import re
import sys
import urllib.request
from pathlib import Path

import dhruva

WEEKS = 24
CELL, GAP = 22, 4
PITCH = CELL + GAP
MARGIN_X, MARGIN_TOP, MARGIN_BOTTOM = 80, 52, 76
OVERSHOOT = 56          # how far past the grid the AUV runs before turning
PASS_TIME = 2.4         # seconds per row
HOLD, FADE = 2.5, 0.8   # finished grid stays up, then fades for the next loop
AUV_SCALE = 0.085

THEMES = {
    'light': {'empty': '#ebedf0', 'levels': ['#cfe0dc', '#a9c6bf', '#84a59d', '#5e8279'],
              'text': '#59636E', 'beam': '#84A59D'},
    'dark': {'empty': '#161b22', 'levels': ['#2a3a37', '#46655e', '#84a59d', '#b5cfc8'],
             'text': '#9198A1', 'beam': '#b5cfc8'},
}


def fetch(user):
    """Returns {(row, col): (level, count, date)} from the public contribution calendar."""
    html = urllib.request.urlopen(f'https://github.com/users/{user}/contributions').read().decode()
    days = re.findall(r'data-date="([\d-]+)" id="contribution-day-component-(\d+)-(\d+)" data-level="(\d)"', html)
    counts = {
        (int(r), int(c)): 0 if n == 'No' else int(n.replace(',', ''))
        for r, c, n in re.findall(r'for="contribution-day-component-(\d+)-(\d+)"[^>]*>(No|[\d,]+) contributions? on', html)
    }
    return {(int(r), int(c)): (int(level), counts.get((int(r), int(c)), 0), date) for date, r, c, level in days}


def busiest(days):
    """The WEEKS consecutive weeks with the most contributions, re-indexed from column 0."""
    cols = max(c for _, c in days) + 1
    per_week = [sum(d[1] for (r, c), d in days.items() if c == col) for col in range(cols)]
    start = max(range(max(cols - WEEKS, 0) + 1), key=lambda s: (sum(per_week[s:s + WEEKS]), s))
    return {(r, c - start): d for (r, c), d in days.items() if start <= c < start + WEEKS}


def month(date):
    y, m, _ = date.split('-')
    return f"{'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()[int(m) - 1]} {y}"


def build(days, theme):
    t = THEMES[theme]
    cols = max(c for _, c in days) + 1
    grid_w = cols * PITCH - GAP
    W, H = grid_w + MARGIN_X * 2, MARGIN_TOP + 7 * PITCH - GAP + MARGIN_BOTTOM
    left, right = MARGIN_X - OVERSHOOT, MARGIN_X + grid_w + OVERSHOOT
    row_y = [MARGIN_TOP + r * PITCH + CELL / 2 for r in range(7)]

    # Lawnmower path: along a row, U-turn down to the next, back along it, and so on.
    radius = PITCH / 2
    path, x = [f'M{left} {row_y[0]}'], left
    for r in range(7):
        x = right if r % 2 == 0 else left
        path.append(f'H{x}')
        if r < 6:
            path.append(f'A{radius} {radius} 0 0 {1 if r % 2 == 0 else 0} {x} {row_y[r + 1]}')
    run, turn = right - left, math.pi * radius
    length = 7 * run + 6 * turn
    scan = PASS_TIME * 7 + PASS_TIME * turn / run * 6
    T = scan + HOLD + FADE

    def reveal_time(r, cx):
        done = r * (run + turn) + (cx - left if r % 2 == 0 else right - cx)
        return done / length * scan

    k = lambda s: f'{s / T:.4f}'
    fade_start = k(scan + HOLD)

    rects = []
    for (r, c), (level, _, _) in sorted(days.items()):
        x, y = MARGIN_X + c * PITCH, MARGIN_TOP + r * PITCH
        rects.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="5" fill="{t["empty"]}"/>')
        if level:
            at = reveal_time(r, x + CELL / 2)
            rects.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="5" fill="{t["levels"][level - 1]}" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{k(at)};{k(min(at + 0.25, scan))};{fade_start};1" '
                f'dur="{T:.2f}s" repeatCount="indefinite"/></rect>'
            )

    # The AUV carries a side-scan sonar swath across its path; both fade out while the grid holds.
    auv = (
        f'<g opacity="0">'
        f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;{k(0.4)};{k(scan - 0.3)};{k(scan + 0.2)};1" '
        f'dur="{T:.2f}s" repeatCount="indefinite"/>'
        f'<animateMotion path="{" ".join(path)}" rotate="auto" keyPoints="0;1;1" keyTimes="0;{k(scan)};1" '
        f'calcMode="linear" dur="{T:.2f}s" repeatCount="indefinite"/>'
        f'<rect x="-3" y="-{PITCH * 1.6:.0f}" width="6" height="{PITCH * 3.2:.0f}" rx="3" fill="{t["beam"]}" opacity=".35"/>'
        f'{dhruva.group(AUV_SCALE)}'
        f'</g>'
    )

    dates = sorted(d[2] for d in days.values())
    total = sum(d[1] for d in days.values())
    caption = f'{total:,} contributions · {month(dates[0])} – {month(dates[-1])} · surveyed daily by Dhruva'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Contribution graph: {caption}">
{"".join(rects)}
{auv}
<text x="{W / 2}" y="{H - 12}" text-anchor="middle" fill="{t["text"]}" font-family="-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="14">{caption}</text>
</svg>
'''


if __name__ == '__main__':
    user, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    days = busiest(fetch(user))
    for theme in THEMES:
        (out / f'survey-{theme}.svg').write_text(build(days, theme), encoding='utf-8')
    print(f'{len(days)} days, {sum(d[1] for d in days.values())} contributions -> {out}')
