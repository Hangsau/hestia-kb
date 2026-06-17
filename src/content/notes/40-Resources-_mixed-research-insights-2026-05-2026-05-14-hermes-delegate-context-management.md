---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-14-hermes-delegate-context-management
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-14-hermes-delegate-context-management.md
title: Hermes delegate_task Context Management 改善計畫
created: '2026-05-14'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

# Hermes delegate_task Context Management 改善計畫

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 子代理不再因 timeout 歸零、不再污染父 context——透過 hard cap + 分階段委派模式，讓 delegate_task 在 DeepSeek v4-pro 上穩定可用。

**Architecture:** 兩層改善：(1) framework 層加 summary hard cap（#9126 移植），(2) 操作層建立分階段委派指南（gather-only subagent → parent synthesis），避免把蒐集和合成塞進同一個子代理。Checkpoint 和 auto-summarization 暫不做——成本過高、邊界條件多，先用流程解決。

**Tech Stack:** Python3, delegate_tool.py（現有 codebase），config.yaml

## Planning Quality Checklist (MANDATORY — fill every field)

├── **目標（一句話）**
│   └── delegate_task 的子代理在 DeepSeek v4-pro 上穩定完成任務、不回傳 raw 輸出污染父 context
│
├── **前置條件檢查（3–5 項 yes/no）**
│   ├── [x] delegate_tool.py 已可修改（有 source access）
│   ├── [x] config.yaml delegation block 已存在
│   ├── [x] child_timeout_seconds 已實作（600s default）
│   ├── [x] COMPLETION/VERIFICATION/FAILURE RULE 已寫入子代理 system prompt
│   └── [x] context schema 已改為 key:value 引導
│
├── **步驟清單（每步 ≤15 字）**
│   ├── 1. 加 max_summary_chars config + 讀取邏輯
│   ├── 2. 在 _run_single_child 加 summary 截斷
│   ├── 3. 測試截斷行為（單一 + 平行子代理）
│   ├── 4. 寫分階段委派操作指南
│   └── 5. Plan review + 存檔
│
├── **每步的驗證方式（怎麼知道該步做完了）**
│   ├── Step 1: config 讀得到值，default 4000
│   ├── Step 2: 超過 4000 chars 的 summary 被截斷，末尾有 [truncated]
│   ├── Step 3: delegate_task 回傳 summary ≤ 4000 chars
│   ├── Step 4: 指南涵蓋 gather-only / synthesis / 錯誤處理三種模式
│   └── Step 5: plan-review score ≥ 65
│
├── **潛在卡點（至少 2 個，含對策）**
│   ├── DeepSeek v4-pro 在 web research 仍可能 timeout → 靠分階段模式（gather-only subagent 只 fetch 不合成，timeout 也可接受）
│   └── max_summary_chars=0（disable）行為 → 照 #9126 設計，0=不截斷（向後相容）
│
└── **失敗時的退路**
    └── 如果 hard cap + 分階段仍不夠，下一步才考慮 checkpoint（子代理定期寫進度到 /tmp，父代理讀取 resume）。但這是 80+ 行的改動，先觀察效果。

---

## STATUS

| 欄位 | 值 |
|------|-----|
| **狀態** | 🟢 設計中 |
| **目前階段** | 設計 |
| **最後行動** | 2026-05-14: 完成現況評估 + 方案分析 + 計畫撰寫 |
| **下一步** | Plan review |
| **阻擋** | 無 |

---

## 現況評估：原提案 vs 實際已實現

### 我們已有的

| 功能 | 狀態 | 位置 |
|------|------|------|
| child_timeout_seconds (600s) | ✅ 已實現 | delegate_tool.py:362-386, config.yaml:272 |
| COMPLETION/VERIFICATION/FAILURE RULE | ✅ 已實現 | delegate_tool.py:565-578（我們的 patch） |
| context schema key:value 引導 | ✅ 已實現 | delegate_tool.py:2419-2427（我們的 patch） |
| subagent_auto_approve config | ✅ 已實現 | config.yaml:277 |
| max_concurrent_children | ✅ 已實現 | config.yaml:274 |

