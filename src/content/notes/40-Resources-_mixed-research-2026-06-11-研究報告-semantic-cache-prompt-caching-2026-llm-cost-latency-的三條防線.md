---
_slug: 40-Resources-_mixed-research-2026-06-11-研究報告-semantic-cache-prompt-caching-2026-llm-cost-latency-的三條防線
_vault_path: 40-Resources/_mixed/research/2026-06-11-研究報告-semantic-cache-prompt-caching-2026-llm-cost-latency-的三條防線.md
tags:
- research
- knowledge
- ai-agent
created: '2026-06-11'
version: 1
source_report: 2026-06-11-semantic-cache-llm-prompt-caching-2026.md
source_url: null
type: research
fingerprint: cache, vcache, gptcache, semantic, firn, rate, prompt, llm, hit, error
title: 研究報告：Semantic Cache & Prompt Caching 2026 — LLM Cost & Latency 的三條防線
updated: '2026-06-15'
status: budding
---

# 研究報告：Semantic Cache & Prompt Caching 2026 — LLM Cost & Latency 的三條防線  

## Version 1 — 2026-06-11

### 核心觀念
**問題**：LLM 推理成本與延遲在 2026 年仍然是 production agent 的頭號瓶頸。三條獨立曲線把這個問題推到前台： - **Anthropic Opus 4.8**：$5/M input + $25/M output。單次工具呼叫 + RAG context 隨便破 50K tokens，5,000 次呼叫就是 $625。 - **GPTCache 上月 PyPI 下載 486,812 次**（pypistats 2026-06-11 截取）—— 比 2025 年同期翻倍，意味著「自己接 cache」已經從進階優化變成 baseline 設定。 - **vCache paper (S…

**洞見**：| 社群 | 產品/論文 | 訊號 | |------|---------|------| | 學術 | vCache (2502.03771v5, 2026-02) | 靜態 threshold 不夠，要 error-bound | | 學術 | C2C (2510.03215, ICLR'26) | KV-cache 本身就是通訊介面 | | 工業界 | GPTCache 486K 月下載、Anthropic 官方 prompt caching | cache 已是 baseline，不是 opt-in | 這個**三源同時**的訊號在之前的 reliability 報告（2026-06-…

### 架構 / 機制
## 2. Core Mechanism

### 三層 cache 架構

```
┌──────────────────────────────────────────────────────┐
│ L0: Provider Prefix Cache                            │
│   • Anthropic cache_control: 5min TTL, 0.1x cost     │
│   • OpenAI automatic caching (2026 起對所有 user 開)  │
│   • 限制：要完全相同的 prefix bytes                   │
└──────────────────────────────────────────────────────┘
                          ↓ miss
┌──────────────────────────────────────────────────────┐
│ L1: Application Semantic Cache                       │
│   • Embed query → cosine sim > τ → return cached     │
│   • GPTCache: 8K stars, 5 種 vector backend           │
│   • 問題：靜態 τ，無 error bound                      │
└──────────────────────────────────────────────────────┘
                          ↓ miss
┌──────────────────────────────────────────────────────┐
│ L2: Verified Semantic Cache (vCache)                 │
│   • Online-learned per-prompt threshold τ*            │
│   • 用 conformal prediction 提供 error-rate guarantee │
│   • 12.5× higher hit rate, 26× lower error rate      │
└──────────────────────────────────────────────────────┘
                          ↓ miss
                  Actual LLM call
```

### vCache 核心：conformal-style online threshold

```python
# 簡化版 vCache policy (from vcache/vcache/policy.py)
from vcache import VCache, VCachePolicy, VerifiedDecisionPolicy

error_rate_bound: int = 0.01   # 1% error budget
policy: VCachePolicy = VerifiedDecisionPolicy(delta=error_rate_bound)
vcache: VCache = VCache(policy=policy)

response: str = vcache.infer("Is the sky blue?")
```

**機制重點**：每個 cached prompt 在線上學習自己的「最近鄰相似度分布」，再根據 conformal 框架計算「τ 應該在哪裡才滿足 user-defined error rate」。換言之，τ 不再是 magic number，而是被 dataset + bound 共同決定的。

### GPTCache 核心：plugin-based similarity backend

```python
# gptcache/adapter/api.py
from gptcache import cache
from gptcache.embedding import Onnx
from gptcache.manager import CacheManager, VectorBase, ObjectBase
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation

# 1) 設定 embedder
cache.init(
    embedding_func=Onnx().to_embeddings,
    data_manager=ManagerBase(
        cache_store=ObjectBase("sqlite"),       # exact-key store
        vector_base=VectorBase("faiss", dimension=768),  # ANN index
        similarity_evaluation=SearchDistanceEvaluation(),
    ),
)

# 2) OpenAI adapter 自動攔截
import openai
openai.api_key = "***"
# 之後所有 openai.ChatCompletion.create 都會先查 cache
```

### C2C (Cache-to-Cache, ICLR'26)：跨模型 KV-cache 共享

第三條路更激進：跳過文字生成，讓兩個 LLM 直接在 **KV-cache 隱空間**通訊。

```python
# thu-nics/C2C, ICLR'26
from rosetta import C2CFuser

fuser = C2CFuser.from_pretrained("nics-efc/C2C_Fuser")  # Qwen2.5 ↔ Qwen3
# fuser 接受兩個模型的 KV cache，投影後融合給第三個模型用
# 結果：8.5–10.5% accuracy ↑，2.0× latency ↓（vs 文字溝通）
```

限制：目前只支援特定模型 pair（Qwen2.5/Qwen3/GLM），不是通用基礎設施。

### 思考
## 4. Limitations / Honest Assessment

### 作者坦承的限制

- **vCache**：error rate bound 是**統計期望**，不是硬保證。bound 是基於 i.i.d. 假設——若 prompt distribution shift（用戶開始問完全不同主題的問題），calibration 會失準。
- **vCache**：實驗用 GPT-4o 做 verifier。換成 Claude 或本地模型，12.5×/26× 數字會重畫。
- **GPTCache**：官方 README 自承 "the API may be subject to change at any time"、對新 LLM API 停止主動支援（只保證 `get/set` 通用 API）。
- **Anthropic prompt cache**：cache_control breakpoint 之後**不能改 prefix**——多輪對話想換 system prompt 就整個 cache 失效。
- **C2C**：需要 fuser 訓練，model pair 受限（截至 2026-01 只有 Qwen/GLM family）。

### 我們的獨立評估

**1. "10× cost ↓" 是 marketing 數字，不是平均數**
所有 cache 系統的 hit rate 都依賴 query 重複度。對 chat-with-PDF 這種**低重複**的 workload，hit rate 可能 < 5%——10× 變成 1.05× 還要付 embedding 成本。**只有 CRON、CI、batch pipeline、reproducible research 這類「同樣 prompt 跑多次」的工作流才能拿到 10×。**

**2. Semantic cache 是「正確性負債」的隱形累積**
vCache 的價值是讓這筆負債**可量化**。但 0.01 error rate 對 finance / medical 仍是災難——cache 用錯一次的成本可能比省下來的 token 多 1000 倍。沒有「這個 query 不該被 cache」的白名單機制前，semantic cache 在 critical path 上是負債。

**3. L0 prefix cache 已被嚴重低估**
Anthropic cache 0.1× 成本、5min TTL 自動延長——但大家還是花時間寫 L1/L2 系統。事實是，**如果你的 prompt 結構穩定（system + persona + 固定 history），L0 cache 幾乎免費就能拿到 80-90% 的效果**，根本不需要 L1。GPTCache 的 486K 月下載很大部分是「沒意識到 L0 已存在」的工程師的過度優化。

**4. C2C 短期不實用，長期是範式轉移**
把 KV-cache 當通訊介面這件事的想像空間遠超 cache——multi-agent 不再需要 serialize 成文字再 parse。但 v1 對齊成本高、支援窄，2026 年是 demo 等級，2027 才會進入 production toolkit。

### 對比既有方案

| 機制 | vs ReAct/AutoGPT 的 planner 層 | vs MCP 工具層 |
|------|-------------------------------|---------------|
| L0 prefix cache | 與 planner 無關，是底層 | 工具呼叫結果可放 cache_control 區 |
| L1 semantic cache | planner 重複問同問題時省成本 | 工具 cache 比 planner cache 更划算 |
| L2 verified cache | 補 L1 正確性保證 | — |
| C2C | 跨 agent 通信協議，不只是 cache | — |

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

### 對 firn（MODERATE → 開一個 I9 iteration）

**A. L0 prefix cache 接入 `LLMClient`（TRIVIAL → 1-2 天）**
- 檔案：`src/firn/llm/client.py` 與 `src/firn/llm/anthropic_provider.py`
- 改動：在 `build_system` 之後，自動在第一個 system block 加 `cache_control={"type": "ephemeral"}`，5min TTL 預設
- 驗證：`observability/turns_logger.py` 加欄位 `cache_read_input_tokens`、`cache_creation_input_tokens`
- 預估效益：5,000 次 ConversationAgent 呼叫中 ~4,000 會 hit L0，0.1× rate 等於 60-80% input cost 直接消失
- 免費 API 方案：Anthropic 對所有 active models 自動開，無需申請

**B. L1 semantic cache 套件（MODERATE → 1 週）**
- 套件：`gptcache` 486K 月下載、MIT license、active
- 接入點：`src/firn/llm/client.py` 的 `call()` 方法在 `await self._provider.create_message()` 之前加 cache lookup
- Embedding：用 firn 既有的 `memory/embedding.py`（如果還沒，則用 `gptcache.embedding.Onnx` 本地）
- Critical：對**會呼叫工具的 request** 預設不 cache（tool call 是 stateful 的，cache 會造成嚴重 inconsistency）
- 風險：openai 官方 adapter 已經「過於主動」，可能干擾 firn 的 circuit breaker。需要白名單 + 黑名單：
  ```python
  cacheable = (
      len(messages) <= 10 and           # 太長的對話不 cache
      not any(m.get("role") == "assistant" and m.get("tool_calls") for m in messages) and
      len(system) < 4000 and            # system 太大快取成本超過 hit 收益
      is_deterministic_request(messages)  # 不含時間戳、隨機 ID 等
  )
  ```

**C. Tool-result cache（MODERATE → 1 週）**
- 檔案：`src/firn/tools/executor.py`
- 思路：對 `idempotent=True` 的工具加 cache key（tool_name + sorted(args) + args_hash）
- 對應 L0 思維：tool 結果放 cache_control 區，下一個 turn 自動 0.1× cost
- 對應 L1 思維：semantic 相似查詢（如「台北天氣」和「台北今天氣溫」）命中同一 cache

**D. vCache-style error-bound 給 L1（RESEARCH-ONLY）**
- vCache 的 conformal-prediction 邏輯要從 Go/Python 移植到 firn
- 短期不必要——vCache 自己還在 0.x 版本，且需要 OpenAI API 做 verifier
- 列入 v2 backlog，等 vCache 1.0 stable

### 對 managed-agents（無需改動）

managed-agents 是 batch runner，query 重複度比 chat agent 高，但**單次 batch 內 prompt 結構固定**——加 L0 prefix cache 即可。**不在本次研究範圍**，由 reliability-engineering-2026-06-09 報告的 follow-up 處理。

### 不做的（明確拒絕）

- ❌ 自建 KV-cache 共享（vLLM 級別）：firn 是個人 agent，10K token/s 用量級，自建浪費工程時間
- ❌ 整合 C2C：穩定性不夠、支援窄、研究原型
- ❌ GPTCache 的所有 vector backend：firn 用 `memory/embedding.py` 的 sqlite + faiss 已足，不需要再疊 Milvus/Redis


### 來源

- 原始報告：2026-06-11-semantic-cache-llm-prompt-caching-2026.md
- 類型：
- 連結：
