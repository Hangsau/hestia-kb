# Hestia KB Site

個人知識庫網站 — 把 `~/obsidian-vault/` 1198 篇 .md 變成可被外人探索的「數位花園」。

🌐 **Live**: https://hangsau.github.io/hestia-kb/
📦 **Repo**: https://github.com/Hangsau/hestia-kb

## 設計

依 `~/projects/hestia-kb/docs/hestia-kb-design-spec.md` 設計：
- **風格**：Soft Warm Digital Garden（Maggie Appleton + Gwern 互補）
- **配色**：`#FAF7F0` 米色 / `#1A1814` 深棕黑 / `#C75D2C` 暖橘
- **狀態色**：🌱 seedling / 🌿 budding / 🌳 evergreen
- **字型**：serif body（Iowan Old Style / Charter / Source Serif Pro fallback）

## 技術棧

- **Astro 5** — 靜態站生成 + island architecture
- **Tailwind v4** — 樣式系統（custom `@theme` 變數）
- **Pagefind** — build-time 全文搜尋（中文無 stemming 但仍可搜）
- **vis-network** — 知識地圖視覺化（CDN 載入）
- **GitHub Pages** — 部署

## 架構

```
~/obsidian-vault/  (1198 .md)
   ↓
[ Hestia VM cron 每 30 分鐘 ]
   ↓
scripts/sync-vault.py   → site/src/content/notes/*.md (強化 frontmatter)
scripts/build-graph.py  → site/public/graph.json (wikilink 邊)
   ↓
[ git commit + push to Hangsau/hestia-kb ]
   ↓
[ GitHub Actions ]
   ↓
npm run build  (astro build + pagefind --site dist)
   ↓
[ GitHub Pages deploy ]
   ↓
https://hangsau.github.io/hestia-kb/
```

## 頁面結構

| 路由 | 內容 | 來源 |
|------|------|------|
| `/` | 首頁（hero + 領域分佈 + 標籤雲 + 最近照料 + 知識樞紐 + MOC） | `src/pages/index.astro` 動態算 |
| `/notes/` | 全部 1198 筆記目錄 | `src/pages/notes/` 動態 |
| `/notes/{slug}/` | 單篇筆記（1198 頁，動態生成） | `src/pages/notes/[...slug].astro` |
| `/tags/{tag}/` | tag 頁（477 個） | `src/pages/tags/[tag].astro` 動態 |
| `/graph/` | 知識地圖（200 節點 / 111 邊） | `src/pages/graph.astro` + vis-network |
| `/search/` | Pagefind 全文搜尋 | `src/pages/search.astro` |
| `/about/` | 關於 + 設計理念 | `src/pages/about.astro` |

## 開發流程

### 在 Hestia VM 上（本地開發 + 自動 deploy）

```bash
# 1. 同步 vault
cd ~/projects/hestia-kb/site
python3 scripts/sync-vault.py         # 1198 .md → src/content/notes/
python3 scripts/build-graph.py        # wikilink 邊 → public/graph.json

# 2. 本地預覽
npm run dev                          # http://localhost:4321/hestia-kb

# 3. 完整 build（本地）
npm run build-full                    # sync + graph + astro + pagefind

# 4. 自動 deploy（手動觸發）
~/.hermes/scripts/hestia-kb-site-deploy.sh

# 5. 自動 deploy（自動，每 30 分鐘）
#    由 systemd timer `hestia-kb-site-deploy.timer` 觸發
systemctl --user list-timers hestia-kb-site-deploy.timer
```

## 自動 Deploy 鏈

1. user 改 vault 任一 .md
2. systemd timer（`hestia-kb-site-deploy.timer`）每 30 分鐘跑 `hestia-kb-site-deploy.sh`
3. script 跑 `sync-vault.py` + `build-graph.py` 重新生成
4. 比對 git diff，沒變動就跳過
5. 有變動 → `git commit + push`
6. GitHub Action 自動 `npm run build`（astro + pagefind）
7. deploy 到 `https://hangsau.github.io/hestia-kb/`
8. **整個 cycle 全自動**，vault 改完 30 分鐘內網站更新

## 檔案結構

```
~/projects/hestia-kb/site/
├── astro.config.mjs            # Astro 配置（base: /hestia-kb for GitHub Pages）
├── package.json
├── .github/workflows/deploy.yml  # GitHub Actions deploy
├── public/                      # 靜態資源
│   ├── favicon.svg
│   └── graph.json              # 從 vault wikilink 產的
├── scripts/
│   ├── sync-vault.py           # vault → content collection
│   └── build-graph.py          # wikilink → graph.json
├── src/
│   ├── content.config.ts        # Astro 5 content collection schema
│   ├── content/
│   │   ├── _manifest.json       # 全部 notes 索引
│   │   └── notes/*.md          # 1198 個 vault .md 強化版
│   ├── layouts/
│   │   └── Layout.astro         # 全站 layout（navbar + footer）
│   ├── styles/
│   │   └── global.css           # Tailwind v4 + design-spec 主題
│   └── pages/
│       ├── index.astro          # 首頁（用真實資料）
│       ├── about.astro
│       ├── search.astro         # Pagefind 全文搜尋
│       ├── graph.astro          # vis-network 知識地圖
│       ├── notes/
│       │   ├── [...slug].astro  # 1198 動態頁
│       │   └── index.astro      # 筆記目錄
│       └── tags/
│           └── [tag].astro      # 477 動態 tag 頁
└── README.md
```

## 設計依據

- `~/projects/hestia-kb/docs/hestia-kb-design-spec.md` — 完整設計規格書
- `~/projects/hestia-kb/docs/web-design-methodology.md` — 設計方法論
- `~/projects/hestia-kb/docs/web-design-styles.md` — 視覺風格指南
- `~/projects/hestia-kb/docs/web-design-layouts.md` — Layout + component 規格

## 已知限制

- **中文無 stemming**（Pagefind）：搜尋中文時不會詞根化（如「發展」不會匹配到「發展中」）。功能 OK，但召回率低於英文。
- **1198 篇是 batch build**，vault 加新檔要等下次 sync（≤ 30 分鐘）。
- **TL;DR 自動生成**未做（W2.4 pending）：每篇頂部沒有一句話摘要，未來用 LLM 生成。
- **首頁地圖是 placeholder**：vis-network 圖在 `/graph/` 頁有，但首頁只放領域分佈。

## Phase 進度（hestia-kb 整體）

- **P0 規範** ✅
- **P1 強化存取** ✅（FTS5 + vector embed + hybrid search + FastAPI）
- **P2 自動維護** ✅（5 個 systemd timer 跑 cron job）
- **P3 對話回流** ⏳ 待開始
- **P4 整合 + 監控** 🟡 進行中（本站 = P4.3 的一部分）

## 維護者

- 專案交接單：`~/projects/hestia-kb/CLAUDE.md`
- Hestia 系統交接單：`~/.claude/SYSTEM_HANDOVER.md`
- 索引：`~/.claude/memory/INDEX.md`
