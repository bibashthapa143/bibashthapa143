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
