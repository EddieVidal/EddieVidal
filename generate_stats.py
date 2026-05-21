import os, json, math, urllib.request

USERNAME = 'EddieVidal'
TOKEN    = os.environ.get('GITHUB_TOKEN', '')

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

LANG_COLORS = {
    'Python':'#3572A5','JavaScript':'#f1e05a','HTML':'#e34c26','CSS':'#563d7c',
    'TypeScript':'#2b7489','Jupyter Notebook':'#DA5B0B','Shell':'#89e051',
    'Java':'#b07219','C++':'#f34b7d','C':'#555555','Ruby':'#701516',
    'Go':'#00ADD8','PHP':'#4F5D95','Rust':'#dea584','Swift':'#F05138',
    'Kotlin':'#A97BFF','Dart':'#00B4AB','Vue':'#41b883','SCSS':'#c6538c',
    'PowerShell':'#012456','Batchfile':'#C1F12E',
}

# ── Cores (tema TokyoNight) ──────────────────────────────────────────────────
BG      = '#1a1b27'
BORDER  = '#2d2d44'
TITLE   = '#70a5fd'
TEXT    = '#a9b1d6'
ICON    = '#bf91f3'
VAL     = '#e0def4'
RING    = '#70a5fd'
# ────────────────────────────────────────────────────────────────────────────

def fetch(url, accept=None):
    req = urllib.request.Request(url, headers=HEADERS)
    if accept:
        req.add_header('Accept', accept)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def calc_grade(stars, commits, prs, issues, followers):
    s = commits*0.1 + prs*0.5 + stars*0.5 + issues*0.25 + followers*0.45
    for thr, grade, pct in [(200,'S',100),(100,'A+',90),(60,'A',80),
                              (40,'B+',70),(20,'B',60),(10,'C',45)]:
        if s >= thr: return grade, pct
    return 'C-', 30

def donut(cx, cy, r, pct):
    circ = 2 * math.pi * r
    dash = (pct / 100) * circ
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
            f'stroke="{BORDER}" stroke-width="6"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
            f'stroke="{RING}" stroke-width="6" stroke-linecap="round" '
            f'stroke-dasharray="{dash:.1f} {circ:.1f}" '
            f'transform="rotate(-90 {cx} {cy})"/>')

ICON_SVG = {
    'star':   'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z',
    'commit': 'M9 12a3 3 0 1 0 6 0 3 3 0 0 0-6 0M3 12h6M15 12h6',
    'pr':     'M18 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6M6 3a3 3 0 1 0 0 6 3 3 0 0 0 0-6M13 6h2a2 2 0 0 1 2 2v8M6 9v12',
    'issue':  'M12 22c5.52 0 10-4.48 10-10S17.52 2 12 2 2 6.48 2 12s4.48 10 10 10M12 8v4M12 16h.01',
    'repo':   'M3 3h18v18H3zM3 9h18M9 21V9',
}

def icon_svg(name, x, y, size=13):
    path = ICON_SVG[name]
    scale = size / 24
    return (f'<g transform="translate({x},{y-size+1}) scale({scale:.4f})">'
            f'<path d="{path}" fill="none" stroke="{ICON}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round"/></g>')

def fmt(n): return f'{n:,}'.replace(',','.')

