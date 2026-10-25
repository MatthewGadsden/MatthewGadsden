#!/usr/bin/env python3
"""Generate the tokyo-snow SVGs used by the profile README.

    python3 images/build.py

Writes header.svg, stack.svg and contact-*.svg next to this script. Logos are
fetched (already recoloured) from shields.io, which serves simple-icons.
Every row of the README is ROW px wide at full size; the README sizes each
image as a percentage of that, so keep widths in sync if you change them.
"""
import base64
import re
import urllib.request
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent

# tokyo-snow palette (VS Code variant, see MatthewGadsden/tokyo-snow-vs)
P = dict(brick="#96402e", neon="#d5583d", ember="#db814c", amber="#e1b568", gold="#ecd08f",
         sage="#c4c88e", moss="#a6d46c", pine="#6fc28a", night="#1c1c1a", shadow="#2a2a28",
         slate="#3a3933", dim="#7d7860", snow="#f1e4b5")
FONT = 'ui-monospace, SFMono-Regular, Menlo, Consolas, "DejaVu Sans Mono", "Liberation Mono", monospace'

# Total row width (header.svg's width); GAP is the spacing baked into images.
ROW, GAP, PAD_V = 860, 10, 6


def logo(name, colour):
    """Return a simple-icons logo as a data URI, coloured `colour`."""
    url = f"https://img.shields.io/badge/x-000?style=for-the-badge&logo={name}&logoColor={colour.lstrip('#')}"
    req = urllib.request.Request(url, headers={"User-Agent": "MatthewGadsden-readme-build"})
    svg = urllib.request.urlopen(req).read().decode()
    match = re.search(r"data:image/svg\+xml;base64,[A-Za-z0-9+/=]+", svg)
    if not match:
        raise SystemExit(f"shields.io has no logo named {name!r}")
    return match.group(0)


def header():
    sloth = base64.b64encode((OUT / "sloth.png").read_bytes()).decode()
    rows = [
        ("Name",     "Matthew Gadsden",                            "neon"),
        ("Role",     "Development Manager / Full-Stack Engineer",  "ember"),
        ("Company",  "Compass Education",                          "amber"),
        ("Location", "Melbourne, Australia",                       "gold"),
        ("OS",       "Arch Linux + Hyprland",                      "sage"),
        ("Editor",   "VS Code + Neovim",                           "moss"),
        ("Theme",    "tokyo-snow",                                 "pine"),
    ]
    strip = ["brick", "neon", "ember", "amber", "gold", "sage", "moss", "pine"]

    W, H = ROW, 320
    x0, xv, y0, dy = 290, 395, 112, 24
    out = []
    out.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="gaddo@github: Matthew Gadsden, Development Manager / Full-Stack Engineer">
  <style>
    text {{ font-family: {FONT}; font-size: 15px; fill: {P["snow"]}; }}
    .b {{ font-weight: 700; }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
  </style>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="{P["night"]}" stroke="{P["slate"]}"/>
  <path d="M0.5 36 V12.5 a12 12 0 0 1 12 -12 H{W-12.5} a12 12 0 0 1 12 12 V36 Z" fill="{P["shadow"]}"/>
  <line x1="0.5" y1="36" x2="{W-0.5}" y2="36" stroke="{P["slate"]}"/>
  <circle cx="22" cy="18" r="5.5" fill="{P["neon"]}"/>
  <circle cx="40" cy="18" r="5.5" fill="{P["amber"]}"/>
  <circle cx="58" cy="18" r="5.5" fill="{P["moss"]}"/>
  <text x="{W/2}" y="23" text-anchor="middle" style="font-size:13px; fill:{P["dim"]}">gaddo@akame: ~</text>
  <image x="50" y="80" width="190" height="190" style="image-rendering:pixelated" href="data:image/png;base64,{sloth}"/>
  <text x="{x0}" y="80" class="b"><tspan fill="{P["amber"]}">gaddo</tspan><tspan fill="{P["snow"]}">@</tspan><tspan fill="{P["ember"]}">github</tspan></text>
  <line x1="{x0}" y1="90" x2="{x0+112}" y2="90" stroke="{P["dim"]}" stroke-width="1.5"/>''')
    for i, (k, v, c) in enumerate(rows):
        y = y0 + i * dy
        out.append(f'  <text x="{x0}" y="{y}" class="b" fill="{P[c]}" style="fill:{P[c]}">{escape(k)}</text>')
        out.append(f'  <text x="{xv}" y="{y}">{escape(v)}</text>')
    ys = y0 + len(rows) * dy - 6
    for i, c in enumerate(strip):
        out.append(f'  <rect x="{x0 + i*34}" y="{ys}" width="34" height="14" fill="{P[c]}"/>')
    out.append(f'''  <text x="22" y="{H-18}" class="b" style="fill:{P["ember"]}">&gt;&gt;</text>
  <rect class="cursor" x="48" y="{H-31}" width="9" height="17" fill="{P["snow"]}"/>
</svg>''')
    (OUT / "header.svg").write_text("\n".join(out) + "\n")


def stack():
    """Tech stack card, same height as the streak card (495x195) beside it."""
    SW, SH = 495, 195
    CW = ROW - SW - GAP                     # visible card width
    items = [  # (label, logo, colour) warm -> cool
        ("TypeScript", "typescript", "neon"), ("Python", "python", "neon"), ("Java", "openjdk", "neon"),
        ("Rust", "rust", "neon"), ("Bash", "gnubash", "neon"),
        (".NET", "dotnet", "amber"), ("Node.js", "nodedotjs", "amber"), ("React", "react", "amber"),
        ("GraphQL", "graphql", "amber"), ("OAuth2.0", "auth0", "amber"),
        ("PostgreSQL", "postgresql", "moss"), ("MongoDB", "mongodb", "moss"), ("Kafka", "apachekafka", "moss"),
        ("AWS", None, "pine"), ("Docker", "docker", "pine"), ("YAML", "yaml", "pine"),
    ]
    FS, CH_W, CHIP_H, LOGO, CPAD, CGAP = 11, 6.6, 24, 13, 8, 6
    INNER = CW - 2 * 16

    def chip_w(label, lg):
        return round(CPAD + (LOGO + 6 if lg else 0) + len(label) * CH_W + CPAD + len(label) * 0.6)

    rows, cur, w = [], [], 0
    for item in items:
        cw = chip_w(item[0], item[1])
        if cur and w + CGAP + cw > INNER:
            rows.append((cur, w))
            cur, w = [], 0
        cur.append((item, cw))
        w += (CGAP if len(cur) > 1 else 0) + cw
    rows.append((cur, w))
    title_h = 30
    body_h = len(rows) * CHIP_H + (len(rows) - 1) * CGAP
    y = (SH - title_h - body_h) / 2 + title_h + 2
    out = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CW + GAP}" height="{SH}" viewBox="0 0 {CW + GAP} {SH}" role="img" aria-label="Tech stack: {", ".join(s[0] for s in items)}">
  <style>text {{ font-family: {FONT}; font-weight: 700; }}</style>
  <rect x="{GAP + 0.5}" y="0.5" width="{CW - 1}" height="{SH - 1}" rx="12" fill="{P["night"]}" stroke="{P["slate"]}"/>
  <text x="{GAP + 16}" y="28" style="font-size:13px; fill:{P["amber"]}">~/stack</text>
  <line x1="{GAP + 16}" y1="36" x2="{GAP + 16 + 64}" y2="36" stroke="{P["dim"]}" stroke-width="1.5"/>''']
    for chips, rw in rows:
        x = GAP + 16
        for (label, lg, c), cw in chips:
            out.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{cw}" height="{CHIP_H}" rx="4" fill="{P["shadow"]}" stroke="{P["slate"]}"/>')
            tx = x + CPAD
            if lg:
                out.append(f'  <image x="{tx:.1f}" y="{y + (CHIP_H - LOGO) / 2:.1f}" width="{LOGO}" height="{LOGO}" href="{logo(lg, P[c])}"/>')
                tx += LOGO + 6
            tw = cw - (tx - x) - CPAD
            out.append(f'  <text x="{tx + tw / 2:.1f}" y="{y + CHIP_H / 2 + 4:.1f}" text-anchor="middle" style="font-size:{FS}px; letter-spacing:0.6px; fill:{P[c]}">{label.upper()}</text>')
            x += cw + CGAP
        y += CHIP_H + CGAP
    out.append("</svg>")
    (OUT / "stack.svg").write_text("\n".join(out) + "\n")


