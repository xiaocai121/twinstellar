# Twinstellar · 宇宙签名体验（纯静态单文件 MVP）

一个**纯静态**网站（无需服务器、无需数据库）。输入生日 → 算出你的五行 + 星座 → 匹配 60 种专属「宇宙签名」之一 → 展示称号 / 融合释义 / 真言 / 能量石，并可通过社交分享与推荐裂变传播。

> **纯数字品牌**：无实物、零供应链。**基础核心解读永久免费**（礼物经济获客钩子）；唯一付费路径为一次性「核心解读 · 深度版」——解锁更深内容（合盘边界与完整叙事、日运全本、专属仪式与叩问）。详见 `Twinstellar落地路径.md`（品牌与落地策略总纲）。

## 文件
- `index.html` — **单文件自包含**（HTML + CSS + JS + 60 组合数据全部内联，部署零依赖）
- `build_seo.py` — P1 构建脚本：解析 `index.html` 中的 `TWIN_COMBOS / ELEMENTS / ZODIAC`，批量生成 60 个长尾 SEO 落地页 + 宇宙签名墙
- `combo/` — 构建产物（60×`<slug>.html` + `index.html` 签名墙 + `combo.css`），**提交进仓库**由 GitHub Pages 直接托管
- `Twinstellar落地路径.md` — 品牌手册与落地路径（定位 / 系统 / 变现 / 裂变 / 免费·付费内容架构）
- `CNAME` — 自定义域名 `twinstellar.com`

## 本地预览
```bash
cd /workspace
python3 -m http.server 8123
# 浏览器打开 http://localhost:8123
```

## 部署（GitHub Pages · 免费）
仓库已设为 **公开仓库**，由 **GitHub Pages** 自动构建并托管到 `twinstellar.com`（自定义域名 + 强制 HTTPS，零成本、无 Netlify 额度限制）。
- 改完 `index.html` / `Twinstellar落地路径.md` → `git add` → `git commit` → `git push origin main`
- GitHub Pages 自动重建上线（通常 1–2 分钟）
- 注意根目录的 `.nojekyll`：禁用 Jekyll，确保 `combo/` 等含下划线路径的静态资源被原样托管。

### 自定义域名 DNS（twinstellar.com）
GitHub Pages 已配置 `cname: twinstellar.com` 且构建正常（API 确认 `status: built`）。若线上仍显示旧内容（如 Netlify 旧构建），是 DNS 未指向 GitHub Pages 所致。在域名服务商处：
1. **删除**指向 Netlify 的解析记录（Netlify 负载均衡 IP / `apex-loadbalancer.netlify.com` 等）。
2. **添加 4 条 A 记录**（主机名 `@` / 根域名）：
   - `185.199.108.153`
   - `185.199.109.153`
   - `185.199.110.153`
   - `185.199.111.153`
3. （可选）`www` 用 CNAME 指向 `xiaocai121.github.io`。
4. 若 DNS 服务商支持 CNAME 扁平化（如 Cloudflare），也可 CNAME `@` → `xiaocai121.github.io`。
5. 改完等待传播（数分钟～48h），验证：`curl -sI https://twinstellar.com/` 应返回 `server: GitHub.com`，且页面无 `bracelet`/`手链`。
> 若仓库 Settings → Pages 显示域名待验证，重新保存自定义域名并按提示添加一条 TXT 验证记录即可。

## 变现（单一付费路径 · 需 Stripe Payment Link）
全站**仅保留一条收费路径**：一次性「核心解读 · 深度版」。

`index.html` 中的 `PAY_BASE` 留空时，结果页 / 日运页 / 合盘页的「解锁深度版」按钮走本地预览解锁（写入 `localStorage` 的 `twin_leads`，附 `ref` 推荐字段），便于设计评审与本地调试。
接入 Stripe 后，把 `PAY_BASE` 改为对应的 **Payment Link** 即可转为真实一次性结账（全站三处 CTA 共用同一 `PAY_BASE`）。

| 路径 | 内容 | 价格 |
|------|------|------|
| 免费 | 基础核心解读（称号 + 元素 + 星座 + 融合释义 + 真言 + 能量石）+ 合盘免费预览（分数/等级/闪光点）+ 日运免费版 | $0 |
| 一次性付费 | 「核心解读 · 深度版」：更深的织合叙事 + 专属仪式 + 可带身上的叩问；并解锁合盘边界与完整叙事、日运全本 | 一次性 |

> 话术铁律（礼物经济）：全站禁用 `buy` / `claim` / `limited` / 限量 / 限时；统一用「礼物 / 邀请 / 深化」语态。

## 自定义
- **改价格/文案**：`index.html` 中英文案直改（搜索 `data-i18n` 键或常量即可定位）；变现阶梯逻辑见本文件「变现」一节。
- **P1 免费内容引擎（已上线）**：运行 `python3 build_seo.py` 解析 `index.html` 常量，生成 `combo/<element>-<zodiac>.html`（60 页，含 `<title>`/meta/OG/Twitter/canonical/H1、五行×星座融合、真言、能量石、同元素+同星座内部链接、回主站 CTA 带 `?e=&z=`）、`combo/index.html`（60 张「宇宙签名墙」卡片）、`combo/combo.css`。产物提交进仓库，GitHub Pages 直接托管（见 `Twinstellar落地路径.md` §4.6 / §6.1）。
- **P3 合盘报告（已上线）**：`index.html` 的 `#compat` 视图，输入两个生日 → `computeCompatibility()` 用 **五行 生克比和 + 星座共鸣** 算出 1–99 分、等级（天作之合/知音相惜/相成长/互补之美）、闪光点与边界。免费预览分数+等级+元素之契+星座共鸣+闪光点；**edges 与完整叙事为「核心解读 · 深度版」一次性解锁**（Stripe 落地后，当前 `PAY_BASE` 空时点击即解锁预览）。
- **病毒裂变**：结果页原生分享按钮（X / Facebook / Pinterest / WhatsApp / Reddit）+ 复制链接自带 `?ref=` 推荐参数；`?ref=` 在加载时捕获进 `localStorage`。

## 已验证
- 计算逻辑：60 组合零缺失（木/火/土/金/水 × 12 星座全覆盖）
- 静态托管：GitHub Pages 返回 200，全站无 `bracelet`/`手链`/`buy`/`claim`/`limited`
- JS 语法：`node --check` 通过
- Playwright E2E：24/24（P1 入口/签名墙/详情页、P3 合盘计算+解锁门控+EN·ZH、?ref= 捕获、零 console error）

## 合规
- 脚注已含 "For intention and reflection — not a substitute for medical or spiritual counsel"。请勿对水晶/能量石做任何医疗/疗效宣称。
