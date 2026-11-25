"""
Generates profile.svg: an animated "terminal" card for your GitHub profile README,
with your photo turned into a glowing dot portrait.

Usage:
    pip install pillow
    python generate_profile.py            # uses photo.jpg in this folder
    python generate_profile.py me.png     # or any other photo

Then commit profile.svg + README.md to the repo named exactly like your username.
"""
import sys
from html import escape
from PIL import Image, ImageChops, ImageFilter, ImageOps

# ───────────────────────── EDIT YOUR INFO HERE ─────────────────────────
USERNAME = "kabyik"          # shown in the terminal prompt and title bar
NAME = "Kabyik Paul"
INFO = [  # (label, value) — use a list of strings for multi-line values
    ("Name", NAME),
    ("Role", "B.Tech CSE Student"),
    ("Specializing", "IoT, Cybersecurity, Blockchain"),
    ("Currently", "Full Stack Development"),
    ("Languages", ["Python, Java, C++, C, JavaScript", "Solidity"]),
    ("Web", ["React, Node.js, Express.js", "Tailwind CSS, Bootstrap, PostgreSQL"]),
    ("Interests", ["Networking protocols (BLAST, DASH7, CORPL)", "Open source, DSA"]),
]
SECTION_TITLE = "Goals"
PROJECTS = [
    ("Secure IoT", "Full-stack apps with IoT + blockchain"),
    ("Security", "Practical cybersecurity projects"),
    ("Open Source", "Reliable, high-performance software"),
]
LINKS = [  # (icon, label, value)  icons: github, web, linkedin, instagram, youtube, mail, x
    ("linkedin", "LinkedIn", "in/kabyik-paul-77387b2ba"),
    ("youtube", "YouTube", "@kabyikpaul5651"),
    ("x", "X", "@KabyikP"),
    # ("github", "GitHub", "github.com/YOUR-GITHUB-USERNAME"),
]
NAV = ["Code", "IoT", "Security", "Contact"]
# ───────────────────────────────────────────────────────────────────────

W, H = 1200, 690
CYAN, VIOLET, GREEN = "#22d3ee", "#818cf8", "#22c55e"
TEXT, MUTED, BG = "#e2e8f0", "#475569", "#060b14"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

# Portrait panel geometry
PX, PY, PW, PH = 24, 82, 530, 560
# Info panel geometry
IX, IY, IW, IH = 578, 82, 598, 560


def portrait_dots(path):
    """Turn a photo into glowing dots: bright outline + facial features, dark background.
    Works best with a plain background (like a passport/ID-style photo)."""
    cols, rows = 100, 104
    step_x = (PW - 30) / cols
    step_y = (PH - 50) / rows
    k = 6  # work at 6x grid resolution, then average down
    rgb = Image.open(path).convert("RGB")
    rgb = ImageOps.fit(rgb, (cols * k, rows * k), centering=(0.5, 0.3))
    size = rgb.size

    # 1) separate person from background using the corner color
    corners = [rgb.crop((0, 0, 20, 20)), rgb.crop((size[0] - 20, 0, size[0], 20))]
    bg = tuple(sum(c.resize((1, 1), Image.BOX).getpixel((0, 0))[i] for c in corners) // 2 for i in range(3))
    diff = ImageChops.difference(rgb, Image.new("RGB", size, bg)).convert("L")
    mask = diff.point(lambda p: 255 if p > 28 else 0).filter(ImageFilter.MedianFilter(9))

    # 2) silhouette outline (thick, bright)
    outline = mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))

    # 3) inner details: eyes, hairline, mouth, collar, tie
    lum = ImageOps.autocontrast(rgb.convert("L"), cutoff=1).filter(ImageFilter.GaussianBlur(1.5))
    detail = ImageOps.autocontrast(lum.filter(ImageFilter.FIND_EDGES), cutoff=1)
    detail = ImageChops.multiply(detail, mask.filter(ImageFilter.MinFilter(7)))

    lines = ImageChops.lighter(outline, detail).resize((cols, rows), Image.BOX)
    body = mask.resize((cols, rows), Image.BOX)

    out = []
    for y in range(2, rows - 1):
        for x in range(1, cols - 1):
            v = min(1.0, lines.getpixel((x, y)) / 255 * 2.3)
            if v < 0.2:
                if body.getpixel((x, y)) < 128:
                    continue
                v = 0.12  # faint fill so the silhouette reads as solid
            cx = PX + 15 + x * step_x + step_x / 2
            cy = PY + 40 + y * step_y + step_y / 2
            r = 0.55 + v * 1.25
            out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.2f}" opacity="{min(1, 0.2 + v):.2f}"/>')
    return "\n".join(out)


