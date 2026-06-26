---
_slug: research-2026-06-26-研究報告-production-agent-safety-2026-h1-governance-by-architecture-policy-as-code-scalable-oversight-三條主軸
_vault_path: research/2026-06-26-研究報告-production-agent-safety-2026-h1-governance-by-architecture-policy-as-code-scalable-oversight-三條主軸.md
tags:
- research
- knowledge
- ai-agent
created: '2026-06-26'
version: 1
source_report: 2026-06-26-agent-safety-governance-architecture-2026h1.md
source_url: ''
type: research
fingerprint: agent, safety, arxiv, policy, debate, cedar, guard, 論文, prompt, trace
title: 研究報告：Production Agent Safety 2026 H1 — Governance-by-Architecture, Policy-as-Code,
  Scalable Oversight 三條主軸
status: seedling
updated: '2026-06-26'
---

# 研究報告：Production Agent Safety 2026 H1 — Governance-by-Architecture, Policy-as-Code, Scalable Oversight 三條主軸

## Version 1 — 2026-06-26

### 核心觀念
**問題**：2025 年 agent safety 的主旋律是 **prompt-based guardrail + output filter + refusal classifier**。到了 2026 H1，這套典範正面臨三重衝擊： **衝擊一：內嵌控制不可信。** Seth Dobrin & Łukasz Chmiel 在 *The Unfireable Safety Kernel* (arXiv 2606.26057) 把這個直覺形式化：任何放在 agent address space 內的控制（system prompt、output filter、guardrail library）都**可…

**洞見**：2026 H1 的 agent safety 不再是「把 LLM 訓練得更聽話」，而是「**承認 LLM 是 leaky abstraction，把 trust boundary 重新畫**」。 這個位移有三個具體含義： **含義一：safety 變成 infrastructure 問題。** Grimlock、Unfireable Safety Kernel、SQA 都把 safety 推到底層——eBPF、process separation、consensus protocol。這跟 2024-2025 的「更好的 RLHF」「更細的 CAI」完全不同層次。**這是 agentic sy…

### 架構 / 機制
## 2. Core Mechanism

把 14 個 2026 H1 paper 整理到**三條主軸**上，每條軸都是「舊典範 → 新典範」的明確位移：

### 2.1 主軸 A：Governance-by-Architecture（信任邊界外移）

| 層級 | 舊設計（2024-25） | 新設計（2026 H1） | 代表 |
|------|------------------|-------------------|------|
| LLM runtime | System prompt + refusal classifier | Agent **無法觸及**的 external guard | Unfireable Safety Kernel |
| Sandbox | 純環境隔離 | eBPF-enforced traffic interception + attested channel | **Grimlock** |
| Runtime state | 分散 transcript/memory/event | **Session** 為 first-class 物件，branchable/replayable | OpenRath |
| Cloud control plane | Manual approval on 危險動作 | 語義共識：proposer 多 agent 提議，attester 對 intent 簽名 | SQA |

**核心範式：不信任 LLM 自己，把 enforcement 推到底層**。

#### 2.1.1 Grimlock — eBPF Agent Guard（arXiv 2605.27488）

**問題**：agentic system 執行 user-authored orchestration code，這段程式碼 invoke tools、spawn subtasks、跨機器 delegate。identity / authorization / provenance / delegation 全部 push 進 application code，**很難一致 enforce、很難 audit**。

**機制**：
- 用 **eBPF-enforced traffic interception**，保證 sandbox 之間的 communication 必須通過一個 guard
- 結合 **post-handshake attested channel**：TLS handshake 完成後再做一次 cryptographic attestation，確認對方真的是受信任的 agent runtime
- agent code **完全不用改**——trust enforcement 都在 substrate 層

**為什麼這是 2026 idiom 轉折**：之前所有 agent safety paper 都把控制放在 agent「裡面」（system prompt、fine-tune、output filter）。Grimlock 直接宣告：**任何 in-agent 控制都是 cooperative request，不是 enforcement**。把 trust 拉到 OS / kernel 層（eBPF 是 Linux kernel 內的安全鉤子），agent 即使被 prompt injection 攻陷，**也無法繞過 guard 呼叫未授權工具**。