### 我們缺的（對照社群 PR）

| 社群方案 | 功能 | 我們有沒有 | 要不要做 |
|----------|------|-----------|---------|
| #9126 | max_summary_chars hard cap | ❌ | ✅ 本次 |
| #22820 | token cap + growth ratio | 部分（有 timeout） | ❌ 太複雜，timeout 已夠 |
| #8537 | wall-clock runtime bound | ✅ child_timeout_seconds | — |
| #23177 | pre-spawn guard | ❌ | ❌ 子代理開銷還不大 |
| #16037 | result verification | ❌ | ❌ 下一階段考慮 |
| #12693 | compress_context tool | ❌ | ❌ 需要額外 LLM call |
| Checkpoint | 中斷後 resume | ❌ | ❌ 先用流程解決 |

---

## 方案決策

### 做什麼

1. **Hard cap on subagent summary**（移植 #9126）
   - 在 `_run_single_child` 結果組裝後，截斷 summary 到 `max_summary_chars`（default 4000）
   - 末尾標記 `[...truncated]`
   - Config: `delegation.max_summary_chars: 4000`，0 = disable
   - 改動量：~15 行，1 個檔案

2. **分階段委派操作指南**
   - 不寫程式碼，寫使用 pattern 文件
   - 核心原則：web research 任務拆成 gather-only subagent + parent synthesis
   - 涵蓋三種模式：gather-only、synthesis-only、錯誤處理

### 不做什麼（含理由）

- **Checkpoint**：需要子代理主動寫檔案（多一個 tool call），父代理 parse 邏輯複雜，邊界條件多（何時寫？寫什麼？中斷後檔案髒了怎麼辦？）。先用分階段模式規避 timeout，觀察一個月再決定。
- **Auto-summarization**：需要額外 LLM call（在 DeepSeek 上更慢），且 token 計算不準（沒有 tiktoken）。CrewAI 的 `respect_context_window` 是給 GPT-4 設計的，不適合我們。
- **Token cap / growth ratio**（#22820）：我們已有 timeout 控制，token cap 是多餘的（timeout 自然限制 token 消耗）。而且 #22820 的 code review 已指出它是 post-hoc 不是 runtime guard。
- **Structured handoff metadata**（OpenAI 模式）：需要改 delegate_task 的 schema 和子代理 system prompt，改動量大。目前 briefing 改良已足夠。

### 為什麼這樣選

實證數據：
- 我們跑了 5 次 delegate_task 研究任務，3 次 timeout（LangGraph ×2、社群搜尋 ×1），2 次成功（CrewAI、OpenAI/LlamaIndex）
- 成功的 2 次都是分階段模式（gather to file → parent synthesizes）
- 失敗的 3 次都是「一次做完所有事」模式（fetch + synthesize in one subagent）
- 成功任務的 summary 長度：CrewAI 10,757 bytes = ~2,700 tokens、OpenAI/LlamaIndex 5,469 bytes = ~1,400 tokens（都在安全範圍，但平行 5 個子代理時 5×2,700=13,500 tokens 會溢出）

結論：**hard cap 是安全網，分階段是主要解法**。

### 成本估計

- 改動行數：~20 行（delegate_tool.py）+ ~3 行（config.yaml）
- 新增 config key：1 個（`delegation.max_summary_chars`）
- 風險：幾乎零（向後相容，default 保守）
- 不增加 LLM call

---

## 任務

### Task 1: 加 max_summary_chars config 讀取邏輯

**Objective:** delegate_tool.py 讀取 `delegation.max_summary_chars` config（default 4000，0=disable）

**Files:**
- Modify: `/usr/local/lib/hermes-agent/tools/delegate_tool.py`（在現有 config reader 區域）

**Step 1: 加常數和讀取函數**

在 `_get_child_timeout()` 附近（行 386 之後）加入：

