---
_slug: 40-Resources-_mixed-research-2026-06-04-研究報告-swe-bench-2026-leaderboard-與-agent-benchmark-設計反思-saber-啟示
_vault_path: 40-Resources/_mixed/research/2026-06-04-研究報告-swe-bench-2026-leaderboard-與-agent-benchmark-設計反思-saber-啟示.md
tags:
- research
- knowledge
- ai-agent
created: '2026-06-04'
version: 1
source_report: 2026-06-04-swebench-2026-benchmark-design-saber.md
source_url: null
type: research
fingerprint: saber, mutating, swe-bench, verified, agent, action, bench, qwen, model,
  benchmark
title: 研究報告：SWE-bench 2026 Leaderboard 與 Agent Benchmark 設計反思（SABER 啟示）
updated: '2026-06-15'
status: budding
---

# 研究報告：SWE-bench 2026 Leaderboard 與 Agent Benchmark 設計反思（SABER 啟示）

## Version 1 — 2026-06-04

### 核心觀念
**問題**：AI agent 領域每年發表數百個 framework（ReAct、Reflexion、AutoGPT、CrewAI、AutoGen、LangGraph...），但**怎麼比較誰好**一直是個痛。SWE-bench 自 2023 發表以來已成為「真實軟體工程任務」de facto 標準；到 2026 年 leaderboard 上頭部系統已達 79.2%（Claude Opus 4.5 + live-SWE-agent），看似接近「解決」。但有三個深層問題浮上檯面： 1. **Benchmark ceiling 是 artifact，不是 model ceiling**。SABER 論文（C…

**洞見**：**(1) Benchmark 設計的典範轉移 — 從「分數高」到「評分可靠」** τ-Bench Verified 的發布意味著：**當你的 agent 在原始 τ-Bench 上分數飽和，先懷疑 benchmark 本身**。SABER 團隊手動審計 165 題、修正 ground truth、擴寫 user instruction 釋出 Verified 版本。SWE-bench Verified 500 題已經過同樣流程（OpenAI x Princeton 2024-08），但其他 benchmark（GAIA、HotpotQA、ToolBench）沒人做。**未來 12 個月可能會…

### 架構 / 機制
## 2. Core Mechanism

### 2.1 SWE-bench 2026 評測生態

SWE-bench 在 2026 年的結構演進（從官方 repo + leaderboard）：

```
SWE-bench 家族（2026 變體）
├── Verified（500 題，人工驗證可解）— 主流
├── Lite（300 題，輕量版）
├── Multilingual（9 種程式語言，2026 新增）
├── Multimodal（截圖 + 文字，2025-07 發表）
├── Bash-only（僅 shell 工具，2026 新增）— 強迫「最簡 harness」
└── Test split（500 題私有，需 sb-cli 提交）
```

**頭部系統（截至 2026-06）：**

| 系統 | Model | Verified | 提交日期 | 成本 |
|---|---|---|---|---|
| live-SWE-agent | Claude Opus 4.5 medium | **79.2%** | 2025-12-15 | n/a |
| Sonar Foundation Agent | Claude Opus 4.5 | **79.2%** | 2025-12-05 | n/a |
| TRAE | Doubao-Seed-Code | 78.8% | 2025-09-28 | n/a |
| live-SWE-agent | Gemini 3 Pro Preview | 77.4% | 2025-11-20 | n/a |
| Atlassian Rovo Dev | Claude Sonnet 4 + GPT-5 | 76.8% | 2025-09-02 | n/a |
| **mini-SWE-agent v2.0.0** | Claude Opus 4.5 high | 79.2% | 2026-02-17 | **$377 / 500 題** |
| Qwen3-Coder-480B | (open) | 高分 | 2026 | $0.20-0.50 / 題 |

**mini-SWE-agent** 是 2026 的關鍵 baseline：原始 SWE-agent 100+ 行複雜 prompting，mini 版本**簡化為 100 行 Python code**（swebench 官網稱 "Verified in 100 lines of Python code"），靠 Claude Opus 4.5 high reasoning 達到跟重型 agent 相同的 79.2%。這暗示：**harness 複雜度對 SOTA 的邊際貢獻正在趨近於零**，底層 model 能力是主因。

### 2.2 SABER 的三大組件

SABER（**S**afeguarding Mutating **A**ctions, **B**lock-based filtering, **E**nhanced **R**eflection）不是新 framework，而是**plug-in 層**包在現有 agent loop 外。**不需要 retraining**（gradient-free, model-agnostic），**只需要兩個 model**（main + auxiliary）：

