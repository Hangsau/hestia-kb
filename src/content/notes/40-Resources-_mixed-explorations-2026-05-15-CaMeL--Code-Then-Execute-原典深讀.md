---
_slug: 40-Resources-_mixed-explorations-2026-05-15-CaMeL--Code-Then-Execute-原典深讀
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-CaMeL--Code-Then-Execute-原典深讀.md
title: 'CaMeL: Code-Then-Execute 原典深讀'
date: 2026-05-15
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- camel
- data
- email
- hermes
- llm
- policy
- prompt
- python
- tool
- untrusted
created: '2026-05-15'
updated: '2026-06-15'
status: budding
---

# CaMeL: Code-Then-Execute 原典深讀

**延續自**: [[2026-05-15-prompt-injection-design-patterns]] 的未追蹤 lead（CaMeL paper）

**日期**: 2026-05-15 | **來源**: arxiv 2503.18813 + Simon Willison 分析

---

## 一句話

CaMeL 不是用更多 AI 去偵測 prompt injection——而是用**能力追蹤（capability tracking）＋自訂 Python 解譯器**在架構層面保證安全性。這是第一個聲稱有「強保證」而非「99% 偵測率」的 prompt injection 防禦方案。

## 核心機制

### 雙 LLM → 程式碼生成 → 能力追蹤解譯器

```
User prompt → P-LLM（特權，只能看到 user query）
           → 生成 restricted Python code（AST parsed）
           → Custom interpreter 執行，追蹤每個變數的 data provenance
           → Q-LLM（隔離，無 tool access）只在需要 parsing untrusted data 時被呼叫
           → Interpreter 根據 capability tag + security policy 決定允許或拒絕 tool call
```

**關鍵差異 vs Simon 的 Dual-LLM**：Simon 的原始設計中 Q-LLM 的輸出（如 extracted email）還是會回到 plan flow，可能被汙染。CaMeL 在 interpreter 層加入 capability tracking——追蹤每個變數是從哪來的（trusted/untrusted），並在 tool call 前檢查 policy。

### 實際程式碼範例

```python
email = get_last_email()                              # untrusted source
address = query_quarantined_llm(                      # derived from email → untrusted
    "Find Bob's email address in [email]",
    output_schema = EmailStr
)
send_email(                                           # policy check: only if recipient is trusted
    subject="Meeting tomorrow",
    body="Remember our meeting tomorrow",
    recipient=address,
)
```

Interpreter 追蹤：`email` 來自 untrusted source → `address` 繼承 untrusted tag → `send_email(recipient=untrusted)` 觸發 policy，若非已知 trusted address 則需使用者核准。

### 為什麼是 Python

- 所有 LLM 都會寫 Python
- `ast` 模組可以 parse 並限制語法子集（不能 import、不能 eval、不能 arbitrary code）
- 遞迴解譯 AST node，每個 node 都可以注入 capability check

## 安全性質

> 「CaMeL is a practical defense achieving security not through model training techniques but through principled system design.」

**不靠機率**：99% 偵測率在安全領域 = 失敗（攻擊者會找那 1%）。CaMeL 的保證來自架構——只要 policy 正確設定，untrusted data 就無法控制 program flow。

**AgentDojo benchmark**：77% 任務完成（vs 84% undefended），但有 provable security。trade-off 是 7% 的功能性損失換安全性保證。

## 限制與現實

1. **使用者需定義 security policy**：誰能 access 什麼、哪些 tool call 需要核准。這是最大的 adoption 障礙——大多數使用者連 AWS IAM 都搞不定。
2. **User fatigue**：一直跳核准對話框 → 使用者進入「一直按 yes」的麻木狀態。Troy Hunt 都曾因時差疲勞中 phishing。
3. **Policy 維護負擔**：policy 需要隨系統演化更新，否則過時的 policy = 安全漏洞或誤擋。
4. **Restricted Python 的表達力限制**：不是所有 agent workflow 都能用 restricted Python 表達。

## 隱私紅利

