# Twinstellar · 宇宙签名体验（纯静态单文件 MVP）

一个**纯静态**网站（无需服务器、无需数据库）。输入生日 → 算出你的五行 + 星座 → 匹配 60 种专属「宇宙签名」之一 → 展示称号 / 融合释义 / 真言 / 能量石，并可通过社交分享与推荐裂变传播。

> **纯数字品牌**：无实物、零供应链。免费解读 + 证书 ($5–9) + 订阅 ($19/月 或 $149/年)。详见 `Twinstellar落地路径.md`（唯一权威文档）。

## 文件
- `index.html` — **单文件自包含**（HTML + CSS + JS + 60 组合数据全部内联，部署零依赖）
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

## 接收入（未来 · 需 Stripe）
`index.html` 中的 `SUBSCRIBE_BASE` 留空时，订阅/证书按钮走本地 `mailto` 线索捕获（写入 `localStorage` 的 `twin_leads`，附 `ref` 推荐字段）。
接入 Stripe 后，把 `SUBSCRIBE_BASE` / 证书链接改为对应 Payment Link 即可转为真实结账（见路线图 P4）。

## 自定义
- **改价格/文案**：`index.html` 中英文案直改（搜索关键词即可定位）；阶梯逻辑见 `Twinstellar落地路径.md` §4。
- **加 60 个 SEO 长尾页（P1）**：60 组合数据都在 `index.html` 的 `TWIN_COMBOS` 里，可用构建脚本批量渲染为独立静态落地页（见 `Twinstellar落地路径.md` §4.6 / §6.1）。
- **病毒裂变**：结果页原生分享按钮（X / Facebook / Pinterest / WhatsApp / Reddit）+ 复制链接自带 `?ref=` 推荐参数；`?ref=` 在加载时捕获进 `localStorage`。

## 已验证
- 计算逻辑：60 组合零缺失（木/火/土/金/水 × 12 星座全覆盖）
- 静态托管：GitHub Pages 返回 200，全站无 `bracelet`/`手链`/`buy`/`claim`/`limited`
- JS 语法：`node --check` 通过
- Playwright E2E：19/19（结果页渲染、分享 URL、?ref= 捕获、EN/ZH 切换、零 console error）

## 合规
- 脚注已含 "For intention and reflection — not a substitute for medical or spiritual counsel"。请勿对水晶/能量石做任何医疗/疗效宣称。
