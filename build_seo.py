#!/usr/bin/env python3
"""
Twinstellar · P1 构建脚本
解析 index.html 中的 TWIN_COMBOS / ELEMENTS / ZODIAC，
生成 60 个长尾 SEO 落地页 (combo/<slug>.html) + 宇宙签名墙 (combo/index.html) + 共享样式 combo/combo.css。
纯静态、零后端；生成结果提交进仓库，由 GitHub Pages 直接托管。
视觉与主站 (index.html) 统一：Cormorant Garamond / Inter / Noto Serif SC 字体、金色渐变、暗色星云、CN/EN 切换。
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

# 通用双语片段：英文 + 中文，靠 .lang-en / .lang-cn 切换
def dual(en, cn, tag="span", cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<{tag} class="lang-en"{c}>{en}</{tag}><{tag} class="lang-cn"{c}>{cn}</{tag}>'

# ---------- 共享脚本（语言切换 + 星空 + 分享） ----------
COMBO_SCRIPT = """<script>
(function(){
  var root = document.documentElement;
  var btn = document.getElementById('langSwitch');
  function applyLang(lang){
    var zh = lang === 'zh';
    root.classList.toggle('lang-zh', zh);
    root.classList.toggle('lang-en', !zh);
    root.lang = zh ? 'zh-CN' : 'en';
    if (btn) btn.textContent = zh ? 'EN' : '中文';
    try { localStorage.setItem('twin_lang', lang); } catch(e){}
  }
  var saved = null; try { saved = localStorage.getItem('twin_lang'); } catch(e){}
  var nav = (navigator.language || 'en').toLowerCase();
  applyLang(saved || (nav.indexOf('zh') === 0 ? 'zh' : 'en'));
  if (btn) btn.addEventListener('click', function(){
    applyLang(root.classList.contains('lang-zh') ? 'en' : 'zh');
  });

  // ref 捕获
  try { var p = new URLSearchParams(location.search).get('ref'); if (p) localStorage.setItem('twin_ref', p); } catch(e){}

  // 复制宇宙链接
  var cbtn = document.getElementById('copyBtn');
  if (cbtn) cbtn.onclick = function(){
    var ref = ''; try { ref = localStorage.getItem('twin_ref'); } catch(e){}
    var m = location.pathname.match(/combo\\/([a-z]+)-([a-z]+)\\.html$/);
    var url = 'https://twinstellar.com/';
    if (m) url += '?e=' + m[1] + '&z=' + m[2];
    if (ref) url += (url.indexOf('?') >= 0 ? '&' : '?') + 'ref=' + encodeURIComponent(ref);
    if (navigator.share) { navigator.share({ title: 'Twinstellar', text: 'My cosmic signature', url: url }).catch(function(){}); return; }
    if (navigator.clipboard) navigator.clipboard.writeText(url).then(function(){
      cbtn.textContent = (root.classList.contains('lang-zh') ? '链接已复制 ✓' : 'Link copied ✓');
      setTimeout(function(){ cbtn.textContent = (root.classList.contains('lang-zh') ? '复制我的宇宙链接' : 'Copy my universe link'); }, 2000);
    });
  };

  // 星空
  var c = document.getElementById('stars'); if (!c) return;
  var ctx = c.getContext('2d');
  function size(){ c.width = innerWidth; c.height = innerHeight; }
  size(); addEventListener('resize', size);
  var stars = []; for (var i=0;i<130;i++){ stars.push({ x: Math.random()*c.width, y: Math.random()*c.height, r: Math.random()*1.2+0.2, a: Math.random()*6.28 }); }
  function draw(){
    ctx.clearRect(0,0,c.width,c.height);
    for (var s of stars){ s.a += 0.012; var tw = 0.4 + 0.6*Math.abs(Math.sin(s.a)); ctx.globalAlpha = tw; ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, 6.2832); ctx.fill(); }
    requestAnimationFrame(draw);
  }
  draw();
})();
</script>
"""

# ---------- 2. 组合页模板 ----------
SHARED_HEAD = """  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@300;400;500;600&family=Noto+Serif+SC:wght@500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="combo.css">
"""

COMBO_TPL = """<!DOCTYPE html>
<html lang="en" class="lang-en">
<head>
{SHEAD}<title>{title_en} Cosmic Signature Meaning · Twinstellar</title>
<meta name="description" content="{desc_en}">
<meta property="og:title" content="{title_en} Cosmic Signature · Twinstellar">
<meta property="og:description" content="{desc_en}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{canonical}">
</head>
<body>
<canvas id="stars"></canvas>
<div class="nebula"></div>
<header class="topbar">
  <a class="brand" href="{site}/">TWINSTELLAR</a>
  <nav>
    <a href="{site}/">Home</a>
    <a href="index.html">Signatures</a>
  </nav>
  <button id="langSwitch" class="lang-switch" type="button">中文</button>
