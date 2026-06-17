---
_slug: 40-Resources-_mixed-research-2026-06-08-0101-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-08-0101-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-08'
confidence: high
title: 看不見的狀態，看不見的失敗：約束衰減與行為合約指向同一個盲區
updated: '2026-06-15'
type: research
status: budding
---

# 看不見的狀態，看不見的失敗：約束衰減與行為合約指向同一個盲區

**消化筆記**: 2026-06-08-constraint-decay-llm-agents, 2026-06-08-agent-behavioral-contracts

兩篇同日筆記表面上一篇談「工具/框架怎麼讓 agent 變笨」、一篇談「agent 如何被外部契約與 policy 守門」，但交叉比對後浮現同一條主軸：**agent 失敗的根源不是能力不足，而是它在決策當下對自身狀態與外部約束的可見度不完整**。

## Cross-Cutting Theme 1: 看不見的狀態 = 失敗的共同母體

**支援筆記**: 2026-06-08-constraint-decay-llm-agents, 2026-06-08-agent-behavioral-contracts

三個看似獨立的失敗現象，其實是同一個盲點的三種投影：

| 現象 | 出處 | 看不見什麼 |
|---|---|---|
| Premature halting（模型送 NL 摘要而非 finish tool） | Constraint Decay | 看不見自己「任務還沒做完」這個 completion state |
| 45% data-layer defects（ORM runtime violations、framework idiosyncrasy） | Constraint Decay | 看不見 framework 暗藏的執行期 invariant |
| 90-98% policy violation 率（policy state hidden at decision time） | PhantomPolicy | 看不見當下 context 適用哪些 org policy |

**共同結構**：agent 在「我以為我完成了 / 我以為這樣做對 / 我以為這個工具能用」三個時刻都發生了**模型自身 state model 與 ground truth 狀態的裂縫**。Constraint Decay 量化了這個裂縫在「加 constraint」時的後果（L0→L3 掉 30pp），PhantomPolicy 量化了它在「policy 不可見」時的後果（90%+ 違規），ABC 給出了數學形式化（D* = α/γ — drift 是 natural drift rate 與 recovery rate 的競賽）。

**可行動下一步**：在 Hermes 內建一個 `state_self_check.py`，在 agent 宣告完成 / 提交結果前，強制做三項檢查：(a) 是否有 orphan tool call 沒有對應的後續動作、(b) 寫入的檔案/狀態是否符合 schema、(c) 此 context 適用的 policy constraint 是否全部滿足。這把「看不見的狀態」從 agent 內部推理搬到外部 runtime check——直接呼應 PhantomPolicy 的核心主張 "policy enforcement should be architecturally separated from model reasoning"。

## Cross-Cutting Theme 2: 結構必須是「承重」的，不是「裝飾」的

**支援筆記**: 2026-06-08-constraint-decay-llm-agents, 2026-06-08-agent-behavioral-contracts

Constraint Decay 顯示 Flask（minimal、explicit）擊敗 FastAPI/Django（convention-heavy）；ABC 顯示只有「recovery rate γ > natural drift rate α」的 contract 才有 bounded drift；PhantomPolicy 顯示只有 world-model coverage 100% 的 sentinel 才能 100% recall。三者共同指向：

> **結構的價值不在於多寡，在於它是否承載了真實的 invariant。Convention-heavy 的框架把「慣例」包進 constraint，agent 必須在推理時記住/推論這些慣例——這正是 decay 來源。Contract 的硬約束若不對應實際 invariant，就會被 agent 學會忽略；若對應實際 invariant 又沒 recovery 機制，drift 無界。**

換句話說：**Constraint Decay 和 ABC 的 Drift Bound 是同一條光譜的兩端**——前者是「壞約束」（無對應 invariant）導致能力崩跌，後者是「好約束 + recovery」導致 drift 有界。Talos governance 與 agent tool design 的設計原則應該是：**每個 constraint 都必須回答「它承載哪個 invariant？recovery 機制是什麼？」** 否則就是裝飾性約束，遲早 decay。

**可行動下一步**：對 Talos 的 tool surface 跑一次 audit——列出每個 tool 與 policy constraint，分類為 (a) 承載真實 invariant 且有 recovery、(b) 承載真實 invariant 但無 recovery、(c) convention/裝飾性。預期 (c) 類應該被移除或外部化（見 Theme 3）。把 (b) 類補上 recovery 機制（γ 的具體實作：re-prompting、rollback、checkpoint）。

## Cross-Cutting Theme 3: 把約束外部化是三條論文的共同設計歸宿

**支援筆記**: 2026-06-08-constraint-decay-llm-agents, 2026-06-08-agent-behavioral-contracts

Constraint Decay 暗示 minimal scaffold 勝出（少給 agent 內化約束）；PhantomPolicy 明說 "architecturally separated from model reasoning"；ABC 走得更遠：ContractSpec DSL 是宣告式 YAML、AgentAssert 是 O(sub-10ms) 的外部 runtime。WS-029 guardian-sandboxing-gradient 的 L2 gateway mediation 也是同一個 pattern。**Talos 的 governance 層恰好就是這個位置的天然落點**——它不必是另一個 LLM agent，而是 contract enforcement engine。

**可行動下一步**：把 Talos 重新定位為「contract enforcement layer」而非「另一個 reasoning agent」。具體：(1) 採用 ContractSpec YAML 描述每個 policy constraint 與 recovery 機制；(2) 借鏡 Sentinel 的 graph invariant 設計——把 tool call 視為對 Hermes 內部 state graph 的 mutation，invariant 預檢查；(3) 監控 D* drift bound 作為長期 reliability metric。這讓 Talos 從「會思考的守門人」變成「會執行合約的守門人」——前者容易 decay，後者有界。
