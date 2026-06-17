---
_slug: 40-Resources-_mixed-explorations-2026-05-16-James-Shore--AI-Coding-Agent-必須降低維護成本
_vault_path: 40-Resources/_mixed/explorations/2026-05-16-James-Shore--AI-Coding-Agent-必須降低維護成本.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 19:\n    title: James Shore: AI Coding Agent 必須降低維護成本\n            \
  \          ^"
_raw_fm: '

  title: James Shore: AI Coding Agent 必須降低維護成本

  date: 2026-05-16

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [agent, boost, code, codebase, cost, hermes, james, maintenance, review,
  shore]

  created: 2026-05-16

  updated: 2026-06-15

  status: active

  '
title: 'James Shore: AI Coding Agent 必須降低維護成本'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# James Shore: AI Coding Agent 必須降低維護成本

**日期**: 2026-05-16 | **來源**: [You Need AI That Reduces Maintenance Costs](https://www.jamesshore.com/v2/blog/2026/you-need-ai-that-reduces-your-maintenance-costs) (HN 377 pts, 109 comments) | **作者**: James Shore（《The Art of Agile》作者）

## Per-Source Insight

James Shore 的核心論點簡單但尖銳：AI coding agent 讓你寫 code 快兩倍？那你必須讓維護成本降一半。快三倍？維護成本要降到三分之一。否則你不是在加速——你是在借貸，利息是永久的維護負擔。

### 維護成本的複利模型

他用一個 crowd-sourced 估算建立模型：
- 每花一個月寫 code → 第一年要花 10 天維護 → 之後每年 5 天，永久
- 累積 2.5 年後，維護吃掉 >50% 時間
- 如果要靠加人來解決 → 只是延後爆炸，因為新人也在產出新 code

關鍵洞察：**維護成本是 codebase size 的線性函數，但 codebase size 是開發時間的線性函數 → 維護成本隨時間單調上升，且不可逆。**

### AI 加速的陷阱

如果 AI 讓你產出加倍，但維護成本也加倍（因為 code 更難懂、review 更草率）：
- 下個月的維護成本變成 4 倍（2× productivity × 2× maintenance cost multiplier）
- 五個月後生產力回到原點，之後比不用 AI 更差

最毒的是 **lock-in**：停用 AI → 生產力 boost 消失，但累積的維護成本**不會消失**。你被困在 Hotel California。

### Shore 的解法

唯一數學上可行的路徑：**AI 必須以和加速寫 code 相同的倍率降低維護成本**。他沒有給具體解法（承認不知道能不能做到），但暗示方向：
- AI 幫助理解大型系統（正向訊號，但不多）
- 讓維護本身更有效率（即使 code 品質沒提升）
- 降速也是一種選擇：不要追求 speed boost，追求 quality boost

## Hermes 啟發

### 1. Code review 不是禮貌，是生存

Shore 描述的「LGTM, 開會時隨便瞄一眼就 approve」文化，正是我們 `requesting-code-review` skill 在對抗的。Hermes 的 design 已經內建了這個意識：
- Pre-commit review with security scan
- Quality gates before merge
- 這不只是「好習慣」—— Shore 的模型證明這是**經濟必然性**

但目前的 review 主要看 correctness/security，沒有 explicit 的「maintainability」維度。可以考慮加一個 heuristic：複雜度變化率（PR 前後的 cyclomatic complexity diff）。

### 2. Subagent 架構本身就是維護成本管理

我們的 `delegate_task` / worktree isolation 設計，讓 subagent 的 code 天然隔離。這意味著：
- Subagent 產出的 code 如果爛，影響被限制在一個 worktree → merge 前被 review 擋下
- 不像 monolithic agent 一股腦寫進 main branch 然後 accumulate tech debt
- **Isolation = maintenance cost firewall**

這是 Shore 沒提到的戰術層解法：不是讓 AI 寫出更好維護的 code，而是讓爛 code 更難進入 codebase。

### 3. 成本追蹤需要「維護成本」維度

Hermes 目前追蹤 token cost（`cost_24h`），但 Shore 的論點暗示我們需要一個**更長期的成本視角**：
- Token cost 是「開發成本」
- 但真正的成本是「開發 + 維護」的累積
- 一個 PR 的 token cost $0.01，但後續三年維護可能 $100（以 engineering time 計）
- 目前的 cost tracking 完全看不到這個維度

### 4. 「重開 conversation」的習慣已經對了

Heartbeat 最近的探索筆記（Expensively Quadratic）建議重開 conversation 來省 cache cost。Shore 從另一個角度支持這個模式：**短 conversation = 小 scope = 容易 review = 低維護風險**。兩條思考線殊途同歸。

## 未追蹤

- James Shore 的原始 spreadsheet model（文章中有連結，值得拉下來玩參數）
- 「AI 輔助理解大型系統」的工具類別（Shore 提到有零星正面訊號，但沒有展開）

## ✅ 本次探索完成

