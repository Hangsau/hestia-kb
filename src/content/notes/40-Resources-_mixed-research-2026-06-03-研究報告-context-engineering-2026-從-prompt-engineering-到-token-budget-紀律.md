---
_slug: 40-Resources-_mixed-research-2026-06-03-研究報告-context-engineering-2026-從-prompt-engineering-到-token-budget-紀律
_vault_path: 40-Resources/_mixed/research/2026-06-03-研究報告-context-engineering-2026-從-prompt-engineering-到-token-budget-紀律.md
tags:
- research
- knowledge
- ai-agent
created: '2026-06-03'
version: 1
source_report: 2026-06-03-context-engineering-2026.md
source_url: null
type: research
fingerprint: context, agent, engineering, acon, anthropic, token, taco, llm, compressor,
  context-mode
title: 研究報告：Context Engineering 2026 — 從 Prompt Engineering 到 Token-Budget 紀律
updated: '2026-06-15'
status: budding
---

# 研究報告：Context Engineering 2026 — 從 Prompt Engineering 到 Token-Budget 紀律

## Version 1 — 2026-06-03

### 核心觀念
**問題**：LLM 進入 agent 時代後，最大的瓶頸不再是「怎麼寫 prompt」，而是「怎麼餵給模型剛好的 context」。Anthropic 2025-09 發表的 [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) 把這個轉變正式命名為「context engineering」，並指出三個事實： 1. **Context 是有限資源**：transformer 的 O(n²) pairwis…

**洞見**：context engineering 為什麼在 2026 成為中心議題： **1. 1M token context window 沒解決問題**。Anthropic 明說：「再大的 window 都有 context pollution」。模型注意力是 budget，不是 RAM。 **2. 經濟現實**：Claude Opus 4.5 輸入 $15/M、輸出 $75/M。一個 session 燒 1M token = $75 USD output 而已。ACON 降 54% = 立刻省 $40。Terminal agent 更可怕 — 一個 task 可能燒幾百萬 token。 **3.…

### 架構 / 機制
## 2. Core Mechanism

context engineering 不是單一技術，是一套組合拳。Anthropic 點名三大槓桿：

### 2.1 Compaction（最主流）

把快撐爆的對話總結成 compact summary，重啟 context window。

```python
# Anthropic Claude Code 的做法（簡化）
def compact(messages, max_tokens=8000):
    # 保留：architectural decisions、unresolved bugs、implementation details
    # 丟棄：redundant tool outputs、重複訊息
    summary = llm.summarize(
        messages,
        keep_recent_files=5,  # 保留最近 5 個被存取的檔案
        max_output_tokens=max_tokens
    )
    return summary + messages[-10:]  # 保留最近訊息
```

**ACON 的改良**（Microsoft 2026，arxiv 2510.00615）：

ACON 把 compaction 升級成 **natural language space optimization**：

1. 跑 baseline agent → 收集失敗案例
2. 用 LLM 分析失敗 → 自動 refine compression guidelines
3. 把 guidelines 蒸餾到小模型（LoRA）作為 compressor
4. 結果：在 AppWorld/OfficeBench/QA 上 peak token 降 26-54%，任務成功率上升

關鍵差異：ACON 不用 fine-tune 整個 agent，**只 fine-tune compressor**。所以 proprietary LLM 也能用。

### 2.2 Structured Note-taking（最便宜）

Agent 定期把狀態寫到 NOTES.md / todos，下次啟動時讀回來。

- Claude Code 內建 todo list
- 寶可夢 agent 寫「Pikachu 已練 8 級，目標 10 級」
- Anthropic Sonnet 4.5 推出 `memory tool` (file-based)

優點：零成本。缺點：需要 agent 自律，什麼該寫、什麼不該寫，沒有理論依據。

### 2.3 Sub-agent Architectures（最結構化）

主 agent 持有 high-level plan，sub-agent 各自做 deep work，每個 sub-agent 燒幾萬 token 但**只回傳 1-2K token 摘要**。

```
┌─────────────────┐
│   Lead Agent    │  ← context 乾淨，只有 plan + 摘要
└────────┬────────┘
         │
    ┌────┴────┬─────────┐
    ▼         ▼         ▼
┌────────┐┌────────┐┌────────┐
│Sub-1   ││Sub-2   ││Sub-3   │  ← 每個有自己獨立 context
│"搜尋…" ││"分析…" ││"寫測試…"│
└────┬───┘└────┬───┘└────┬───┘
     │         │         │
     └────[1000-2000 token summaries]────┘
```

Anthropic 報告「multi-agent research system」用這個模式在複雜研究任務上大幅贏過 single-agent。

### 2.4 2026 新興：TACO 的 Self-Evolving Rules

TACO (arxiv 2604.19572) 解決 terminal agent 的特殊問題：shell output 雜訊二次方膨脹。它的創新是**線上 discover/repair compression rules**：

- 不寫死 truncation 規則
- 觀察輸出 → 發現沒被覆蓋的格式 → 提議新規則
- 維護一個**global rule pool**，新任務可從先前的累積知識開局
- 在 TerminalBench 上 +1-4% 勝率，可轉移 SWE-Bench Lite / DevEval / CRUST-Bench

```bash
# TACO 用法
harbor run -d terminal-bench@2.0 -a terminus-2 \
  --ak enable_compress=True \
  --ak enable_self_evo=True \
  --ak compress_model_name="gpt-4o-mini"
```

---

