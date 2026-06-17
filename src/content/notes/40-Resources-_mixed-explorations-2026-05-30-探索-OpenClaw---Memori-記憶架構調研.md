---
_slug: 40-Resources-_mixed-explorations-2026-05-30-探索-OpenClaw---Memori-記憶架構調研
_vault_path: 40-Resources/_mixed/explorations/2026-05-30-探索-OpenClaw---Memori-記憶架構調研.md
title: 探索：OpenClaw + Memori 記憶架構調研
date: 2026-05-30
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- com
- hermes
- https
- hybrid
- llm
- memori
- memory
- openclaw
- pycoclaw
created: '2026-05-30'
updated: '2026-06-15'
status: budding
---

# 探索：OpenClaw + Memori 記憶架構調研

**日期**: 2026-05-30 | **來源**: HN Algolia (LLM agent memory optimization) | **類型**: 主題式延續

## Per-Source Insights

### 1. PycoClaw — OpenClaw for Embedded ($5 Microcontroller AI Agent)
**URL**: https://pycoclaw.com/ | **HN Points**: 31

**核心發現**:
- **硬體 + 軟體一體的 AI Agent**：完整 OpenClaw agent 跑在 $5 ESP32 微控制器上，MicroPython runtime
- **Dual-loop architecture**：完整推理引擎，遞迴 tool calls、context compaction、雙迴圈架構
- **Hybrid Memory**：TF-IDF + vector search hybrid（Persistent Memory），SD card backed。與主流純向量檢索不同，PycoClaw 選擇 TF-IDF + vector 的混合方案，可能因為嵌入式裝置的資源限制
- **ScriptOs Skills**：Agent 可自主搜尋/安裝 ScriptoHub 上的 skill packs（感測器驅動、硬體整合、顯示 widget），不需要手動設定
- **對比其他 embedded agent**：PycoClaw 是唯一做到 Full dual-loop + scripted runtime + LVGL touchscreen 的embedded 方案

**Hermes 啟發**:
- **TF-IDF + vector hybrid 的動機**：嵌入式記憶受限環境下的取捨。heartbeat_learning.py 若在 memory-constrained 情境，可用類似 hybrid approach
- **ScriptOs skill discovery**：agent 自主發現、安裝 skill — 與 Hermes skill system 的方向一致，但 OpenClaw 實現了完全自主的 discover → install flow

### 2. Memori — Agent-Native Memory Infrastructure
**URL**: https://github.com/GibsonAI/memori | **GitHub Stars**: 15.1k | **最新**: 2026-05-28 (v3.3.6)

**核心發現**:
- **LoCoMo benchmark**：81.95% accuracy，average 1,294 tokens/query（僅 4.97% full-context footprint）。相比 Zep、LangMem、Mem0 表現更好，context cost 降低 20x+
- **三層 augmentation**：entity / process / session，各有 attributes、events、facts、preferences、relationships、rules、skills
- **Hermes Agent 原生整合**：`hermes-memori` pip package 已存在，可作為 memory provider
  ```
  pip install hermes-memori
  hermes-memori install
  hermes config set memory.provider memori
  ```
- **支援 LLM**：Anthropic, DeepSeek, Bedrock, Gemini, Grok, OpenAI
- **支援 Framework**：Agno, LangChain, Pydantic AI
- **OpenClaw Plugin**：`openclaw plugins install @memorilabs/openclaw-memori` — 自動捕捉對話和 agent execution 後的結構化記憶

**Hermes 啟發**:
- **`hermes-memori` package 直接可用**：Talos 若要升級 memory 架構，可評估 `hermes-memori` 而非從零實作 WS-035
- **LoCoMo benchmark 數字可直接作為 WS-035 drift penalty target**：81.95% accuracy / 4.97% token footprint 是量化目標
- **三層 augmentation schema**（entity/process/session）比目前 heartbeat learning 的 single-layer distillate 更結構化，考慮移植這個 schema

## Cross-Article Synthesis

1. **記憶系統的兩條路線**：PycoClaw 用 TF-IDF + vector（在資源受限環境），Memori 用結構化 augmentation（在 production LLM API 層）。兩者都指向同一結論：純向量檢索不是最優解，結構化 > embedding。
2. **Agent memory 逐漸收斂到「結構化勝過純嵌入」**（與 2026-05-25 exploration synthesis 一致）。YantrikDB、Mem0、agentmemory、Engram、Memori 全都收斂到這個結論。
3. **`hermes-memori` 是 WS-035 的潛在捷徑**：若 `hermes-memori` 已實作 LoCoMo benchmark 等級的架構，Talos 可能不需要從零建 drift penalty 機制，直接整合現有 package 即可。

## 未追蹤 Leads
- https://github.com/liquidos-ai/AutoAgents — composable middleware for LLM inference (PyPI: `autoclaw` exists)
- https://memorilabs.ai/docs/memori-byodb/ — Memori BYODB 架構，Talos 可能用於本地部署
- https://github.com/GibsonAI/memori/blob/main/benchmarks/loco — LoCoMo benchmark 詳細方法論

## ✅ 本次探索完成

