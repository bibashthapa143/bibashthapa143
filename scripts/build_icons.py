def build_constellation_svg() -> str:
    # 1. Define groups with clean layout positions (X, Y)
    groups = [
        {
            "title": "LANGUAGES",
            "bounds": (30, 40, 180, 460),
            "items": [
                ("Python", "py", "#3776AB", (120, 110), True),
                ("C", "c", "#5C6BC0", (80, 210), False),
                ("C++", "cpp", "#00599C", (160, 210), False),
                ("Java", "java", "#EA2D2E", (120, 310), False),
            ],
            "connections": [("Python", "C"), ("Python", "C++"), ("Python", "Java")]
        },
        {
            "title": "WEB DEVELOPMENT",
            "bounds": (230, 40, 250, 460),
            "items": [
                ("React", "react", "#61DAFB", (355, 100), True),
                ("Next.js", "nextjs", "#c0caf5", (280, 190), False),
                ("TypeScript", "ts", "#3178C6", (430, 190), False),
                ("Node.js", "nodejs", "#339933", (280, 280), False),
                ("JavaScript", "js", "#F7DF1E", (430, 280), False),
                ("HTML/CSS", "html", "#E34F26", (305, 370), False),
                ("PostgreSQL", "postgres", "#4169E1", (405, 370), False),
            ],
            "connections": [
                ("React", "Next.js"), ("React", "TypeScript"),
                ("React", "Node.js"), ("React", "JavaScript"),
                ("Node.js", "HTML/CSS"), ("Node.js", "PostgreSQL")
            ]
        },
        {
            "title": "CYBERSECURITY",
            "bounds": (500, 40, 180, 215),
            "items": [
                ("Kali", "kali", "#557C93", (590, 110), True),
                ("Linux", "linux", "#FCC624", (540, 185), False),
                ("BurpSuite", "burpsuite", "#FF6600", (640, 185), False),
            ],
            "connections": [("Kali", "Linux"), ("Kali", "BurpSuite")]
        },
        {
            "title": "TOOLS &amp; INFRA",
            "bounds": (500, 285, 180, 215),
            "items": [
                ("Git", "git", "#F05032", (590, 350), True),
                ("VS Code", "vscode", "#007ACC", (540, 430), False),
                ("GitHub", "github", "#c0caf5", (640, 430), False),
            ],
            "connections": [("Git", "VS Code"), ("Git", "GitHub")]
        }
    ]

    # Horizontal pipeline bridges connecting categories
    cross_bridges = [
        ((120, 110), (355, 100)),  # Python -> React
        ((120, 310), (590, 110)),  # Java -> Kali
        ((355, 100), (590, 350)),  # React -> Git
        ((590, 110), (590, 350)),  # Kali -> Git
    ]

    W, H = 710, 520
    parts = [
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">',
        f'  <rect x="0" y="0" width="{W}" height="{H}" rx="16" fill="#1a1b27"/>',
    ]

    # Draw Category Group Cards
    for g in groups:
        gx, gy, gw, gh = g["bounds"]
        parts.append(f'  <rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="12" fill="#24283b" opacity="0.5" stroke="#414868" stroke-width="1"/>')
        parts.append(f'  <text x="{gx + gw/2:.1f}" y="{gy + 24}" font-family="Fira Code, monospace" font-size="11" font-weight="bold" fill="#7aa2f7" text-anchor="middle">{g["title"]}</text>')

    # Draw Inter-Group Pipeline Connections with Pulse Animations
    for i, ((x1, y1), (x2, y2)) in enumerate(cross_bridges):
        begin = round(i * 0.4, 2)
        parts.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#bb9af7" stroke-width="1.5" opacity="0.4" stroke-dasharray="4 4"/>')
        parts.append(f'''  <circle r="3" fill="#7dcfff">
    <animateMotion dur="3s" begin="{begin}s" repeatCount="indefinite" path="M {x1} {y1} L {x2} {y2}"/>
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.9;1" dur="3s" begin="{begin}s" repeatCount="indefinite"/>
  </circle>''')

    # Draw Node Connections & Nodes
    for g in groups:
        pos_dict = {item[0]: item[3] for item in g["items"]}
        
        # Intra-group lines
        for src, dst in g["connections"]:
            x1, y1 = pos_dict[src]
            x2, y2 = pos_dict[dst]
            parts.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#565f89" stroke-width="1.2" opacity="0.6"/>')

        # Nodes
        for name, slug, color, (x, y), is_hub in g["items"]:
            r = 20 if is_hub else 15
            icon_size = r * 1.3
            data_uri = fetch_as_data_uri(f"https://skillicons.dev/icons?i={slug}")

            if is_hub:
                parts.append(f'''  <circle cx="{x}" cy="{y}" r="{r+6}" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.5">
    <animate attributeName="r" values="{r+4};{r+10};{r+4}" dur="2.5s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.5;0;0.5" dur="2.5s" repeatCount="indefinite"/>
  </circle>''')

            parts.append(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="#1a1b27" stroke="{color}" stroke-width="2"/>')
            parts.append(f'  <image x="{x - icon_size/2:.1f}" y="{y - icon_size/2:.1f}" width="{icon_size:.1f}" height="{icon_size:.1f}" href="{data_uri}"/>')
            parts.append(f'  <text x="{x}" y="{y + r + 11}" font-family="Fira Code, monospace" font-size="9" fill="#c0caf5" text-anchor="middle">{name}</text>')

    parts.append('</svg>')
    return "\n".join(parts) + "\n"