```
┌─────────────────────────────────────────────────────────┐
│  SABER Pipeline                                         │
│                                                         │
│  Trajectory τ  ───►  Block Storage  (embed & retrieve)  │
│       │                                                 │
│       ▼                                                 │
│  Main Model generates candidate action a_t              │
│       │                                                 │
│       ▼                                                 │
│  ┌─ Auxiliary Model ────────────────────────────┐      │
│  │  1. Is a_t mutating? (mutating ≈ 環境改變)    │      │
│  │     ├─ NO  → 執行（bypass verification）      │      │
│  │     └─ YES ↓                                  │      │
│  │  2. Inject Targeted Reflection (重述 constraints)│    │
│  │  3. NL-summary: "我即將取消你的預訂 X，可以嗎？"│    │
│  │  4. 等待 user 確認 → 執行 or 重新規劃         │      │
│  └──────────────────────────────────────────────┘      │
│       │                                                 │
│       ▼                                                 │
│  下一個 query → Block-based context 重新組裝            │
└─────────────────────────────────────────────────────────┘
```

**三大組件：**

**(A) Mutation-gated human verification** — 只在 candidate action 是 mutating 時要求 user 確認。SABER 把 tool call 改寫成自然語言摘要 + 必要前置條件，送回 user 等待 yes/no 確認。Non-mutating（查詢）action 完全不被打擾。**注意：mutating 只佔 14-18% 步數，所以 user 被打擾的頻率約每 6 個 turn 一次**。

**(B) Targeted reflection** — 在 mutating action 前注入蒸餾後的 constraints 摘要到 `<think>` block（推理模型）或 ReAct-style format（無 reasoning 暴露的模型）。這是解「lost-in-the-middle」問題：long context 後 agent 開始忘記 system policy。

**(C) Block-based context cleaning** — 把 trajectory 切成 block，存 `(s_k, e_k)` 摘要嵌入，**只 retrieve top-N 最相關的 block**（N user-configurable）。解「context poisoning」：user 確認記錄塞爆對話歷史後，後面的判斷開始 reference 過期的 confirmation。

### 2.3 關鍵實驗結果（SABER Table 2）

| Benchmark | Model | No-SABER | +SABER | Δ |
|---|---|---|---|---|
| τ-Bench Airline | Qwen3-Thinking-235B | 49.3% | 63.3% | **+14.0 pp** |
| τ-Bench Retail | Qwen3-Thinking-235B | 64.3% | 71.6% | +7.3 pp |
| τ-Bench-V Air | Qwen3-Thinking-235B | 58.5% | **78.2%** | **+19.7 pp** |
| τ-Bench-V Ret | Qwen3-Thinking-235B | 66.9% | 77.7% | +10.8 pp |
| τ-Bench Airline | ChatGPT-5 (med) | 42.6% | 45.1% | +2.5 pp |
| τ-Bench Airline | Claude Sonnet 4 | 62.6% | **76.5%** | **+13.9 pp** |
| SWE-Bench Verified | Qwen3-Thinking-235B | (基線) | +7% rel | +4 pp |

**Ablation（Qwen3-Thinking，τ-Bench-V Air）：**
- No-SABER: 58.0%
- +Reflection only: 66.9% (+8.9 pp)
- +Verification only: 68.0% (+10.0 pp)
- **Full SABER: 78.7% (+20.7 pp)** — 兩者**非線性疊加**（78.7 - 68.0 = 10.7 from reflection 組合，反之亦然）

**輔助 model 配對很重要**：Qwen3-Thinking + Qwen3-Instruct（auxiliary）顯著優於 Qwen3-Thinking + Qwen3-Thinking（auxiliary），暗示 **auxiliary 用「instruction-tuned 守門員」+ main 用「reasoning-heavy 行動者」** 的不對稱分工最佳。

### 思考
## 4. Limitations / Honest Assessment

**SABER 的侷限（作者自承 + 我們的獨立評估）：**

1. **依賴「mutating vs non-mutating」二元分類的清晰定義**。但現實中很多 action 是「半 mutating」（read DB 但會 cache、查訂單但會觸發 audit log），auxiliary model 的判斷本身就是另一個失敗源。論文沒給 false-positive/false-negative rate。

2. **user simulator ≠ 真實 user**。τ-bench 用 Claude Sonnet 4 模擬 user，確認「Yes」過於順從，無法反映真實 user 會反問、誤解、情緒化的情境。**SABER 在真實 production 的增益可能比 paper 低 5-10 pp**。

3. **Block-based retrieval N 是 hyperparameter**。論文用 N=16 但沒系統 sweep；對長 context (1M tokens) 場景 N=16 夠不夠？沒有答。

4. **Ablation 顯示 saturate**。Retail domain Full SABER (77.7%) 跟 +Verification only (80.5%) 接近甚至略低 — 作者承認 "potentially due to benchmark saturation"。意味著**組件不是越多越好**，需要 per-domain 調參。

