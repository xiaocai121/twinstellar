#!/usr/bin/env python3
"""
Twinstellar · P1 构建脚本
解析 index.html 中的 TWIN_COMBOS / ELEMENTS / ZODIAC，
生成 60 个长尾 SEO 落地页 (combo/<slug>.html) + 宇宙签名墙 (combo/index.html) + 共享样式 combo/combo.css。
纯静态、零后端；生成结果提交进仓库，由 GitHub Pages 直接托管。
"""
import os
import re
import json
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(ROOT, "index.html")
OUT = os.path.join(ROOT, "combo")
SITE = "https://twinstellar.com"

# ---------- 1. 用 node 安全解析 JS 常量 ----------
node_src = r'''
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
function grab(name, openCh, closeCh){
  const re = new RegExp('(?:const\\s+|window\\.)' + name + '\\s*=\\s*');
  const m = html.match(re);
  if (!m) return null;
  const eqEnd = m.index + m[0].length;        // position right after the '='
  const start = html.indexOf(openCh, eqEnd);   // opening bracket
  if (start < 0) return null;
  let depth = 0;
  let i = start;
  for (; i < html.length; i++){
    const ch = html[i];
    if (ch === openCh) depth++;
    else if (ch === closeCh){ depth--; if (depth === 0){ i++; break; } }
  }
  const text = html.slice(start, i);
  try { return JSON.stringify(eval('(' + text + ')')); }
  catch (e) { return null; }
}
process.stdout.write(JSON.stringify({
  combos: grab('TWIN_COMBOS', '[', ']'),
  elements: grab('ELEMENTS', '{', '}'),
  zodiac: grab('ZODIAC', '{', '}'),
}));
'''
tmp = os.path.join(ROOT, ".extract.js")
with open(tmp, "w", encoding="utf-8") as f:
    f.write(node_src)
try:
    res = subprocess.run(["node", tmp, HTML], capture_output=True, text=True, check=True)
    data = json.loads(res.stdout)
finally:
    if os.path.exists(tmp):
        os.remove(tmp)

combos = json.loads(data["combos"])
elements = json.loads(data["elements"])
zodiac = json.loads(data["zodiac"])

# ---------- helpers ----------
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def rich(s):
    """escape HTML, then **bold** -> <strong>"""
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return s

def slug_of(c):
    return f"{c['element'].lower()}-{c['zodiac'].lower()}"

def find_combo(element, zodiac):
    for c in combos:
        if c["element"].lower() == element.lower() and c["zodiac"].lower() == zodiac.lower():
            return c
    return None

os.makedirs(OUT, exist_ok=True)

# ---------- 2. 组合页模板 ----------
COMBO_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_en} Cosmic Signature Meaning · Twinstellar</title>
<meta name="description" content="{desc_en}">
<meta property="og:title" content="{title_en} Cosmic Signature · Twinstellar">
<meta property="og:description" content="{desc_en}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{canonical}">
<link rel="stylesheet" href="combo.css">
</head>
<body>
<main class="combo-page">
  <a class="back" href="{site}/">&larr; Twinstellar</a>
  <header class="combo-head">
    <p class="eyebrow">Five Elements &times; Zodiac</p>
    <h1>{title_en}<br><span class="cn">「{title_cn}」</span></h1>
    <p class="sig-meta">{el_symbol} {el_cn} &middot; {zk_symbol} {zk_cn}</p>
  </header>

  <section class="pair">
    <div class="pair-card">
      <h2>Your Element &middot; {el_name}</h2>
      <p class="big-sym">{el_symbol}</p>
      <p>{el_key}</p>
      <p class="cn">{el_key_cn}</p>
    </div>
    <div class="pair-card">
      <h2>Your Zodiac &middot; {zk_name}</h2>
      <p class="big-sym">{zk_symbol}</p>
      <p>{zk_arche}</p>
      <p class="cn">{zk_arche_cn}</p>
    </div>
  </section>

  <section class="fusion">
    <h2>The Fusion</h2>
    <p class="en">{fusion_en}</p>
    <p class="cn">{fusion_cn}</p>
  </section>

  <section class="mantra">
    <h2>Mantra</h2>
    <p class="en">&ldquo;{mantra_en}&rdquo;</p>
    <p class="cn">「{mantra_cn}」</p>
  </section>

  <section class="stones">
    <h2>Power Stones</h2>
    <ul class="stone-list">{stones_li}</ul>
    <p class="src">Source numbers: {source_numbers}</p>
  </section>

  <section class="related">
    <h2>Explore more signatures</h2>
    <ul class="rel-list">{related_li}</ul>
  </section>

  <section class="cta">
    <a class="btn" href="{site}/?e={element}&z={zodiac}">Reveal your own cosmic signature &rarr;</a>
    <button class="btn-ghost" id="copyBtn" type="button">Copy my universe link</button>
  </section>