def icon(kind, x, y):
    c = f'stroke="{TEXT}" fill="none" stroke-width="1.3"'
    if kind == "github":
        return f'<circle cx="{x+6}" cy="{y-4}" r="6" {c}/><path d="M{x+3} {y-1}v-3a3 3 0 0 1 6 0v3" {c}/>'
    if kind == "web":
        return (f'<circle cx="{x+6}" cy="{y-4}" r="6" {c}/><ellipse cx="{x+6}" cy="{y-4}" rx="2.6" ry="6" {c}/>'
                f'<line x1="{x}" y1="{y-4}" x2="{x+12}" y2="{y-4}" {c}/>')
    if kind == "linkedin":
        return (f'<rect x="{x}" y="{y-10}" width="12" height="12" rx="2" {c}/>'
                f'<text x="{x+6}" y="{y-1}" font-size="8" fill="{TEXT}" text-anchor="middle" font-weight="700">in</text>')
    if kind == "instagram":
        return (f'<rect x="{x}" y="{y-10}" width="12" height="12" rx="3.5" {c}/>'
                f'<circle cx="{x+6}" cy="{y-4}" r="2.8" {c}/><circle cx="{x+9.3}" cy="{y-7.3}" r=".7" fill="{TEXT}"/>')
    if kind == "youtube":
        return (f'<rect x="{x-1}" y="{y-9.5}" width="14" height="11" rx="3" {c}/>'
                f'<path d="M{x+4.5} {y-6.5}v5l4-2.5z" fill="{TEXT}"/>')
    if kind == "mail":
        return f'<rect x="{x}" y="{y-9}" width="12" height="9" rx="1.5" {c}/><path d="M{x} {y-9}l6 5 6-5" {c}/>'
    if kind == "x":
        return f'<path d="M{x} {y-10}l12 12M{x+12} {y-10}l-12 12" {c}/>'
    return ""


def panel(x, y, w, h, label):
    return f'''
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#04121a" fill-opacity=".85"
        stroke="{CYAN}" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="14 6" class="flow" filter="url(#glow)"/>
  <path d="M{x+10} {y+1}h112l-12 18h-100z" fill="#0b2a33"/>
  <text x="{x+16}" y="{y+14}" font-size="11" letter-spacing="2" fill="{CYAN}" font-weight="700">{label}</text>'''


def leader(x1, x2, y):
    return f'<line x1="{x1}" y1="{y-4}" x2="{x2}" y2="{y-4}" stroke="{MUTED}" stroke-width="1.4" stroke-dasharray="1 5"/>'


def info_block():
    lx, vx = IX + 24, IX + 220
    y = IY + 56
    parts = [f'<text x="{lx}" y="{y}" font-size="14" font-weight="700">'
             f'<tspan fill="{VIOLET}">{escape(USERNAME)}@developer</tspan><tspan fill="{TEXT}">:~# ./profile.sh</tspan></text>']
    y += 32

    def row(label, value, bullet=">", indent=0, color=CYAN):
        nonlocal y
        values = value if isinstance(value, list) else [value]
        parts.append(f'<text x="{lx+indent}" y="{y}" font-size="13" fill="{color}" font-weight="600">'
                     f'{bullet} {escape(label)}</text>')
        parts.append(leader(lx + indent + 18 + len(label) * 8 + 8, vx - 10, y))
        for i, v in enumerate(values):
            parts.append(f'<text x="{vx}" y="{y + i*20}" font-size="13" fill="{TEXT}">{escape(v)}</text>')
        y += 23 + (len(values) - 1) * 20

    for label, value in INFO:
        row(label, value)
    y += 14
    parts.append(f'<text x="{lx}" y="{y}" font-size="13" fill="{CYAN}" font-weight="600">&gt; {escape(SECTION_TITLE)}</text>')
    y += 23
    for label, value in PROJECTS:
        row(label, value, bullet="•", indent=14)
    y += 14
    parts.append(f'<text x="{lx}" y="{y}" font-size="13" fill="{CYAN}" font-weight="600">&gt; Links</text>')
    y += 23
    for kind, label, value in LINKS:
        parts.append(icon(kind, lx + 20, y))
        parts.append(f'<text x="{lx+40}" y="{y}" font-size="13" fill="{CYAN}" font-weight="600">{escape(label)}</text>')
        parts.append(leader(lx + 40 + len(label) * 8 + 8, vx - 10, y))
        parts.append(f'<text x="{vx}" y="{y}" font-size="13" fill="{TEXT}">{escape(value)}</text>')
        y += 22
    y += 6
    parts.append(f'<text x="{lx}" y="{y}" font-size="14" font-weight="700"><tspan fill="{VIOLET}">'
                 f'{escape(USERNAME)}@developer</tspan><tspan fill="{TEXT}">:~#</tspan></text>')
    parts.append(f'<rect x="{lx + (len(USERNAME)+13)*8.4 + 8}" y="{y-12}" width="8" height="15" fill="{CYAN}" class="blink"/>')
    return "\n  ".join(parts), y