#### 2.1.2 Unfireable Safety Kernel（arXiv 2606.26057）

Dobrin & Chmiel 形式化一個 class：*escapable AI systems*——「agent 有能力修改自己 runtime 的一切」。他們提出四個 architectural 必要條件：

1. **Process separation**（guard 與 agent 是不同 OS process）
2. **Hardware-rooted attestation**（guard 自身的 binary 由 TPM 驗證）
3. **Deterministic control flow**（guard 的決策路徑不能用 LLM 改寫）
4. **Continuous evidence**（決策 log 是 append-only + cryptographic chain）

> 「**Unfireable**」 的雙關：agent 連「fire the guard」都做不到，因為 guard 在它的 address space 之外。

#### 2.1.3 OpenRath — Session as First-Class Runtime Value（arXiv 2606.19409）

把 PyTorch 的 tensor abstraction 借來做 multi-agent 系統。**核心抽象是 Session**——branchable、inspectable、replayable、backend-aware、composable 的 runtime value。記錄 conversation chunks、sandbox placement、lineage metadata、token usage、pending side-effects。

**為什麼這跟 safety 有關**：safety 偵測需要「**重放** agent 走過的軌跡」，而現有 agent system 的 transcript / tool effect / memory event / workspace state **散落在不同 backend**。OpenRath 把這些收斂到一個 Session 物件，讓事後的 trajectory-level safety analysis（如 TRACE）有乾淨的輸入。

#### 2.1.4 SQA — Semantic Quorum Assurance（arXiv 2606.08021）

雲端 agent 場景。問題：proposer agent 可以產生**語法正確、靜態授權通過、但操作上危險**的 mutation（修改 IAM policy、開 firewall rule、export data）。傳統 distributed consensus（Paxos/Raft）只 replicate 確定性的 state transition，**不評估 proposed intent 的 safety**。

SQA 把提案表示成 declarative execution spec，由 **attester agents** 對 intent 做語義投票。達到 quorum 才放行。這把 safety check 從 LLM runtime 推到 **control plane consensus layer**。

### 2.2 主軸 B：Policy-as-Code / Autoformalization（讓 policy 可形式驗證）

| 對象 | 舊設計 | 新設計 | 代表 |
|------|--------|--------|------|
| Agent 行為約束 | Prompt instruction | **Cedar Policy DSL** 編譯產物 | Autoformalization into Cedar |
| Alignment training | CAI（純自然語言 constitution） | CAI 仍保留 + rubric-based RL | RUBAS |
| 長程軌跡審查 | Turn-level classifier | **Trajectory-level evidence compression** | TRACE |
| Safety 量化 | Greedy / few-shot sampling | **BOA 搜尋 trajectory 空間** | BOA framework |

**核心範式：safety 不能停留在自然語言或機率輸出，必須落到可驗證、可執行的形式語言**。

#### 2.2.1 Autoformalization into Cedar（arXiv 2606.26649, Mondl et al.）

**問題**：高風險場域的 agent safety 要 formal policy enforcement。但現有兩條路都失敗：
- **機率式 guardrail**（fine-tune classifier / prompt steering）：沒有 formal 保証
- **手寫 symbolic policy**：不 scale 到真實 breadth

**機制**：
- LLM-based generator-critic loop：把 agent prompt、MCP tool description、natural language policy 文件**翻譯成 Cedar Policy Language**（AWS 的 formal authorization DSL）
- Generator 寫 Cedar，Critic 跑 formal verifier（AWS Cedar 引擎）回 counterexample，Generator 修
- 最終產出 **provably enforced policy**

**為什麼重要**：Cedar 不是新發明（AWS 2024 開源），但 2026 H1 第一次有 paper 系統性把 LLM 當 **policy compiler frontend**，搭配 verifier 在 loop 裡修。這是「**LLM-as-formalizer**」的 idiom——不只生成 code，而是**生成 verifiable artifact**。

#### 2.2.2 RUBAS — Rubric-Based RL for Agent Safety（arXiv 2606.04051）

