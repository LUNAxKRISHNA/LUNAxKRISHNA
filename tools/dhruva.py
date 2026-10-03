"""Dhruva, top-down, as flat SVG shapes in the portfolio palette.

Traced by eye from dhruva-top.png (1280x1024 render, front = bottom of the image).
Coordinates are in that image's pixels; callers scale and rotate the group.
"""

CORAL, BRONZE, TEAL, LINEN, INK = '#F28482', '#F6BD60', '#84A59D', '#F7EDE2', '#20201E'
CENTER = (640, 530)

THRUSTERS = [(178, 165), (1100, 165), (178, 815), (1100, 815)]
VERTICAL_PODS = [(318, 275, 38), (962, 275, -38), (318, 712, -38), (962, 712, 38)]


def thruster(cx, cy):
    blades = ''.join(
        f'<rect x="{cx - 9}" y="{cy - 52}" width="18" height="44" rx="6" fill="{BRONZE}" '
        f'transform="rotate({a} {cx} {cy})"/>'
        for a in (45, 135, 225, 315)
    )
    return (f'<circle cx="{cx}" cy="{cy}" r="68" fill="none" stroke="{BRONZE}" stroke-width="12"/>'
            f'{blades}<circle cx="{cx}" cy="{cy}" r="30" fill="{INK}"/>')


def shapes():
    parts = []
    # Arms from the frame out to the corner thrusters.
    for (tx, ty), (fx, fy) in zip(THRUSTERS, [(420, 260), (860, 260), (420, 720), (860, 720)]):
        parts.append(f'<line x1="{tx}" y1="{ty}" x2="{fx}" y2="{fy}" stroke="{CORAL}" stroke-width="58" stroke-linecap="round"/>')
    # Top plate and the two side rails.
    parts.append(f'<rect x="300" y="140" width="680" height="16" rx="6" fill="{LINEN}"/>')
    for x in (388, 808):
        parts.append(f'<rect x="{x}" y="150" width="84" height="680" rx="14" fill="{CORAL}"/>')
    # Angled vertical-thruster pods.
    for x, y, a in VERTICAL_PODS:
        parts.append(f'<rect x="{x - 62}" y="{y - 40}" width="124" height="80" rx="30" fill="{TEAL}" transform="rotate({a} {x} {y})"/>')
    # Clear main hull with carbon rods, and its end caps.
    parts.append(f'<rect x="520" y="190" width="240" height="600" rx="10" fill="{LINEN}" fill-opacity=".85"/>')
    for x in (556, 598, 670, 712):
        parts.append(f'<rect x="{x - 5}" y="200" width="10" height="580" fill="{INK}" fill-opacity=".35"/>')
    parts.append(f'<rect x="512" y="128" width="256" height="70" rx="12" fill="{INK}"/>')
    parts.append(f'<rect x="494" y="778" width="292" height="44" rx="10" fill="{INK}"/>')
    # Front shell with the camera window.
    parts.append(f'<path d="M262 822 H1018 Q1004 872 906 888 Q780 916 640 920 Q500 916 374 888 Q276 872 262 822 Z" fill="{LINEN}"/>')
    parts.append(f'<ellipse cx="640" cy="900" rx="118" ry="16" fill="{INK}" fill-opacity=".35"/>')
    for x, y in THRUSTERS:
        parts.append(thruster(x, y))
    return ''.join(parts)


def group(scale, extra_transform=''):
    """Dhruva centred on (0, 0), front facing +x, at the given scale."""
    cx, cy = CENTER
    return (f'<g transform="{extra_transform} rotate(-90) scale({scale}) translate({-cx} {-cy})">'
            f'{shapes()}</g>')


if __name__ == '__main__':
    from pathlib import Path
    out = Path(__file__).with_name('dhruva-preview.svg')
    out.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="560" viewBox="0 0 1100 560">'
                   f'<rect width="550" height="560" fill="#ffffff"/><rect x="550" width="550" height="560" fill="#0d1117"/>'
                   f'<g transform="translate(275 280)">{group(0.4, "rotate(90)")}</g>'
                   f'<g transform="translate(825 280)">{group(0.4, "rotate(90)")}</g></svg>')
    print(out)
