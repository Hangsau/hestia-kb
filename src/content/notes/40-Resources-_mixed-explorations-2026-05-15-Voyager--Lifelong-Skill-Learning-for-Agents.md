---
_slug: 40-Resources-_mixed-explorations-2026-05-15-Voyager--Lifelong-Skill-Learning-for-Agents
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-Voyager--Lifelong-Skill-Learning-for-Agents.md
title: 'Voyager: Lifelong Skill Learning for Agents'
date: 2026-05-15
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- action
- agent
- code
- curriculum
- embedding
- hermes
- llm
- skill
- skills
- voyager
created: '2026-05-15'
updated: '2026-06-15'
status: budding
---

# Voyager: Lifelong Skill Learning for Agents

**延續自**: [[2026-05-15-behavior-cache-muscle-mem]] 的未追蹤 lead（Voyager paper）

**日期**: 2026-05-15 | **來源**: arXiv 2305.16291 → GitHub MineDojo/Voyager → 原始碼分析

**標籤**: #agent-skill #lifelong-learning #skill-library #curriculum #code-generation #hermes-inspiration

---

## Insight 1: 三大核心組件

Voyager（NVIDIA, 2023）是第一個 LLM-powered embodied lifelong learning agent，在 Minecraft 中自主探索、學習技能、解鎖科技樹。

| 組件 | 功能 | 實作 |
|------|------|------|
| **Automatic Curriculum** | 提議越來越難的任務 | `CurriculumAgent`：從已完成/失敗任務歷史 + 當前 inventory + biome 決定下一步 |
| **Skill Library** | 存可執行的 code + embedding 索引 | `SkillManager`：每個 skill = 一個 JS async function + LLM 生成的描述 → Chroma vectordb |
| **Iterative Prompting** | 產生 code → 執行 → 錯誤回饋 → 自我修正 | Action agent 寫 code → Critic agent 檢查 → 環境執行 → 錯誤回傳 → 重試最多 4 次 |

**架構流程**：
```
CurriculumAgent("下一步做什麼？")
  → Action agent 產生 JS code（可引用既有 skills + control primitives）
  → Critic agent 檢查 code（執行前驗證）
  → Minecraft 環境執行
  → 成功？→ SkillManager.add_new_skill() → 存 code + embedding
  → 失敗？→ 錯誤回饋 → Action agent 修正，最多 4 輪
```

---

## Insight 2: Skill Library 是核心引擎

### Skill 生命週期

```python
# SkillManager.add_new_skill()
1. LLM 生成 skill description（從 code 推導自然語言描述）
2. embedding description → Chroma vectordb
3. 存 code 到 skills.json + /code/{name}.js
4. vectordb 和 skills.json 必須保持 sync（有 assertion check）
```

### Skill 檢索

```python
# SkillManager.retrieve_skills(query)
query = "crafting a wooden pickaxe"
→ embedding query → Chroma similarity_search_with_score → top-k skills
→ 回傳對應的 JS code 字串（注入到 Action agent 的 prompt）
```

### Skill 組合

技能可以互相調用，形成依賴圖：
```
craftWoodenPickaxe()
  ├─ craftCraftingTable()
  │    └─ mineBlock("oak_log")
  └─ craftItem("stick")
       └─ craftItem("oak_planks")
```

這是 Voyager 最強的屬性：**compound growth**。每新增一個 skill，不只解決一個問題，而是為未來所有 skill 增加一個可用的 building block。

### 關鍵設計決策

1. **儲存 code 而非自然語言**：技能的 representation 是 executable code，不是 prompt。這確保確定性——同一個 skill 每次執行結果一致。
2. **Embedding-based retrieval**：技能描述存成 embedding，task query 用 similarity search 找相關技能。這比 keyword search 或 hand-crafted taxonomy 更靈活。
3. **技能版本控制**：同名技能會 overwrite 舊版（`craftWoodenPickaxeV2`），舊 code 保留。

---

## Insight 3: Automatic Curriculum 的探索驅動

```python
# CurriculumAgent 的決策輸入
- completed_tasks: [...]  # 已完成任務（避免重複）
- failed_tasks: [...]     # 失敗任務（短期內避免）
- inventory: {...}        # 當前持有物品
- biome: "plains"         # 環境 context
- nearby_blocks: [...]    # 可用資源
```

Curricumum 的 prompt 指示 LLM 提出「下一個合理且可行的任務」，條件是：
- 比已完成任務更難一步（proximal development）
- 不需要目前沒有的資源（feasibility）
- 不在 failed_tasks 中（除非環境改變）

**與 heartbeat scoring 的類比**：heartbeat 的 autonomic layer 用 scoring function 決定下一步做什麼（snapshot → scoring → select → execute）。Voyager 的 curriculum 本質上也是 scoring，只是用 LLM 而非 hand-crafted weights。

---

## Hermes 啟發

### 可以借鏡的

1. **Runtime skill generation**
   - Voyager：成功的 task execution → 自動存成 skill
   - Hermes：成功的 task execution → ??? （目前沒有任何自動化學習機制）
   - **機會**：如果 Hermes 在完成複雜任務後，自動將關鍵步驟萃取成 skill（或至少提示「要不要把這個存成 skill？」），可以逐步累積能力
   - Hermes 已有 `skill_manage(action='create')` 和 `heartbeat_learning.py`（萃取 patterns），缺少的是 trigger：**何時觸發學習？**

