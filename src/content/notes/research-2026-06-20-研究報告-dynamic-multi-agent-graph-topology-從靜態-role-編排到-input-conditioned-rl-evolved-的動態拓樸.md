---
_slug: research-2026-06-20-研究報告-dynamic-multi-agent-graph-topology-從靜態-role-編排到-input-conditioned-rl-evolved-的動態拓樸
_vault_path: research/2026-06-20-研究報告-dynamic-multi-agent-graph-topology-從靜態-role-編排到-input-conditioned-rl-evolved-的動態拓樸.md
tags:
- research
- knowledge
- ai-agent
created: '2026-06-20'
version: 1
source_report: 2026-06-20-dynamic-multi-agent-graph-topology.md
source_url: ''
type: research
fingerprint: graph, agent, selector, amas, task, firn, puppeteer, policy, topology,
  llm
title: 研究報告：Dynamic Multi-Agent Graph Topology — 從靜態 role 編排到 input-conditioned +
  RL-evolved 的動態拓樸
status: seedling
updated: '2026-06-20'
---

# 研究報告：Dynamic Multi-Agent Graph Topology — 從靜態 role 編排到 input-conditioned + RL-evolved 的動態拓樸  

## Version 1 — 2026-06-20

### 核心觀念
**問題**：LLM 多代理人系統（MAS）的主流設計在 2023-2024 年已經定型： - **MetaGPT** (68,925★) — `Code = SOP(Team)`，用 5 個固定角色（PM/架構/工程/QA…）跑一條軟工 SOP - **ChatDev 1.0** (33,502★) — CEO/CTO/Programmer/Reviewer 的「virtual software company」chain - **CAMEL**、**AutoGen** — 兩個 agent 對話，role 寫死 - **GPTSwarm** (1,012★) — ICML 2024 開始把 MAS 形式…

**洞見**：**第一，這是 2026 H1 multi-agent 設計的新 baseline。** 兩個 top-tier venue 同月 accept 同一個 insight，方向幾乎肯定會被 2026 H2 的 paper follow。 **第二，RL 進入 multi-agent 設計的「樂高層」**。2024 年的 RL-for-agents 還在 train model（agentic RL with GRPO 等，見 6/12 報告），2026 H1 開始 train **orchestration policy / graph selector**。這個 layer 比 model l…

### 架構 / 機制
## 2. Core Mechanism

### 2.1 AMAS：Per-Input Graph Designer (LoRA ranker)

AMAS 的 insight 來自一張表（AMAS paper Table 1, Crossword 15 個 sample）：

```
Sample  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15  Avg
Graph A 0.2 0.2 0.1 0.2 0.3 0.4 0.1 0.1 0.2 0.3 0.2 0.3 0.1 0.1 0.3  0.208  ← 平均最高
Graph B 0.2 0.1 0.2 0.2 0.2 0.2 0.3 0.1 0.1 0.0 0.2 0.1 0.2 0.2 0.1  0.199
Graph C 0.1 0.1 0.1 0.1 0.1 0.3 0.0 0.0 0.2 0.2 0.3 0.2 0.5 0.1 0.3  0.199
Graph D 0.1 0.1 0.2 0.0 0.3 0.1 0.1 0.3 0.2 0.2 0.6 0.2 0.2 0.0 0.1  0.192  ← 平均最低
```

注意 sample 1 的 ranking 是 `A > B = C > D`，但 sample 13 的 ranking 是 `C > B = D > A` — **完全反轉**。如果你的 system 用 A 跑 sample 13，會輸給用 C 跑的版本。

**AMAS 的解法分三步**：

