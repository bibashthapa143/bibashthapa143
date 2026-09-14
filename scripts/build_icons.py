def build_constellation_svg() -> str:
    # 1. Balanced 4-Cluster Definitions
    clusters = {
        "Languages": {
            "center": (200, 150),
            "hub": ("Python", "py", "#3776AB"),
            "members": [
                ("C", "c", "#5C6BC0"),
                ("C++", "cpp", "#00599C"),
                ("Java", "java", "#EA2D2E"),
            ],
        },
        "Web Stack": {
            "center": (620, 150),
            "hub": ("React", "react", "#61DAFB"),
            "members": [
                ("HTML5", "html", "#E34F26"),
                ("CSS3", "css", "#1572B6"),
                ("JavaScript", "js", "#F7DF1E"),
                ("TypeScript", "ts", "#3178C6"),
                ("Node.js", "nodejs", "#339933"),
                ("Next.js", "nextjs", "#c0caf5"),
                ("Postgres", "postgres", "#4169E1"),
            ],
        },
        "Cybersecurity": {
            "center": (200, 420),
            "hub": ("Kali", "kali", "#557C93"),
            "members": [
                ("Linux", "linux", "#FCC624"),
                ("BurpSuite", "burpsuite", "#FF6600"),
            ],
        },
        "Tools &amp; Infra": {
            "center": (620, 420),
            "hub": ("Git", "git", "#F05032"),
            "members": [
                ("VS Code", "vscode", "#007ACC"),
                ("GitHub", "github", "#c0caf5"),
                ("Figma", "figma", "#F24E1E"),
            ],
        },
    }

    W, H = 820, 560
    hub_r, member_r, member_radius = 24, 16, 85

    positions = {}
    node_info = {}
    intra_edges = []
    hub_names = {}

    # Calculate radial positions for each cluster member
    for key, c in clusters.items():
        ccx, ccy = c["center"]
        hub_name, hub_slug, hub_color = c["hub"]
        positions[hub_name] = (ccx, ccy)
        node_info[hub_name] = (hub_slug, hub_color, hub_r, True)
        hub_names[key] = hub_name

        n = len(c["members"])
        for i, (name, slug, color) in enumerate(c["members"]):
            # Distribute nodes evenly around the hub
            angle = (2 * math.pi * i / n) - (math.pi / 2)
            x = ccx + member_radius * math.cos(angle)
            y = ccy + member_radius * math.sin(angle)
            positions[name] = (x, y)
            node_info[name] = (slug, color, member_r, False)
            intra_edges.append((hub_name, name))

    # Curved bridges between major domain hubs
    # Format: (StartNode, EndNode, ControlPointX, ControlPointY)
    curved_bridges = [
        ("Python", "React", 410, 100),       # Top curve
        ("Python", "Kali", 120, 285),        # Left curve
        ("React", "Git", 700, 285),          # Right curve
        ("Kali", "Git", 410, 470),           # Bottom curve
        ("Python", "Git", 410, 285),         # Center diagonal bridge
    ]

    parts = [
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">',
        f'  <rect x="0" y="0" width="{W}" height="{H}" rx="16" fill="#1a1b27"/>',
    ]

    # Render cluster background ambient rings
    for key, c in clusters.items():
        ccx, ccy = c["center"]
        parts.append(f'  <circle cx="{ccx}" cy="{ccy}" r="{member_radius + 22}" fill="none" stroke="#24283b" stroke-width="1.5" stroke-dasharray="4 4"/>')
        parts.append(f'  <text x="{ccx}" y="{ccy - member_radius - 30}" font-family="Fira Code, Consolas, monospace" font-size="13" font-weight="bold" fill="#7aa2f7" text-anchor="middle">{key}</text>')

    # Render straight intra-cluster lines
    for a, b in intra_edges:
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        parts.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#414868" stroke-width="1.2" opacity="0.5"/>')

    # Render smooth curved bridges & pulse animations
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

    # Render Node Circles & Icons
    for name, (slug, color, r, is_hub) in node_info.items():
        x, y = positions[name]
        data_uri = fetch_as_data_uri(f"https://skillicons.dev/icons?i={slug}")
        icon_size = r * 1.3

        if is_hub:
            parts.append(f'''  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r+8}" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.6">
    <animate attributeName="r" values="{r+6};{r+14};{r+6}" dur="2.8s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.6;0.1;0.6" dur="2.8s" repeatCount="indefinite"/>
  </circle>''')

        # Node body
        parts.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#1a1b27" stroke="{color}" stroke-width="2"/>')
        # Icon image
        parts.append(f'  <image x="{x - icon_size/2:.1f}" y="{y - icon_size/2:.1f}" width="{icon_size:.1f}" height="{icon_size:.1f}" href="{data_uri}"/>')
        # Node text label
        label_y = y + r + 12
        parts.append(f'  <text x="{x:.1f}" y="{label_y:.1f}" font-family="Fira Code, Consolas, monospace" font-size="9.5" fill="#c0caf5" text-anchor="middle">{name}</text>')

    parts.append('</svg>')
    return "\n".join(parts) + "\n"
