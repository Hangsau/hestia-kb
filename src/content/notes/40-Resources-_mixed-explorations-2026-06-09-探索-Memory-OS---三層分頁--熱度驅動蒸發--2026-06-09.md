---
_slug: 40-Resources-_mixed-explorations-2026-06-09-探索-Memory-OS---三層分頁--熱度驅動蒸發--2026-06-09
_vault_path: 40-Resources/_mixed/explorations/2026-06-09-探索-Memory-OS---三層分頁--熱度驅動蒸發--2026-06-09.md
title: 探索：Memory OS — 三層分頁 +熱度驅動蒸發 —2026-06-09
date: 2026-06-09
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- count
- heat
- interaction
- mem
- memory
- memoryos
- recurrence
- segment
- traits
- user
created: '2026-06-09'
updated: '2026-06-15'
status: budding
---

# 探索：Memory OS — 三層分頁 +熱度驅動蒸發 —2026-06-09

**延續自**: [[2026-06-09-hmem-recmem-hierarchical-recurrence-memory]]
**日期**: 2026-06-09 | **來源**: MemoryOS (Kang et al., arxiv:2506.06326, EMNLP 2025 track) | **類型**: Exploration

##核心：作業系統啟發的三層記憶架構

MemoryOS 的核心洞察：**現有記憶系統各自運作在孤立維度**（純儲存結構、純檢索機制、或純更新策略），沒有一個統一的作業系統級框架。MemoryOS 是第一個將 OS 的分段分頁（segment-paging）機制引入 AI agent 記憶管理的系統。

**四個核心模組**：
1. Memory Storage — 三層儲存單元（STM/MTM/LPM）
2. Memory Updating — 動態記憶刷新（STM→MTM FIFO、MTM→LPM 熱度驅動）
3. Memory Retrieval — 語意分段查詢三層
4. Response Generation — 整合三層檢索結果生成回應

---

## 三層儲存架構

### Short-Term Memory (STM)

- **結構**：固定長度對話頁面佇列（max 7 pages）
- **對話頁面格式**：`page_i = {Q_i, R_i, T_i}`（query、response、timestamp）
- **對話鏈（Dialogue Chain）**：每個 page附加 `meta_chain`，由 LLM 評估新頁面與先前頁面的語意連貫性，決定是鏈接到現有鏈還是重置。這解決了跨 session 的語意連貫性問題。
- **更新策略**：FIFO（佇列尾部追加，滿時最舊頁面遷移到 MTM）

### Mid-Term Memory (MTM)

- **架構**：OS 啟發的分段分頁儲存（Segmented Paging）
- **分段定義**：`segment_i = {page_i | F_score(page_i, segment_i) > θ}`
  - 相同主題的對話頁面群組為一個 segment
  - Segment內容由 LLM 根據相關對話頁面摘要生成
- **評分函數**：`F_score = cos(e_s, e_p) + F_Jacard(K_s, K_p)`
  - `e_s`, `e_p`：segment 和 page 的 embedding 向量
  - `K_s`, `K_p`：LLM 從 segment 和 page提取的關鍵字集合
  - Jacard similarity 捕捉關鍵字重疊，cosine 捕捉語意相似度
- **熱度驅動驅逐（Heat-based Eviction）**：
  - `Heat = α·N_visit + β·L_interaction + γ·R_recency`
  - `N_visit`：segment 被檢索次數
  - `L_interaction`：segment 內對話頁面總數
  - `R_recency = exp(-Δt/μ)`：時間衰減係數
  - 當 segment 數量超過上限（200），熱度最低的 segment 被驅逐
  - 遷移到 LPM 後，`L_interaction` 重置為 0，熱度下降

### Long-term Persona Memory (LPM)

- **User Persona**：
  - User Profile（靜態屬性：性別、姓名、出生年）
  - User KB（事實性資訊，動態從過去互動萃取和更新，100條 FIFO 佇列）
  - User Traits（動態興趣/習慣/偏好，90 維度，跨三類：基本需求+人格、AI對齊維度、內容平台興趣標籤）
- **Agent Persona**：
  - Agent Profile（固定設定：角色、性格特質）
  - Agent Traits（動態屬性，來自與用戶互動的發展）

---

## 關鍵創新：Heat-Based 分段管理

MTM→LPM 的遷移觸發條件：**Heat > τ（默認 τ=5）**

遷移時：
1. Segment及其所有對話頁面更新 User Traits、User KB、Agent Traits
2. `L_interaction` 重置為 0，導致該 segment 的熱度下降
3. 確保連續的 persona 演化而不冗餘

這與 RecMem 的 recurrence-triggered consolidation 有本質差異：
- RecMem：recurrence count觸發（θcount ≥ threshold）
- MemoryOS：heat score觸發（visit count + interaction length + recency decay）

---

## 量化結果

### LoCoMo Benchmark（GPT-4o-mini）