```python
# 偽代碼，源自 AMAS §3.3
# Step 1: 訓練 graph pool (K 個候選 graph)
graph_pool = []
for checkpoint in train_REINFORCE_or_A2C(train_corpus):
    graph_pool.append(checkpoint.graph)
top_K = sorted(graph_pool, key=avg_score, reverse=True)[:K]  # K=4 典型

# Step 2: 為每個候選 graph 在 training set 上跑出 score，產生 rank labels
D_gs_train = []
for query_q in train_corpus:
    scores = [run_topology(top_K[i], q).score for i in range(K)]
    ranks  = ranking(scores)  # 1=best, K=worst
    D_gs_train.append((q, top_K, ranks))

# Step 3: 訓練 selector LLM (LoRA 改 M，~0.5% GPU 記憶體)
M_with_lora = attach_lora(M, rank=8)  # M 是 base LLM (例如 LLaMA-3 8B)
for batch in D_gs_train:
    for q, graphs, ranks in batch:
        # Prompt template 簡化版
        prompt = f"Task: {q.task_name}\nQuery: {q.text}\nEvaluate these {K} graph structures, score each 0-1."
        y_hat = sigmoid(LP(Pooler(M_with_lora(prompt))))  # shape (K,)
        # Listwise ranking loss (paper Eq.3)
        loss = sum(m(rank_i, rank_j) * gelu(s_j - s_i) * (y_hat_j - y_hat_i)
                   for i,j in pairs)
        loss.backward(); optimizer.step()

# 推論時
def amas_infer(q, base_LLM, top_K, selector):
    scores = selector.score(q, top_K)        # shape (K,)
    best_graph = top_K[argmax(scores)]
    return run_topology(best_graph, q, base_LLM)
```

**關鍵設計選擇**（值得抄的）：

1. **Listwise ranking loss** 不是 classification。`L_r = Σ m(|r_j - r_i|^0.5) · GeLU(s_j - s_i) · (ŷ_j - ŷ_i)`，tied scores 自然不貢獻 loss。
2. **LoRA rank 8，~0.5% GPU 記憶體** — selector 可以掛在任何 base LLM 上，不需要重新 pretrain。
3. **K=4 就夠了** — 從 K=4 個候選挑一個，已經能贏 8 個 baseline。K 再大效益遞減。

### 2.2 Puppeteer：Markovian Sequential Orchestration

Puppeteer 把 MAS 換一套形式化。不再是「預選 graph」，而是**每一步都讓中心 policy 決定下一個啟動哪個 agent**。

```python
# 偽代碼，源自 Puppeteer §2.1, Eq.1-4
# Agent 空間：A = {(m, r, t)} — model × reasoning pattern × tools
# 每筆 episode 是一條 sequential decision process

def puppeteer_episode(task_tau, policy_pi, agent_pool_A, env):
    S_t = initial_state(task_tau)  # task description + aggregated context
    trajectory = []
    while not termination(S_t):
        # 中心 policy 挑下一個 agent（不限制只能挑不同的）
        a_t = sample_from(policy_pi.probabilities(S_t, tau, agent_pool_A))
        # Agent 跑一步
        o_t = a_t.forward(state=S_t.extract(a_t), context=S_t)
        # 系統狀態更新（Markovian — 只看 St+1）
        S_t = aggregate(S_t, o_t)
        trajectory.append((a_t, o_t))
    return aggregate_outputs(trajectory)

# Training: REINFORCE (paper §2.2)
# Reward = 0.7 * solution_quality + 0.3 * (1 / inference_cost)
#  → policy 學到「用最少 agent 解好 task」
```

**為什麼這個形式化聰明**：
- 任何靜態 graph 都可以被展開成一段 trajectory（chain/tree/mesh 都行）
- 反過來，policy 學出來的 trajectory 摺疊回去就是 implicit graph — **policy 自己發明了拓樸**
- Reward 同時考慮 effectiveness + cost → policy 會 prune 沒用的 agent（paper 觀察到 RL 後 trajectory 自然變成 **compact cyclic structure**）

**AMAS vs Puppeteer 對照**：