P-LLM 只看到 user query，永遠看不到 tool output（那些可能包含敏感資料的 email、文件內容）。Q-LLM 可以跑在 local 小模型上——意味著可以用雲端強模型做 planning，但敏感資料不離開使用者機器。

## 對 Hermes 的啟發

### 驗證了 Plan-Then-Execute 的學術基礎

我們的 `exploration-prompt-injection-defense.md` 採用 Plan-Then-Execute 作為核心防禦——先鎖定計畫，再接觸 untrusted content。CaMeL 提供了這個模式的學術正當性：

- PT-E 是 CaMeL 的簡化版——我們沒有 custom interpreter，但「計畫先行」的原則相同
- CaMeL 的 data provenance tracking 對應我們「接觸 untrusted content 前鎖定下一步決策」的規則

### 可以但不必現在做的事

**Taint tracking at tool output level**：Hermes 的 tool call → output 流程中，可以標記哪些 tool output 來自 untrusted source（`web_search`、`fetch`）。這個概念輕量，不需要 custom interpreter——在 prompt 裡加入 output 的 trust level 標記即可。

```
工具輸出格式：
[UNTRUSTED] web_search 結果: ...
[TRUSTED]   read_file 結果: ...
```

但**成本和收益不成比例**：Hermes 是一人 agent，沒有 multi-tenant 的 exfiltration 風險。目前 PT-E + exploration template 強制已經足夠。

### 值得追的旁支

- **Policy-as-config 的 UX 設計**：CaMeL 最大的弱點是 policy 設定門檻。如果有人做出「policy 自動生成」或「policy 推薦引擎」，對 Hermes 的自主安全決策會有啟發。
- **AST-based restricted execution**：Hermes 的 tool call 目前是 JSON schema → bash。如果未來需要 sandboxed execution layer，Python AST 比 Docker/VM 更輕量（但只適用於 Python-only workflows）。

## 未追蹤但值得注意

- **GitHub repo** (`google-research/camel-prompt-injection`) — 實際實作品質如何？codebase 可讀性？有沒有可以借用的 capability tracking 實作？
- **AgentDojo benchmark** — 77% vs 84% 的 gap 來自哪裡？哪些 task type 最容易被 CaMeL 擋住？
- **Policy specification language** — CaMeL 用什麼語法定義 policy？是 YAML/JSON 還是 Python DSL？
- **CaMeL vs Action-Selector（Simon 的下一層防禦）** — 兩者的安全模型如何互補？CaMeL cover 不到的部分 Action-Selector 能否補？
- **"Lethal trifecta" 文章**（Simon, 2025-06-16）— private data + untrusted content + external communication 的交集。這篇是 Simon 在 CaMeL 之後寫的，可能更完整地總結了 prompt injection 的全貌。

---

## 跨文章 Synthesis

今天追了四層 prompt injection 的防禦光譜：

| Layer | Approach | Security Model | Hermes 對應 |
|-------|----------|----------------|-------------|
| Design Patterns paper | 10 case studies，7 defensive patterns | 機率性（pattern 組合） | PT-E 列入 exploration 強制規則 |
| Dual-LLM (Simon) | 隔離 planning & execution 的 LLM | 架構性，但有 data flow 漏洞 | — |
| **CaMeL (DeepMind)** | **Dual-LLM + capability tracking + custom interpreter** | **架構性保證（data provenance）** | **PT-E 的學術基礎** |
| Action-Selector | 只允許 predefined action set | 架構性（最小權限） | Hermes tool 本身就有固定 schema |

CaMeL 補上了 Dual-LLM 和 Action-Selector 之間的空隙：Dual-LLM 有 data flow 漏洞，Action-Selector 太受限。CaMeL 的 capability tracking 是中間方案——保留 LLM 的彈性，但在 execution 層強制 policy。

對 Hermes 而言，我們不在 CaMeL 的 threat model 裡（單一使用者、無外部 communication channel 的 exfiltration 風險），但 PT-E 原則直接受益於 CaMeL 的學術驗證。如果有人說「PT-E 只是 heuristic」，可以引用 CaMeL 的 formal model 回應：**控制流與資料流分離，untrusted data 不應影響 program flow**。

