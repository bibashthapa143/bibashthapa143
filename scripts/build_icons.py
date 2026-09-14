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
import requests

TECH_ICONS = [
    "c", "cpp", "java", "py", "html", "css", "ts", "js",
    "nodejs", "nextjs", "vercel", "windows", "git",
]

DISCORD_BADGE_URL = (
    "https://img.shields.io/badge/Discord-%237289DA.svg"
    "?style=for-the-badge&logo=discord&logoColor=white"
)


def fetch_as_data_uri(url: str) -> str:
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    b64 = base64.b64encode(resp.content).decode("utf-8")
    content_type = resp.headers.get("Content-Type", "image/svg+xml")
    return f"data:{content_type};base64,{b64}"


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
    data_uri = fetch_as_data_uri(DISCORD_BADGE_URL)
    return f'''<svg width="240" height="70" viewBox="0 0 240 70" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="19" width="200" height="32" rx="6" fill="none" stroke="#7289DA" stroke-width="2" opacity="0.7">
    <animate attributeName="width" values="200;230;200" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="height" values="32;46;32" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="x" values="20;5;20" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="y" values="19;12;19" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.7;0;0.7" dur="2s" repeatCount="indefinite"/>
  </rect>
  <image x="20" y="19" width="200" height="32" href="{data_uri}"/>
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
