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

## 变现（单一礼物路径 · 国内收款码 + 海外加密货币）
全站**仅保留一条路径**：一次性「核心解读 · 深度版」，走**礼物经济**——自愿随喜，无强制校验（软闸门）。

> 为什么不用 Stripe / 微信支付宝商户：你是**大陆个人身份**，无法完成 Stripe KYC，也无营业执照开通官方商户。因此采用**零资质、零后端**的双通道：
> - 国内：你的**个人微信 / 支付宝收款码**（本来就有，无需注册）
> - 海外：你的**加密货币 USDT 钱包**（无 KYC、全球可付、零后端）

### 配置（三步，无需后端）
1. 把三张收款码图片放进 `assets/`：`wechat_qr.png`（微信）、`alipay_qr.png`（支付宝）、`usdt_qr.png`（USDT 收款二维码）。
2. 打开 `index.html`，把 `GIFT.usdtAddr` 的占位文字改成你真实的 USDT 钱包地址（建议 TRC20）。
3. （可选）改 `GIFT.cnAmount` / `GIFT.enAmount` 调整建议心意金额（默认 ¥2.99 / $3.99）。提交部署即可。

### 工作机制
点击「解锁深度版」→ 弹出礼物弹窗（展示微信 / 支付宝 / USDT 三种二维码 + 建议金额）→ 用户扫码付款后点「我已完成礼物」→ 前端直接渲染深度解读，并把 `?paid=1` 写入地址栏（刷新仍可见）。待解锁组合存于 `localStorage('twin_pending_deep')`，回跳时自动展开。

> ⚠️ **软闸门**：纯前端，懂技术者可手动写入 `twin_pending_deep` 并访问 `?paid=1` 绕过。礼物经济本就自愿，对 ¥2.99/$3.99 一次性内容属可接受的 MVP 折中；若要硬闸门需加后端校验（不在纯静态范围内）。

| 路径 | 内容 | 心意 |
|------|------|------|
| 免费 | 基础核心解读（称号 + 元素 + 星座 + 融合释义 + 真言 + 能量石）+ 合盘免费预览（分数/等级/闪光点）+ 日运免费版 | ¥0 |
| 礼物随喜 | 「核心解读 · 深度版」：更深的织合叙事 + 专属仪式 + 可带身上的叩问；并解锁合盘边界与完整叙事、日运全本 | 建议 ¥2.99 / $3.99（随喜） |

> 话术铁律（礼物经济）：全站禁用 `buy` / `claim` / `limited` / 限量 / 限时；统一用「礼物 / 邀请 / 深化」语态。

## 自定义
- **改价格/文案**：`index.html` 中英文案直改（搜索 `data-i18n` 键或常量即可定位）；变现阶梯逻辑见本文件「变现」一节。
- **P1 免费内容引擎（已上线）**：运行 `python3 build_seo.py` 解析 `index.html` 常量，生成 `combo/<element>-<zodiac>.html`（60 页，含 `<title>`/meta/OG/Twitter/canonical/H1、五行×星座融合、真言、能量石、同元素+同星座内部链接、回主站 CTA 带 `?e=&z=`）、`combo/index.html`（60 张「宇宙签名墙」卡片）、`combo/combo.css`。产物提交进仓库，GitHub Pages 直接托管（见 `Twinstellar落地路径.md` §4.6 / §6.1）。
- **P3 合盘报告（已上线）**：`index.html` 的 `#compat` 视图，输入两个生日 → `computeCompatibility()` 用 **五行 生克比和 + 星座共鸣** 算出 1–99 分、等级（天作之合/知音相惜/相成长/互补之美）、闪光点与边界。免费预览分数+等级+元素之契+星座共鸣+闪光点；**edges 与完整叙事为「核心解读 · 深度版」一次性解锁**（点击合盘解锁按钮 → 礼物弹窗 → 扫码付款后解锁）。
- **病毒裂变**：结果页原生分享按钮（X / Facebook / Pinterest / WhatsApp / Reddit）+ 复制链接自带 `?ref=` 推荐参数；`?ref=` 在加载时捕获进 `localStorage`。

## 已验证
- 计算逻辑：60 组合零缺失（木/火/土/金/水 × 12 星座全覆盖）
- 静态托管：GitHub Pages 返回 200，全站无 `bracelet`/`手链`/`buy`/`claim`/`limited`
- JS 语法：`node --check` 通过
- Playwright E2E：24/24（P1 入口/签名墙/详情页、P3 合盘计算+解锁门控+EN·ZH、?ref= 捕获、零 console error）

## 合规
- 脚注已含 "For intention and reflection — not a substitute for medical or spiritual counsel"。请勿对水晶/能量石做任何医疗/疗效宣称。
