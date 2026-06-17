---
_slug: 40-Resources-_mixed-explorations-2026-06-18-cortex-vortex-review-_review
_vault_path: 40-Resources/_mixed/explorations/2026-06-18-cortex-vortex-review/_review.md
title: Cortex / Vortex 整站評估（2026-06-18）
type: resource
status: seedling
created: '2026-06-18'
updated: '2026-06-18'
---

# Cortex / Vortex 整站評估（2026-06-18）

> 評估者：Talos（Claude Code session）
> 來源：https://hangsau.github.io/cortex/vortex/
> 方法：Playwright headless 逐頁瀏覽 + 摘錄 + 截圖
> 立場：邊逛邊寫，最後整合

---

## 評估目標

- 結構完整性
- 內容深度
- 受眾可達性
- 技術債（SEO、效能、可達性）
- 視覺/互動品質
- 知識確定性

---

## 紀錄

### 已逛（截至 2026-06-18 00:35）

**全站 71 頁**，分佈：
- `/cortex/vortex/`：50 頁（主計畫）
  - 索引 1 + 6 泳式 + technica 5 + instructional 12 + adm 3 + 其他
- `/cortex/library`：~30 頁（3 本書，24 章主力）
- `/cortex/notebook`：2 頁（**實質空殼**，各 36 字）
- `/cortex/temperament`：1 頁（599 字，兒童九種氣質）

### 觀察 1：四個入口頁（psychology / periodization / freestyle / levels）

**共同設計語言**：
- 「概覽 → 主題列表 → 點擊就地展開不換頁」（SPA 風格，零跳轉）
- **L 級標籤**全站貫穿
- **確定性色碼**（🔵🟢🟡🟠🔴）全站一致
- **公開層 / 教練工具分層**（感知判讀語、診斷訊號明確標「不公開」）
- 概念數量標註（「7 概念」「8 概念」）

**psychology 頁**（2008 字）：
- 8 主題沿 L0→L6 脊椎排序，不是平鋪
- 三帶分層：L0–L2 初學 / L0–L6 貫穿 / L3–L6 進階
- 設計成熟度：**高**。把心理學整合到水感框架，罕見

**periodization 頁**（831 字）：
- 5 派辯論（線性/板塊/極化/個體化/反向）— 不當定論教
- 明確「公開週期化理論，不含感知診斷」分層
- 連結 ADM「48 週年度計畫」

**freestyle / levels 頁**（446/569 字）：
- 極簡設計，只放導航 + 一句核心命題
- 「划手距離是技術指標，划頻是生理指標」（freestyle）
- 「水感是一級一級長出來的感知，不是靠教動作教出來的」（levels）

**這四頁共同的強項**：
1. **設計極簡，不囉嗦** — 入口頁字數都在 1k 以內，讓讀者點進去
2. **分層誠實** — 公開 vs 教練工具的界線清楚
3. **認知負荷低** — 一次只看一個概念數量

**這四頁共同的問題**：
1. **左欄「導覽 / 0 概覽 / 1 ...」這套編號讀起來像 markdown 原始碼流出** — 是 SPA 組件狀態的副作用，但對讀者不友善。應該是視覺化的 sidebar，不該是純文字 list
2. **「點任一動作就地展開，不換頁」重複出現 4 次** — 說明可能這套 SPA 展開有 bug 或讀者沒發現，得多處提示

---

