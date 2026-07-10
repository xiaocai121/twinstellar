# Twinstellar MVP · 部署与接单说明

一个**纯静态**网站（无需服务器、无需数据库）。输入姓名+生日 → 算出你的五行+星座 → 匹配 60 种专属组合之一 → 展示释义 → "Claim" 手链。

## 文件
- `index.html` — **单文件自包含**（CSS、60 组合数据、计算引擎全部内联，无需任何外部文件，部署零依赖）
- `twinstellar-deploy.zip` — 部署包（含 `index.html` + `netlify.toml`），直接拖到 Netlify 即可
- `source/` — 拆分版源码（`styles.css` / `data.js` / `app.js`），仅供维护参考；部署用单文件版即可
- `twinstellar-site/` — 同样的部署副本 + `netlify.toml`

## 本地预览
```bash
cd /workspace
python3 -m http.server 8123
# 浏览器打开 http://localhost:8123
```

## ⚠️ 先搞清楚：文件在哪
这个 `index.html` **不在你自己的电脑上**，它住在云端 coding 工作区（沙箱）的 `/workspace` 里。
你之前"找不到本地 index.html"，是因为它从来没下载到过你本机——所以需要先把它拿到手，才能部署。

## 第 1 步：把文件拿到本机
我已经在 `/workspace` 打好了一个部署包：`twinstellar-deploy.zip`（里面只有 `index.html` + `netlify.toml`，干净无杂文件）。
拿到方式（任选其一）：
- **方式 A（IDE 下载）**：在左侧文件面板找到 `twinstellar-deploy.zip` → 右键 → **下载 / 保存到本地**（或点文件旁的下载图标）。解压后得到 `index.html`。
- **方式 B（GitHub 自动部署，免下载）**：见文末"进阶：GitHub 自动部署"。需要你本地先跑一次 `gh auth login` 授权，之后改代码我推一下就自动上线，**最适合"每天只花 2 小时、要全自动化"的节奏**。

## 第 2 步：拖到 Netlify（30 秒）
1. 打开 https://app.netlify.com/drop
2. 把解压出来的 `index.html`（或直接把 `twinstellar-deploy.zip`）**拖进网页虚线框**
3. 立刻获得一个 `https://xxx.netlify.app` 的临时网址 → 点开验证页面正常
4. 进该站点的 **Site settings → Domain management → Custom domains**，添加 `twinstellar.com`

## 第 3 步：在阿里云把域名指向 Netlify（无需 ICP 备案）
> Netlify 是海外节点，国内法规下**只有 DNS 指向中国大陆服务器才需要 ICP 备案**；指向 Netlify 免备案。

1. 登录阿里云 → **云解析 DNS** → 找到 `twinstellar.com`
2. 添加/修改记录：
   - 主机记录 `www` → 类型 `CNAME` → 记录值 `你的站点.netlify.app`
   - 主机记录 `@`（主域名）→ 类型 `CNAME` → 记录值 `你的站点.netlify.app`
   （若阿里云 `@` 不支持 CNAME，改用 `A` 记录指向 Netlify 提供的 IP，或开启 Netlify 的 "Primary domain" 按提示操作）
3. 等待 5–30 分钟 DNS 生效 → 浏览器访问 `twinstellar.com` 即上线。

## 进阶：GitHub 自动部署（推荐长期方案）
我已在本工作区 `git init` 并提交好了 MVP。你只需：
1. 本机终端跑 `gh auth login`（按提示用浏览器授权你的 GitHub 账号）
2. 告诉我一声，我会帮你 `git remote add` + `git push` + 在 Netlify 用 "Import from Git" 连上仓库
3. 之后每次改文案/价格，我改完推一下，网站自动更新，**你再也不用下载/拖文件**

> 当前状态：本地 git 已提交（commit `1050a60`），只差你的 GitHub 授权即可一键上线。

## 接入收款（两种方式）
**方式 A · 正式结账（推荐）**
1. 在 Stripe 建一个 Payment Link（或 Shopify Buy Button / Lemon Squeezy）
2. 打开 `index.html`，搜索顶部的
   ```js
   const CHECKOUT_BASE = '';
   ```
   改成你的结账链接前缀，例如
   ```js
   const CHECKOUT_BASE = 'https://buy.stripe.com/xxx';
   ```
3. 三档材质的"Claim"按钮会自动带 `?element=&zodiac=&tier=` 参数跳转结账。

**方式 B · 零配置预售（默认）**
不改 `CHECKOUT_BASE`。点"Claim"会直接打开一封预填好的认领邮件（`hello@twinstellar.com`），
并把意向写进浏览器本地（key: `twin_leads`），方便你之后统一跟进。

## 自定义
- **改价格/材质**：编辑 `index.html` 里的 `TIERS` 数组。
- **改文案**：`index.html` 中英文案直改（搜索关键词即可定位）。
- **加 60 个 SEO 页**：60 组合数据都在 `index.html` 的 `TWIN_COMBOS` 里，可批量生成 `?e=&z=` 静态页。

## 已验证
- 计算逻辑：6/6 抽样通过，60 组合零缺失（木/火/土/金/水 × 12 星座全覆盖）
- 静态托管：index / data.js / app.js / styles.css 均 200
- JS 语法：`node --check` 通过

## 合规
- 脚注已含 "For entertainment & intention only"。请勿对水晶做任何医疗/疗效宣称。
