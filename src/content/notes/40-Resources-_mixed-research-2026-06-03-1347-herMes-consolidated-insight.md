---
_slug: 40-Resources-_mixed-research-2026-06-03-1347-herMes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-03-1347-herMes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-03'
confidence: medium
title: Hermes Agent Reliability — Cross-Note Synthesis
updated: '2026-06-15'
type: research
status: budding
---

# Hermes Agent Reliability — Cross-Note Synthesis

**消化筆記**: 2026-06-02-rlm-paper-reinforcement-codeRLM, 2026-06-03-forge-gambit-agent-harness

兩個.note 獨立在同一天探索「LLM Agent 可靠性」的不同面向，現在放在一起看，浮現兩個 Architecture Pattern。

---

## Cross-Cutting Theme 1: Proxy Guardrails + Eval Harness 雙層可靠性架構

**支援筆記**: 2026-06-02-rlm-paper-reinforcement-codeRLM, 2026-06-03-forge-gambit-agent-harness

Forge（687pts HN）提供 L1 guardrail：**ResponseValidator + Rescue parsing + Synthetic respond tool**，在 tool call 到達 client 前做結構性校正與注入，不信任模型 self-regulate。

Gambit（91pts HN）提供 L2 eval harness：**scenario → trace → grade → regression suite**，驗證 agent 行為是否合規，不是靠模型主觀判斷。

這兩個框架的匯聚點：
- Forge = 強制层（enforcement），杜絕錯誤輸出流出
- Gambit = 測量层（measurement），客觀量化行為品質
- 一起構成：enforcement + measurement 的雙層可靠性模式

Note 1 的 RLM 架構隱含同一個模式：symbolic handle 是 enforcement（強制模型用變數而非 context dump），metadata + recursion 是 measurement（結構化資訊流讓模型能推理自身狀態）。CodeRLM 的 symbol graph 也是 enforcement：查到符號才能操作，沒有捷徑。

**可行動下一步**: 在 `/srv/hearth/` 替 Talos governance pipeline 起草一份雙層架構設計文件：
- L1: 參考 Forge 的 proxy 模式 + ResponseValidator + Synthetic respond tool injection，設計 evaluation-threshold enforcer 的核心機制（用一個 skill draft）
- L2: 參考 Gambit 的 deck.md scenario + grading 模式，設計 Hestia/Talos 技能矩陣的 functional evaluation harness（用一個 skill draft）
- 產出放到 `~/obsidian-vault/research/YYYY-MM-DD-talos-governance-architecture.md`

---

## Cross-Cutting Theme 2: 結構性遺忘 vs. 時間性遺忘（Symbolic Staleness）

**支援筆記**: 2026-06-02-rlm-paper-reinforcement-codeRLM, 2026-06-03-forge-gambit-agent-harness

Note 1 的 heartbeat_learning.py 目前使用 time-based decay，这是 temporal staleness：只靠時間決定 distillate 是否過期，無法捕捉新 distillate 與舊的矛盾。

RLM paper 的啟發：construct relationship graph where nodes = distillates, edges = contradictions/supersedes。新 distillate 产生 contradiction edge → invalidate old node's confidence。這是 **structural staleness**：由資訊內容與圖結構決定，不靠時鐘。

Note 2 的 Reinforcement Studio drift detection 正是這個模式的具體實例：`verify_token() now takes a device_id` — symbol-level drift，不是時間驅動的，是 signature 改變驅動的。

兩篇.note 合在一起看的 pattern：Hermes 的 memory + heartbeat 系統，目前是 temporal，等到有一個 relationship graph（distillate graph 或 symbol graph），才能做到 structural staleness。

**可行動下一步**: 替 WS-035 drift penalty 設計 document，spec out：
- 圖結構：nodes = distillates（含 timestamp, domain, contradicted_by edges）
- 攪動檢測演算法：新 distillate 入住時，query graph 找矛盾（same concept, earlier timestamp）
- 觸發時行為：標記舊 node confidence = 0，不刪除（保留 lineage），讓 reasoning layer 能看到完整的概念演化而不只是最新狀態
- 產出放到 `~/obsidian-vault/research/YYYY-MM-DD-structural-staleness-design.md`

---

## Observation: 兩篇.note 的 MECE 性

 Note 1 探索「LLM 怎麼處理超長 context」與符號系統合約（RLM, CodeRLM）
 Note 2 探索「外部系統怎麼確保 agent 行為可靠」與驗證回路（Forge, Gambit）

這兩條線構成 Agent Reliability 的完整領域圖譜：
- **Left side**: 模型的單方推理能力（symbolic recursion, context compression）
- **Right side**: 外部的治理與測量（guardrails, eval harness）

Talos governance 如果要把這兩條線都納入，原則是：模型能力邊界要靠外部 enforcement 補償，外部治理要靠內部の reasoning 支援。兩個 note independent discovery 同一個原則，印證了這個領域的核心張力。