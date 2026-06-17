---
_slug: 10-Daily-2026-05-15-skill-code-gap
_vault_path: 10-Daily/2026-05-15-skill-code-gap.md
tags:
- hermes
- architecture
- system-map
- skill-code-gap
source: session_20260514_220400_d70175
created: '2026-05-15'
title: Skill-Code 斷層：文件層與實作層的溝通問題
updated: '2026-06-15'
type: daily
status: budding
---

# Skill-Code 斷層：文件層與實作層的溝通問題

## 發現過程

在討論 heartbeat 系統時，agent 第一次只讀了 skills（文件層），完全沒發現底層的 `heartbeat/` package、`heartbeat_learning.py`、action log、patterns 等真正引擎。

真相是：`heartbeat_v2.py` 是**純 Python 指令碼，零 LLM 介入**。流程是：

```
cron 觸發 → heartbeat_v2.py 執行 →
  snapshot (收集系統狀態) →
  scoring (六項行動加權計分) →
  select (最高分 + cooldown/backpressure 過濾) →
  execute (對應的 action function) →
  log (寫入 action_log + rotate)
```

## 根本原因

**技能（文件）和程式碼（實作）之間的斷層。** Skills 不參考它們對應的實作檔案路徑，agent 只從 skills 理解系統，結果只看到一半。

## 已修復

System Map Generator (`~/.hermes/scripts/generate_system_map.py`) 已建置，自動產生 `AGENTS.md` + `maps/{9domains}.md`，從 skill frontmatter + script @domain docstrings + cron jobs 提取資訊，讓 agent 能在 session 開始時看到完整地圖。

## 相關筆記

- [[2026-05-15-AGENTS.md 社群實踐研究]]
- [[Heartbeat v2 架構驗證]]
