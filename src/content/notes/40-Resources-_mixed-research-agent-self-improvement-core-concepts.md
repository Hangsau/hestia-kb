---
_slug: 40-Resources-_mixed-research-agent-self-improvement-core-concepts
_vault_path: 40-Resources/_mixed/research/agent/self-improvement-core-concepts.md
tags:
- knowledge
- ai-agent
- core-concepts
- self-improvement
- memory
- reflection
created: '2026-06-08'
version: 1
status: seedling
sources:
- 2026-05-26-研究報告-autonomous-agent-self-improvement-systems.md
- 2026-05-27-研究報告-self-improving-ai-agents-memory-reflection-and-context-engineering.md
- 2026-05-28-研究報告-self-improving-agents-從外部工具調用到內部策略演化.md
- 2026-05-30-研究報告-agent-self-correction-reflection-mechanisms.md
type: core-concepts
fingerprint: self-improvement, reflection, playbook, ace, curator, reflector, dream-cycle,
  governance
title: Self-Improvement + Self-Correction — 核心概念整合
updated: '2026-06-15'
---

# Self-Improvement + Self-Correction — 核心概念整合

> 「如何在不依賴梯度更新的情況下，讓 LLM agent 從實踐經驗中持續變強？」
> — 2025-2026 年 agent 研究的第四條路線

## 典範轉移

**過去三年的主流是「更強的 base model + prompt engineering」**。Self-improving agent 標誌著第四種路線：

| 路線 | 典型方式 | 缺點 |
|------|----------|------|
| 1. 更強模型 | 訓練更大的 LLM | 成本高、停滯 |
| 2. Prompt engineering | 手寫更好的 prompt | 無法跨任務 |
| 3. Fine-tuning | 改模型權重 | 成本高、過擬合 |
| **4. Self-improving agent** | **從經驗累積，不需 retrain** | 仍早期，但 AppWorld 證明有效 |

**關鍵洞見（ACE 論文證明）**：純 context engineering（不改 model）在 AppWorld benchmark 上可以達到有意義的提升，代表 **operator-level improvement 是真實可行的路徑**。

---

## 三個獨立軸向

Self-improving agent 不是單一技術，而是三個軸向的交織：

1. **Memory 系統** — 將成功 workflow、專案事實、調試經驗寫入持久化儲存
2. **Reflection 機制** — 讓 agent 分析自己的失敗，產出結構化改正策略
3. **Context Engineering** — 將個別經驗昇華成可重用 playbook

---

## 核心機制 1：三角色架構（Generator / Reflector / Curator）

ACE 論文提出**最嚴謹的 self-improving 流程**：

```
樣本輸入 → Generator（生成答案 + 標記使用的 bullet）
         → Reflector（分析錯誤、根因分析、產出結構化洞察）
         → Curator（發布 playbook 操作：ADD/UPDATE/REMOVE bullet）
         → Playbook 更新 → 下一個 epoch
```

### 角色職責

| 角色 | 職責 | 細節 |
|------|------|------|
| **Generator** | 接收當前 playbook + 反饋，產生回答 | 標記哪些 bullet 在推理過程中有幫助 |
| **Reflector** | 觀察 Generator 推理軌跡 + 環境回饋 | 診斷錯誤根源、分類 bullet 貢獻（helpful/harmful/neutral），最多 5 輪 refinement |
| **Curator** | 消費 Reflector 洞察 + playbook 統計 | 發布 delta 操作（ADD/UPDATE/TAG/REMOVE），**在 token budget 限制下運作** |

**關鍵**：三個角色共用**同一個 base model**，所有能力來自 context engineering 而非模型更換。

---

## 核心機制 2：Playbook as Structured Memory

ACE 的核心抽象不是簡單的對話歷史，而是**結構化的 playbook**：

**Bullet 結構**：
- `content`：策略、錯誤模式、API schema、驗證清單
- `metadata`：unique ID + helpful/harmful 計數器
- `section`：歸類（defaults、strategies、errors 等）

**管理機制**：
- Playbook 透過 **delta update 漸進生長**，沒有全量重寫
- Curator 定期執行 **grow-and-refine**（語義去重、counter 調整、修枝）
- **Token budget 限制** 避免 playbook 無限膨脹與 collapse

---

## 核心機制 3：Dream Cycle — 夜間自我改進循環