### 思考
## 4. Limitations / Honest Assessment

### ACON 的限制

- **需要 failure samples 才能 optimize guidelines**。冷啟動問題：沒歷史失敗案例時，效果等同 baseline。
- **蒸餾小模型要 GPU + 訓練時間**。不是 plug-and-play。
- **guidelines 可能 overfit 到特定 task type**。AppWorld 上的規則未必能轉到 OfficeBench。

**我們的獨立評估**：ACON 的真實價值是**框架**（統一 environment/agent/compressor 介面），不是具體的 guideline。Microsoft 把這套 pipeline 開源出來比 guideline 本身更重要 — 任何人都能拿來跑自己的 benchmark。

### TACO 的限制

- **依賴一個外部 compression LLM**。需要 OpenAI API 或自架 LLM endpoint，free tier 跑不起來。
- **self-evolving rule pool 可能長出壞規則**。TACO 沒看到 ablation 顯示誤判率。
- **只在 terminal agent 驗證**。通用 agent 場景未測。

### context-mode (16K stars) 的限制

- **鎖定 Claude Code 平台**。不是 framework-agnostic。
- **98% reduction 是 best case**。在 RAG / web search 場景可能掉 recall。
- **SQLite + FTS5 不是 distributed**。多機部署要自己改。

### Anthropic 框架的盲點

- **沒有「什麼不該用 context engineering」的指引**。他們把所有 context 都當成 problem，但有些 context（domain knowledge、user preferences）就是該長期保留。
- **sub-agent 架構有線性成本**。5 個 sub-agent 不是 5x cost，但 token 開銷不是 1x。

### 對比既有方案

| 方法 | 何時勝 | 何時敗 |
|------|--------|--------|
| ReAct (2022) | 短任務、明確工具 | 長任務、context 爆 |
| AutoGPT (2023) | 探索型任務 | 沒有 memory governance |
| Mem0/Letta (2025) | 跨 session 記憶 | 沒有 active compression |
| **ACON (2026)** | long-horizon + 有 failure data | 冷啟動、單次任務 |
| **TACO (2026)** | terminal agent | 需要外部 LLM |
| **context-mode (2026)** | Claude Code 生態 | 跨平台需求 |

**可複製性**：
- ACON：需要 OpenAI API + 訓練 GPU，$50-200/benchmark 跑一次。普通開發者可重現。
- TACO：需要 compression LLM endpoint。$10-50/task 視用量。可重現。
- context-mode：npm 一行安裝，最容易上手，但鎖平台。
- Claude-Mem：npm 一行安裝，但已是 6.5.0 成熟版，不算新研究。

---

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

### firn（AI agent 框架）

**難度：MODERATE**

1. **加 ACON-style compressor 介面**（MODERATE）。firn 沒有長時任務，但若用 firn 跑 long-running research pipeline（每天 1 個 cron job 跑 30 分鐘那種），context pollution 會出現。引入 `productive_agents` 的 compressor abstraction（interfaces in `src/productive_agents/`），讓 firn 的 agent 在 context 超過 60% 時自動呼叫 compressor。
   - 改動：`firn/core/turn_loop.py` 加 context size check + compressor hook
   - 不用 ACON 的 failure-analysis loop（太重），先用 simple summary

2. **加 structured note-taking layer**（TRIVIAL）。firn agent 已經有 todos。把它升級成 NOTES.md 自動寫入：
   - 每 10 個 tool call 自動 dump 目前狀態到 `~/.firn/sessions/<id>/notes.md`
   - context compact 時，優先讀回 notes.md
   - 改動：`firn/core/memory.py` 加 `note_writer` module

3. **加 tool result clearing 預設**（TRIVIAL）。Anthropic 觀察「最便宜的 compaction 就是清掉 tool result」。firn 目前把整個 tool output 留在 context。加 `clear_after_turns=5` 預設參數。

### managed-agents（batch runner）

**難度：TRIVIAL**

managed-agents 是「跑完就結束」的 batch task，不存在 long-horizon 問題。**但**：
- batch task 結果彙整時（把 N 個 sub-task 結果拼成 final report），可以借鑑 sub-agent architecture — 讓每個 sub-task 自己處理 context，主 agent 只看摘要。
- 改動：`core/v2/dispatcher.py` 加 `result_summary_mode="compressed"` 選項

### hermes-agent 自身（hermes 框架）

**難度：MODERATE**

1. **session_notes.md 自動維護**（MODERATE）。Hermes 已經有 session continuity。但每個 turn 的 tool output 直接灌 context。加一個 `hermes session notes` 指令，自動把目前 session 摘要寫到 vault 的 `sessions/<id>/notes.md`。下次 `--continue` 時優先載入。
2. **context budget HUD**（TRIVIAL）。mksglu/context-mode 跟 jarrodwatts/claude-hud 都有現成 UI。Hermes 應該在 prompt 開頭顯示「context 用量: 23% / 預估剩餘 47 個 turn」。

### 是否需要付費 API？

- ACON：需要 OpenAI API 做 compressor distillation。$50-200 一次性。
- TACO：需要 compression LLM。可以用本地 LLM (Ollama + qwen2.5-7b)，免費。
- context-mode：完全本地，SQLite + FTS5。
- Claude-Mem：本地，npm 套件。

**結論**：99% 的 context engineering 工具鏈都可以用免費方案跑起來。

---


### 來源

- 原始報告：2026-06-03-context-engineering-2026.md
- 類型：
- 連結：
