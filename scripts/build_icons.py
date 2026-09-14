def build_constellation_svg() -> str:
    clusters = {
        "Languages": {
            "center": (190, 140),
            "hub": ("Python", "py", "#3776AB"),
            "members": [
                ("C", "c", "#5C6BC0"),
                ("C++", "cpp", "#00599C"),
                ("Java", "java", "#EA2D2E"),
            ],
        },
        "Web Stack": {
            "center": (610, 140),
            "hub": ("React", "react", "#61DAFB"),
            "members": [
                ("HTML", "html", "#E34F26"),
                ("CSS", "css", "#1572B6"),
                ("JS", "js", "#F7DF1E"),
                ("TS", "ts", "#3178C6"),
                ("Node", "nodejs", "#339933"),
                ("Next", "nextjs", "#c0caf5"),
                ("Postgres", "postgres", "#4169E1"),
            ],
        },
        "Cybersecurity": {
            "center": (190, 410),
            "hub": ("Kali", "kali", "#557C93"),
            "members": [
                ("Linux", "linux", "#FCC624"),
                ("BurpSuite", "burpsuite", "#FF6600"),  # Valid skillicon slug
            ],
        },
        "Tools &amp; Infra": {
            "center": (610, 410),
            "hub": ("Git", "git", "#F05032"),
            "members": [
                ("VSCode", "vscode", "#007ACC"),
                ("GitHub", "github", "#c0caf5"),
                ("Figma", "figma", "#F24E1E"),
            ],
        },
    }

    W, H = 800, 560
    hub_r, member_r, member_radius = 24, 17, 82

    positions = {}
    node_info = {}
    intra_edges = []
    hub_names = {}

    for key, c in clusters.items():
        ccx, ccy = c["center"]
        hub_name, hub_slug, hub_color = c["hub"]
        positions[hub_name] = (ccx, ccy)
        node_info[hub_name] = (hub_slug, hub_color, hub_r, True)
        hub_names[key] = hub_name

        n = len(c["members"])
        for i, (name, slug, color) in enumerate(c["members"]):
            # Angle offset ensures clean circular distribution
            angle = (2 * math.pi * i / n) - (math.pi / 2)
            x = ccx + member_radius * math.cos(angle)
            y = ccy + member_radius * math.sin(angle)
            positions[name] = (x, y)
            node_info[name] = (slug, color, member_r, False)
            intra_edges.append((hub_name, name))

    bridge_edges = [
        (hub_names["Languages"], hub_names["Cybersecurity"]),
        (hub_names["Languages"], hub_names["Web Stack"]),
        (hub_names["Tools &amp; Infra"], hub_names["Web Stack"]),
        (hub_names["Tools &amp; Infra"], hub_names["Cybersecurity"]),
    ]

    parts = [
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">',
        f'  <rect x="0" y="0" width="{W}" height="{H}" rx="16" fill="#1a1b27"/>',
    ]

    # Render intra-cluster connector lines
    for a, b in intra_edges:
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        parts.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#414868" stroke-width="1.2" opacity="0.45"/>')

    # Render bridge animated lines
    for i, (a, b) in enumerate(bridge_edges):
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        begin = round(i * 0.35, 2)
        parts.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#BB9AF7" stroke-width="1.5" opacity="0.6"/>')
        parts.append(f'''  <circle r="3" fill="#BB9AF7">
    <animateMotion dur="2.6s" begin="{begin}s" repeatCount="indefinite" path="M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}"/>
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.9;1" dur="2.6s" begin="{begin}s" repeatCount="indefinite"/>
  </circle>''')

    # Render Nodes & Labels
    for name, (slug, color, r, is_hub) in node_info.items():
        x, y = positions[name]
        data_uri = fetch_as_data_uri(f"https://skillicons.dev/icons?i={slug}")
        icon_size = r * 1.35

        if is_hub:
            glow_r0, glow_r1 = r + 6, r + 16
            parts.append(f'''  <circle cx="{x:.1f}" cy="{y:.1f}" r="{glow_r0}" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.6">
    <animate attributeName="r" values="{glow_r0};{glow_r1};{glow_r0}" dur="2.5s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.6;0;0.6" dur="2.5s" repeatCount="indefinite"/>
  </circle>''')

        # Node background and border
        parts.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#24283b" stroke="{color}" stroke-width="2"/>')
        
        # Embedded icon
        parts.append(
            f'  <image x="{x - icon_size/2:.1f}" y="{y - icon_size/2:.1f}" '
            f'width="{icon_size:.1f}" height="{icon_size:.1f}" href="{data_uri}"/>'
        )
        
        # Micro text label under node for better readability
        label_y = y + r + 12
        parts.append(f'  <text x="{x:.1f}" y="{label_y:.1f}" font-family="Fira Code, Consolas, monospace" font-size="10" fill="#a9b1d6" text-anchor="middle">{name}</text>')

    # Render Cluster Headers
    label_offsets = {
        "Languages": (-35, -105),
        "Web Stack": (-35, -105),
        "Cybersecurity": (-45, 135),
        "Tools &amp; Infra": (-45, 135),
    }
    for key, c in clusters.items():
        ccx, ccy = c["center"]
        dx, dy = label_offsets[key]
        parts.append(f'  <text x="{ccx+dx:.1f}" y="{ccy+dy:.1f}" font-family="Fira Code, Consolas, monospace" font-size="14" font-weight="bold" fill="#7aa2f7">{key}</text>')

    parts.append('</svg>')
    return "\n".join(parts) + "\n"