</header>
<main class="combo-page">
  <a class="back" href="index.html">&larr; All signatures</a>
  <header class="combo-head">
    <p class="eyebrow">Five Elements &times; Zodiac</p>
    <h1><span class="lang-en">{title_en}</span><span class="lang-cn">{title_cn}</span></h1>
    <p class="sig-meta"><span class="lang-en">{el_name} &middot; {zk_name}</span><span class="lang-cn">{el_cn} &middot; {zk_cn}</span></p>
  </header>

  <section class="pair">
    <div class="pair-card">
      <h2>{el_h}</h2>
      <p class="big-sym">{el_symbol}</p>
      <p class="lang-en">{el_key}</p>
      <p class="lang-cn">{el_key_cn}</p>
    </div>
    <div class="pair-card">
      <h2>{zk_h}</h2>
      <p class="big-sym">{zk_symbol}</p>
      <p class="lang-en">{zk_arche}</p>
      <p class="lang-cn">{zk_arche_cn}</p>
    </div>
  </section>

  <section class="fusion">
    <h2>{fusion_h}</h2>
    <p class="lang-en">{fusion_en}</p>
    <p class="lang-cn">{fusion_cn}</p>
  </section>

  <section class="mantra">
    <h2>{mantra_h}</h2>
    <p class="lang-en">&ldquo;{mantra_en}&rdquo;</p>
    <p class="lang-cn">「{mantra_cn}」</p>
  </section>

  <section class="stones">
    <h2>{stones_h}</h2>
    <ul class="stone-list">{stones_li}</ul>
    <p class="src">Source numbers: {source_numbers}</p>
  </section>

  <section class="related">
    <h2>{related_h}</h2>
    <ul class="rel-list">{related_li}</ul>
  </section>

  <section class="cta">
    <a class="btn" href="{site}/?e={element}&z={zodiac}">{cta_reveal}</a>
    <button class="btn-ghost" id="copyBtn" type="button">{cta_copy}</button>
  </section>