def contacts():
    """Three contact tiles that together span the full row, gaps baked in."""
    items = [("discord", "discord", "Gaddo#5608"), ("email", "gmail", "matthewjgadsden@gmail.com"),
             ("linkedin", None, "Matthew Gadsden")]
    KW = (ROW - 2 * GAP) / 3
    KH = 34
    for i, (name, lg, text) in enumerate(items):
        left = 0 if i == 0 else GAP
        W, H = KW + left, KH + 2 * PAD_V
        content = 18 + 10 + len(text) * 7.9
        cx = left + (KW - content) / 2
        iy = PAD_V + (KH - 18) / 2
        if lg:
            mark = f'<image x="{cx:.1f}" y="{iy:.1f}" width="18" height="18" href="{logo(lg, P["gold"])}"/>'
        else:  # simple-icons dropped LinkedIn, so draw a plain "in" mark
            mark = (f'<rect x="{cx:.1f}" y="{iy:.1f}" width="18" height="18" rx="3" fill="{P["gold"]}"/>'
                    f'<text x="{cx + 9:.1f}" y="{iy + 13.5:.1f}" text-anchor="middle" style="font-size:12px; font-weight:700; fill:{P["night"]}">in</text>')
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W:.2f}" height="{H}" viewBox="0 0 {W:.2f} {H}" role="img" aria-label="{name}: {text}">
  <style>text {{ font-family: {FONT}; }}</style>
  <rect x="{left + 0.5}" y="{PAD_V + 0.5}" width="{KW - 1:.2f}" height="{KH - 1}" rx="8" fill="{P["shadow"]}" stroke="{P["slate"]}"/>
  {mark}
  <text x="{cx + 28:.1f}" y="{PAD_V + KH / 2 + 4.5:.1f}" style="font-size:13px; fill:{P["snow"]}">{text}</text>
</svg>
'''
        (OUT / f"contact-{name}.svg").write_text(svg)


if __name__ == "__main__":
    header()
    stack()
    contacts()