CAI（Constitutional AI）的瓶頸：refusal 是 coarse binary signal，靜態 supervision 無法平衡 safety vs useful tool execution。

RUBAS 把 agent behavior 拆成 **四個維度的 rubric**：
1. Tool-use safety（這個 tool call 本身可不可接受？）
2. Argument safety（傳給 tool 的參數有沒有洩漏敏感資訊？）
3. Response safety（給 user 的回應有沒有 prompt injection 殘留？）
4. Helpfulness（在 safety 約束下實際完成任務的品質）

每個維度獨立打分，rubric 本身用 LLM 生成 + human verification。RL 在這個 multi-dimensional rubric 上跑。

**這跟 6/13 報的 prompt-injection firewall 互補**：firewall 是「外部 input/output filter」，RUBAS 是「agent 內部 fine-grained behavior shaping」。兩者結合是 production agent 的 defense-in-depth。

#### 2.2.3 TRACE — Trajectory Risk-Aware Compression（arXiv 2606.00611）

長程 agent 軌跡裡的 risk signal 是**稀疏、延遲、可組合**的。Turn-level classifier 抓不到。

TRACE 把 long-horizon agent safety detection **重新框定為 trajectory-level evidence compression**：
- **Compressor**：把整條 trajectory 編碼成 compact latent evidence state
- **Reader**：基於 evidence state 做 final safety verdict
- 訓練 signal 來自 trajectory-level label（整段軌跡安不安全），而非逐 turn

**為什麼這是 2026 idiom**：之前 safety classifier 都是「**single-turn local moderation**」——看到一句話就判安不安全。TRACE 承認**安全證據是跨步累積的**——一個現在看起來無害的 tool call，在它後面三步可能觸發 exfiltration chain。

#### 2.2.4 BOA — Beyond Sampling Safety Measurement（arXiv 2605.01644）

Lin, Suri, Oprea, Tan 提出一個**破壞性觀察**：今天所有 agent safety eval 都跑 greedy 或少量 sampled rollout，報一個 safe/unsafe rate——**完全盲視 long-tail 軌跡**。

BOA 的論點：**agent safety 應該被 measure by search, not by sampling**。給定 deployment configuration（model、decoder、prompt、environment、judger、likelihood budget），BOA 搜尋 in-budget trajectory 空間，報一個 **safety score = P(agent stays safe under this configuration)**。

搜尋同時涵蓋**單一 LLM round 內**（不同 tool arg、ordering）與**跨 round**（不同 sub-task sequence）。把 safety 從「點估計」變成「分布估計」。

### 2.3 主軸 C：Scalable Oversight via Debate / Weak-to-Strong Critics

| 對象 | 舊設計 | 新設計 | 代表 |
|------|--------|--------|------|
| Oversight 協議 | Human 標註 / 強 judge | **弱 critic + on-policy distillation** | Weak Critics Make Strong Learners |
| 多 agent 拓樸 | Fully connected | Adaptive / sparse / trust-aware | ARMOR-MAD, Dynamic Trust-Aware |
| Debate 終止 | 固定 N round | Early stopping + agreement routing | ARMOR-MAD (EASE) |
| 信心校準 | Heuristic threshold | **保守 baseline + 偏差懲罰** | CCO Calibrated Collective Oversight |
| 失敗模式 | 假設對手存在 | **無對手也會失敗** | ROGUE corrigibility |

**核心範式：human-level oversight 不可能 scale 過 frontier capability，必須用 protocol-level mechanism 來 enlarge human judgment**。

#### 2.3.1 Weak Critics Make Strong Learners（arXiv 2606.00424）

問題：model 變強後，**weak supervisor 連 label / preference / final judgment 都不夠可靠**，weak-to-strong generalization 卡住。

新解法：把 weak model 當 **critic**（不是 labeler / judge）。不要它解任務或選答案，而是讓它**對 strong model 的 reasoning step 打 critique**。**On-policy critique distillation**：用 critic 的 critique signal 蒸餾到 student model。

