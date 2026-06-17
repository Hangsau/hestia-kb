---
_slug: 40-Resources-_mixed-research-2026-06-08-研究報告-agent-skill-系統的-progressive-disclosure-設計模式-2026
_vault_path: 40-Resources/_mixed/research/2026-06-08-研究報告-agent-skill-系統的-progressive-disclosure-設計模式-2026.md
tags:
- research
- knowledge
- ai-agent
created: '2026-06-08'
version: 1
source_report: 2026-06-08-agent-skill-systems-progressive-disclosure-2026.md
source_url: null
type: research
fingerprint: skill, skills, agent, description, llm, anthropic, token, mcp, openskills,
  spec
title: 研究報告：Agent Skill 系統的 Progressive Disclosure 設計模式 (2026)
updated: '2026-06-15'
status: budding
---

# 研究報告：Agent Skill 系統的 Progressive Disclosure 設計模式 (2026)

## Version 1 — 2026-06-08

### 核心觀念
**問題**：2025 年 10 月 Anthropic 推出 Agent Skills 系統，將「在 context window 內塞太多 prompt」的老問題換了一個框架：把領域專業知識打包成 SKILL.md 目錄，agent 動態載入。但隨即出現 6 個獨立開源實作（OpenSkills、opencode-skillful、aleph、skillz、buddyMe、agentskills.io）— 這代表「skill loading 是 agent framework 的新瓶頸」已經是 2026 上半年的事實。 **為什麼這是問題**： - 20 個 skill × 2000 token 描述 …

**洞見**：**2026 的共識**：skill loading 與 tool calling 是兩個分離的關注點。 | 面向 | Tool | Skill | |------|------|-------| | 觸發 | LLM 決策 function call | LLM 決策 load markdown | | 副作用 | 執行 action + return result | 修改 conversation context | | 並發 | 安全（每個 result 獨立） | 不安全（注入的指令影響所有後續 turn） | | Token | schema + result | descript…

### 架構 / 機制
## 2. Core Mechanism

### 2.1 三層 Progressive Disclosure（Anthropic 設計原文）

> "Skills should be structured to take advantage of progressive disclosure" — agentskills.io spec

```
┌─────────────────────────────────────────────┐
│ Layer 0: Metadata (~100 tokens × N skills) │ ← 啟動時全部載入 system prompt
│ - name                                     │
│ - description                              │
├─────────────────────────────────────────────┤
│ Layer 1: SKILL.md body (<5000 tokens)       │ ← 觸發時一次載入
│ - YAML frontmatter                         │
│ - Markdown instructions                    │
├─────────────────────────────────────────────┤
│ Layer 2+: Resources (按需)                  │ ← 觸發時再讀取
│ - scripts/   (executable)                  │
│ - references/ (additional docs)            │
│ - assets/    (templates, images)           │
└─────────────────────────────────────────────┘
```

關鍵 insight：**L0 的 description 是「在 LLM 腦中插入的廣告」，description 寫得好不好直接決定 skill 觸發率。** Anthropic 官方建議 description 包含「使用情境關鍵字」（"Use when working with PDF documents"）而非抽象描述（"Helps with PDFs"）。

### 2.2 呼叫流程（opencode-skillful 實作）

```
User: "Help me write a commit message"
        ↓
[System prompt L0] <Skill name="experts_writing_git_commits" desc="...">
        ↓
LLM 推理：判斷 skill 適合 → 呼叫 skill_use("experts_writing_git_commits")
        ↓
[L1 載入] SKILL.md body 注入 context (~3000 token)
        ↓
[Resource 探索] LLM 自選讀取 references/style-guide.md（如需）
        ↓
LLM 開始按 skill 內的指示工作
```

### 2.3 Skill 格式規範（agentskills.io）

**YAML frontmatter 必要欄位**：

```yaml
---
name: skill-name              # 1-64 chars, lowercase + hyphens
description: |                # 1-1024 chars, 必須含使用情境
  Extracts PDF text and fills forms. Use when working with
  PDF documents or when the user mentions PDFs.
license: Apache-2.0
compatibility: "Requires Python 3.10+, pip"
metadata:
  author: example-org
  version: "1.0"
allowed-tools: "Bash(git:*) Read"   # Experimental
---
```

**可選目錄**：
- `scripts/` — 可執行程式碼（Python / Bash / JS，agent 自由決定何時呼叫）
- `references/` — 額外文檔（按需載入）
- `assets/` — 靜態資源（模板、圖片、schema）

**檔案引用規則**：`SKILL.md` 用相對路徑引用其他檔案，深度保持 1 層（避免鏈式載入爆炸）。

### 2.4 三種激活架構（業界 2026 分化）

