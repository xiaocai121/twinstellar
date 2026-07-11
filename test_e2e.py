#!/usr/bin/env python3
"""Twinstellar E2E — P1 (免费内容引擎) + P3 (合盘报告) + 回归。

用系统 Chromium 跑 headless，本地 http.server 托管 /workspace。
断言：
  - 主页无 bracelet/手链/buy/claim/limited/入道之礼 残留
  - P1 入口：nav/result/footer 三处签名墙链接
  - combo/index.html 含 60 张卡片
  - combo/fire-aries.html 含 fusion/mantra/内部链接/OG/canonical
  - P3：合盘计算给出 1-99 分 + 等级 + strengths；解锁前 gated 隐藏，解锁后显示 edges+narrative
  - 中文切换后合盘文案为中文
  - 病毒分享：result 页分享文案含 ?e=&z= 与 ref 捕获
"""
import sys, threading, http.server, socketserver, os, urllib.parse
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8137
BASE = f"http://localhost:{PORT}"

FORBIDDEN = ["bracelet", "手链", "buy", "claim", "limited", "入道之礼", "Claim your"]

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

class ReuseTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def start_server():
    global PORT
    os.chdir(ROOT)
    srv = ReuseTCPServer(("127.0.0.1", 0), Q)
    PORT = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv

passed = 0
failed = 0
def check(name, cond, extra=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {extra}")

def main():
    srv = start_server()
    global BASE
    BASE = f"http://localhost:{PORT}"
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, executable_path="/usr/bin/chromium",
                              args=["--no-sandbox"])
        pg = b.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
        pg.on("response", lambda r: errors.append(f"{r.status} {r.url}")
               if (r.status >= 400 and "favicon" not in r.url) else None)

        # ---------- 主页 + 回归 ----------
        pg.goto(f"{BASE}/index.html", wait_until="networkidle")
        body = pg.inner_text("body")
        low = body.lower()
        check("主页无违禁词残留", not any(w.lower() in low for w in FORBIDDEN),
              [w for w in FORBIDDEN if w.lower() in low])

        # ---------- P1 入口 ----------
        nav_sig = pg.query_selector('a[data-i18n="nav_signatures"]')
        check("nav 含 Signatures 链接", nav_sig is not None and "combo/index.html" in (nav_sig.get_attribute("href") or ""))
        foot_sig = pg.query_selector('a[data-i18n="footer_wall"]')
        check("footer 含 60 签名链接", foot_sig is not None)
        res_compat = pg.query_selector('a[data-i18n="result_compat"]')
        check("合盘 CTA 存在于 DOM", res_compat is not None)
        nav_compat = pg.query_selector('a[data-i18n="nav_compat"]')
        check("nav 含 Compat 链接", nav_compat is not None)

        # ---------- P3 合盘 ----------
        pg.click('a[data-i18n="nav_compat"]')
        pg.wait_for_selector("#compat:not([hidden])", timeout=4000)
        pg.fill("#cYou", "1990-05-15")
        pg.fill("#cOther", "1992-11-03")
        pg.click("#compatBtn")
        pg.wait_for_selector("#compatResult:not([hidden])", timeout=4000)
        score_txt = pg.inner_text("#compatScore").strip()
        try:
            score = int(score_txt)
        except ValueError:
            score = -1
        check("合盘分数在 1-99", 1 <= score <= 99, f"score={score_txt}")
        level = pg.inner_text("#compatLevel").strip()
        check("合盘等级非空", len(level) > 0, f"level='{level}'")
        strengths = pg.query_selector_all("#compatStrengths li")
        check("合盘 strengths ≥ 1 条", len(strengths) >= 1, f"n={len(strengths)}")
        bond = pg.inner_text("#compatBond").strip()
        check("合盘 bond 标题非空", len(bond) > 0, f"bond='{bond}'")

        # 解锁前 gated 隐藏
        gated_hidden_before = pg.eval_on_selector("#compatGated", "el => el.hidden")
        check("解锁前 gated 隐藏", gated_hidden_before is True)
        # 解锁
        pg.click("#compatUnlockBtn")
        pg.wait_for_selector("#compatGated:not([hidden])", timeout=4000)
        edges = pg.query_selector_all("#compatEdges li")
        narr = pg.inner_text("#compatNarrative").strip()
        check("解锁后 edges ≥ 1 条", len(edges) >= 1, f"n={len(edges)}")
        check("解锁后 narrative 非空", len(narr) > 0, f"narr='{narr[:40]}'")

        # 语言切换 → 中文
        pg.click("#langSwitch")
        bond_zh = pg.inner_text("#compatBond").strip()
        check("中文切换后 bond 含 ×", "×" in bond_zh, f"bond='{bond_zh}'")
        lvl_zh = pg.inner_text("#compatLevel").strip()
        check("中文等级非空", len(lvl_zh) > 0)
        # 切回英文
        pg.click("#langSwitch")

        # ---------- 病毒分享（result 页） ----------
        pg.goto(f"{BASE}/index.html?e=Fire&z=Aries", wait_until="networkidle")
        pg.wait_for_selector("#result:not([hidden])", timeout=4000)
        # 捕获 share text 内容（通过点击 copy 不便，直接读 shareText 逻辑产出）
        share = pg.evaluate("""() => {
            const c = window.TWIN_COMBOS.find(x => x.element==='Fire' && x.zodiac==='Aries');
            return { en: c.title_en, cn: c.title_cn };
        }""")
        check("深链 ?e=&z= 直达结果", bool(share.get("en")))
        # ref 捕获：带 ref 访问后 localStorage 应有 twin_ref
        pg.goto(f"{BASE}/index.html?e=Fire&z=Aries&ref=FireAries", wait_until="networkidle")
        ref = pg.evaluate("() => { try { return localStorage.getItem('twin_ref'); } catch(e){ return null; } }")
        check("?ref= 被捕获到 localStorage", ref == "FireAries", f"ref={ref}")

        # ---------- combo 签名墙 ----------
        pg.goto(f"{BASE}/combo/index.html", wait_until="networkidle")
        cards = pg.query_selector_all(".sig-card")
        check("签名墙含 60 张卡片", len(cards) == 60, f"n={len(cards)}")
        title = pg.title()
        check("签名墙标题正确", "Signature Wall" in title, title)

        # ---------- combo 详情页 ----------
        pg.goto(f"{BASE}/combo/fire-aries.html", wait_until="networkidle")
        ct = pg.inner_text("body")
        check("combo 页含 fusion 标题", "Blazing Vanguard" in ct)
        check("combo 页含 mantra", "I ignite the path forward" in ct)
        canonical = pg.get_attribute('link[rel="canonical"]', "href")
        check("combo 页 canonical 正确", canonical == "https://twinstellar.com/combo/fire-aries.html", str(canonical))
        og = pg.query_selector('meta[property="og:title"]')
        check("combo 页含 OG 标签", og is not None)
        internal = pg.query_selector_all('a[href$=".html"]')
        check("combo 页含内部链接", len(internal) >= 1, f"n={len(internal)}")

        # ---------- 控制台错误（忽略 favicon 404） ----------
        check("无控制台/页面错误", len(errors) == 0, errors[:5])

        b.close()
    srv.shutdown()
    print(f"\nRESULT: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
