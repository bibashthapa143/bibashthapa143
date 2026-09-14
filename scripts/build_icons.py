"""
Fetches real icons from skillicons.dev + img.shields.io, converts them to
base64 data URIs, and embeds them into self-contained animated SVGs.

Usage:
    pip install requests
    python build_icons.py

Outputs:
    techstack-fadein-float.svg
    connect-pulse.svg
"""

import base64
import re
import requests

TECH_ICONS = [
    "c", "cpp", "java", "py", "html", "css", "ts", "js",
    "nodejs", "nextjs", "vercel", "windows", "git",
]

DISCORD_BADGE_URL = (
    "https://img.shields.io/badge/Discord-%237289DA.svg"
    "?style=for-the-badge&logo=discord&logoColor=white"
)


def fetch(url: str) -> bytes:
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.content


def to_data_uri(content: bytes, content_type: str = "image/svg+xml") -> str:
    b64 = base64.b64encode(content).decode("utf-8")
    return f"data:{content_type};base64,{b64}"


def get_svg_dimensions(svg_bytes: bytes) -> tuple[float, float]:
    """Extract the real width/height (or viewBox) from an SVG's root tag."""
    text = svg_bytes.decode("utf-8", errors="ignore")
    w_match = re.search(r'width="([\d.]+)"', text)
    h_match = re.search(r'height="([\d.]+)"', text)
    if w_match and h_match:
        return float(w_match.group(1)), float(h_match.group(1))
    vb_match = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', text)
    if vb_match:
        return float(vb_match.group(1)), float(vb_match.group(2))
    return 200.0, 32.0  # fallback


def fetch_as_data_uri(url: str) -> str:
    return to_data_uri(fetch(url))


def build_techstack_svg() -> str:
    icon_size = 40
    gap = 14
    x = 10
    parts = []
    for i, icon in enumerate(TECH_ICONS):
        url = f"https://skillicons.dev/icons?i={icon}"
        data_uri = fetch_as_data_uri(url)
        begin = round(i * 0.15, 2)
        parts.append(f'''  <image x="{x}" y="10" width="{icon_size}" height="{icon_size}"
    href="{data_uri}" opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur="0.4s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate"
      values="0 0;0 -8;0 0" dur="2s" begin="{begin}s" repeatCount="indefinite"/>
  </image>''')
        x += icon_size + gap

    width = x + 10
    body = "\n".join(parts)
    return (
        f'<svg width="{width}" height="60" viewBox="0 0 {width} 60" '
        f'xmlns="http://www.w3.org/2000/svg">\n{body}\n</svg>\n'
    )


def build_connect_svg() -> str:
    raw = fetch(DISCORD_BADGE_URL)
    natural_w, natural_h = get_svg_dimensions(raw)
    data_uri = to_data_uri(raw)

    # scale to a target height, keep the real aspect ratio
    target_h = 32
    scale = target_h / natural_h
    img_w = natural_w * scale
    img_h = target_h

    canvas_w, canvas_h = 240, 70
    img_x = (canvas_w - img_w) / 2
    img_y = (canvas_h - img_h) / 2

    ring_w, ring_h = img_w + 20, img_h + 14
    ring_x, ring_y = img_x - 10, img_y - 7

    return f'''<svg width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}" xmlns="http://www.w3.org/2000/svg">
  <rect x="{ring_x:.1f}" y="{ring_y:.1f}" width="{ring_w:.1f}" height="{ring_h:.1f}" rx="6" fill="none" stroke="#7289DA" stroke-width="2" opacity="0.7">
    <animate attributeName="width" values="{ring_w:.1f};{ring_w+30:.1f};{ring_w:.1f}" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="height" values="{ring_h:.1f};{ring_h+14:.1f};{ring_h:.1f}" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="x" values="{ring_x:.1f};{ring_x-15:.1f};{ring_x:.1f}" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="y" values="{ring_y:.1f};{ring_y-7:.1f};{ring_y:.1f}" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.7;0;0.7" dur="2s" repeatCount="indefinite"/>
  </rect>
  <image x="{img_x:.1f}" y="{img_y:.1f}" width="{img_w:.1f}" height="{img_h:.1f}" href="{data_uri}"/>
</svg>
'''