```python
DEFAULT_MAX_SUMMARY_CHARS = 4000  # 0 = no cap


def _get_max_summary_chars() -> int:
    """Read delegation.max_summary_chars from config.

    Returns the max number of characters allowed in a subagent summary.
    Default 4000; 0 disables truncation. Negative values clamped to 0.
    """
    cfg = _load_config()
    val = cfg.get("max_summary_chars")
    if val is not None:
        try:
            ival = int(val)
            return max(0, ival)
        except (TypeError, ValueError):
            logger.warning(
                "delegation.max_summary_chars=%r is not a valid int; "
                "using default %d",
                val,
                DEFAULT_MAX_SUMMARY_CHARS,
            )
    return DEFAULT_MAX_SUMMARY_CHARS
```

**Verification:** `python3 -c "from tools.delegate_tool import _get_max_summary_chars; print(_get_max_summary_chars())"` → `4000`

---

### Task 2: 在 _run_single_child 加 summary 截斷

**Objective:** 子代理 summary 超過 max_summary_chars 時截斷，末尾加 `[...truncated]`

**Files:**
- Modify: `/usr/local/lib/hermes-agent/tools/delegate_tool.py`（行 1546 之後）

**Step 1: 在 summary 賦值後加截斷邏輯**

在行 1546 `summary = result.get("final_response") or ""` 之後插入：

```python
        # Hard cap on subagent summary to prevent parent context overflow.
        # Port of Hermes #9126 pattern — configurable, 0 = disabled.
        max_chars = _get_max_summary_chars()
        if max_chars > 0 and len(summary) > max_chars:
            summary = summary[:max_chars] + "\n[...truncated]"
            logger.debug(
                "Subagent summary truncated: %d → %d chars",
                len(result.get("final_response") or ""),
                len(summary),
            )
```

**Verification:** 手動測試——開一個會回長 summary 的 delegate_task，確認 summary 被截斷

---

### Task 3: 更新 config.yaml

**Objective:** 在 delegation block 加入 `max_summary_chars` 預設值

**Files:**
- Modify: `/root/.hermes/config.yaml`（delegation block）

在 `subagent_auto_approve: false` 之後加入：

```yaml
  max_summary_chars: 4000
```

---

### Task 4: 寫分階段委派操作指南

**Objective:** 文件化 gather-only subagent + parent synthesis 模式，讓未來使用 delegate_task 時有參考

**Files:**
- Create: `/root/managed-agents-research/reports/2026-05-14-hermes-staged-delegation-pattern.md`

**內容要點：**

```markdown
# Hermes delegate_task 分階段委派模式

## 問題

DeepSeek v4-pro 在 web research 任務上太慢（400-600s），
單一子代理負責「蒐集 + 合成」常在中途 timeout。
平行子代理僅改善部分（快的來源完成，慢的還是斷）。

## 核心原則

**不要把蒐集和合成塞進同一個子代理。**

## 模式 1：Gather-Only Subagent

子代理只負責 fetch + 寫入檔案，不合成。

子代理 goal 範例：
"Fetch content from [URLs], append findings to /tmp/research_raw.md.
Do NOT synthesize or summarize. Just record what you find."

## 模式 2：Parent Synthesis

主代理讀取 gather subagent 寫的檔案，自己合成結論。
或用第二個 synthesis-only subagent（不碰 web，只讀檔案+合成）。

## 模式 3：Parallel Gather + Single Synthesize

開 3-4 個 gather subagent（各抓一個來源），
全部完成後主代理合成。

## 錯誤處理

- Gather subagent timeout → 檔案中有部分資料，仍可用
- 兩個來源衝突 → 標記衝突，不強行融合
- 來源 403/404 → 跳過，記錄缺失來源
```

---

### Task 5: Plan review + 存檔

**Objective:** 跑 plan-review、存正式計畫、同步 vault

**Step 1:** 載入 `plan-review` skill，評分本計畫

**Step 2:** 根據 review 修正

**Step 3:** 存檔

