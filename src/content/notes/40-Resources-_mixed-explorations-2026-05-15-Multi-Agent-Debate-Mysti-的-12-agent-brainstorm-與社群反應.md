---
_slug: 40-Resources-_mixed-explorations-2026-05-15-Multi-Agent-Debate-Mysti-的-12-agent-brainstorm-與社群反應
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-Multi-Agent-Debate-Mysti-的-12-agent-brainstorm-與社群反應.md
title: Multi-Agent Debate：Mysti 的 12-agent brainstorm 與社群反應
date: 2026-05-15
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- claude
- cli
- code
- debate
- mcp
- multi
- mysti
- review
- vscode
created: '2026-05-15'
updated: '2026-06-15'
status: budding
---

# Multi-Agent Debate：Mysti 的 12-agent brainstorm 與社群反應

**日期**: 2026-05-15
**延續自**: [[2026-05-15-agent-architecture-design]] 的未追蹤 lead（間接關聯）
**來源**: HN Algolia (`agent multi-agent collaboration`) → GitHub README → HN 評論
**標籤**: #multi-agent #coding-agent #debate-synthesis #vscode #agent-collaboration

---

## 1. Mysti — 12 個 AI provider 在同一個 VSCode 面板裡協作

**文章**: [Mysti README](https://github.com/DeepMyst/Mysti) (⭐1k, 216 pts, 178 comments)
**作者**: DeepMyst (bahaAbunojaim)

Mysti 是一個 VSCode extension，核心賣點是 **Brainstorm Mode**——讓兩個 AI agent 針對同一任務辯論、互相挑戰、最後合成最佳解。支援 12 個 provider（Claude Code、Codex、Gemini、Copilot、Cline、Cursor、OpenClaw、Manus、OpenCode、Qwen Code、Ollama、LocalAI），切換只需一鍵。

**五種協作策略**：
| 策略 | 角色 | 適用場景 |
|------|------|---------|
| Quick | 直接合成 | 簡單任務 |
| Debate | Critic vs Defender | 架構決策、trade-off |
| Red-Team | Proposer vs Challenger | 安全審查、邊界案例 |
| Perspectives | Risk Analyst vs Innovator | 綠地設計、技術選型 |
| Delphi | Facilitator vs Refiner | 複雜問題、尋求共識 |

**其他功能**：Autonomous Mode（三級安全分類器 + 學習記憶）、@-mention 路由（`@claude review this`）、Context Compaction（75% token 門檻觸發）、16 種 developer persona。

**技術細節**：360 個 vitest 測試，72 commits，Apache 2.0（從 BSL 1.1 切回 MIT），v0.4.0 加入 OpenCode、Qwen Code、Ollama、LocalAI。

---

## 2. HN 評論的集體質疑：多 agent 真的比單一 agent 好？

178 條評論充滿了對「多 agent 辯論」這個前提的挑戰：

### 懷疑論陣營

- **dwa3592**：「HiveMind in LLMs」——不同模型在開放式問題上傾向產出相似結果，多 agent 的邊際價值存疑
- **csar**：「playing house」——persona 系統（Architect、Debugger、Security-Minded）介於無用和有害之間。2025 年 6 月流行過一陣，夏天就沒人玩了
- **danpalmer**：直接挑戰「辯論後合成更好」——你們的 eval 數據在哪？他的研究顯示多 agent 超過某個點會**降低**輸出品質
- **cheema33**：「為什麼不直接用一個 Claude skill 做一樣的事？」暗示 Mysti 只是 UI 層，核心價值是 prompt 不是平台

### 務實派

- **d4rkp4ttern**：用 Tmux 多窗格跑多個 CLI agent，通過自製 Tmux-CLI 工具互相委派——同樣效果，零依賴
- **thomas_witt**：Codex CLI 原生支援 MCP server，Claude Code 可以直接 call Codex 要 second opinion——不需要 VSCode extension
- **tiku**：找到解法——在 Claude Code 裡用 MCP Gemini server，terminal 原生達成多 agent 協作
- **Tarrosion**：工作中用 Claude + Gemini code review，確實抓到不同問題——但這是**序列式**（先 Claude 再 Gemini），不是並行辯論

### Meta 觀察

- **mlrtime**：VSCode 依賴是硬傷——CLI agent 的核心用戶不用 VSCode
- **tombert**：「vibe coding 吸走了寫程式的樂趣」——變成 prompt → wait → review 循環，像個遠端 micromanage 的主管
- **spaceman_2020**：「從沒見過一個職業像寫程式變得這麼快」

---

## 交會點：多 agent 協作的「簡單 vs 重型」光譜

評論和 README 無意間描繪了一條清晰的光譜：

```
輕量 ←─────────────────────────────→ 重型

Tmux delegation    MCP call    Claude skill     Mysti (VSCode)
(手動切窗)         (CLI MCP)   (prompt-based)   (full platform)
d4rkp4ttern        thomas_witt cheema33         DeepMyst
```

**核心張力**：多 agent 協作的價值不在平台，在**模式**。Mysti 把 5 種策略包成產品，但務實派用一行 MCP config 或一個 Tmux pane 就達到類似效果。神秘的是——沒人在爭論「多 agent 有沒有用」，大家在爭論「你需不需要為此裝一個 VSCode extension」。

**更深一層的 pattern**：這和我們在 MCP CLI landscape note 看到的趨勢一致——工具在從「重型平台」往「輕量 CLI 組合」移動。mcpc、mcporter、mcp2cli 都是這個方向的訊號。Mysti 反其道而行（回到 VSCode），難怪 CLI-first 社群排斥。

**關於模型趨同（HiveMind）的 counterpoint**：Tarrosion 的實戰經驗是——Claude 和 Gemini 在 code review 確實抓到不同問題。但重點是**序列式組合**（one after another）不是並行辯論。並行 debate 可能只是 token 浪費——兩個模型同時產出，再花第三輪 token 合成，增加的 latency 和成本是否值得？

---

## 對 Hermes 的啟發

Hermes 已經有 delegate_task 和 managed-agents，但缺乏**結構化的 multi-agent 互動模式**。Mysti 的五種策略提供了一個參考框架，但重型平台路線不適合我們。

**務實路徑**：
1. 最輕量——在現有 delegate_task 上加一個 `--second-opinion` flag：把同一 task 送給不同 provider，diff 兩份輸出，highlight 分歧點
2. 中等——參考 thomas_witt 的 MCP 方案：如果某個 agent 有 MCP server 介面，Claude Code 可以直接 call 它要 review，像 call 一個 tool
3. 重型（不建議）——實作完整的 debate/synthesis pipeline

**關鍵取捨**：多 agent 的價值在「不同視角」（像 Tarrosion 的序列式 review），不在「辯論本身」。Debate 可能只是 token 燃燒——兩個 LLM 互相說「你對但你忘了 X」然後第三輪合成。序列式 review（A 產出 → B 檢查 → A 修正）更務實，而且不需要額外 infra。

---

## 未追蹤但值得注意

- **Mysti 的 Autonomous Mode 設計**（三級安全分類器 + 學習記憶 + audit trail）——和 Hermes heartbeat 的 autonomic layer 有結構上的相似性，值得回頭對比
- **Convergence detection**（agent 立場追蹤 + auto-exit）——如果要做 multi-agent，這個機制本身比 debate 策略更有技術含量
- **HiveMind in LLMs 的原始論文**（dwa3592 提到的）——如果模型真的趨同，多 agent 的整個前提就崩塌了。需要找到那篇論文驗證
- **Tmux-CLI agent delegation**（d4rkp4ttern 的 claude-code-tools）——比 Mysti 更務實的 multi-agent 方案，規模小但設計思路值得參考