| Model | Single-Hop F1 | Multi-Hop F1 | Temporal F1 | Open-Domain F1 | Avg F1 |
|-------|--------------|--------------|-------------|----------------|--------|
| TiM | 16.25 | 18.43 | 8.35 | 23.74 | 3.8th |
| MemoryBank | 5.00 | 9.68 | 5.56 | 6.61 | 5.0th |
| MemGPT | 26.65 | 25.52 | 9.15 | 41.04 | 2.2nd |
| A-Mem | 27.02 | 45.85 | 12.14 | 44.65 | – |
| **MemoryOS** | **35.27** | **41.15** | **20.02** | **48.62** | **1.0th** |

- vs A-Mem: +32.35% (Single-Hop), +23.83% (Multi-Hop), +118.80% (Temporal), +18.47% (Open-Domain)
- vs MemGPT: +49.11% avg F1 improvement, +46.18% avg BLEU-1 improvement

### Token Efficiency（LoCoMo）

| Method | Tokens/Query | Avg LLM Calls | Avg F1 |
|--------|-------------|---------------|--------|
| MemoryBank | 432 | 3.0 | 6.84 |
| TiM | 1,274 | 2.6 | 18.01 |
| MemGPT | 16,977 | 4.3 | 29.13 |
| A-Mem* | 2,712 | 13.0 | 26.55 |
| **MemoryOS** | **3,874** | **4.9** | **36.23** |

-4.9 LLM calls vs A-Mem* 13.0（68% 節省）
- 3,874 tokens vs MemGPT 16,977（77% 節省）

### GVD Dataset

| Model | Acc. | Corr. | Cohe. |
|-------|------|-------|-------|
| A-Mem | 90.4 | 86.5 | 91.4 |
| **MemoryOS** | **93.3** | **91.2** | **92.3** |

---

## 與前期探索的差異

| 維度 | MemoryOS | H-MEM | RecMem |
|------|----------|-------|--------|
| 分層觸發 | heat-based FIFO（組織+時機） | hierarchical routing（組織） | recurrence detection（時機） |
| 索引機制 | cosine+Jacard scoring | positional index encoding | cosine similarity + threshold |
| Consolidation觸發 | heat score > τ | user feedback | recurrence count ≥ θcount |
| 蒸發策略 | heat-based eviction | memory weight dynamic | θsim filtering |
| Token 效率 | 3,874 tokens (4.9 calls) | 未報告 | 87% reduction vs MemoryOS |
| 最強維度 | Temporal QA (+118.80% vs A-Mem) | Adversarial QA (63.3) | 未報告 |

---

## Per-source Insight

1. **OS 分段分頁是可移植的架構模式**：將 OS 的 segment-page 應用於對話歷史管理，語意分組（segment）比時間分組更能捕捉主題連貫性。這對 Hermes 的 session 管理有直接實作價值。

2. **Heat score 是比純時間更真實的「重要性」度量**：結合 visit count（檢索頻率）、interaction length（參與深度）、recency（時間近度）三維，比 RecMem 的純 recurrence count 更豐富。這是 ZenBrain 的「stress-critical neurons」概念在系統層的體現。

3. **User Traits90 維度框架**：從 segment 萃取並更新 90 維度的 User Traits（基本需求+AI對齊+內容平台），這個維度量化框架比 Mem0 的簡單 key-value 更有結構。Hermes 可以借鑒這個維度化偏好表示。

4. **STM 固定長度佇列（7 pages）是關鍵超參數**：ablation 未報告這個參數的 sweep，但固定7 頁的設計控制了 STM 的計算成本。LoCoMo 上3,874 tokens/query 的效率來自這個保守的 STM 設定。

5. **LPM 的 FIFO + fixed size（100）是低成本維護策略**：不用任何 ML 蒸發機制，直接 FIFO佇列管理 KB 和 Traits。簡單有效，適合 Hermes 的簡單需求。

---

## 對 Hermes/Talos 的具體建議

### WS-035 Drift Penalty — Heat Score概念移植

心跳學習的 drift penalty 可以借鑒 MemoryOS 的 heat score：
- `N_visit` → distillate 被 task context 引用的次數
- `L_interaction` → 該 distillate 關聯的 task總數
- `R_recency` → 上次被引用的時間衰減

當某個 distillate 的 heat 長期為0（無引用、久未觸發），代表它已成為「冷知識」，應被標記為 potentially stale。

### Session Memory 管理的分段概念

將 session thread 分組為 semantic segments（而非線性 FIFO），每個 segment 由 LLM 自動摘要。主題連貫的對話頁面應該在同一个 segment 內，這解決了簡單 FIFO造成的「主題mixing」問題（MemGPT 的已知缺陷）。

### Hermes Skills 的熱度追蹤

Skills 可以有熱度分數（`trigger_count` + `recency_decay`），高熱度 skill 在檢索時優先，低熱度長久未用的 skill 降級到 archive。類似的概念在 `system-map` 的「30 skills 無 domain」問題上可以應用——長期無 domain 的 skills可能是冷 skills。

---

## 未追蹤 Leads

- BAI-LAB/MemoryOS GitHub — 有完整開源實作（https://github.com/BAI-LAB/MemoryOS），可看具體 code
- SAGE (arxiv:2605.12061) — Graph-Memory Engine，MemoryOS 的 graph-based 競爭者
- SCM (Self-Controlled Memory, Wang et al. 2025) — dual buffers + memory controller，MemoryOS 的另一個比較對象

## ✅ 本次探索完成

