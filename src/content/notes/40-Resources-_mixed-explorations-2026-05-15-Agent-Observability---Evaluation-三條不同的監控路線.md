---
_slug: 40-Resources-_mixed-explorations-2026-05-15-Agent-Observability---Evaluation-三條不同的監控路線
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-Agent-Observability---Evaluation-三條不同的監控路線.md
title: Agent Observability & Evaluation：三條不同的監控路線
date: 2026-05-15
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- bench
- benchmark
- cua
- hermes
- llm
- observability
- openllmetry
- otel
- voker
created: '2026-05-15'
updated: '2026-06-15'
status: budding
---

# Agent Observability & Evaluation：三條不同的監控路線

**日期**: 2026-05-15 | **來源**: HN Algolia → Voker, Cua-Bench, OpenLLMetry

---

## Source 1: Voker — Agent Analytics for Product Teams

**文章**: [voker.ai](https://voker.ai) (Launch HN, 59 pts, 22 comments)
**定位**: YC S24 startup，做 agent analytics 的商業產品

### 核心命題

不是給工程師的 trace viewer，而是給 PM 和業務團隊的 agent 績效儀表板。

三個核心 metric：

| Metric | 對應問題 |
|--------|---------|
| **Intents** | 使用者想要什麼？（自動分類對話意圖） |
| **Corrections** | 使用者在哪裡糾正 agent？（摩擦點偵測） |
| **Resolutions** | agent 是否解決了使用者的意圖？（成功率） |

**技術面**：輕量 SDK（`pip install voker`，兩行整合），支援 OpenAI/Anthropic/Gemini + LangChain/CrewAI/Vercel AI SDK。Self-hosted 僅 Enterprise tier。

**定價**：Free (2K events) → $80/mo (20K) → $400/mo (2M) → Enterprise。一個 conversation 平均 ~15 events。

### 值得注意的設計取捨

1. **不追蹤 technical metrics（latency, token count, error rate）** — Voker 公開頁面完全沒提到這些。他們的賭注是：產品團隊在乎「agent 有沒有幫到使用者」，不在乎「哪個 API call 慢了 200ms」。
2. **Correction detection 是殺手級功能**：偵測使用者說「不對，日期錯了」→ 量化使用者挫折。這比 error log 更有訊號——error log 告訴你系統壞了，correction detection 告訴你體驗壞了。
3. **自有模型做 intent classification**（非 LLM-based？）— 定價 $0 就能用 intent detection，成本結構不像每次 call LLM。

---

## Source 2: Cua — 全端 Computer-Use Agent 基礎建設

**GitHub**: [trycua/cua](https://github.com/trycua/cua) (Show HN, 40 pts, 8 comments)
**定位**: 不是 benchmark，是整個 computer-use agent 的基礎設施（benchmark 只是其中一個產品）

### 生態系全景

```
Cua Driver ─── 背景 macOS 操控（不搶游標、不搶 focus）
Cua Sandbox ── 跨 OS ephemeral VM（Linux/macOS/Windows/Android）
CuaBot ────── 多人協作 sandbox（H.265 桌面串流、共用剪貼簿）
Cua-Bench ─── Benchmark datasets（OSWorld, ScreenSpot, Windows Arena）
Lume ──────── macOS VM on Apple Silicon（Virtualization.Framework）
```

### Benchmark 設計

三個現成 dataset + 自訂：

```
cb run dataset datasets/cua-bench-basic --agent cua-agent --max-parallel 4
```

**Cua-Bench 的核心設計**：給 agent 一個 sandbox VM → 給一個自然語言任務（「打開 Chrome，搜尋 X，點第一個結果」）→ 測 completion rate 和 trajectory quality。

### 三個有趣的觀察

1. **Cua Agent 的內部架構**提到用 OmniParser（Microsoft 的 screen parsing model，CC-BY-4.0）做視覺理解。但 OmniParser 依賴 ultralytics（AGPL-3.0）— license minefield。
2. **Cua Driver 的 "background" 模式**是真正的技術突破：macOS 上不搶游標的 GUI automation。大多數 agent 會搶你的滑鼠（所以需要 VM），Cua Driver 在本地就能做到。
3. **從 benchmark provider 變成全端平台**：開始只是 Cua-Bench，現在變成 sandbox + agent + driver + VM。這條演化路徑和 LangChain（tool → platform）很像。

---

## Source 3: OpenLLMetry — OpenTelemetry-based LLM Observability

**GitHub**: [traceloop/openllmetry-js](https://github.com/traceloop/openllmetry-js) (Show HN, 102 pts, 23 comments)
**定位**: 用 OpenTelemetry 標準做 LLM observability

### 設計哲學

> "You don't need to adopt new tools for LLM observability"

核心賭注：LLM observability 不需要新的 protocol——OTel 的 span/trace/metric 模型可以直接套用。他們的 LLM semantic conventions 正在被納入 OpenTelemetry 官方標準。

**兩行啟用**：
```js
import * as traceloop from "@traceloop/node-server-sdk";
traceloop.initialize();
```

### Instrumentation 範圍

| 類別 | 已支援 |
|------|--------|
| LLM Providers | OpenAI, Anthropic, Cohere, Vertex AI, Bedrock |
| Vector DBs | Pinecone, Chroma, Qdrant |
| Frameworks | LangChain, LlamaIndex |
| Export targets | Datadog, Honeycomb, Grafana, New Relic, Splunk, SigNoz, any OTel collector |

### 關鍵設計決策

1. **不自己造 protocol**：直接用 OTel。優點是生態整合零成本（任何支援 OTel 的後端都能吃）；缺點是 OTel 的 tracing model 對 LLM call 不是最自然的抽象。
2. **Semantic conventions 標準化**：他們推動的 LLM span attributes 規範（`gen_ai.request.model`、`gen_ai.usage.input_tokens` 等）正在進入 OTel 標準。這是正確的 long game——一旦標準化，所有 LLM observability 工具都能互操作。
3. **不強制你用自己的後端**：可以 export 到任何 OTel collector。這是和 LangSmith/Helicone 等封閉平台的本質差異。

### OpenLLMetry 的隱含論點

選擇 OTel 作為 LLM observability 的底層，等於主張：**LLM observability 是 distributed tracing 的子問題**。這是一個有爭議的論點——LLM call 有很多 distributed tracing 沒有的語義（prompt template、token count、cache hit/miss、streaming vs non-streaming），需要擴充 semantic conventions。

---

## 跨文章 Synthesis

### 三條路線的對比

| | Voker | Cua-Bench | OpenLLMetry |
|---|---|---|---|
| **量什麼** | 業務成效（intent/correction/resolution） | 任務完成率（GUI task completion） | 技術 telemetry（span/trace/metric） |
| **對象** | Product teams | Agent researchers/devs | Dev/SRE teams |
| **底層技術** | 自有分類模型 | Sandbox VM + OmniParser | OpenTelemetry |
| **商業模式** | SaaS ($0-$400/mo) | OSS (MIT) + cloud sandbox | OSS (Apache 2.0) + Traceloop cloud |
| **開放性** | 封閉平台 | 開放 benchmark, 封閉 sandbox infra | 開放 protocol, 開放 SDK |

### 對 Hermes Heartbeat 的定位啟發

三條路線的對比讓 Hermes heartbeat 的定位更清楚：

```
產品分析層   ← Voker（用量者行為、意圖解決率）
   ↑ 我們沒有
任務評估層   ← Cua-Bench（task completion rate）
   ↑ 我們沒有
技術健康層   ← Hermes Heartbeat（error rate, severity, retry）
   ↑ 我們有，但只用在家裡
開放遙測層   ← OpenLLMetry（span/trace/metric via OTel）
   ↑ 我們沒有
```

**Hermes 的 heartbeat 是「技術健康層」的高度特化版本**——它知道 Hermes 的內部架構（config drift、script integrity、pytest canary、system map drift），這是 OpenLLMetry 這種通用方案做不到的。但 Hermes 缺少上面兩層：我們不知道 agent 的回應品質好不好（Voker 的 correction detection）、不知道任務是否真的完成了（Cua-Bench 的 task completion）。

### 務實的路徑

1. **不需要 OTel**：一個人用的 agent，不需要 export 到 Datadog。heartbeat 的 custom tracing（severity.json + action_log + state file）已經夠用。
2. **但可以借 Voker 的 correction detection 概念**：heartbeat 可以偵測「agent 自我修正的頻率」作為一個新的 health metric。如果在一個 session 裡 LLM 重複修正自己的輸出 > N 次 → 可能是 prompt rot 或 model degradation。
3. **Cua-Bench 的啟發**：為 Hermes 建立一個小的 self-eval benchmark（5-10 個任務，自動評分），不是為了跟別人比，而是 detect regression。「上次心跳修 system map drift 花了 1 輪，這次花了 3 輪 → something changed」。

---

## 未追蹤但值得注意

- **Voker 的 HN 討論**（22 comments）— Launch HN 通常有競品比較和創辦人 Q&A，可能有更多 agent analytics 生態的討論。等需要深入了解 agent analytics 市場時回頭看。
- **Cua Driver 的 background macOS automation 技術** — README 說「不搶游標、不搶 focus」，這在 macOS accessibility API 上很難做到。技術細節在 `libs/cua-driver/README.md`。
- **OmniParser (Microsoft)** — Cua 用的 screen parsing model。如果 Hermes 未來需要做任何 GUI-related task，這是關鍵依賴。但 license (CC-BY-4.0 for OmniParser, AGPL-3.0 for ultralytics dependency) 是問題。
- **OpenTelemetry LLM Semantic Conventions** — OTel community 正在標準化 LLM spans。如果 Hermes 未來需要和任何外部 observability 工具整合，這會是 entry point。GitHub: `open-telemetry/community` → `projects/llm-semconv.md`。
- **Langfuse**（Voker 提到與之共存）— OSS LLM tracing platform，和 OpenLLMetry 路線不同（有自己的 protocol 而非 OTel）。值得和 OpenLLMetry 對比。

---

## ✅ 本次探索完成