def nav():
    out, x = [], 760
    for item in NAV:
        out.append(f'<text x="{x}" y="52" font-size="12" fill="#7dd3fc">{escape(item)}</text>')
        x += len(item) * 8 + 34
    return "\n  ".join(out)


def build(photo):
    dots = portrait_dots(photo)
    info, _ = info_block()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">
  <defs>
    <linearGradient id="dotfill" gradientUnits="userSpaceOnUse" x1="0" y1="{PY}" x2="0" y2="{PY+PH}">
      <stop offset="0" stop-color="#67e8f9"/><stop offset=".6" stop-color="#60a5fa"/><stop offset="1" stop-color="{VIOLET}"/>
    </linearGradient>
    <linearGradient id="scan" x1="0" x2="1">
      <stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/><stop offset=".5" stop-color="#a5b4fc"/>
      <stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="7" height="7" patternUnits="userSpaceOnUse">
      <circle cx="3.5" cy="3.5" r=".7" fill="#1e3a5f"/>
    </pattern>
    <filter id="glow" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="dotglow"><feGaussianBlur stdDeviation="1.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <clipPath id="pclip"><rect x="{PX+12}" y="{PY+30}" width="{PW-24}" height="{PH-42}" rx="6"/></clipPath>
    <style>
      .flow {{ animation: flow 6s linear infinite; }}
      @keyframes flow {{ to {{ stroke-dashoffset: -200; }} }}
      .blink {{ animation: blink 1s steps(1) infinite; }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
      .pulse {{ animation: pulse 2s ease-in-out infinite; }}
      @keyframes pulse {{ 50% {{ opacity: .35; }} }}
      .scan {{ animation: scan 5s ease-in-out infinite alternate; }}
      @keyframes scan {{ from {{ transform: translateY(0); }} to {{ transform: translateY({PH-60}px); }} }}
      .face {{ animation: shimmer 4s ease-in-out infinite; }}
      @keyframes shimmer {{ 50% {{ opacity: .8; }} }}
      @media (prefers-reduced-motion: reduce) {{ .flow,.blink,.pulse,.scan,.face {{ animation: none; }} }}
    </style>
  </defs>

  <!-- outer frame -->
  <rect x="4" y="4" width="{W-8}" height="{H-8}" rx="22" fill="{BG}" stroke="{CYAN}" stroke-width="2" filter="url(#glow)"/>
  <line x1="40" y1="{H-24}" x2="{W-40}" y2="{H-24}" stroke="{CYAN}" stroke-opacity=".35" stroke-width="2" stroke-dasharray="30 60" class="flow"/>
  <line x1="40" y1="22" x2="{W-40}" y2="22" stroke="{VIOLET}" stroke-opacity=".35" stroke-width="2" stroke-dasharray="30 70" class="flow"/>

  <!-- title bar -->
  <circle cx="40" cy="48" r="6.5" fill="#ff5f57"/><circle cx="62" cy="48" r="6.5" fill="#febc2e"/><circle cx="84" cy="48" r="6.5" fill="#28c840"/>
  <text x="112" y="53" font-size="14" font-weight="700" fill="{CYAN}">{escape(USERNAME)}/README.md</text>
  {nav()}

  <!-- portrait -->
  {panel(PX, PY, PW, PH, "VISUAL.MAP")}
  <g clip-path="url(#pclip)">
    <rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="url(#grid)"/>
    <g fill="url(#dotfill)" filter="url(#dotglow)" class="face">
{dots}
    </g>
    <rect x="{PX+12}" y="{PY+40}" width="{PW-24}" height="3" fill="url(#scan)" class="scan"/>
  </g>

  <!-- info -->
  {panel(IX, IY, IW, IH, "SYSTEM.INFO")}
  <circle cx="{IX+IW-76}" cy="{IY+26}" r="5" fill="{GREEN}" class="pulse"/>
  <text x="{IX+IW-64}" y="{IY+30}" font-size="12" fill="{GREEN}" font-weight="700">online</text>
  {info}
</svg>
'''


if __name__ == "__main__":
    photo = sys.argv[1] if len(sys.argv) > 1 else "photo.jpg"
    svg = build(photo)
    with open("profile.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"profile.svg written ({len(svg)//1024} KB)")