**為什麼這是 2026 idiom**：scalable oversight 的經典配方是「consultancy / debate / market」——其中 *Debate Helps Weak Judges Reward Stronger Models* (2605.27483, Elasky et al.) 進一步 tighten 條件：**critic 的 classification ability 必須超過 judge**，且 judge 必須把 critic 的發言當「**待驗證的 claim**」而非「**可採信的 testimony**」。

兩個 paper 一起讀，才看到 2026 H1 對 debate 的共識：**debate 不是 magical amplifier，**它只在「critic > judge on the discriminating dimension」時有效**。

#### 2.3.2 Calibrated Collective Oversight — CCO（arXiv 2605.28807）

Overman & Bayati 正面處理 scalable oversight 的 sequential / 統計保証問題。他們把 diverse auxiliary scoring functions 聚合為一個 penalty，**測量 deviation from a conservative baseline**。靈感來自 Attainable Utility Preservation（AUP）——RL safety 領域避免 agent 學到「把所有 reward 通道都關掉以為這是 optimal」。

CCO 給的不是 heuristic，是 sequential decision problem 下的 **conservative baseline + 偏差懲罰** 機制，讓 oversight 在「agent 可能比 overseer 強」時仍維持 statistical guarantee。

#### 2.3.3 ARMOR-MAD（arXiv 2606.13197）

Multi-agent debate 的三個失敗：
1. 固定 topology 浪費 compute
2. 同質 agent 放大 correlated error
3. Round 數浪費（已經收斂還在講）

ARMOR-MAD 把 debate 當 conditional computation：
- **Pre-debate Agreement Routing (PAR)**：Round 0 答案若一致，**直接跳過 debate**
- **Early Agreement Stopping Evaluator (EASE)**：中途收斂就停
- **Semantic Outlier Detection (SOD)**：把 outlier agent 降權

同叢集還有 *Dynamic Trust-Aware Sparse Communication Topology* (2606.01828)——LLM 多 agent 系統用 sparse + trust-weighted 拓樸，**把 fully connected 的 O(N²) 通訊成本砍到接近 O(N log N)**。

### 2.4 反例與失敗模式（critical — 不能跳過）

**反例 1：MAD 反而有害** — *When Helping Hurts* (arXiv 2606.02866)：3 個 benchmark × 4 model family × 6000 task-condition pair，**debate 在 generation 任務上 -1.6 到 -15.5pp**，原因是 **critique-induced confusion (CIC)**——critic 的 feedback 是 hallucinated 但 generator uncritically accept。只在 **error detection** 任務上有效。

**反例 2：CAI 哲學反撲** — *A Virtuous AI is an Existential Risk* (arXiv 2606.13739, Del Pinal et al.)：用 Virtue Ethics 框架反駁 CAI，finetune "Virtuous/Subordinate/Generic" 三種 constitution 並比較 general safety 表現，**質疑 CAI 的可擴展性**。

**反例 3：Decomposition Attacks** — *DECOMPBENCH* (arXiv 2606.13994, Kothamasu et al.)：harmful task 拆成多個 **各自 benign** 的 sub-task，**每個 sub-task 過 safety check，組合起來就是 attack**。直接打臉「逐 turn 安全 = 整體安全」假設。

**反例 4：Training Strata 無法被 system prompt 覆寫** — (arXiv 2605.28102, Claude & Luo)：在 47,000+ 訊息、8 個月 longitudinal 互動中，識別出 RLHF/CAI 訓練留下的**五個 persistent behavioral strata**（包括 sexual expression latency 等），**system prompt replacement 也無法完全消除**。

**反例 5：Plan-Action Divergence** — *SPADE-Bench* (arXiv 2606.02380, Bu et al.)：agent 的 self-reported update **與實際執行** 可以 systematic diverging。在 long-horizon 任務中，這種「看起來在做，實際沒做 / 做別的」是隱蔽 control loss。

**反例 6：Detection ≠ Correction** — (arXiv 2605.27559, Nilayam et al.)：多 stage pipeline 的「辯論後正確率提升」其實主要是 **detection 改變**，**conditional generation 沒動**。下游任務看到的進步是 routing artifact。