</main>
<script>
(function(){{
  try {{ var p = new URLSearchParams(location.search).get('ref'); if (p) localStorage.setItem('twin_ref', p); }} catch(e){{}}
  var btn = document.getElementById('copyBtn');
  if (btn) btn.onclick = function() {{
    var ref = ''; try {{ ref = localStorage.getItem('twin_ref'); }} catch(e){{}}
    var url = '{site}/?e={element}&z={zodiac}' + (ref ? '&ref=' + encodeURIComponent(ref) : '');
    if (navigator.share) {{ navigator.share({{ title: 'Twinstellar', text: 'My cosmic signature', url: url }}).catch(function(){{}}); return; }}
    if (navigator.clipboard) navigator.clipboard.writeText(url).then(function(){{ btn.textContent = 'Link copied ✓'; setTimeout(function(){{ btn.textContent = 'Copy my universe link'; }}, 2000); }});
  }};
}})();
</script>
</body>
</html>
"""

# 预计算同元素/同星座的关联组合
by_element = {}
by_zodiac = {}
for c in combos:
    by_element.setdefault(c["element"], []).append(c)
    by_zodiac.setdefault(c["zodiac"], []).append(c)

count = 0
for c in combos:
    el = elements[c["element"].lower()]
    zk = zodiac[c["zodiac"].lower()]
    s = slug_of(c)
    desc_en = (
        f"Discover the {c['title_en']} cosmic signature — where {c['element']} meets {c['zodiac']}. "
        f"{c['mantra_en']} Explore your Five Elements × Zodiac reading on Twinstellar."
    )
    # related: interleave same-element + same-zodiac (excluding self), dedupe, cap 6
    el_list = [x for x in by_element[c["element"]] if x is not c]
    zk_list = [x for x in by_zodiac[c["zodiac"]] if x is not c]
    rel = []
    for i in range(max(len(el_list), len(zk_list))):
        if i < len(el_list):
            rel.append(el_list[i])
        if i < len(zk_list):
            rel.append(zk_list[i])
    seen = set()
    rel_unique = []
    for x in rel:
        k = slug_of(x)
        if k not in seen:
            seen.add(k)
            rel_unique.append(x)
    rel_unique = rel_unique[:6]
    rel_li = "".join(
        f'<li><a href="{slug_of(x)}.html">{x["title_en"]} '
        f'<span class="cn">「{esc(x["title_cn"])}」</span></a></li>'
        for x in rel_unique
    )
    stones_li = "".join(f"<li>{esc(st)}</li>" for st in c["stones"])
    html = COMBO_TPL.format(
        title_en=esc(c["title_en"]),
        title_cn=esc(c["title_cn"]),
        desc_en=esc(desc_en),
        canonical=f"{SITE}/combo/{s}.html",
        site=SITE,
        el_symbol=el["symbol"], el_cn=esc(el["cn"]), el_name=esc(el["name"]),
        el_key=esc(el["key"]), el_key_cn=esc(el["key_cn"]),
        zk_symbol=zk["symbol"], zk_cn=esc(zk["cn"]), zk_name=esc(zk["name"]),
        zk_arche=esc(zk["arche"]), zk_arche_cn=esc(zk["arche_cn"]),
        fusion_en=rich(c["fusion"]), fusion_cn=rich(c["fusion_cn"]),
        mantra_en=esc(c["mantra_en"]), mantra_cn=esc(c["mantra_cn"]),
        stones_li=stones_li, source_numbers=esc(c["source_numbers"]),
        related_li=rel_li,
        element=esc(c["element"]), zodiac=esc(c["zodiac"]),
    )
    with open(os.path.join(OUT, f"{s}.html"), "w", encoding="utf-8") as f:
        f.write(html)
    count += 1

# ---------- 3. 签名墙 ----------
cards = []
for c in combos:
    el = elements[c["element"].lower()]
    zk = zodiac[c["zodiac"].lower()]
    cards.append(
        f'<a class="sig-card" href="{slug_of(c)}.html" style="--el:{el["color"]}">'
        f'<span class="sig-sym">{el["symbol"]}{zk["symbol"]}</span>'
        f'<span class="sig-en">{esc(c["title_en"])}</span>'
        f'<span class="sig-cn">{esc(c["title_cn"])}</span>'
        f'<span class="sig-z">{zk["cn"]}</span>'
        f"</a>"
    )
wall = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Cosmic Signature Wall · Twinstellar</title>
<meta name="description" content="All 60 cosmic signatures — where the Five Elements meet the Zodiac. Find yours and share it with a kindred spirit.">
<meta property="og:title" content="The Cosmic Signature Wall · Twinstellar">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE}/combo/">
<link rel="stylesheet" href="combo.css">
</head>
<body>
<main class="wall">
  <a class="back" href="{SITE}/">&larr; Twinstellar</a>
  <header class="wall-head">
    <p class="eyebrow">Five Elements &times; Zodiac</p>
    <h1>The Cosmic Signature Wall</h1>
    <p class="sub">All 60 signatures — each a living union of your Element and Zodiac. Find yours, then reveal your own.</p>
    <a class="btn" href="{SITE}/">Reveal my cosmic signature &rarr;</a>
  </header>
  <section class="wall-grid">
    {''.join(cards)}
  </section>
  <footer class="wall-foot">Twinstellar &middot; Two Beads. One Universe.</footer>
</main>
</body>
</html>
"""
with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(wall)