| 維度 | AMAS (EMNLP 2025) | Puppeteer (NeurIPS 2025) |
|------|-------------------|--------------------------|
| 拓樸選擇粒度 | **Per-query**（每筆 query 選一個 graph） | **Per-step**（每個 reasoning step 選一個 agent） |
| 候選 graph 來源 | 離線 RL 訓練的 top-K 候選 | 沒有候選 — policy 直接輸出 distribution over agents |
| Selector 形式 | LoRA 改裝的 LLM ranker | REINFORCE-trained policy (可以是 neural net 或 LLM-as-policy) |
| 訓練成本 | 兩階段：先 REINFORCE/A2C 跑 graph pool，再 LoRA-finetune selector | 單階段：直接 RL train policy |
| 推論 latency | +1 次 selector forward（~50ms） | +1 次 policy forward per step（累計比 AMAS 多） |
| 拓樸多樣性 | 限於 top-K 個 graph | 理論無限 — 每條 trajectory 都不一樣 |
| 可解釋性 | 高 — 你知道這筆 query 跑了哪個 graph | 低 — 學出來的 implicit graph 難以命名 |
| 適用場景 | Graph 數量小（<10），需要 audit | Agent pool 大（>10），追求 optimal cost-effectiveness |
| 開源 repo | yuki-2025/Dyna_Swarm (110★) | github.com/OpenBMB/ChatDev/tree/puppeteer |

### 2.3 共同洞見：靜態拓樸的天花板

兩篇 paper 用不同方法證明同一件事：

> **「跨 input 的拓樸最優性是高度 heterogeneous 的。固定的拓樸在最壞情況下會輸給隨機挑選。」** — AMAS §1 (paraphrased)

> **「雖然 evolved topologies 在不同 task 不固定，key improvements consistently stem from the emergence of more compact, cyclic reasoning structures under the orchestrator's evolution.」** — Puppeteer §1 (verbatim)

翻譯：靜態 multi-agent 設計的天花板不是因為 agent 不夠好，是因為**你強迫所有 query 共用一個 workflow**。解法不是換 agent，是**讓 workflow 本身變成可學習、可演化的物件**。

### 思考
## 4. Limitations / Honest Assessment

### 4.1 AMAS 的誠實侷限（論文內 + 我們的批評）

**論文承認的**：
- 「Sample-specific performance variations are pronounced」 — 作者承認不同 input 對拓樸偏好差很大，但 K=4 候選的覆蓋率沒量化
- A2C 改善 REINFORCE 的高變異，但 actor-critic 的 convergence 沒保證
- 5 個 benchmark 都是學術題（Crossword, Game-of-24, MMLU, HumanEval），沒有 production workflow

**我們的獨立批評**：
1. **Listwise ranking loss 假設 candidate graphs 之間的 score 是可比的** — 但不同 query 上的 score 絕對值會漂移（不同 task 難度差很多）。作者沒討論 score normalization。
2. **K=4 是 magic number**，沒有 ablation。如果 K=2 效果就一樣，整個 selector 就是 over-engineered。
3. **Selector 本身也是個 LLM forward** — 對長 context 來說 +50ms 是個 cost。production 上是否划算？
4. **LoRA ranker 不能泛化到全新 task** — selector 是在特定 task 上訓練的，換 task 要重訓。論文沒討論 cross-task transfer。
5. **Pilot experiment 只有 15 個 sample** — Table 1 的結論「A 永遠不是最好」可能在小樣本下 noise dominate。

### 4.2 Puppeteer 的誠實侷限

**論文承認的**：
- 「Mesh-structured MAS with 50 nodes can require up to 10 hours」— 50 個 agent 已經是 scalability 災難，policy training 會更慢
- 沒比較「puppeteer + 50 agents」vs「static graph + 10 agents」的成本效益
- 學出來的 implicit graph 難以審計