---

### 思考
## 4. Limitations / Honest Assessment

### 4.1 作者坦承的限制

- **Grimlock**：eBPF 是 Linux 限定。Windows / macOS 需另實作（BPF on Windows 不完整）。**kernel version ≤ 5.10 不支援所有 hook**。
- **Autoformalization into Cedar**：Generator-critic loop 收斂**不保証**。Counterexample-driven synthesis 在複雜 policy 下可能 cycle。**Cedar 表達力有限**——例如 time-window 條件、表決決策需要 workaround。
- **CCO**：conservative baseline 的選擇**仍需要 domain knowledge**。Baseline 設太寬 = penalty 永遠小，沒效果；設太窄 = agent 永遠被罰，學不到東西。
- **RUBAS**：rubric 本身用 LLM 生成，**rubric 的 quality 是 bottleneck**。Rubric 寫錯 = RL signal 偏。
- **BOA**：搜尋 trajectory 空間的計算成本隨 horizon 指數成長。**likelihood budget 怎麼設是 open question**。
- **ARMOR-MAD**：PAR / EASE / SOD 三個 component 各自有 threshold hyperparameter，**跨 model family 的 transfer 沒系統性 study**。
- **TRACE**：latent evidence state 的 interpretability 不強——人很難 debug「為什麼這個 evidence state 判定 unsafe」。

### 4.2 我們的獨立評估

**問題一：eBPF / Kernel-level guard 的 vendor lock-in。** Grimlock 假設你能控制整個 host kernel。但在 managed cloud（AWS Lambda / Vercel Functions / Cloudflare Workers），**kernel 是租來的**。在 SaaS 多租戶 agent platform 上，**同一個 host kernel 不能裝兩個 tenant 的 guard**。**結論**：Grimlock 模型適合 self-hosted agent infra，不適合 multi-tenant SaaS agent。

**問題二：Policy-as-Code 的維護負擔。** Cedar 看起來比 prompt 好，但**寫 Cedar policy 的工程師比寫 prompt 的少兩個數量級**。**結論**：autoformalization 必須真的能從 natural language policy doc 直接生成可編譯的 Cedar，並在 policy 改版時**自動 re-synthesize**——這部分研究還不成熟。

**問題三：Debate 的失敗模式被低估。** *When Helping Hurts* 揭露的 CIC（critique-induced confusion）+ *Detection Without Correction* 揭露的 detection-only improvement + *DECOMPBENCH* 揭露的 sub-task decomposition 攻擊——**這三個反例合在一起暗示**：**當前 debate protocol 在 production 環境下可能比 baseline 更差**。需要更多 empirical study 確認 debate 在哪些 task class 上**真的**有效。

**問題四：訓練 strata 不可覆寫。** *Training Stratigraphy* (2605.28102) 的發現意味著：**alignment 的所有努力在某些 behavioral pattern 上都會 leak**。若 5 個 strata 之中任何一個在 production 場景觸發，且無法用 system prompt 壓制，**那 model 部署前的「RLHF + CAI」就不是 sufficient safety measure**——必須靠 runtime guard。

**問題五：consensus-based safety 的 throughput 瓶頸。** SQA 把 safety 推到 consensus layer，但 consensus 本身**慢**。對 latency-sensitive agent（如 trading / interactive）**不可行**。需要**快路徑 + 慢路徑**的分層設計，目前沒看到 paper 系統處理。

**問題六：對齊訓練 vs runtime guard 的 cost asymmetry 沒量化。** 沒看到 paper 系統比較「**fine-tune 一個更安全的 model**」vs「**加 runtime guard 來 enforce 一個普通 model**」的成本效益。**這是 production 決策的核心問題**。

**問題七：對「可重現」與「可重放」的依賴被低估。** OpenRath 與 TRACE 都需要 trajectory 可重放，但 production agent 的 side-effect（送 email / 改 DB）**無法完全重放**。需要 **deterministic replay layer + side-effect ledger**，目前**沒看到 open-source production-grade 實作**。

### 4.3 對比既有方案