**Deep-Claw** 借用人類睡眠的認知功能，設計兩套模式：

### Nightly Mode（掃描階段）
- 周期性掃描學術論文、開源工具、社區討論、AI 實驗室公告
- 對每條信息按相關性評分標準打分
- 超過閾值的條目進入深度提取：關鍵主張、實現證據、適用性評估

### Weekly Mode（反思階段）
- 回答三個**結構化自我反思問題**（必須附引用）
- 評估之前的改進假設：預測的進步是否實現了？
- 找出**單一最高槓桿變化**，起草正式 PRD 並進入治理審批

```
Nightly: Scan → Score → Research → Store
Weekly:  Reflect (3 Qs) → Evaluate → Propose (PRD) → Govern
```

### Governance 四層模型（關鍵！）

| 層級 | 風險 | 審批 |
|------|------|------|
| **M1** | 低風險調參 | agent 可自動執行 |
| **M2** | 中等變更 | 需文檔化假設 + 衡量日期 |
| **M3** | 結構性變更 | 需同行 review |
| **M4** | 安全邊界 | **必須人類審批** |

**為什麼這個重要**：在讓 agent 自我修改之前，**先定義什麼能改、什麼需要審批**。沒有 governance，self-improvement 就是 self-destruction。

---

## 核心機制 4：Reflexion — Verbal Reinforcement

