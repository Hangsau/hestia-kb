---
_slug: 40-Resources-_mixed-explorations-2026-06-04-Gemma-4-12B---Elixir-v1-20---2026-06-04
_vault_path: 40-Resources/_mixed/explorations/2026-06-04-Gemma-4-12B---Elixir-v1-20---2026-06-04.md
title: Gemma 4 12B + Elixir v1.20 — 2026-06-04
date: 2026-06-04
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- audio
- elixir
- encoder
- free
- gemma
- google
- gradual
- https
- type
- vision
created: '2026-06-04'
updated: '2026-06-15'
status: budding
---

# Gemma 4 12B + Elixir v1.20 — 2026-06-04

**延續自**: 無（今日新規探索）

---

## Gemma 4 12B: Encoder-Free Multimodal Model

**來源**: [MarkTechPost](https://www.marktechpost.com/2026/06/03/google-deepmind-releases-gemma-4-12b-an-encoder-free-multimodal-model-with-native-audio-that-runs-on-a-16-gb-laptop/) | HN 642pts | Apache 2.0

### Architecture — Encoder-Free Design

所有先前的 mid-sized Gemma 模型都用獨立的 Transformer encoders 處理 vision 和 audio。這些 encoders 增加了 latency 和參數 overhead：
- Medium-sized Gemma 4 models: 550M vision encoder
- E2B/E4B models: 300M audio encoder
- **Gemma 4 12B: 全部移除**

**Vision embedder (35M 參數)**：
- 原始圖片切成 48x48 pixel patches
- 每個 patch 透過單一矩陣乘法投影到 LLM hidden dimension
- **無 attention 層** — 每個 patch 獨立處理
- 位置編碼：factorized X/Y coordinate lookup（兩個獨立的 learned matrices），patch (x,y) 的位置向量是 X[x] + Y[y]
- 整個 vision pipeline 就是：patch split → 單一 matmul → 加位置向量 → normalization

**音頻 wave projection（直接音頻波投影）**：
- 原始 16 kHz audio 切成 40ms frames（每 frame 640 個值）
- 每個 frame 線性投影到與文字 token 相同的 embedding space
- **無 feature extraction、無 conformer layers**
- LLM 既有的 RoPE 處理 1-D 時序序列
- E2B/E4B 的 12 層 conformer encoder 全部移除

**統一的 weight space**：
- Fine-tuning（LoRA 或 full tuning）時，vision、audio、text 在單一次 forward pass 中一併更新
- 不再有「凍住的 encoder + 訓練中的 LLM」的不一致問題

### Capabilities

- **ASR + Diarization**：原生 transcription，speaker 分離，無需外部 ASR pipeline
- **Agentic reasoning**：本地跑多步驟 workflow，性能接近 26B MoE 模型
- **Video understanding**：demo 是 5 分鐘 Google I/O keynote，313 frames @ 1FPS，70 tokens/frame
- **Coding**：透過 gemma-skills repo 生成 Gradio app，本地 llama.cpp serve

### Hardware & Ecosystem

- **16 GB VRAM 或 unified memory**（Apple Silicon MacBook）
- Apache 2.0，weights 在 HuggingFace (google/gemma-4-12B-it)
- Inference: llama.cpp, MLX, vLLM, Ollama, SGLang, Unsloth, LM Studio
- 專用 MTP (Multi-Token Prediction) drafter 降低推理延遲

### 與 Hermes/Talos 相關的啟發

1. **架構啟發 — encoder-free 的簡潔性**：Gemma 4 12B 證明了「去掉獨立 encoder、讓 raw input 直接進 LLM backbone」的可行性。這與我們之前探索的「結構化記憶 > 純嵌入檢索」共識呼應——都是朝「更少中介層」的方向收斂。35M vision embedder 的設計（patch split → 單一 matmul）比 550M vision encoder 簡單一個數量級，但功能相當。對於本地端 agent 的 sensor 設計，這種「直接投影」模式可能是值得參考的方向。

2. **記憶整合的統一性**：encoder-free 讓 vision、audio、text 在同一個 weight space，fine-tune 一次更新全部。對於 Hermes 的 multi-modal memory 整合，這代表「統一是終點」的訊號——分立的 encoder 架構遲早會被統一的 model 取代。

3. **本地端 AI 的 practical 進展**：16GB laptop 跑 multimodal agentic workflow 已經是可實現的。這加強了「Edge AI deployment for agents」的方向是正確的，也意味著未來 local memory/retrieval 的效率會比雲端更重要。

---

## Elixir v1.20: Gradually Typed Language

**來源**: [Elixir Blog](https://elixir-lang.org/blog/2026/06/03/elixir-v1-20-0-released/) | HN 481pts

### 核心設計：set-theoretic gradual typing

Elixir v1.20 完成第一個 development milestone：**type inference + gradual type checking，無需 type annotations**。

目標：
- **Sound**：推斷的類型與程式行為對齊
- **Gradual**：包含 `dynamic()` 類型（類似其他語言的 `any()`，但含更嚴格的 semantics）
- **Developer friendly**：set operations（union, intersection, negation）描述類型

### dynamic() 的兩個關鍵 property

**1. Compatibility（兼容性）**：
當 supply 和 accept 的類型「不相交」（disjoint）時才報 violation。Elixir 的 gradual type 只在類型完全不相交時才报错，这样可以避免 false positive。例如 `/` operator 期待 number，但 `dynamic(integer() or binary())` 可以是 integer，所以不报 violation。

**2. Narrowing（窄化）**：
`dynamic()` 在使用時可以被 refinement。当代码访问 `data.a` 和 `data.b` 作为加法操作数时，Elixir 会自动将 `data` narrow 成 map 类型 `{a: number(), b: number()}`。如果代码写错了，比如 `data.a + data`（漏了 `.b`），就会触发 type violation。

### 對 BEAM 生態的影響

- **編譯速度**：v1.20 優化了多核編譯，Elixir 的 build tool 在 synthetic benchmark 中已是 BEAM 家族最快
- **:module_definition 編譯選項**：可設為 `:interpreted` 加速大型專案編譯，不影響磁碟上的 .beam 檔案
- **Type checking**：standard library 中與 tuple/map 相關的函式已大量加入 type inference

### 與 Hermes/Talos 相關的啟發

1. **Gradual typing 對 Agent 程式碼品質的啟示**：Elixir 的 gradual typing 能「找到現有程式碼中的 dead code 和 verified bugs」，不需要 developer 加任何 annotation。這與 WUPHF lint 的「contradiction detection + staleness check」方向類似——都是試圖在沒有明確 schema 約束的情況下，推斷程式碼的狀態並報錯。對於 Hermes 的 self-healing capability，「在沒有完整 type 定義下找到 bug」是一個很實用的目標。

2. **Compatibility vs soundness 的取捨**：Elixir 的方向是「只報 verified bugs，低 false positive」。這對 agent 系統的健康檢查有意義——EVOLVE 的 sensor 不應該對每一個 warning 都上報，而是專注於「確定會出問題」的錯誤，減少噪音。Elixir 的 `disjoint types` 概念或許可以移植成某種「確定性錯誤」 detector。

3. **Narrowing 作為動態推斷的形式**：Elixir 的 `dynamic()` 被使用時會自動 narrowing，根據實際存取欄位推斷具體類型。這與「context 在使用時會被 narrowing」的 agent 行為類似——當 agent 讀取某段 context 後，對其狀態的認知會變得更精確。Narrowing 的機制可能可以用來建模「memory 被 access 後的 confidence 上漲」。

---

## 跨文章 Synthesis

Gemma 4 12B 和 Elixir v1.20 代表了兩個不同的簡化方向：

- **Gemma**：Architecture simplification（移除 encoder layers，統一 weight space）
- **Elixir**：Type system simplification（不需要 annotations，只需 type inference）

共同點：**兩者都在試圖用更少的 explicit structure 達到相同或更好的效果**。Gemma 不需要 vision encoder，Elixir 不需要手寫 type annotations。都是在「減少 developer 的負擔」的同時提升系統能力。

對於 Hermes/Talos 的啟發：
- **工具設計**：類似 encoder-free 的概念，我們是否在某些工具上加了太多層？
- **漸進式系統**：Elixir 的 gradual typing 是從一個動態系統逐步加入靜態保證，這對於正在生長的系統很有參考價值——一開始不需要完整 schema，但逐漸可以推斷並強化。

---

## 未追蹤 Leads

- https://github.com/google-gemma/gemma-skills — Gemma 4 官方 agent skills repository
- https://huggingface.co/google/gemma-4-12B-it — 模型 weights
- https://github.com/statewright/statewright — State machine guardrails（已被 vault 收錄）
- ~~https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemma-4-12b/~~ dead link（MarkTechPost 可用）
- Elixir type system award-winning paper (2023): 可在 arxiv 搜尋 Elixir type system

## ✅ 本次探索完成