def generate_stats(user, repos, prs, issues, commits):
    stars    = sum(r.get('stargazers_count',0) for r in repos)
    contribs = sum(1 for r in repos if not r.get('fork'))
    followers = user.get('followers', 0)
    name      = (user.get('name') or USERNAME)[:28]

    grade, pct = calc_grade(stars, commits, prs, issues, followers)
    W, H = 495, 195
    cx, cy, rad = 430, 115, 40

    rows = [
        ('star',   'Total de estrelas:',             stars),
        ('commit', 'Total de commits:',               commits),
        ('pr',     'Total de PRs:',                   prs),
        ('issue',  'Total de issues:',                issues),
        ('repo',   'Contribuiu para (ano passado):',  contribs),
    ]

    rows_svg = ''
    for i, (ico, label, val) in enumerate(rows):
        y = 80 + i * 24
        rows_svg += (icon_svg(ico, 25, y) +
            f'<text x="45" y="{y}" font-size="12" fill="{TEXT}" font-family="Segoe UI,sans-serif">{label}</text>'
            f'<text x="340" y="{y}" font-size="12" fill="{VAL}" font-weight="bold" '
            f'font-family="Segoe UI,sans-serif" text-anchor="end">{fmt(val)}</text>')

    return f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
  <text x="25" y="45" font-size="14" font-weight="bold" fill="{TITLE}" font-family="Segoe UI,sans-serif">Estatísticas do GitHub de {name}</text>
  {rows_svg}
  {donut(cx, cy, rad, pct)}
  <text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" font-size="19" font-weight="bold" fill="{VAL}" font-family="Segoe UI,sans-serif">{grade}</text>
</svg>'''

def generate_langs(repos):
    lm = {}
    for r in repos:
        lang = r.get('language')
        if lang:
            lm[lang] = lm.get(lang, 0) + 1

    total = sum(lm.values())
    if not total:
        return None

    sorted_langs = sorted(lm.items(), key=lambda x: -x[1])[:8]
    W, H = 320, 195
    bx, by, bw, bh = 20, 70, 280, 8

    segs = ''
    x = bx
    for lang, cnt in sorted_langs:
        w = (cnt / total) * bw
        color = LANG_COLORS.get(lang, '#888888')
        segs += f'<rect x="{x:.2f}" y="{by}" width="{w:.2f}" height="{bh}" fill="{color}"/>'
        x += w

    leg = ''
    for i, (lang, cnt) in enumerate(sorted_langs):
        col = i % 2
        row = i // 2
        lx = 20 + col * 148
        ly = 103 + row * 22
        color = LANG_COLORS.get(lang, '#888888')
        pct   = (cnt / total) * 100
        label = lang[:14]
        leg += (f'<circle cx="{lx+5}" cy="{ly-4}" r="4" fill="{color}"/>'
                f'<text x="{lx+14}" y="{ly}" font-size="11" fill="{TEXT}" font-family="Segoe UI,sans-serif">{label}</text>'
                f'<text x="{lx+143}" y="{ly}" font-size="11" fill="{VAL}" font-weight="bold" '
                f'font-family="Segoe UI,sans-serif" text-anchor="end">{pct:.2f}%</text>')

    return f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
  <defs><clipPath id="bc"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="4"/></clipPath></defs>
  <rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
  <text x="20" y="48" font-size="14" font-weight="bold" fill="{TITLE}" font-family="Segoe UI,sans-serif">Tecnologias</text>
  <g clip-path="url(#bc)">{segs}</g>
  {leg}
</svg>'''

# ── Main ─────────────────────────────────────────────────────────────────────
print(f'Buscando dados de @{USERNAME}...')
user  = fetch(f'https://api.github.com/users/{USERNAME}')
repos = fetch(f'https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated')

prs = issues = commits = 0
try:
    prs     = fetch(f'https://api.github.com/search/issues?q=type:pr+author:{USERNAME}&per_page=1').get('total_count',0)
    issues  = fetch(f'https://api.github.com/search/issues?q=type:issue+author:{USERNAME}&per_page=1').get('total_count',0)
    commits = fetch(f'https://api.github.com/search/commits?q=author:{USERNAME}&per_page=1',
                    accept='application/vnd.github.cloak-preview').get('total_count',0)
except Exception as e:
    print(f'Aviso (search API): {e}')

with open('github_stats_card.svg','w',encoding='utf-8') as f:
    f.write(generate_stats(user, repos, prs, issues, commits))
print('✓ github_stats_card.svg')

langs_svg = generate_langs(repos)
if langs_svg:
    with open('github_langs_card.svg','w',encoding='utf-8') as f:
        f.write(langs_svg)
    print('✓ github_langs_card.svg')

print('Concluído!')