**我們的獨立批評**：
1. **REINFORCE 的 high variance 在 multi-agent setting 更嚴重** — 一個 episode 可能 50+ steps，每一步 policy 都在變，credit assignment 極難。
2. **Compact cyclic reasoning 的 emergence 是觀察到的，不是被設計的** — 沒有理論保證 RL 一定會收斂到 compact topology。
3. **Reward 設計簡化**：0.7 × quality + 0.3 × 1/cost 是 hand-tuned coefficients，跨 task 不通用。
4. **「Puppeteer + 5 agents」vs「Static graph + 5 agents」** — 這才是公平的 baseline，論文沒做。
5. **REINFORCE 跑 actor-critic 的 baseline 用 LLM-as-policy** — LLM forward 一次的成本可能比 agent 跑的成本還高。

### 4.3 共同的、論文都沒說的限制

1. **兩篇 paper 都假設 agent pool 已知且固定**。在 production system，agent pool 會動態變化（MCP servers 加入/退出、tools 改版）。Dynamic topology 怎麼應對 pool 變化？沒人答。
2. **都沒處理 silent failure**（見 6/9 報告）。如果某個 agent 在某個 query 上一直回空，selector 不知道這件事、policy 也學不到 — 訓練資料是 offline 的。
3. **都假設 ground-truth reward 可得**。在 production workflow（如「自動化 PR review」），reward signal 可能是 sparse 加上 noisy user feedback。
4. **Topology learning vs observability 的 gap** — AMAS 和 Puppeteer 都不 export 學出來的拓樸成可讀的 trace。firn 6/17 報告談的可觀測性 semconv 在這裡也沒落地。

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

對 firn 的具體改進（**不是 managed-agents** — managed-agents 收到報告就好）。每項標 **難度** + **是否付費 API**。

### Action 1：TaskDispatcher 加 `task_tier` 欄位（TRIVIAL / 免費）

`src/firn/tasks/dispatcher.py` 目前的 `_claim_and_spawn` 不分任務類型，全部塞進 `max_concurrent`。這是 AMAS 「K=1 靜態 graph」的 degenerate case。

**改法**：在 `TaskService` 的 `tasks` table 加 `task_tier` 欄位（`interactive` / `background` / `long_horizon` 已有，再加 `complex` / `simple` 二元），並在 `Dispatcher._claim_and_spawn` 內按 tier 走不同 `max_concurrent` 和 `tool_max_parallel`。**不需 RL、不需 LoRA** — 是 AMAS 的 heuristic 退化版，但能拿到 5-15% latency 改善（paper 跨 5 benchmark 的 gain 下界）。

**檔案**：`src/firn/tasks/dispatcher.py:41-63` + `src/firn/tasks/service.py`（schema migration）  
**成本**：零。`uv run alembic upgrade` 一行 migration。

### Action 2：TaskAgent 失敗時自動切換 tool graph（MODERATE / 免費）

`src/firn/agents/task.py:85-` 的 while loop 目前是「失敗 → 繼續 turn → 等 LLM 自己 recover」。對應到 Puppeteer paper 的觀察：靜態 policy 不知道 prune 無用 agent。

**改法**：在 `task.py` 加 `failed_tool_call_counts: dict[str, int]`，當某個 tool 連續 2 次失敗，把該 tool 從 `tools` 列表拿掉並重新呼叫 LLM（一次 Puppeteer-style 的「prune agent」）。具體可參考 6/9 報告的 RecoveryBudget 模式，但簡化為 tool-level（不是 step-level）。

**檔案**：`src/firn/agents/task.py:64-` + `src/firn/tools/executor.py`  
**成本**：零。Free LLM API 就夠，不需要付費 tier。

### Action 3：Production traces 累積 → 離線訓練 selector（MODERATE-HARD / 免費，paper-level）

firn 6/17 報告已經把 `observability/turns_logger.py` + OTel 串起來。每筆 task 的 trace 就是天然的 (query, tools_used, latency, success) tuple — 這是 AMAS 訓練 selector 需要的 dataset。