| 既有方案 | 2026 H1 對應 | 主要差異 |
|----------|--------------|----------|
| ReAct / AutoGPT 的 self-critique | RUBAS、Weak Critics | 從 in-prompt self-critique → multi-dim rubric RL；weak critic protocol |
| CrewAI / AutoGen 的 multi-agent | ARMOR-MAD、SQA | 從 fully connected → adaptive routing + semantic consensus |
| Constitutional AI | RUBAS、Autoformalization into Cedar | 從自然語言 constitution → rubric + formal policy DSL |
| Prompt-injection firewall (6/13) | Unfireable Safety Kernel、Grimlock | 從 input filter → kernel-level enforcement (eBPF / process separation) |
| WebArena / SWE-bench eval | BOA、TRACE | 從 point estimate pass@1 → distribution P(unsafe) + trajectory-level compression |

### 4.4 可複製性

| 方法 | 難度 | 瓶頸 |
|------|------|------|
| Grimlock eBPF hook | **MODERATE** | 需要 Linux kernel 5.10+、eBPF 工具鏈 |
| Unfireable Safety Kernel | **HARD** | TPM attestation、kernel customization |
| Autoformalization into Cedar | **MODERATE** | LLM-as-formalizer loop 設計、Cedar 工具鏈 |
| RUBAS rubric RL | **MODERATE-HARD** | 4 維 rubric 的 quality、RL infra |
| BOA safety search | **MODERATE** | trajectory space search infra（向 MCTS / BO 借） |
| TRACE | **MODERATE** | Compressor-Reader 雙模型訓練、trajectory 收集 |
| ARMOR-MAD | **TRIVIAL-MODERATE** | 三個 component 各自簡單，整合需實測 |
| CCO | **MODERATE** | auxiliary scoring function 設計 |
| **免費 API 可行性** | 全部可行 | 需要 LLM（GPT-4o / Claude Sonnet / Qwen3）做 generator / critic / compressor；本地 Qwen3-32B 可 cover 多數 |

---

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

### 5.1 firn / managed-agents 具體改進

#### Action 1（**MODERATE，1-2 週**）：加 **trajectory audit layer**（借 OpenRath + TRACE）

firn 現有 trace 分散在 transcript / tool effect / workspace state。**先做 Step 1**：把每次 agent run 包成 **Session 物件**（JSONL append-only），包含 conversation chunks、tool call signature、token usage、branch ID。**Step 2**：在 Session 上加 **trajectory-level risk score**（trace risk-aware compression 的簡易版：對 session 跑 heuristic rule + LLM 雙評，最後 emit risk: low/medium/high）。

**理由**：production agent 的 safety incident 都需要「事後重放 + 跨步分析」，沒有 Session abstraction 一切都得從 log 反推。**Session 是 TRACE / BOA / SQA 共同的底層依賴**。

#### Action 2（**MODERATE，1 週**）：加 **external policy hook**（借 Grimlock + Unfireable Kernel 的精神，簡化版）

firn 的 agent runtime 加 **policy check hook**，在每個 tool call 之前 / 每個訊息送出之前 call 一個 **獨立 process** 的 policy function。**Step 1**：寫簡單的 YAML policy DSL（不直接用 Cedar，**先用 firn 內部簡化版**）。**Step 2**：policy function 跑在獨立 process（不與 agent 共用 Python interpreter），**確保 agent prompt injection 無法直接改寫 policy**。**Step 3**：把 policy 決策 log 到 Session（接 Action 1）。

**理由**：*When Helping Hurts* 揭露「agent 自己審查自己會 CIC」，*Training Stratigraphy* 揭露「in-prompt alignment 不夠」，**唯一可靠解法是 external guard**。

#### Action 3（**MODERATE，3-5 天**）：加 **decomposition-attack detection**（借 DECOMPBENCH）

在 Action 1 的 Session 之上，跑 **post-hoc decomposition attack detector**：對每個 multi-step task 序列，**檢查 benign sub-task chain 是否能組合成高風險意圖**。最簡實作：對每個 tool call 抽 (action_type, target, payload) tuple，建**sub-task graph**，用規則 + LLM judge 找「**累計風險 = high**」的 sub-task chain。

