import base64
import html
import math
import os
import re
import requests

# Tech icons for the simple floating header row
TECH_ICONS = [
    "c", "cpp", "java", "py", "html", "css", "ts", "js",
    "nodejs", "nextjs", "vercel", "windows", "git",
]

DISCORD_BADGE_URL = (
    "https://img.shields.io/badge/Discord-%237289DA.svg"
    "?style=for-the-badge&logo=discord&logoColor=white"
)


# --- Utility Functions ---

def fetch(url: str) -> bytes | None:
    """Fetch bytes, or None if it fails / returns a non-image."""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        if len(resp.content) < 100:
            print(f"Warning: suspiciously small response from {url}")
            return None
        return resp.content
    except requests.exceptions.RequestException as e:
        print(f"Warning: Failed to fetch {url}: {e}")
        return None


def to_data_uri(content: bytes, content_type: str = "image/svg+xml") -> str:
    b64 = base64.b64encode(content).decode("utf-8")
    return html.escape(f"data:{content_type};base64,{b64}")


def fetch_as_data_uri(url: str) -> str | None:
    content = fetch(url)
    return to_data_uri(content) if content else None


def get_svg_dimensions(svg_bytes: bytes) -> tuple[float, float]:
    text = svg_bytes.decode("utf-8", errors="ignore")
    w_match = re.search(r'width="([\d.]+)"', text)
    h_match = re.search(r'height="([\d.]+)"', text)
    if w_match and h_match:
        return float(w_match.group(1)), float(h_match.group(1))
    vb_match = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', text)
    if vb_match:
        return float(vb_match.group(1)), float(vb_match.group(2))
    return 200.0, 32.0


def render_node_glyph(slug: str, label: str, color: str, x: float, y: float, size: float) -> str:
    """Real icon if skillicons has it; otherwise a clean colored text badge
    in the tool's brand color (never a blank grey blob)."""
    data_uri = fetch_as_data_uri(f"https://skillicons.dev/icons?i={slug}") if slug else None
    if data_uri:
        return (
            f'  <image x="{x - size/2:.1f}" y="{y - size/2:.1f}" '
            f'width="{size:.1f}" height="{size:.1f}" href="{data_uri}"/>'
        )
    fs = size * 0.42
    return (
        f'  <text x="{x:.1f}" y="{y + fs/3:.1f}" font-size="{fs:.1f}" font-weight="bold" '
        f'fill="{color}" text-anchor="middle" '
        f'font-family="Fira Code, Consolas, monospace">{label}</text>'
    )


# --- SVG Builders ---

