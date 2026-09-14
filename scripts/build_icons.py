def build_constellation_svg() -> str:
    # Card-based Matrix Layout Definitions
    cards = [
        {
            "title": "LANGUAGES",
            "accent": "#7aa2f7",
            "rect": (30, 40, 360, 220),
            "hub": ("Python", "py", "#3776AB", (110, 110)),
            "nodes": [
                ("C", "c", "#5C6BC0", (220, 110)),
                ("C++", "cpp", "#00599C", (310, 110)),
                ("Java", "java", "#EA2D2E", (110, 190)),
                ("JavaScript", "js", "#F7DF1E", (220, 190)),
            ],
            "links": [("Python", "C"), ("C", "C++"), ("Python", "Java"), ("Python", "JavaScript")]
        },
        {
            "title": "WEB STACK",
            "accent": "#73daca",
            "rect": (430, 40, 360, 220),
            "hub": ("React", "react", "#61DAFB", (510, 110)),
            "nodes": [
                ("TypeScript", "ts", "#3178C6", (610, 110)),
                ("Next.js", "nextjs", "#c0caf5", (710, 110)),
                ("Node.js", "nodejs", "#339933", (510, 190)),
                ("HTML/CSS", "html", "#E34F26", (610, 190)),
                ("PostgreSQL", "postgres", "#4169E1", (710, 190)),
            ],
            "links": [("React", "TypeScript"), ("TypeScript", "Next.js"), ("React", "Node.js"), ("Node.js", "HTML/CSS"), ("Node.js", "PostgreSQL")]
        },
        {
            "title": "CYBERSECURITY",
            "accent": "#f7768e",
            "rect": (30, 290, 360, 220),
            "hub": ("Kali Linux", "kali", "#557C93", (110, 360)),
            "nodes": [
                ("Linux", "linux", "#FCC624", (220, 360)),
                ("Burp Suite", "burpsuite", "#FF6600", (310, 360)),
                ("Bash", "bash", "#4EAA25", (110, 440)),
            ],
            "links": [("Kali Linux", "Linux"), ("Linux", "Burp Suite"), ("Kali Linux", "Bash")]
        },
        {
            "title": "TOOLS &amp; INFRA",
            "accent": "#bb9af7",
            "rect": (430, 290, 360, 220),
            "hub": ("Git", "git", "#F05032", (510, 360)),
            "nodes": [
                ("VS Code", "vscode", "#007ACC", (610, 360)),
                ("GitHub", "github", "#c0caf5", (710, 360)),
                ("Figma", "figma", "#F24E1E", (510, 440)),
            ],
            "links": [("Git", "VS Code"), ("VS Code", "GitHub"), ("Git", "Figma")]
        }
    ]

    # Inter-card Cross Bridges (Source Pos, Target Pos)
    matrix_bridges = [
        ((310, 110), (510, 110)),  # Languages -> Web
        ((110, 190), (110, 360)),  # Languages -> Security
        ((710, 190), (710, 360)),  # Web -> Tools
        ((310, 360), (510, 360)),  # Security -> Tools
    ]

    W, H = 820, 540
    parts = [
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">',
        f'  <rect x="0" y="0" width="{W}" height="{H}" rx="16" fill="#1a1b27"/>',
    ]

    # 1. Render Matrix Cards & Accent Headers
    for c in cards:
        cx, cy, cw, ch = c["rect"]
        parts.append(f'  <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="12" fill="#24283b" opacity="0.4" stroke="#414868" stroke-width="1"/>')
        parts.append(f'  <path d="M {cx+12} {cy} L {cx+cw-12} {cy}" stroke="{c["accent"]}" stroke-width="3" stroke-linecap="round"/>')
        parts.append(f'  <text x="{cx+20}" y="{cy+25}" font-family="Fira Code, Consolas, monospace" font-size="12" font-weight="bold" fill="{c["accent"]}">{c["title"]}</text>')

    # 2. Render Cross-Matrix Bridges with Pulse Animation
    for i, ((x1, y1), (x2, y2)) in enumerate(matrix_bridges):
        begin = round(i * 0.45, 2)
        parts.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#bb9af7" stroke-width="1.5" opacity="0.35" stroke-dasharray="4 4"/>')
        parts.append(f'''  <circle r="3.5" fill="#7dcfff">
    <animateMotion dur="2.8s" begin="{begin}s" repeatCount="indefinite" path="M {x1} {y1} L {x2} {y2}"/>
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.9;1" dur="2.8s" begin="{begin}s" repeatCount="indefinite"/>
  </circle>''')

    # 3. Render Card Intra-Links & Skill Nodes
    for c in cards:
        all_nodes = [c["hub"]] + c["nodes"]
        pos_map = {item[0]: item[3] for item in all_nodes}

        # Draw local connectors
        for src, dst in c["links"]:
            x1, y1 = pos_map[src]
            x2, y2 = pos_map[dst]
            parts.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#414868" stroke-width="1.2" opacity="0.6"/>')

        # Draw nodes
        for item in all_nodes:
            name, slug, color, (x, y) = item[0], item[1], item[2], item[3]
            is_hub = (name == c["hub"][0])
            r = 18 if is_hub else 14
            icon_size = r * 1.35
            data_uri = fetch_as_data_uri(f"https://skillicons.dev/icons?i={slug}")

            if is_hub:
                parts.append(f'''  <circle cx="{x}" cy="{y}" r="{r+6}" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.5">
    <animate attributeName="r" values="{r+4};{r+10};{r+4}" dur="2.5s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.5;0;0.5" dur="2.5s" repeatCount="indefinite"/>
  </circle>''')

            parts.append(f'  <rect x="{x-r}" y="{y-r}" width="{r*2}" height="{r*2}" rx="6" fill="#1a1b27" stroke="{color}" stroke-width="2"/>')
            parts.append(f'  <image x="{x - icon_size/2:.1f}" y="{y - icon_size/2:.1f}" width="{icon_size:.1f}" height="{icon_size:.1f}" href="{data_uri}"/>')
            parts.append(f'  <text x="{x}" y="{y + r + 12}" font-family="Fira Code, Consolas, monospace" font-size="9" fill="#c0caf5" text-anchor="middle">{name}</text>')

    parts.append('</svg>')
    return "\n".join(parts) + "\n"