</main>
{SCRIPT}
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
        f'<li><a href="{slug_of(x)}.html">'
        f'<span class="lang-en">{esc(x["title_en"])}</span>'
        f'<span class="lang-cn">{esc(x["title_cn"])}</span></a></li>'
        for x in rel_unique
    )
    stones_li = "".join(f"<li>{esc(st)}</li>" for st in c["stones"])
    html = COMBO_TPL.format(
        SHEAD=SHARED_HEAD,
        title_en=esc(c["title_en"]),
        title_cn=esc(c["title_cn"]),
        desc_en=esc(desc_en),
        canonical=f"{SITE}/combo/{s}.html",
        site=SITE,
        el_symbol=el["symbol"], el_cn=esc(el["cn"]), el_name=esc(el["name"]),
        el_key=esc(el["key"]), el_key_cn=esc(el["key_cn"]),
        el_h=dual("Your Element &middot; " + esc(el["name"]), "你的元素 &middot; " + esc(el["cn"]), tag="span"),
        zk_symbol=zk["symbol"], zk_cn=esc(zk["cn"]), zk_name=esc(zk["name"]),
        zk_arche=esc(zk["arche"]), zk_arche_cn=esc(zk["arche_cn"]),
        zk_h=dual("Your Zodiac &middot; " + esc(zk["name"]), "你的星座 &middot; " + esc(zk["cn"]), tag="span"),
        fusion_h=dual("The Fusion", "融合能量", tag="span"),
        fusion_en=rich(c["fusion"]), fusion_cn=rich(c["fusion_cn"]),
        mantra_h=dual("Mantra", "真言", tag="span"),
        mantra_en=esc(c["mantra_en"]), mantra_cn=esc(c["mantra_cn"]),
        stones_h=dual("Power Stones", "守护石", tag="span"),
        stones_li=stones_li, source_numbers=esc(c["source_numbers"]),
        related_h=dual("Explore more signatures", "探索更多签名", tag="span"),
        related_li=rel_li,
        cta_reveal=dual("Reveal your own cosmic signature &rarr;", "揭示你自己的宇宙签名 &rarr;", tag="span"),
        cta_copy=dual("Copy my universe link", "复制我的宇宙链接", tag="span"),
        element=esc(c["element"]), zodiac=esc(c["zodiac"]),
        SCRIPT=COMBO_SCRIPT,
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
<html lang="en" class="lang-en">
<head>
{SHARED_HEAD}<title>The Cosmic Signature Wall · Twinstellar</title>
<meta name="description" content="All 60 cosmic signatures — where the Five Elements meet the Zodiac. Find yours and share it with a kindred spirit.">
<meta property="og:title" content="The Cosmic Signature Wall · Twinstellar">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE}/combo/">
</head>
<body>
<canvas id="stars"></canvas>
<div class="nebula"></div>
<header class="topbar">
  <a class="brand" href="{SITE}/">TWINSTELLAR</a>
  <nav>
    <a href="{SITE}/">Home</a>
    <a href="index.html">Signatures</a>
  </nav>
  <button id="langSwitch" class="lang-switch" type="button">中文</button>
</header>
<main class="wall">
  <header class="wall-head">
    <p class="eyebrow">Five Elements &times; Zodiac</p>
    <h1><span class="lang-en">The Cosmic Signature Wall</span><span class="lang-cn">宇宙签名墙</span></h1>
    <p class="sub"><span class="lang-en">All 60 signatures — each a living union of your Element and Zodiac. Find yours, then reveal your own.</span><span class="lang-cn">全部 60 种签名——每一种都是你元素与星座的活生生的融合。找到你的，再揭示你自己的。</span></p>
    <a class="btn" href="{SITE}/"><span class="lang-en">Reveal my cosmic signature &rarr;</span><span class="lang-cn">揭示我的宇宙签名 &rarr;</span></a>
  </header>
  <section class="wall-grid">
    {''.join(cards)}
  </section>
  <footer class="wall-foot">Twinstellar &middot; Two Beads. One Universe.</footer>