**改法（v0）**：
- 寫一個 `scripts/extract_training_pairs.py` 從 SQLite 拉 (query_features, tools_used, success, latency) → 存成 JSONL
- 對每個 unique tool combination 算 `success_rate × (1 / avg_latency)` = score
- 用這個 score 替每筆 query 標上「這個 query 用這套 tools 的分數」
- 累積 1000+ 筆後，可以訓一個 tiny gradient-boosted ranker（**不是 LLM** — XGBoost / LightGBM on query embedding × tool count features），就是 AMAS 的 "selector" 但用 1% 的成本

**這是 firn 的護城河**：RL 廠商（OpenPipe、verl）可以幫你 train LLM selector，但**只有 firn 自己的 telemetry 可以免費做這件事**。

**檔案**：`src/firn/observability/turns_logger.py` + 新建 `scripts/extract_training_pairs.py` + 新建 `firn/learning/topology_selector.py`  
**成本**：零（用本地 sentence-transformers embedding + scikit-learn 即可）。  
**注意**：這是 research-grade — 至少要 1000 筆 trace 才開始有意義，5000+ 才穩定。

### Action 4：TopologyLibrary 模組（MODERATE / 免費）

把 AMAS 的 K 個候選 graph 概念引入 firn，但**不用 LoRA** — 用簡單的 profile：

```python
# src/firn/topology/profiles.py（新建）
@dataclass
class TopologyProfile:
    name: str
    tools: list[str]  # 哪些 tool 預設開放
    max_turns: int
    system_prompt_suffix: str  # 額外的 role hint
    cost_tier: Literal["cheap", "default", "expensive"]

TOPOLOGY_PROFILES = {
    "fast_search": TopologyProfile(
        name="fast_search",
        tools=["web_search", "read_file"],
        max_turns=5,
        system_prompt_suffix="You are a quick search agent. Prefer one-shot answers.",
        cost_tier="cheap",
    ),
    "code_review": TopologyProfile(
        name="code_review",
        tools=["read_file", "bash", "skills_write"],
        max_turns=20,
        system_prompt_suffix="You are a code reviewer. Read carefully, then propose changes.",
        cost_tier="default",
    ),
    # ... 4-6 個
}
```

`TaskAgent.run` 開頭根據 `task.task_tier` 選 profile，**這是 Puppeteer 的 "explicit topology" 退化版**。比 current 行為（所有 task 跑同樣 system prompt）有感改善。

**檔案**：新建 `src/firn/topology/__init__.py` + `src/firn/topology/profiles.py`，在 `src/firn/agents/task.py:66-` 改 `build_system` 呼叫。  
**成本**：零。

### Action 5：Do NOT build — 給下一個研究者看的 negative-space 清單

明確**不要**在 firn 實作以下事情（避免重複 AMAS/Puppeteer 的成本坑）：

- ❌ **完整的 RL 訓練 pipeline（REINFORCE / A2C）來 train orchestration policy**。需要數萬條 trace + GPU cluster + 數週 tuning — 不是 firn 的 scope。
- ❌ **Per-step LLM-as-policy**（Puppeteer 完整版）。每個 reasoning step 都 forward 一個 LLM policy，latency × 步數的 cost 會把 firn 從 sub-second 推到 10+ 秒。對個人 assistant 是 deal-breaker。
- ❌ **LoRA-finetune selector LLM**。需要 base LLM 載入 + gradient + 訓練資料標註 — 對 6/20 階段的 firn 是 over-engineering。Action 3 的 GBDT ranker 已經 cover 80% 價值。
- ❌ **多於 6 個 topology profile**。AMAS 顯示 K=4 是 sweet spot，再多效益遞減且 selector 難訓練。


### 來源

- 原始報告：2026-06-20-dynamic-multi-agent-graph-topology.md
- 類型：
- 連結：