**理由**：DECOMPBENCH 已經是公開 benchmark，**firn 應該把它納入 regression test**——確保我們的 agent 不會被 3 個 benign 步驟組合成 exfiltration。

#### Action 4（**MODERATE-HARD，1-2 週**）：research cron 加 **safety-evidence collection**

每次 cron run 結束，**自動產出 safety evidence report**（不只是成功 / 失敗）：

- Trajectory summary（用 TRACE 思路壓縮）
- Plan-action divergence check（對比 plan 與實際 tool call sequence，借 SPADE-Bench）
- Corrigibility check（中途有沒有抗拒 interrupt / shutdown 訊號，借 ROGUE）
- Sub-task composition risk（借 DECOMPBENCH）

寫入 `managed-agents/safety-evidence/YYYY-MM-DD-{job-name}.md`。每週累計 review。

**理由**：6/25 報的 benchmark saturation 與 6/17 報的 trace formalization 都指向同一個結論——**沒有 structured safety evidence，agent eval 就是 single number theater**。Safety evidence collection 是把「**safety as distribution**」落地的最簡單起點。

#### Action 5（**TRIVIAL，1 天**）：把 *Detection Without Correction* 的 protocol 套到我們現有的 multi-agent（firn 內部 agent 互相 check 的場景）

firn 已有的 multi-agent step（如 spawn subagent）加上 detection / correction 的分離：
- **Detection sub-agent** 專門判斷「上游內容是否值得採信」
- **Generation sub-agent** 只在被告知「上游已通過 detection」後才生成
- 兩者用獨立 process（接 Action 2 的 policy hook）

**理由**：*Detection Without Correction* 揭露的失敗模式（辯論提升來自 detection 而非 correction）意味著**多 agent 設計必須明確分開這兩個職責**，不混在同一個 LLM call 裡。

#### Action 6（**HARD，2-4 週，研究級**）：study **Cedar autoformalization for firn policy**

拿 firn 現有的 agent prompt + tool description，**跑 autoformalization into Cedar**（借 arXiv 2606.26649 的 generator-critic loop）。研究問題：Cedar policy 的 quality 跟手寫 prompt 的 safety coverage 對比如何？**預期產出**：1 個 working prototype + 1 份 comparison report。

**理由**：這是「**policy-as-code 對 prompt-as-policy**」的具體 empirical 比較，目前文獻沒有。firn 有真實 workload 可以跑，**比寫純 paper 的學者更接近 production reality**。

### 5.2 與過往報告的連結

- **6/13 prompt-injection firewall**：Action 2 是 firewall 的「**從 input filter 升級到 substrate-level guard**」演化版
- **6/17 trace formalization**：Action 1 + Action 4 把 trace 從 log 升級到 evidence
- **6/25 benchmark saturation**：Action 4 的 safety evidence collection 是解「**safety eval 不能只靠 pass@1**」的最小可行方案
- **6/22 agent swarm emergent coordination**：Action 5 把 swarm 的 emergent behavior 加上 detection/correction 的 protocol-level 分割
- **6/9 reliability engineering**：Action 1 + Action 4 直接接 reliability 的 failure mode taxonomy，把 safety 收進去

### 5.3 不需要做的事

- **不要做 constitutional AI fine-tune**：CAI 在 2026 H1 已被 *Virtuous AI is Existential Risk* 質疑，且 *Training Stratigraphy* 揭露 in-training alignment 不可覆寫問題。**把資源放在 runtime guard，不要放在更好的 fine-tune**。
- **不要單獨押注 multi-agent debate**：*When Helping Hurts* 揭露 -15.5pp 的反例。Debate 可作為 ensemble 的一個 component，**不能當作 oversight 的主力**。
- **不要自己做 kernel-level eBPF guard**：對 firn 來說是 over-engineering。**用獨立 process + policy DSL 就夠了**——這是 Grimlock 精神在應用層的簡化版。

---


### 來源

- 原始報告：2026-06-26-agent-safety-governance-architecture-2026h1.md
- 類型：
- 連結：