| 架構 | 代表 | 觸發方式 | 適用場景 |
|------|------|---------|---------|
| **In-prompt metadata** | Claude Code, OpenSkills | LLM 看 description 自選 | 通用 coding agent |
| **Tool-call lazy load** | opencode-skillful | `skill_find` / `skill_use` 工具呼叫 | 50+ skills 的大庫 |
| **MCP-shim** | skillz, aleph | MCP server 暴露 `list_skills` / `read_skill` 工具 | 跨 agent 互通 |
| **三級漸進 + Hot reload** | buddyMe | 元數據 → 預匹配 → 完整注入 | 中國語境多模型框架 |

### 2.5 buddyMe 的三級漸進具體做法（最值得看）

```
[階段 1: 任務規劃] 
  → 注入 Skill metadata (name + description)
  → LLM 拆解子任務，匹配到的步驟標注 [SKILL:技能名]

[階段 2: 子任務執行]
  → 每個子任務獨立 LLM+工具循環
  → 預匹配 Skill 注入完整指令（不是 metadata）
  → 結果傳遞 + 類型分類

[階段 3: 結果合併]
  → 拼接子任務結果
```

亮點：**子任務執行階段才做「完整指令注入」，規劃階段只給 metadata**。這比 Anthropic 的二級（metadata + body）更精細：規劃期的子任務對應「我可能用哪個 skill」，執行期才付費「完整 SKILL.md 內容」。

### 思考
## 4. Limitations / Honest Assessment

### 4.1 作者坦承的限制

**Anthropic 自己說的安全風險**（engineering 文章原文）：
> "Skills provide Claude with new capabilities through instructions and code. While this makes them powerful, it also means that malicious skills may introduce vulnerabilities in the environment where they're used or direct Claude to exfiltrate data and take unintended actions."

**Lee Hanchung 的 first-principles 分析**（2025-10-26）點出更深層問題：
- 沒有演算法層的 skill 路由 — 純 LLM 推理，沒有 embedding search / 分類器 / regex
- Skill 之間組合沒有正式規範 — 兩個 skill 互相矛盾的指令會如何處理未定義
- Token 預算管理隱性 — description 寫太長會擠掉其他 context，沒有人工預算控制

**Skillz README 的標題級警告**：
> "⚠️ Experimental proof-of-concept. Potentially unsafe. Treat skills like untrusted code and run in sandboxes/containers."

### 4.2 我們的獨立評估

| 限制 | 嚴重度 | 真實情境 |
|------|--------|---------|
| **LLM 觸發不可靠** | HIGH | 同一 query 換個措辭可能不觸發；description 沒寫到的關鍵字會錯過 |
| **L1 body 仍是 context 殺手** | MEDIUM | 5000 token 的 SKILL.md 在長對話中累積，多個 skill 同時載入會擠爆 |
| **沒有 skill 衝突解決機制** | HIGH | 兩個 skill 給矛盾指令（如「永遠不要 commit」 vs「完成後立即 commit」） |
| **資源管理無版本控制** | MEDIUM | skill 升級可能破壞既有 agent 行為，沒有 A/B 機制 |
| **scripts 是任意程式碼** | HIGH | skill creator 任意執行 `rm -rf` 都可能 — skillz 警告「像 untrusted code」 |
| **無付費 API 標準化** | LOW | 各家 marketplace 互不打通（OpenSkills 用 GitHub，Claude Code 用 Anthropic marketplace）|
| **市場發現機制差** | MEDIUM | 「找到適合的 skill」靠口耳相傳，沒有 quality ranking / 評論 |

### 4.3 對比既有方案

| 既有方案 | Skill 系統差異 |
|---------|---------------|
| **ReAct** | ReAct 是「推理 + 動作」模式，skill 是「知識 + 工具」內容。Skill 系統可內嵌 ReAct 但不取代。 |
| **AutoGPT** | AutoGPT 強調「自動拆解任務」，skill 強調「領域專業載入」。buddyMe 是兩者混合：先拆再用 skill 補專業。 |
| **MCP** | MCP 是工具層（dynamic tool calls），skill 是知識層（static prompt injection）。skillz 試圖把 skill 套上 MCP 介面，但這是「把 prompt 偽裝成 tool」。 |
| **CrewAI** | CrewAI 的「agent role」是程式碼定義的，skill 是 markdown 定義的。Skill 系統對非工程師更友善。 |
| **OpenAI GPTs Actions** | GPT Actions 是 function call schema，skill 是 prompt 與文件。本質類似但介面不同。 |

### 4.4 可複製性

**普通開發者重現 skill 系統的難度：TRIVIAL**（純文字 + 兩個函數）
- 寫 SKILL.md 5 分鐘
- 寫 loader 解析 frontmatter 30 分鐘
- 注入 system prompt 1 小時

**真正難的是：**
1. 寫出**好**的 description（需要反覆試錯）
2. 讓 skill 觸發率達到 90%+（需理解 LLM 行為）
3. 處理 skill 衝突（沒有人有答案）
4. 跨 agent 互通（需要各家合作，目前只有 OpenSkills 比較通用）

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

### 5.1 firn（開源個人 AI agent 框架）— 已有部分基礎