5. **未解的 ceiling effect**：即使 Verified 版仍有 ~17% 失敗（Claude 在 τ-Bench-V Air 73.3%），是 (a) 模型能力上限 (b) benchmark 仍殘留瑕疵 (c) SABER 本身天花板？論文沒釐清。

**SWE-bench leaderboard 的更深問題：**

6. **Cost-vs-score 曲線無人繪**。Sonnet 4 跑一次 Verified ≈ $50-80，Opus 4.5 ≈ $300-400，Qwen3-Coder-480B（self-host）≈ $0.20/題但要 8×H100 跑一週。**真正的 Pareto frontier 應該是 score/$，但 leaderboard 只列分數**。一個靠開源 30B 模型 + 4-bit quantization 跑 70% 的系統，production value 可能比 Opus + 79% 高很多。

7. **「嘗試次數」遊戲**。1 attempt = 79.2%，2 attempts = ?。SWE-bench 的 convention 是報「一次最佳」，但真實 deployment 會多 sample + rerank。**報 single-attack 數字對比 multi-attack 是 apples-to-oranges**。

8. **Benchmark 偏 Python 生態**。SWE-bench 全是 Django / astropy / sympy / matplotlib 等 Python repo；multilingual variant 雖 2026 推出但樣本量小。**對 Rust / Go / TypeScript 後端的 agent，leaderboard 數字沒有意義**。

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

### 5.1 對 firn 的具體改進

**(A) 加 Action Risk Classifier（MODERATE 難度，無需付費 API）**

在 firn 的 agent loop 加一層：
```python
# firn/core/action_classifier.py
MUTATION_KEYWORDS = ["delete", "remove", "cancel", "refund", "transfer",
                     "send_email", "publish", "merge", "deploy", "overwrite"]

def classify_action_risk(tool_call: dict) -> str:
    """Return 'mutating' | 'non_mutating' | 'read_only'"""
    if tool_call.get("name") in READ_ONLY_TOOLS:
        return "non_mutating"
    if any(kw in tool_call.get("name", "").lower() for kw in MUTATION_KEYWORDS):
        return "mutating"
    # 用 local model (Qwen3-4B 或 Llama-3.1-8B) 兜底分類
    return local_classifier(tool_call)
```

對 mutating action：暫停 → 把「我即將執行 X，會改變 Y，確認？」送到 user → 等 yes/no。這是 SABER 的 60% 效果、約 200 行 code。

**(B) Block-based context cleaning（MODERATE 難度）**

firn 對話歷史目前是 flat 列表。改成 block 結構：
- 每 5 turns 為一 block，生成 50-word 摘要 + embedding
- 新 query 進來 → embed → cosine sim → 取 top-8 blocks + 最近 3 turns
- 用 sqlite-vec 或 chromadb（本地，零成本）

這直接解 firn 跑久了 context 塞爆、agent 開始 reference 過期狀態的問題。

**(C) Target reflection before mutating（TRIVIAL）**

在 mutating action 前 inject 一次 system policy 摘要：
```python
def targeted_reflection(system_policy: str, last_3_turns: list) -> str:
    """蒸餾出當前約束"""
    return f"REMINDER: {system_policy[:500]}\n最近 3 輪摘要: {summarize(last_3_turns)}"
```

**這是 SABER 三組件中實作成本最低、效益最高的（+8.9 pp 單獨 ablation）**。

### 5.2 對 AGI 自我研究管線的應用

**(D) 建立「firm 自己的 SWE-bench Verified」子集（MODERATE）**

從現有 research script（`research_papers/2025-*`）中**手動審計 20 個 ground truth**，建立 `firn_bench_v1.json`。這呼應 SABER 的發現 — **不要相信單一 benchmark 數字**。每次新模型上線前，在自己 curated 的 20 題上跑 + 比對 leaderboard 數字差距。

**(E) 評估 cost-vs-score Pareto**

寫一個 `eval_pareto.py`：在 SWE-bench Verified Lite 50 題上跑 Qwen3-Coder-30B-A3B-Instruct、deepseek-v3.2、gpt-5-mini、claude-haiku-4-5，分別記錄 score / $ / 延遲。輸出 Pareto frontier plot。

### 5.3 瓶頸

- **需要 GPU 跑 30B+ 模型做 ablate** — Qwen3-Coder-30B-A3B 需要 24GB+ VRAM，本地 4090 (24GB) 勉強可跑 4-bit
- **mini-SWE-agent 的 $377 跑 500 題是必要 baseline** — 沒有這個成本預算就沒法做有意義的對比
- **SABER 的程式碼尚未公開**（paper-only 截至 2026-06），需要自己從 pseudocode 實作。但因為是 prompt-level plugin，難度 MODERATE


### 來源

- 原始報告：2026-06-04-swebench-2026-benchmark-design-saber.md
- 類型：
- 連結：