def build_constellation_svg() -> str:
    import math

    # Each cluster: hub name -> (slug, color), members: name -> (slug, color)
    clusters = {
        "Languages": {
            "center": (160, 130),
            "hub": ("C", "c", "#5C6BC0"),
            "members": [
                ("C++", "cpp", "#00599C"),
                ("Java", "java", "#EA2D2E"),
                ("Py", "py", "#3776AB"),
            ],
        },
        "Web": {
            "center": (600, 130),
            "hub": ("HTML", "html", "#E34F26"),
            "members": [
                ("CSS", "css", "#1572B6"),
                ("JS", "js", "#F7DF1E"),
                ("TS", "ts", "#3178C6"),
            ],
        },
        "Runtime": {
            "center": (600, 380),
            "hub": ("Node", "nodejs", "#339933"),
            "members": [
                ("Next", "nextjs", "#c0caf5"),
                ("Vercel", "vercel", "#c0caf5"),
            ],
        },
        "Tools": {
            "center": (160, 380),
            "hub": ("Git", "git", "#F05032"),
            "members": [
                ("VSCode", "vscode", "#007ACC"),
                ("Linux", "linux", "#FCC624"),
                ("Windows", "windows", "#00A4EF"),
                ("Figma", "figma", "#F24E1E"),
                ("GHPages", "github", "#c0caf5"),
            ],
        },
    }

    W, H = 760, 510
    hub_r, member_r, member_radius = 24, 16, 78

    positions = {}   # name -> (x, y)
    node_info = {}   # name -> (slug, color, radius, is_hub)
    intra_edges = []
    hub_names = {}   # cluster_key -> hub name

    for key, c in clusters.items():
        ccx, ccy = c["center"]
        hub_name, hub_slug, hub_color = c["hub"]
        positions[hub_name] = (ccx, ccy)
        node_info[hub_name] = (hub_slug, hub_color, hub_r, True)
        hub_names[key] = hub_name

        n = len(c["members"])
        for i, (name, slug, color) in enumerate(c["members"]):
            angle = (2 * math.pi * i / n) - math.pi / 2
            x = ccx + member_radius * math.cos(angle)
            y = ccy + member_radius * math.sin(angle)
            positions[name] = (x, y)
            node_info[name] = (slug, color, member_r, False)
            intra_edges.append((hub_name, name))

    # bridges between cluster hubs / cross-cluster ties
    bridge_edges = [
        (hub_names["Tools"], hub_names["Languages"]),
        (hub_names["Tools"], hub_names["Web"]),
        (hub_names["Tools"], hub_names["Runtime"]),
        ("JS", hub_names["Runtime"]),
        ("Figma", hub_names["Web"]),
    ]

    parts = [
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">',
        f'  <rect x="0" y="0" width="{W}" height="{H}" rx="14" fill="#1a1b27"/>',
    ]

    for a, b in intra_edges:
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        parts.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#414868" stroke-width="1" opacity="0.4"/>')

    for i, (a, b) in enumerate(bridge_edges):
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        begin = round(i * 0.35, 2)
        parts.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#BB9AF7" stroke-width="1.5" opacity="0.55"/>')
        parts.append(f'''  <circle r="3" fill="#BB9AF7">
    <animateMotion dur="2.6s" begin="{begin}s" repeatCount="indefinite" path="M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}"/>
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.9;1" dur="2.6s" begin="{begin}s" repeatCount="indefinite"/>
  </circle>''')

    for name, (slug, color, r, is_hub) in node_info.items():
        x, y = positions[name]
        data_uri = fetch_as_data_uri(f"https://skillicons.dev/icons?i={slug}")
        icon_size = r * 1.4
        if is_hub:
            glow_r0, glow_r1 = r + 6, r + 15
            parts.append(f'''  <circle cx="{x:.1f}" cy="{y:.1f}" r="{glow_r0}" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.6">
    <animate attributeName="r" values="{glow_r0};{glow_r1};{glow_r0}" dur="2.5s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.6;0;0.6" dur="2.5s" repeatCount="indefinite"/>
  </circle>''')
        parts.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#24283b" stroke="{color}" stroke-width="2"/>')
        parts.append(
            f'  <image x="{x - icon_size/2:.1f}" y="{y - icon_size/2:.1f}" '
            f'width="{icon_size:.1f}" height="{icon_size:.1f}" href="{data_uri}"/>'
        )

    # cluster labels
    label_offsets = {"Languages": (-40, -95), "Web": (-20, -95), "Runtime": (-45, 130), "Tools": (-25, 130)}
    for key, c in clusters.items():
        ccx, ccy = c["center"]
        dx, dy = label_offsets[key]
        parts.append(f'  <text x="{ccx+dx:.1f}" y="{ccy+dy:.1f}" font-family="Fira Code, Consolas, monospace" font-size="13" font-weight="bold" fill="#787c99">{key}</text>')

    parts.append('</svg>')
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    import os
    os.makedirs("assets", exist_ok=True)

    print("Fetching tech stack icons...")
    techstack_svg = build_techstack_svg()
    with open("assets/techstack-fadein-float.svg", "w") as f:
        f.write(techstack_svg)
    print("Saved assets/techstack-fadein-float.svg")

    print("Fetching Discord badge...")
    connect_svg = build_connect_svg()
    with open("assets/connect-pulse.svg", "w") as f:
        f.write(connect_svg)
    print("Saved assets/connect-pulse.svg")

    print("Building constellation graph with real icons...")
    constellation_svg = build_constellation_svg()
    with open("assets/techstack-constellation.svg", "w") as f:
        f.write(constellation_svg)
    print("Saved assets/techstack-constellation.svg")