</main>
{COMBO_SCRIPT}
</body>
</html>
"""
with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(wall)

# ---------- 4. 共享样式（与主站统一的高级视觉） ----------
CSS = """* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
:root {
  --bg: #08080B;
  --gold: #CBA35B;
  --gold-hi: #F2E0AE;
  --gold-soft: #E6D2A0;
  --gold-grad: linear-gradient(135deg, #F4E3B4 0%, #D8B675 42%, #B58A2E 78%, #E7CE92 100%);
  --ink: #F1F0F4;
  --ink-dim: #9a9aa6;
  --line: rgba(203, 163, 91, 0.30);
  --line-soft: rgba(203, 163, 91, 0.16);
  --panel: rgba(28, 28, 35, 0.55);
}
html { background-color: var(--bg); scroll-behavior: smooth; }
body {
  font-family: 'Inter', system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
  color: var(--ink);
  background: radial-gradient(1200px 800px at 50% -10%, #181826 0%, var(--bg) 55%) fixed;
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
  min-height: 100vh;
}
#stars { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
.nebula {
  position: fixed; inset: -25%; z-index: 0; pointer-events: none;
  background:
    radial-gradient(38% 28% at 22% 32%, rgba(79,134,198,.12), transparent 62%),
    radial-gradient(34% 26% at 78% 68%, rgba(201,169,98,.12), transparent 62%),
    radial-gradient(30% 24% at 60% 18%, rgba(120,90,180,.08), transparent 60%);
  filter: blur(22px);
  animation: nebulaDrift 28s ease-in-out infinite alternate;
}
@keyframes nebulaDrift {
  from { transform: translate3d(-3%, -2%, 0) scale(1); }
  to   { transform: translate3d(3%, 2%, 0) scale(1.08); }
}
body::after {
  content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background: radial-gradient(125% 105% at 50% 42%, transparent 55%, rgba(0,0,0,0.55) 100%);
}
.topbar, .combo-page, .wall { position: relative; z-index: 1; }
a { color: var(--gold); text-decoration: none; }

/* ---------- top bar ---------- */
.topbar { display: flex; align-items: center; justify-content: space-between; padding: 22px 30px; max-width: 1100px; margin: 0 auto; }
.brand {
  font-family: 'Cormorant Garamond', serif; letter-spacing: 0.46em; font-weight: 600; font-size: 20px;
  background: var(--gold-grad); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent;
}
.topbar nav a { color: var(--ink-dim); text-decoration: none; margin-left: 26px; font-size: 13px; letter-spacing: 0.1em; transition: color .25s; }
.topbar nav a:hover { color: var(--gold-soft); }

/* ---------- language switch ---------- */
.lang-switch {
  background: rgba(28,28,35,0.4); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--line-soft); color: var(--gold-soft); border-radius: 30px;
  padding: 6px 15px; font-size: 12px; letter-spacing: 0.1em; cursor: pointer; font-family: inherit;
  transition: border-color .2s, color .2s;
}
.lang-switch:hover { border-color: var(--gold); color: var(--gold); }

/* ---------- language visibility (CN/EN 切换) ---------- */
.lang-cn { display: none; }
html.lang-zh .lang-en { display: none; }
html.lang-zh .lang-cn { display: revert; }

/* ---------- combo page ---------- */
.combo-page { max-width: 720px; margin: 0 auto; padding: 8px 24px 80px; }
.back { display: inline-block; margin: 4px 0 18px; color: var(--ink-dim); font-size: 13px; letter-spacing: .04em; }
.back:hover { color: var(--gold); }
.eyebrow { letter-spacing: .4em; text-transform: uppercase; font-size: 12px; color: var(--gold); margin: 0 0 16px; }
.combo-head { text-align: center; padding: 10px 0 4px; }
.combo-head h1 { font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: clamp(38px, 7vw, 60px); line-height: 1.1; margin: 8px 0 14px;
  background: var(--gold-grad); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent; }
.sig-meta { color: var(--ink-dim); letter-spacing: .12em; margin: 0; font-size: 14px; }
.sig-meta .lang-cn { letter-spacing: .2em; }

.pair { display: flex; gap: 18px; margin: 38px 0; }
.pair-card { flex: 1; background: var(--panel); border: 1px solid var(--line-soft); border-radius: 18px; padding: 26px 20px; text-align: center; backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); }
.pair-card h2 { font-size: 13px; letter-spacing: .14em; text-transform: uppercase; color: var(--gold); margin: 0 0 12px; font-weight: 600; }
.big-sym { font-size: 40px; margin: 6px 0 14px; }
.pair-card p { margin: 4px 0; color: var(--ink); }
.pair-card .lang-cn { color: var(--gold-soft); font-size: 14px; font-family: 'Noto Serif SC', serif; }

.fusion, .mantra, .stones, .related, .cta { margin: 46px 0; }
.fusion h2, .mantra h2, .stones h2, .related h2 { font-family: 'Cormorant Garamond', serif; font-size: 26px; letter-spacing: .02em; color: var(--gold); border-bottom: 1px solid var(--line); padding-bottom: 12px; margin: 0 0 18px; font-weight: 500; }
.fusion p, .mantra p { color: var(--ink); font-size: 16px; line-height: 1.95; }
.fusion .lang-cn, .mantra .lang-cn { color: var(--ink); font-family: 'Noto Serif SC', serif; }
.mantra .lang-en { font-family: 'Cormorant Garamond', serif; font-size: 27px; font-style: italic; line-height: 1.5; }
.mantra .lang-cn { font-size: 20px; text-align: center; }

