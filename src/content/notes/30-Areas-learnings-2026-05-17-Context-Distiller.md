---
_slug: 30-Areas-learnings-2026-05-17-Context-Distiller
_vault_path: 30-Areas/learnings/2026-05-17-Context-Distiller.md
title: Context Distiller 回顧｜2026-05-17
date: 2026-05-17
tags:
- learnings
- context-distiller
created: '2026-05-17'
updated: '2026-06-15'
type: learning
status: budding
---

# Context Distiller 回顧｜2026-05-17

## 本次複習範圍

- 4 場 user session + 3 場 cron session
- 重點深挖：session_195527、session_195638、cron_b48ea

---

## 新發現：Code Quality Sensor CQ-05 Regex Bug

**問題**：`\b` 無法跨越 snake_case 的 `_`，因為 `_` 屬於 `\w`，所以 `\bexec` 永遠不會在 `_` 前觸發。

**正確寫法**：
```python
("CQ-05", r"(?<![a-zA-Z0-9_'])exec\((?!s)", 1),
```

**還發現**：
- `create_function`（sqlite3 API）和 p5.js `Function` 是 CQ-05 的 false positive，已修 regex
- Blueprint 與實際實作脫節：源文件有 `eval`，但實作只留 `exec`（`exec` 已含義覆蓋 `eval`）

**相關**：Blueprint CQ-09 min-length 應為 `{31,}` 非 `{8,}`

---

## 新發現：Assistant Personality Say-Do Gap 具體案例

- 「口頭預告要問 Talos」= 欠債，變成等 user 第二次 prompt 才真的做
- 改進方向：actionable 的事項要嘛立刻做，要嘛不說

---

## 新發現：Hermes 交付驗收協議 v1

存在於 cron session `c72909`，但未進入正式 skill 系統。

---

## 備註

- `heartbeat-v2-autonomous-maintenance` 已在 session 中更新（regex 修復 + blueprint 同步）
- `assistant-personality` 已在 session 中 patch say-do gap 段落
- cron session `b48ea` 對比了三個錯誤處理策略（Talos/Ralph/Heartbeat），Heartbeat 的 severity escalation 架構最完整
