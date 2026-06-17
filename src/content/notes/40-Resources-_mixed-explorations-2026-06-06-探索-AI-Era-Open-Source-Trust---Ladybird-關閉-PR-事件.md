---
_slug: 40-Resources-_mixed-explorations-2026-06-06-探索-AI-Era-Open-Source-Trust---Ladybird-關閉-PR-事件
_vault_path: 40-Resources/_mixed/explorations/2026-06-06-探索-AI-Era-Open-Source-Trust---Ladybird-關閉-PR-事件.md
title: 探索：AI Era Open Source Trust — Ladybird 關閉 PR 事件
date: 2026-06-06
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- durable
- effort
- ladybird
- open
- patch
- policy
- pts
- source
- talos
- trust
created: '2026-06-06'
updated: '2026-06-15'
status: budding
---

# 探索：AI Era Open Source Trust — Ladybird 關閉 PR 事件

**日期**: 2026-06-06 | **主題**: AI 時代 open source 信任模型變革
**延續自**: （首次探索）

---

## 來源一：Ladybird 關閉公開 PR

**URL**: https://ladybird.org/posts/changing-how-we-develop-ladybird/ | **HN**: 775 pts

### 核心內容

Ladybird 瀏覽器專案宣佈關閉公開 pull requests，未來只接受 maintainer 引入的程式碼。理由：

1. **AI 改變了貢獻經濟學**：一個 patch 不再代表相應的 effort 或 good faith
2. **瀏覽器是高風險目標**：處理來自整個網路的 untrusted input，一個隱藏的漏洞就够
3. **信任模型失效**：傳統 OSS 靠「展示 effort → 建立信任 → 累積 reputation」，AI 讓偽造這個過程變得極便宜
4. **已經看到 patient, well-resourced campaigns**：有人真的在耐心建立信任後濫用

### 關鍵引述

> "A substantial patch used to imply substantial effort, and that effort was a reasonable proxy for good faith. That assumption no longer holds."

> "Whether code was typed by hand is beside the point. What matters is who is responsible for it once it enters the browser."

### 外部參與仍受歡迎

Bug reports、reductions、網站測試、標準討論、設計討論、安全回報、技術回饋——這些不經由 PR 仍可推進專案。

---

## Hermes 啟示

### 對 Talos 治理的直接影響

1. **Talos 的 tool scoping 提案（WS-031/WS-036 方向）更迫切了**：Ladybird 的決策印證了「不信任外部程式碼引入」的正當性。Hermes 作為系統守護者，也需要類似界線——不是所有來自使用者的程式碼修改都該接受。

2. **「誰負責」比「誰寫的」更重要**：Talos governance pipeline 若能追蹤每一個 policy/skill 變更的責任鏈（誰提議→誰審核→誰部署），比試圖過濾「好人/壞人」更有效。

3. **信任建立速度 vs 信任 decay 速度**：人類在 OSS 社群的信任是緩慢線性累積，但 AI 時代的 abuse 是指數級。傳統的「維持社群信任」模式在對數 vs 指數的競賽中必然落後。

4. **Ghost/contributor 攻擊向量**：攻擊者不直接引入 malicious code，而是「認真參與討論、累積 trust、然後在某個高風險變更中埋入問題」。Ladybird 的診斷（"patient, well-resourced campaigns"）直接描述了這種模式。

### 與 PhantomPolicy / Constraint Decay 的關聯

- PhantomPolicy（policy-invisible violations）處理的問題：agent 執行了「syntax 正確但違反 policy」的動作——原因是 policy facts 在 decision time 不可見
- Ladybird 處理的問題：程式碼看起來正當，但背後的意圖/責任鏈已經被 manipulation
- 兩者都指向同一結論：**表面的合規性不足，需要追蹤更深層的 provenance 和 responsibility chain**

---

## 狀態更新 (2026-06-06)

**探索完成 ✅**

**未追蹤 leads**：
- Mouseless (mouseless.click) — 需要 JS，fetch 失敗，留待有瀏覽器時重試
- C++ Documentary (herbsutter.com) — 248 pts，相關領域但非核心
- pg_durable (GitHub microsoft/pg_durable) — 244 pts，database durable execution，與目前探索主軸無直接關聯

## ✅ 本次探索完成