.stone-list { list-style: none; padding: 0; display: flex; gap: 12px; flex-wrap: wrap; }
.stone-list li { background: rgba(201,162,95,0.10); border: 1px solid rgba(201,162,95,0.30); color: var(--gold-soft); padding: 8px 18px; border-radius: 999px; font-size: 14px; }
.src { color: #7d7d8a; font-size: 12px; margin-top: 14px; letter-spacing: .04em; }
.rel-list { list-style: none; padding: 0; columns: 2; column-gap: 22px; }
.rel-list li { margin: 6px 0; break-inside: avoid; }
.rel-list a { color: var(--ink); font-size: 14px; text-decoration: none; transition: color .2s; }
.rel-list a:hover { color: var(--gold); }
.rel-list .lang-cn { color: var(--gold-soft); font-family: 'Noto Serif SC', serif; margin-left: 6px; font-size: 13px; }
.cta { text-align: center; display: flex; flex-direction: column; gap: 16px; align-items: center; }
.btn { display: inline-block; background: var(--gold-grad); color: #1a1408; font-weight: 700; letter-spacing: .08em; padding: 15px 32px; border-radius: 999px; border: none; text-decoration: none; box-shadow: 0 10px 30px rgba(203,163,91,0.30); transition: transform .25s, box-shadow .25s; }
.btn:hover { transform: translateY(-2px); box-shadow: 0 16px 42px rgba(203,163,91,0.42); }
.btn-ghost { background: transparent; color: var(--gold); border: 1px solid rgba(201,162,95,0.5); padding: 12px 24px; border-radius: 999px; cursor: pointer; font-size: 14px; font-family: inherit; transition: border-color .2s, color .2s; }
.btn-ghost:hover { border-color: var(--gold); color: var(--gold-soft); }

/* ---------- signature wall ---------- */
.wall { max-width: 1100px; margin: 0 auto; padding: 8px 24px 80px; }
.wall-head { text-align: center; padding: 20px 0 8px; }
.wall-head h1 { font-family: 'Cormorant Garamond', serif; font-size: clamp(40px, 7vw, 60px); margin: 10px 0 16px;
  background: var(--gold-grad); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent; }
.wall-head .sub { color: var(--ink-dim); max-width: 560px; margin: 0 auto 22px; }
.wall-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(155px, 1fr)); gap: 16px; margin-top: 30px; }
.sig-card { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 22px 12px; border-radius: 18px; background: var(--panel); border: 1px solid var(--line-soft); border-top: 2px solid var(--el); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); transition: transform .2s, border-color .2s; }
.sig-card:hover { transform: translateY(-4px); border-color: var(--el); }
.sig-sym { font-size: 28px; }
.sig-en { font-weight: 600; font-size: 14px; text-align: center; color: var(--ink); }
.sig-cn { color: var(--gold); font-size: 13px; font-family: 'Noto Serif SC', serif; }
.sig-z { color: var(--ink-dim); font-size: 12px; }
.wall-foot { text-align: center; color: #6f6f7c; margin-top: 46px; font-size: 13px; letter-spacing: .1em; }
@media (max-width: 560px) {
  .topbar { padding: 18px 18px; }
  .topbar nav a { margin-left: 16px; font-size: 12px; }
  .pair { flex-direction: column; }
  .rel-list { columns: 1; }
  .combo-head h1 { font-size: 34px; }
}
"""

# ---------- 5. 写出共享样式 ----------
with open(os.path.join(OUT, "combo.css"), "w", encoding="utf-8") as f:
    f.write(CSS)

# ---------- 6. .nojekyll ----------
with open(os.path.join(ROOT, ".nojekyll"), "w", encoding="utf-8") as f:
    f.write("")

print(f"OK: generated {count} combo pages + wall + combo.css")