def build_techstack_svg() -> str:
    icon_size, gap, x = 40, 14, 10
    parts = []
    for i, icon in enumerate(TECH_ICONS):
        data_uri = fetch_as_data_uri(f"https://skillicons.dev/icons?i={icon}")
        if not data_uri:
            continue
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
    if not raw:
        raise RuntimeError("Could not fetch Discord badge")
    natural_w, natural_h = get_svg_dimensions(raw)
    data_uri = to_data_uri(raw)

    target_h = 32
    scale = target_h / natural_h
    img_w, img_h = natural_w * scale, target_h

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
    """Clustered network graph. Entry format:
    (display name, skillicons slug, brand color, short fallback label)"""
    clusters = {
        "Languages": {
            "center": (200, 160),
            "hub": ("Python", "py", "#3776AB", "Py"),
            "members": [
                ("C", "c", "#5C6BC0", "C"),
                ("C++", "cpp", "#00599C", "C+"),
                ("Java", "java", "#EA2D2E", "Jv"),
            ],
        },
        "Web Stack": {
            "center": (620, 160),
            "hub": ("JavaScript", "js", "#F7DF1E", "JS"),
            "members": [
                ("HTML5", "html", "#E34F26", "H5"),
                ("CSS3", "css", "#1572B6", "C3"),
                ("TypeScript", "ts", "#3178C6", "TS"),
                ("Node.js", "nodejs", "#339933", "Nd"),
                ("Next.js", "nextjs", "#c0caf5", "Nx"),
                ("Vercel", "vercel", "#c0caf5", "Vc"),
            ],
        },
        "Cybersecurity &amp; Labs": {
            "center": (200, 440),
            "hub": ("Kali Linux", "kali", "#557C93", "Kali"),
            "members": [
                ("Linux", "linux", "#FCC624", "Lx"),
                ("Nmap", "nmap", "#4FA92C", "Nmap"),
            ],
        },
        "Tools &amp; Infra": {
            "center": (620, 440),
            "hub": ("Git", "git", "#F05032", "Git"),
            "members": [
                ("GitHub", "github", "#c0caf5", "GH"),
                ("VS Code", "vscode", "#007ACC", "VS"),
                ("Figma", "figma", "#F24E1E", "Fg"),
                ("VMware", "vmware", "#60B2E5", "VM"),
                ("Windows", "windows", "#00A4EF", "Win"),
            ],
        },
    }

    W, H = 820, 600
    hub_r, member_r, member_radius = 24, 16, 88

    positions, node_info, intra_edges, hub_names = {}, {}, [], {}

    for key, c in clusters.items():
        ccx, ccy = c["center"]
        hub_name, hub_slug, hub_color, hub_label = c["hub"]
        positions[hub_name] = (ccx, ccy)
        node_info[hub_name] = (hub_slug, hub_color, hub_label, hub_r, True)
        hub_names[key] = hub_name

        n = max(len(c["members"]), 1)
        for i, (name, slug, color, label) in enumerate(c["members"]):
            angle = (2 * math.pi * i / n) - (math.pi / 2)
            x = ccx + member_radius * math.cos(angle)
            y = ccy + member_radius * math.sin(angle)
            positions[name] = (x, y)
            node_info[name] = (slug, color, label, member_r, False)
            intra_edges.append((hub_name, name))

    curved_bridges = [
        ("Python", "JavaScript", 410, 105),
        ("Python", "Kali Linux", 118, 300),
        ("JavaScript", "Git", 702, 300),
        ("Kali Linux", "Git", 410, 495),
        ("Python", "Git", 410, 300),
    ]

    parts = [
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">',
        f'  <rect x="0" y="0" width="{W}" height="{H}" rx="16" fill="#1a1b27"/>',
    ]

    for key, c in clusters.items():
        ccx, ccy = c["center"]
        parts.append(f'  <circle cx="{ccx}" cy="{ccy}" r="{member_radius + 26}" fill="none" stroke="#24283b" stroke-width="1.5" stroke-dasharray="4 4"/>')
        parts.append(f'  <text x="{ccx}" y="{ccy - member_radius - 36}" font-family="Fira Code, Consolas, monospace" font-size="13" font-weight="bold" fill="#7aa2f7" text-anchor="middle">{key}</text>')

    for a, b in intra_edges:
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        parts.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#414868" stroke-width="1.2" opacity="0.5"/>')

    for i, (src, dst, cx, cy) in enumerate(curved_bridges):
        x1, y1 = positions[src]
        x2, y2 = positions[dst]
        path_d = f"M {x1:.1f} {y1:.1f} Q {cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}"
        begin = round(i * 0.4, 2)
        parts.append(f'  <path d="{path_d}" fill="none" stroke="#bb9af7" stroke-width="1.5" opacity="0.45" stroke-dasharray="5 5"/>')
        parts.append(f'''  <circle r="3.5" fill="#7dcfff">
    <animateMotion dur="3s" begin="{begin}s" repeatCount="indefinite" path="{path_d}"/>
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.9;1" dur="3s" begin="{begin}s" repeatCount="indefinite"/>
  </circle>''')

    for name, (slug, color, label, r, is_hub) in node_info.items():
        x, y = positions[name]
        icon_size = r * 1.3
        if is_hub:
            g0, g1 = r + 6, r + 14
            parts.append(f'''  <circle cx="{x:.1f}" cy="{y:.1f}" r="{g0}" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.6">
    <animate attributeName="r" values="{g0};{g1};{g0}" dur="2.8s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.6;0.1;0.6" dur="2.8s" repeatCount="indefinite"/>
  </circle>''')
        parts.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#1a1b27" stroke="{color}" stroke-width="2"/>')
        parts.append(render_node_glyph(slug, label, color, x, y, icon_size))
        parts.append(f'  <text x="{x:.1f}" y="{y + r + 13:.1f}" font-family="Fira Code, Consolas, monospace" font-size="9.5" fill="#c0caf5" text-anchor="middle">{name}</text>')

    parts.append('</svg>')
    return "\n".join(parts) + "\n"


# --- Main ---

if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)

    print("Building floating tech stack row...")
    with open("assets/techstack-fadein-float.svg", "w", encoding="utf-8") as f:
        f.write(build_techstack_svg())
    print("Saved assets/techstack-fadein-float.svg")

    print("Building Discord connect badge...")
    with open("assets/connect-pulse.svg", "w", encoding="utf-8") as f:
        f.write(build_connect_svg())
    print("Saved assets/connect-pulse.svg")

    print("Building clustered constellation graph...")
    with open("assets/techstack-constellation.svg", "w", encoding="utf-8") as f:
        f.write(build_constellation_svg())
    print("Saved assets/techstack-constellation.svg")