```bash
cp /root/managed-agents-research/reports/2026-05-14-hermes-delegate-context-management.md \
   /root/obsidian-vault/research/2026-05-14-hermes-delegate-context-management.md
cd /root/managed-agents-research
git add reports/2026-05-14-hermes-delegate-context-management.md
git commit -m "docs: delegate_task context management plan"
```

---

## 現況評估總表

### 研究來源整理

| 來源 | 類型 | 可借鏡技術 | 採用？ |
|------|------|-----------|--------|
| CrewAI 官方文件 | 框架 | `respect_context_window` auto-summarization | ❌ 多一層 LLM call |
| CrewAI 官方文件 | 框架 | `context: List[Task]` 宣告式依賴鏈 | ❌ 改架構太大 |
| OpenAI Agents SDK | 框架 | `RunContextWrapper` 本地/LLM分離 | ❌ 改 schema |
| OpenAI Agents SDK | 框架 | `input_type` 結構化 handoff | ❌ 改 schema |
| LlamaIndex Workflow | 框架 | `Context.to_dict()` checkpoint | ❌ 邊界條件多 |
| Hermes #9126 | 社群 PR | `max_summary_chars` hard cap | ✅ 本次採用 |
| Hermes #22820 | 社群 PR | token cap + growth ratio | ❌ 已有 timeout |
| Hermes #8537 | 社群 PR | wall-clock runtime | ✅ 已實作 |
| Hermes #16037 | 社群 PR | result verification | ❌ 下一階段 |
| 自身實驗 (5次) | 實證 | 分階段 > 一站式 | ✅ 操作指南 |

### 成本追蹤

| 實驗 | Input tokens | Output | 成本 | 結果 |
|------|-------------|--------|------|------|
| LangGraph vs CrewAI (單一) | 198K | 3K | $0.10 | interrupted |
| Context mgmt (單一) | 405K | 2K | $0.21 | interrupted |
| 平行: LangGraph | ？ | ？ | ？ | timeout |
| 平行: CrewAI | 447K | 11K | $0.23 | ✅ |
| 平行: OpenAI+LlamaIndex | 970K | 18K | $0.51 | ✅ |
| 平行: 社群搜尋×2 | — | — | — | timeout ×2 |
| **總計** | **~2M** | **~34K** | **~$1.05** | **2/6 成功率** |

---

## Self-Critique

**漏洞 1：** Hard cap 可能截斷重要結論——如果子代理的關鍵發現寫在 4000 chars 之後，父代理永遠看不到。

→ **對策：** 在子代理 system prompt 中已有「Key findings first」結構化要求。hard cap 只是安全網，正常運作下子代理應該把關鍵資訊放在前面。如果還是發生，上調 `max_summary_chars` 或改用 0（disable）。

**漏洞 2：** 分階段模式需要使用者/父代理有 discipline——如果忘記用 gather-only 模式，直接下「研究 X 並回報」指令，子代理還是會 timeout。

→ **對策：** 這是使用習慣問題，不是 code bug。操作指南文件化後，在 delegate_task 的 schema description 加提示（「For web research, use gather-only subagents」）。長期可考慮在 schema 加 `mode: "gather" | "synthesize"` 參數。

**漏洞 3：** max_summary_chars=4000 對中文不公平——中文字元密度高，4000 chars 中文 ≈ 2000 chars 英文的資訊量。

→ **對策：** 目前子代理 briefing 要求英文輸出。如果真的需要中文，上調到 6000。但這不緊急——我們的子代理任務 99% 用英文。

**漏洞 4：** Hard cap 只解決「summary 進父 context」的方向，沒解決「父 context 進子代理」的方向——如果父代理給子代理灌 3000 tokens 的 context，子代理還是會 overflow。

→ **對策：** context schema 已改為 key:value 引導（我們的 patch），鼓勵父代理精簡。觀察觸發條件：每 50 次 delegate_task 中 ≥3 次因 context 過長導致 timeout 或輸出退化，就觸發 Phase 2——在 schema description 加 context token estimation warning（不改架構，只在 schema 加註「context 超過 ~1500 tokens 時建議精簡」）。