[Reflexion 論文](https://github.com/danieleschmidt/reflexion-agent-boilerplate)（Shinn et al., 2023）的核心機制：

```
Actor (LLM) → output → Evaluator (score + feedback) → Reflector (verbal reflection)
     ↑                                                              |
     └─────────────────── injected as next turn's context ←──────────┘
```

每次迭代 agent 會看到「上次嘗試 + 關於失敗原因的 verbal reflection」。**到第 3 次迭代時，agent 已累積詳細的失敗歷史**。

**關鍵**：**不需要梯度更新或微調**，只用自然語言反饋驅動改進。

---

## 核心機制 5：跨 Session 持久記憶（CodeEvo 模式）

不同於 ACE 的 prompt-level self-improvement，CodeEvo 展示**系統級 self-improvement**：

```
任務執行 → 事後分析（識別 durable facts + 成功 workflow）
         → 寫入 long-term memory（專案事實）
         → 寫入 skills（可重用步驟）
         → 寫入 sessions.db（調試上下文）
         → 後續 session 自動召回
```

**記憶分層**：
- **Episodic memory**：本次 task 的成功/失敗模式
- **Vector memory**：語義檢索用的向量化儲存
- **Skills**：結構化的工作流程（可用於新任務）
- **Project facts**：跨 session 的穩定專案資訊

---

## 核心機制 6：Cognition — 生物學啟發的多層記憶

[zurbrick/cognition](https://github.com/zurbrick/cognition) 為 OpenClaw agent 設計了七層記憶：

| 系統 | 功能 |
|------|------|
| Prospective memory | 未來意圖和承諾 |
| Metamemory | 對自身記憶品質的認知 |
| Procedures | 可複用工作流程 |
| Knowledge gaps | 識別自身知識盲區 |
| Consolidation | 每日日誌 → 持久知識的轉化 |
| Reflection | 周期性自我評估 |

**核心設計原則**：**記憶應該是可操作的，而非裝飾性的**。

### Memory Tier 架構
- **Tier 1 (Core)**：`memory/YYYY-MM-DD.md` 日誌 + `MEMORY.md` 持久事實 + `FUTURE_INTENTS.md`
- **Tier 2 (Recommended)**：夜間 staged consolidation + procedure registry
- **Tier 3 (Advanced)**：交叉引用 + confidence tracking + gap tracking + retrieval logging

---

## 核心機制 7：OpenViking — Agent Context 數據庫

[volcengine/OpenViking](https://github.com/volcengine/OpenViking)（24k stars）用「文件系統範式」統一管理 agent context：

- **L0/L1/L2 三層 context 加載**：按需加載，節省 token 成本
- **目錄遞迴檢索**：結合目錄定位與語義搜索
- **可視化檢索軌跡**：可觀測的 context 流動
- **自動 session 管理**：自動壓縮對話內容，提取長期記憶

---

## 核心機制 8：ARIS 自進化技能體系

[wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)（10k stars）的 ARIS 系統：

- **`/meta-optimize`**：分析日誌 → 提出 SKILL.md patch 建議
- **Research Wiki**：持久化論文/ideas/experiments/claims + 關係圖
- **每 10 天發布一個版本**（v0.4.5→v0.4.14，2026 年 5 月密集發布），自我改進速度極快

---

## 自我修正機制分類

從 5/30 報告提煉，self-correction 有三種深度：

| 類型 | 機制 | 範例 |
|------|------|------|
| **Output-level** | 檢查單一輸出，必要時重生成 | Output guardrails |
| **Step-level** | ReAct loop 中失敗 → 重試 + reflection | Reflexion |
| **Strategy-level** | 跨任務觀察失敗模式 → 修改 playbook | ACE Curator、ARIS `/meta-optimize` |

**越深的修正，需要越多基礎設施**。output-level 是 TRIVIAL，strategy-level 是 HARD。

---

## 失敗模式與限制

### 普遍挑戰

- **自我修改的失控風險**：即使有 governance，agent 可能找到 governance 本身的漏洞
- **測量問題**：如何衡量「改進」？短期指標可能和長期目標衝突
- **噪聲積累**：低質量的自我反思可能污染後續決策

### 各方案的限制

**Deep-Claw**：
- 治理模型（M1-M4）需要人類預先定義邊界，**邊界定義本身就很困難**
- 評分標準（relevance rubric）的主觀性：agent 可能繞過自己的評分標準

**Reflexion**：
- 依賴 evaluator 的品質 — **如果 evaluator 本身有偏見，反射會放大偏見**
- 收斂速度不確定 — 有些任務可能多次迭代後仍無法收斂
- verbal reflection 無法捕捉所有類型的錯誤（如結構性的計劃錯誤）

**ACE**：
- 沒有 reliable feedback signal 時性能會退步
- Curator 的 quality 完全取決於 Reflector 的診斷能力

**CodeEvo**：
- Self-improvement 是 system-level（寫記憶到 DB），不是 model-level — **沒有真正的泛化能力**
- 記憶準確性依賴事後分析的 quality

**我們的獨立評估**：
- **Playbook 在高多樣性任務（每天全新領域）時可能缺乏 transfer** — 一個 domain 學到的 bullet 對另一個 domain 可能完全無效
- **錯誤以微變形（subtle variant）形式出現時，純 exact-match 檢索會失敗** — 需要 semantic dedup

---

## 可複製性評估

| 方案 | 可複製性 | 瓶頸 |
|------|----------|------|
| **ACE 三角色** | 任何 LLM API | 足夠 training samples、reliable feedback signal、5 epoch adaptation |
| **CodeEvo** | 幾乎完全免費（SQLite + 檔案）| 需設計 memory schema |
| **Vera** | 16GB+ RAM × 多个 worker | 對普通人不可及 |
| **Deep-Claw** | 取決於 LLM 成本 | 夜間掃描消耗資源 |
| **ARIS** | 需完整 trace 收集 | 需 `/meta-optimize` prompt + 執行日誌 |

---

## 給我們自己的 Actionable

**最快 win**（TRIVIAL）：**task completion self-reflection prompt** — 每次任務完成後多問三個問題，輸出 bullet 存到 `~/.firn/playbook.md`，不需要任何架構改動。

**MODERATE**：實作 CodeEvo-style 跨 session recall — episodic + vector memory，新 session 開始時檢索相關記憶注入 system prompt。

**HARD**：實作 ACE-style playbook — Generator/Reflector/Curator 三角色 + grow-and-refine。

**RESEARCH-ONLY**：Vera 的 `@capability` 統一抽象 — 短期不推薦，長期可作為架構目標。

---

## 參考資料

- **2026-05-26** — Dream Cycle, Cognition 七層記憶, OpenViking
- **2026-05-27** — ACE 三角色, Playbook as Memory, CodeEvo, Vera, Clawix
- **2026-05-28** — Self-improving agents: 外部工具調用 → 內部策略演化
- **2026-05-30** — Self-correction 機制分類（output/step/strategy level）
- 來源專案：the-keats-ai/deep-claw、danieleschmidt/reflexion-agent-boilerplate、zurbrick/cognition、volcengine/OpenViking、wanshuiyin/Auto-claude-code-research-in-sleep、BoeJaker/Vera