# ---------- 4. 共享样式 ----------
CSS = """* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  color: #ECECF1; background: #0B0B11; background-image:
    radial-gradient(1200px 600px at 50% -10%, rgba(201,162,95,0.12), transparent 60%),
    radial-gradient(900px 500px at 80% 20%, rgba(79,134,198,0.10), transparent 60%);
  min-height: 100vh; line-height: 1.6;
}
a { color: #C9A962; text-decoration: none; }
.back { display: inline-block; margin: 22px 0 0 22px; color: #9a9aa6; font-size: 13px; letter-spacing: .04em; }
.back:hover { color: #C9A962; }
.eyebrow { text-transform: uppercase; letter-spacing: .22em; font-size: 12px; color: #C9A962; margin: 0 0 10px; }

/* ---- combo page ---- */
.combo-page { max-width: 720px; margin: 0 auto; padding: 10px 22px 64px; }
.combo-head { text-align: center; padding: 18px 0 8px; }
.combo-head h1 { font-family: Georgia, "Times New Roman", serif; font-size: 40px; line-height: 1.15; margin: 6px 0 10px; }
.combo-head h1 .cn { color: #C9A962; font-size: 26px; }
.sig-meta { color: #b9b9c6; letter-spacing: .08em; margin: 0; }
.pair { display: flex; gap: 16px; margin: 26px 0; }
.pair-card { flex: 1; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 18px; text-align: center; backdrop-filter: blur(8px); }
.pair-card h2 { font-size: 14px; letter-spacing: .04em; color: #C9A962; margin: 0 0 8px; font-weight: 600; }
.big-sym { font-size: 34px; margin: 4px 0; }
.pair-card p { margin: 2px 0; color: #d7d7e0; }
.pair-card .cn { color: #9a9aa6; font-size: 13px; }
.fusion, .mantra, .stones, .related, .cta { margin: 30px 0; }
.fusion h2, .mantra h2, .stones h2, .related h2 { font-size: 15px; letter-spacing: .14em; text-transform: uppercase; color: #C9A962; border-bottom: 1px solid rgba(201,162,95,0.25); padding-bottom: 8px; }
.fusion .en { color: #ECECF1; }
.fusion .cn { color: #c9c2b4; }
.mantra .en { font-size: 20px; font-family: Georgia, serif; }
.mantra .cn { color: #c9c2b4; }
.stone-list { list-style: none; padding: 0; display: flex; gap: 10px; flex-wrap: wrap; }
.stone-list li { background: rgba(201,162,95,0.12); border: 1px solid rgba(201,162,95,0.3); color: #e7d9b8; padding: 6px 14px; border-radius: 999px; font-size: 14px; }
.src { color: #7d7d8a; font-size: 12px; margin-top: 10px; }
.rel-list { columns: 2; column-gap: 18px; padding-left: 18px; }
.rel-list li { margin: 4px 0; break-inside: avoid; }
.rel-list .cn { color: #9a9aa6; }
.cta { text-align: center; display: flex; flex-direction: column; gap: 12px; align-items: center; }
.btn { display: inline-block; background: linear-gradient(180deg, #E2BE73, #C9A962); color: #1a1408; font-weight: 700; letter-spacing: .06em; padding: 13px 26px; border-radius: 999px; border: none; }
.btn:hover { filter: brightness(1.05); }
.btn-ghost { background: transparent; color: #C9A962; border: 1px solid rgba(201,162,95,0.5); padding: 11px 22px; border-radius: 999px; cursor: pointer; font-size: 14px; }

/* ---- signature wall ---- */
.wall { max-width: 1100px; margin: 0 auto; padding: 10px 22px 64px; }
.wall-head { text-align: center; padding: 24px 0; }
.wall-head h1 { font-family: Georgia, serif; font-size: 44px; margin: 6px 0 12px; }
.wall-head .sub { color: #b9b9c6; max-width: 560px; margin: 0 auto 18px; }
.wall-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 14px; margin-top: 26px; }
.sig-card { display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 18px 12px; border-radius: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-top: 2px solid var(--el); transition: transform .2s, border-color .2s; }
.sig-card:hover { transform: translateY(-4px); border-color: var(--el); }
.sig-sym { font-size: 26px; }
.sig-en { font-weight: 600; font-size: 14px; text-align: center; }
.sig-cn { color: #C9A962; font-size: 13px; }
.sig-z { color: #8d8d9a; font-size: 12px; }
.wall-foot { text-align: center; color: #6f6f7c; margin-top: 40px; font-size: 13px; letter-spacing: .1em; }
@media (max-width: 520px) { .pair { flex-direction: column; } .rel-list { columns: 1; } .combo-head h1 { font-size: 32px; } }
"""
with open(os.path.join(OUT, "combo.css"), "w", encoding="utf-8") as f:
    f.write(CSS)

# ---------- 5. .nojekyll ----------
with open(os.path.join(ROOT, ".nojekyll"), "w", encoding="utf-8") as f:
    f.write("")

print(f"OK: generated {count} combo pages + wall + combo.css")