2. **Embedding-based skill retrieval**
   - Voyager：task query → embedding → Chroma → top-k skills
   - Hermes：`skills_list` → LLM 讀 description → 手選（或 skill mentions 靠關鍵字）
   - **差距**：Hermes 目前沒有 semantic search over skills。`skills_list` 只回傳 name + description，沒有 vectordb。如果 skills 增加到數百個，LLM context window 吃不下全部 skill descriptions
   - **可行的第一步**：給 `skills_list` 加 embedding search（用本地 model 如 all-MiniLM-L6-v2），讓 LLM 只看到 top-k relevant skills

3. **Composable skills**
   - Voyager：`craftWoodenPickaxe()` 內部呼叫 `craftCraftingTable()`、`mineBlock()`
   - Hermes：skills 是線性 steps，skill 之間不互相引用（除了 `skill_view` 這個機械操作）
   - **差距**：Hermes skill 之間缺乏「這個 skill 的 step 3 依賴 skill X 的 step 2」的機制。skill authoring 建議過 chain 但沒有 enforce
   - **但注意**：Voyager skill 的組合是 runtime 動態決定的（Action agent 自己選要用哪些 skill），不是預先定義的。Hermes 可能更適合這個模式

4. **Iterative self-correction**
   - Voyager：Action → execution → error → Critic → retry（最多 4 輪）
   - Hermes：skill steps 如果失敗，LLM 會自行重試（ad-hoc），沒有結構化的 error → refinement loop
   - **機會**：心跳 autonomic layer 已經有 `EVOLVE` action 做 structured error tracking。如果加上「錯誤發生時自動建議修正」層，就是 Voyager-style iterative prompting
   - 已有基礎建設：`heartbeat_severity.json`、`ISSUES.md` known-issue suppression、`_categorize_error()`

### 不適合直接搬的

1. **Code-as-skill**：Voyager 技能是 executable code（JS functions），因為 Minecraft 環境是確定性的 API。Hermes 的「環境」是 shell + file system + web API，不確定性高很多，純 code skill 不適合。

2. **Embedding-based curriculum**：Voyager 用 Minecraft 的 tech tree 作為隱性 curriculum（木→石→鐵→鑽石）。Hermes 沒有這種線性 progression，curriculum 更難定義。

3. **GPT-4 dependency**：Voyager 重度依賴 GPT-4（code generation + self-critique），token cost 很高。Hermes 主力是 DeepSeek v4-pro（便宜但 code 能力不如 GPT-4），純 code generation loop 可能不划算。

### 最值得做的實驗

| 優先 | 想法 | 難度 | 影響 |
|:---:|------|:---:|:---:|
| 🥇 | **Skill embedding search**：給 `skills_list` 加 vectordb，讓 LLM 只看到 top-k relevant skills | 中 | 高 — 現在 128 skills 已經快塞不進 context |
| 🥈 | **Task → Skill 自動提示**：heartbeat 偵測到重複成功模式時，自動建議 `skill_manage create` | 中 | 中 — 減少手動 skill authoring |
| 🥉 | **Composable skill references**：skill 格式加 `requires: [skill-name]` field，LLM 載入時自動 chain | 低 | 中 — 讓 skills 從 flat list 變成 graph |

---

## 跨文章 Synthesis

- **[[2026-05-15-behavior-cache-muscle-mem]]** — muscle-mem 的 trajectory replay 和 Voyager 的 skill library 是互補的兩種記憶：muscle-mem 記「步驟序列」（procedural），Voyager 記「可重用的程式碼片段」（declarative）。理想系統應該兩種都有。
- **[[2026-05-13-agent-orchestrator-patterns]]** — Voyager 的 Curriculum → Action → Critic 是典型的 orchestrator pattern，只是三層都在 LLM 內部而非 separate agents
- **[[2026-05-14-compaction-context-rot-handbook]]** — Skill embedding search 是另一種 anti-context-rot 策略：與其壓縮歷史，不如只給 LLM 看相關 skills
- **[[2026-05-15-agent-cost-security-convergence]]** — Voyager 的 token cost 是主要瓶頸之一（每輪 action-critic 都是 full context），這也是為什麼 skill library 的「一次生成、多次使用」模式對省成本有巨大價值

---

## 未追蹤但值得注意

- **GITM（Ghost in the Minecraft）** — Voyager paper 的主要比較對象。用 hierarchical planning 而非 code generation。值得對比。
- **SPRING** — 用 LLM + DQN 在 Minecraft 做 RL。不同 paradigm（RL vs code generation），但和 muscle-mem 的 trajectory replay 有交集。
- **JARVIS-1** — 另一個 Minecraft lifelong learning agent，用 multimodal memory。和 Voyager 比較可以看出 design space 的不同取捨。
- **Voyager paper 的 failure analysis** — paper 裡面有一節分析 Voyager 失敗的案例（spatial reasoning errors、crafting sequence errors）。這些和 Hermes agent 在複雜任務中的失敗模式可能相似。