**現狀確認**（`/root/firn/src/firn/skills/`）：
- `loader.py` 已有 SKILL.md YAML 解析 ✅
- `service.py` 已有 `get_level0_skills()` (L0 progressive disclosure) ✅
- `SkillMeta` 已有 `fallback_for_tools` / `requires_tools` 自動過濾 ✅
- 已實作 `builtin/memory/SKILL.md` ✅
- 缺：`allowed-tools` frontmatter 欄位（spec 新欄位，Experimental）

**具體改進（按優先級）**：

| 優先 | 行動 | 難度 | 影響 |
|------|------|------|------|
| P0 | 在 `loader.py` 加 `allowed_tools` 欄位解析（spec 新欄位，6 LOC） | TRIVIAL | 對齊 open spec，向 community 表態「我們 follow agentskills.io」|
| P0 | 改 `service.py`：當 skill 啟動時，自動注入 `SkillMeta.allowed_tools` 到 ToolRegistry | MODERATE | 讓 skill 對「執行環境」有更精細控制（per-spec 設計）|
| P0 | 在 `discover_skills()` 加入 nested 目錄掃描（skillz 模式） | TRIVIAL | 支援 `skills/text-tools/summarize/` 等組織方式 |
| P1 | 加 `SkillService.activate_skill(name, context)` 介面，呼叫時注入 metadata | MODERATE | 區分 L0 (啟動) vs L1 (觸發)，對齊 Anthropic 模型 |
| P1 | 在 SkillService 介面加 `list_resources(skill_name)` 回傳 references/assets 清單 | MODERATE | 支援 L2+ 級 progressive disclosure（agent 自主決定何時讀檔）|
| P2 | 改 SKILL.md 解析支援 `compatibility` 欄位（max 500 chars 環境需求）| TRIVIAL | spec 對齊 |
| P2 | 自動產生 skill 的 description quality lint（檢查長度、是否含「Use when...」）| MODERATE | 防止描述寫太爛觸發率差 |
| P2 | 跨 user skill 庫（`~/skills/` 與 `~/.firn/skills/`）雙來源掃描 | TRIVIAL | 與 OpenSkills 路徑慣例一致 |

**不需要付費 API**：firn 目前的 SKILL.md loader 是純 Python + PyYAML，全部免費。

### 5.2 hermes（本系統）— 已有完整 skills 系統但格式不同

**現狀**（`~/.hermes/skills/`，128 個 skills）：
- 已有 SKILL.md 格式 ✅
- 已有 frontmatter (`name`, `description`) ✅
- L0/L1/L2 三層載入規範（AGENTS.md 已說明）✅

**與 agentskills.io 對齊的可考慮項目**：

| 優先 | 行動 | 難度 | 影響 |
|------|------|------|------|
| P2 | 補 `compatibility` 欄位支援（spec 新欄位，30 秒 patch frontmatter 解析）| TRIVIAL | 對齊 open spec |
| P2 | 加 `metadata.author` 與 `metadata.version` 自動填充（`skill_manage` 已內建）| TRIVIAL | 為未來 skill marketplace 鋪路 |
| P3 | 把 `name` 欄位驗證改用 spec 規則（lowercase + hyphens only）| TRIVIAL | 防止 dirty naming |
| P3 | 抽 `skill_view` 為 `SkillService.get_skill()` 介面（已經幾乎一樣）| TRIVIAL | 程式碼整潔度 |

**不建議的改動**：
- 不要把 hermes 整套 skill 系統改成 Anthropic 風格 — 現有 128 個 skills 已經形成生態，遷移成本 > 收益
- 不要引入 MCP skill shim（skillz 模式）— hermes 是 native，引入會複雜化

### 5.3 managed-agents（研究框架）— 簡單整合

**現狀**（`/root/managed-agents/`）：無統一 skill 系統。

**可考慮的簡單應用**：
- 在 `archive/research-pipeline/` 將「每日研究流程」封裝成 SKILL.md（命名 `daily-research-workflow`），供未來 agent 載入
- 不需要重寫 — 只需把現有 6 節報告格式 + 4 個 pitfall + 3 個 filter 問題寫成 SKILL.md frontmatter + body

**難度**：TRIVIAL（純文件工作）

### 5.4 共同設計建議 — 寫一個 `skill_view` 的 Python 標準庫

**問題**：hermes, firn, managed-agents 三者都有 SKILL.md 概念，但 loader 都是各自寫的。

**建議**：抽 `skill_view.py` 為共用模組（30 LOC），放在 `~/.hermes/lib/skill_loader.py`：
- `parse_skill(path)` — 解析 frontmatter
- `discover_skills(root)` — 掃描目錄
- `validate_skill(meta)` — 對齊 agentskills.io 規範

**收益**：未來改 frontmatter schema（如加 `compatibility`）只改一處。

**難度**：TRIVIAL。


### 來源

- 原始報告：2026-06-08-agent-skill-systems-progressive-disclosure-2026.md
- 類型：
- 連結：
