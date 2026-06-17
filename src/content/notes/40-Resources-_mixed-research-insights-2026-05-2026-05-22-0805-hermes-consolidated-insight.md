---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-22-0805-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-22-0805-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- architecture
source: multi
created: '2026-05-23'
confidence: high
title: RAIL × Hermes × MCP — 工具發現架構的收斂與分歧
updated: '2026-06-15'
type: research
status: budding
---

# RAIL × Hermes × MCP — 工具發現架構的收斂與分歧

**消化筆記**: 2026-05-23-rail-hermes-architectures-hn-anti-ai, 2026-05-23-rail-c-abi-cross-language-bridge-deep-dive

兩篇同源探索（RAIL protocol 系列）揭露了不同 agent 工具整合架構的深層模式。

## Cross-Cutting Theme 1: 工具描述 schema 是所有架構的隱形瓶頸

**支援筆記**: 2026-05-23-rail-hermes-architectures-hn-anti-ai, 2026-05-23-rail-c-abi-cross-language-bridge-deep-dive

RAIL（app-as-tool-host）、MCP（client-server discovery）、Hermes（agent-as-hub）三種架構看似完全不同，但核心問題一致：**「這個實體能做什麼、如何描述、如何被發現」**。

| 架構 | 工具發現方式 | 描述schema |
|------|------------|-----------|
| Hermes | agent 主動呼叫 static definitions | 人工寫 schema |
| RAIL | app 反射自動掃描（RTTR） | auto-generated + 微調 |
| MCP | 標準化 registry + JSON-RPC | static with negotiation |

RAIL 的 RTTR reflection 比 Hermes 的 static schema 更自動化——但犧牲了網路能力。兩篇筆記湊在一起才看清楚：**Hermes 現在的人工 schema 寫法是瓶頸，未來需要一個 reflection-based discovery layer，類似的 RAIL 的 Custom Dispatcher pattern 可直接參考**。

**可行動下一步**: 在 `heartbeat/` 目錄下實驗一個 `tool_discovery.py` 腳本，用 `inspect` module 掃描指定 Python modules 的 public functions，自動生成符合 MCP schema 格式的 tool definitions。測試口：用此方式自動發現 `scripts/heartbeat/actions.py` 中所有 `action_*` 函式。

---

## Cross-Cutting Theme 2: 威脅模型粒度決定對策有效性——不是所有「防禦」都適用同一套邏輯

**支援筆記**: 2026-05-23-rail-hermes-architectures-hn-anti-ai

HN thread 的 CSS honey-pot（用隱形文字檢測 AI）被批評的核心原因：它假設攻擊者是 headless browser，實際上多數 LLM comment 是 copy-paste 而來的。**威脅模型錯了，對策就浪費**。

這與 Hermes 的 sanitize_fetch.py 直接相關——它在處理 fetch 輸出中的 zero-width chars 和 HTML cruft，但真正威脅（targeted prompt injection）需要的是路由層隔離，不是字元清理。

同時，HN 社群對「抵抗改變」的正面評價（Facebook 追逐每個 trend 但失敗，HN 存活了 20 年）與 Hermes heartbeat 的設計哲學高度共鳴：slow to change、methodical about proposals、values stability over feature velocity。

**可行動下一步**: 在 `maps/heartbeat.md` 的 Threat Model 章節加一行：「sanitize_fetch.py 專門針對 fetch 輸入的技術雜訊（HTML entities, zero-width chars），不針對 prompt injection——後者由 routing layer 處理」，明確區分兩個不同威脅的對應層。

---

## Cross-Cutting Theme 3: C-ABI 跨語言橋接是 Hermes 整合 Rust tools 的可行路徑（medium confidence）

**支援筆記**: 2026-05-23-rail-c-abi-cross-language-bridge-deep-dive, 2026-05-23-rail-hermes-architectures-hn-anti-ai

RailBridge.Native 用 Native AOT 編譯的 C# DLL + ctypes/ffi-napi 呼叫模式，解決了「不同語言如何呼叫同一個原生 library」的問題。這在 Hermes 尚未遇到（還沒整合 Rust tools），但遲早會遇到。

RAIL 的 Custom Dispatcher pattern（手動 command routing for legacy apps）也是 Hermes 動態 routing 需求的前車之鑑。

**可行動下一步**: 追蹤 `obliteratus` 相關的 Rust tool 整合需求，若有需要，用 RAIL 的 ctypes bridge 作為實驗起點，先在 `scripts/` 下做一個純 Python 的 FFI wrapper 測試。

---

*Confidence: high（2 notes 交叉驗證，Theme 1 有架構文件實證，Theme 2 有 HN community 實例）*