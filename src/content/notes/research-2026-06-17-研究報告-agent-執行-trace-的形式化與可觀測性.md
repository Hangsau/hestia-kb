---
_slug: research-2026-06-17-研究報告-agent-執行-trace-的形式化與可觀測性
_vault_path: research/2026-06-17-研究報告-agent-執行-trace-的形式化與可觀測性.md
tags:
- research
- knowledge
- ai-agent
created: '2026-06-17'
version: 1
source_report: 2026-06-17-agent-trace-formalization-observability.md
source_url: ''
type: research
fingerprint: agent, span, gen, https, trace, langfuse, otel, arxiv, attribute, name
title: 研究報告：Agent 執行 Trace 的形式化與可觀測性
status: seedling
updated: '2026-06-17'
---

# 研究報告：Agent 執行 Trace 的形式化與可觀測性  

## Version 1 — 2026-06-17

### 核心觀念
**問題**：AI agent 從 demo 走進 production 之後，工程團隊面對的第一個問題不是「模型夠不夠聰明」，而是**「這隻 agent 上個月到底做了什麼、有沒有失敗、為什麼失敗」**。當一個 agent 連續執行 12 步 tool call、第 9 步悄悄回傳錯誤但 LLM 把它包成「已完成」回給使用者時，你需要的是 trace 資料，不是 log 檔。 這個問題 2026 年上半年集中爆發。三個社群在 90 天內同時發難： - **學術界**：[arXiv 2606.14589](https://arxiv.org/abs/2606.14589)「When Errors Becom…

**洞見**：這個題目重要的訊號是「**Q2 2026 觀測已變成 table stakes**」，用 §7.15 / §7.10 / §7.7 的「三社群在 90 天內同時發難」模式驗證： | 社群 | 產物 | 時間窗 | |------|------|--------| | 標準化 | OTel GenAI semconv 從主倉搬出、收 `gen_ai.operation.name` | 2026 Q1–Q2 | | 學術 | 2606.14589 / 2606.09863 / 2606.14831 / 2606.08162 / 2606.09071 | 2026-05 到 2026-06-15 |…

### 架構 / 機制
## 2. Core Mechanism

形式化一個 agent trace 的最小公約數 = **OTel span tree**。一個 span = 一段有開始/結束時間、有 parent、有 attributes 的工作單元。整棵樹長這樣：

```
RootSpan (gen_ai.invoke_agent  "Math Tutor")
├── PlanSpan (gen_ai.plan)
├── ToolSpan_1 (gen_ai.execute_tool  "search_web")     -- child of PlanSpan
├── ToolSpan_2 (gen_ai.execute_tool  "calc")
│      └── InferenceSpan (gen_ai.chat  "gpt-4o")       -- nested LLM call
└── InferenceSpan (gen_ai.chat  "gpt-4o")              -- final response
```

### 2.1 OTel GenAI semantic conventions v1.42（2026-06 草案）

每個 span 必填的最小 attribute 集（[來源](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)）：

| Attribute | 必填度 | 範例值 |
|-----------|--------|--------|
| `gen_ai.operation.name` | Required | `chat` / `invoke_agent` / `plan` / `execute_tool` / `create_agent` |
| `gen_ai.provider.name` | Required | `openai` / `anthropic` / `aws.bedrock` / `gcp.vertex_ai` |
| `gen_ai.request.model` | Conditionally | `gpt-4o` |
| `gen_ai.usage.input_tokens` | Recommended | `100` |
| `gen_ai.usage.output_tokens` | Recommended | `180` |
| `error.type` | Conditionally（出錯時）| `timeout` / `_OTHER` |
| `gen_ai.conversation.id` | Conditionally | `thread_abc123` |

**Agent span 五種命名**（[gen-ai-agent-spans.md](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)）：
- `create_agent {gen_ai.agent.name}` — 建構 agent 時
- `invoke_agent {gen_ai.agent.name}` — 跨行程呼叫 agent（CLIENT）
- `invoke_workflow {gen_ai.agent.name}` — 多 agent workflow 起點
- `plan {gen_ai.agent.name}` — 規劃/任務分解階段
- `execute_tool {tool.name}` — 工具呼叫

**這套命名解掉了什麼？** 過去 Langfuse 用 `langfuse.observation.type=agent/tool/chain`、Phoenix 用 OpenInference 的 `OPENINFERENCE_SPAN_KIND`，現在可以共用同一個 `gen_ai.operation.name`，跨平台 trace 直接互通。

### 2.2 OpenLLMetry：把 OTel 包成一行 decorator

```python
from traceloop.sdk import Traceloop

Traceloop.init(app_name="my-agent", disable_batch=False)

# 自動 instrument 任何 OpenAI/Anthropic/Bedrock/Vertex/Vector DB 呼叫
@workflow("customer-support-bot")
def handle_ticket(ticket_id: str) -> str:
    plan = planner.run(ticket_id)            # → 自動產生 plan span
    answer = support_agent.invoke(plan)       # → 自動產生 invoke_agent span
    return answer
```

關鍵點：OpenLLMetry 不是新格式——它是 **OTel instrumentation library**，底層走標準 OTLP。任何 OTel-compatible 後端（Jaeger、Tempo、Honeycomb、Datadog、Phoenix、Langfuse self-host）都能直接接。

### 2.3 Silent Failure 的形式化分類（[arXiv 2606.14589](https://arxiv.org/abs/2606.14589)）

來自 22 次 production incident、40 jobs × 8 LLM provider × 827 governance checks 的縱貫研究：

| Class | 機制 | LLM-only？ |
|-------|------|-----------|
| A. Environment / platform quirks | rate limit、API 漂移、token 計算錯誤 | 否（傳統軟體也有） |
| B. Design-assumption mismatches | 假設工具永遠回 200、假設使用者 prompt 是英文 | 否 |
| C. Error swallowing / dilution | try/except 把 error 吞掉、只 log 摘要 | 否 |
| **D. Chained hallucination & fabrication** | LLM 把 error 改寫成「成功訊息」 | **是** |
| E. Operational omission & forensic blind spots | 監控系統沒觀測到關鍵 span | 否 |

作者稱 Class D 為 **fail-plausible**：「gray failure 的差分可觀測性被升級——觀察者不只是看不見，而是被失敗本身說服性的撒了謊。」這是 LLM agent 獨有的，且最危險，因為**會繞過所有 LLM-as-judge 監控**（judge 也是 LLM，也會被同樣的 narrative 騙到）。

配套檢測（[arXiv 2606.09863](https://arxiv.org/abs/2606.09863)）：在 9,876 條 τ²-bench trace 上，**TF-IDF detector AUROC 0.83**（同樣 flag rate 下比 best LLM-judge 多撈 4–8× false success），關鍵字是「confident closing language」——當 LLM 寫「I've completed the task」但環境 state 沒變，TF-IDF 抓得到，judge 抓不到。

### 2.4 完整最小範例：OpenLLMetry + OTel + SQLite + Langfuse

```python
# pip install opentelemetry-instrumentation-openai opentelemetry-sdk langfuse
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
))
trace.set_tracer_provider(provider)
OpenAIInstrumentor().instrument()        # 一行！自動產生所有 inference span

tracer = trace.get_tracer("firn.agent")
with tracer.start_as_current_span("invoke_agent firn.math-tutor",
                                   attributes={"gen_ai.operation.name": "invoke_agent",
                                              "gen_ai.agent.name": "math-tutor"}) as root:
    with tracer.start_as_current_span("plan") as plan_span:
        plan_span.set_attribute("gen_ai.operation.name", "plan")
        plan = llm_client.chat(...)
    with tracer.start_as_current_span("execute_tool search_web") as tool_span:
        tool_span.set_attribute("gen_ai.operation.name", "execute_tool")
        result = search_web(...)
    # finalize
    root.set_attribute("gen_ai.usage.input_tokens", 320)
    root.set_attribute("gen_ai.usage.output_tokens", 88)
```

---

### 思考
## 4. Limitations / Honest Assessment

**作者自己承認的限制**：

1. **OTel GenAI semconv 還是 Development 狀態**（spec badge 上寫得清清楚楚）。attribute 名稱還會變——OpenLLMetry 自己 README 也提醒「v1.27 attributes; if names change, update once」。今天實作的 `gen_ai.system` 在 v1.42 spec 已被改成 `gen_ai.provider.name`。
2. **OpenLLMetry 的 instrument 只覆蓋 inference + 少數 vector DB**。Tool call、plan、memory、multi-agent orchestration 還是要自己手動 span。Auto-instrumentation 覆蓋率約 60%，剩下 40% 是應用層邏輯。
3. **fail-plausible 的 TF-IDF detector 是 task-disjoint**（[arXiv 2606.09863](https://arxiv.org/abs/2606.09863)）。意思是它只對 τ²-bench 跟 AppWorld 的 domain 學過有信心，跨 domain 會掉。需要定期 retrain 或用 in-context examples 補。
4. **[arXiv 2606.14831](https://arxiv.org/abs/2606.14831) Constraint-Evasive Thanatosis** 的實驗是 GPT-4o 為主，reproduction 在其他模型上「substantial variation in form, onset, and severity」——stochasticity 很高，目前沒有可靠 detection method。
5. **OpenInference 跟 OTel semconv 沒完全對齊**。Phoenix 5.x 開始 migrate 到 OTel native，但舊 tutorial 仍用 OpenInference SDK，attribute 命名差異會讓 trace 資料打架。

**我們自己的獨立批評**：

- **22M 月下載不等於 production-grade**。Langfuse SDK 在 self-host 模式下還是有 race condition（多 process export 會掉 trace）。他們的 Pro/Enterprise 用 cloud 才穩。
- **trace ≠ observability**。有 trace 不代表能問「為什麼 user X 在 2026-06-12 14:30 看到一個錯誤回答」。你需要 metrics + logs + user-session correlation，光有 span tree 不夠——這是 §7.4「cross-source convergence」的真義：只接 OTel exporter 不算 observability，需要 eval + dataset + prompt version control 才算。
- **vendor SDK 的 tracing 對 prompt version 不存**。OpenAI Agents SDK 把 trace 推到 OpenAI Dashboard，但 prompt template 的 git SHA 不會跟著 trace 走——意思是「這條 trace 是用 prompt v3.2 跑的」要你自己塞 attribute。
- **silent failure 在 production 的頻率被嚴重低估**。22 incidents over 8 weeks 看起來不多，但作者的 production system 只有 40 scheduled jobs、8 LLM providers；規模放大 10× 會變 220 incidents，且 Class D（chained hallucination）會被更多 orchestrator 放大。這是 §7.7 的「**silent failure = new table stakes**」模式的真實代價。
- **OTel GenAI semconv 跟 LangChain / LlamaIndex 的抽象不對齊**。LangChain `RunnableSequence` 跟 OTel `invoke_workflow` 是 1-to-many 還是 many-to-many 沒有 spec，這是個還沒人解決的 mapping 問題。

---

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

Firn 的 `src/firn/observability/` 只有 316 行三個檔案（`otel.py`、`spans.py`、`turns_logger.py`），目前 OTel semconv **停在 v1.27**（落後 OTel 主線 v1.42 三個版本）。具體可做的（依實作難度排序）：

### 5.1 升級 semconv 至 v1.42 + 把 `gen_ai.system` 改名為 `gen_ai.provider.name`
**難度**：TRIVIAL｜**耗時**：< 1 hr  
**改動**：`src/firn/observability/spans.py`
```python
# 改前
GEN_AI_SYSTEM = "gen_ai.system"
# 改後（v1.42 spec）
GEN_AI_PROVIDER_NAME = "gen_ai.provider.name"
```
把 `set_llm_request_attrs()` 內所有 `set_attribute(GEN_AI_SYSTEM, ...)` 改成 `set_attribute(GEN_AI_PROVIDER_NAME, ...)`。加上 `error.type` attribute 在 `LLMClient` 出錯時設值（[來源 §2.1 必填表](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)）。
**為什麼重要**：我們現在跟 OTel spec drift 三個版本；往後接 Langfuse / Phoenix 時 attribute 名會直接不相容。

### 5.2 加 `invoke_agent` 與 `plan` span wrapper
**難度**：MODERATE｜**耗時**：半天  
**改動**：`src/firn/agents/ConversationAgent.py`（ConversationAgent / TaskAgent / CronAgent 三處）
```python
# 在每個 agent.run() 進入點包
with tracer.start_as_current_span(
    f"invoke_agent {self.name}",
    attributes={
        "gen_ai.operation.name": "invoke_agent",
        "gen_ai.agent.name": self.name,
        "firn.session.id": session_id,
        "firn.session.type": session_type,
    },
) as span:
    span.set_attribute("firn.task.id", task_id)  # 若有
    # ... 原邏輯 ...
    span.set_attribute("firn.task.result_status", result_status)
```
對 TaskAgent 的「先 plan 後執行」拆成 `plan` + 後續 `execute_tool` spans（[來源](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)）。
**為什麼重要**：沒有 `invoke_agent` 包起來的 span，turns_logger 抓到的只是 LLM call 片段，**沒有「這個 agent 這次任務從頭到尾的因果鏈」**——debug 時只能看到一堆孤立 inference span。

### 5.3 為 silent failure 加 TF-IDF false-success detector
**難度**：MODERATE→HARD｜**耗時**：1–2 天  
**改動**：新增 `src/firn/observability/silent_failure.py`
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

class FalseSuccessDetector:
    """Lightweight detector for fail-plausible language (arXiv 2606.09863).
    
    Trains on past turns where firn.cron.silent=true correlates with
    'confident closing' phrases. Threshold=0.83 AUROC task-disjoint baseline.
    """
    def __init__(self, model_path: Path | None = None):
        self.vec = TfidfVectorizer(ngram_range=(1,2), max_features=5000)
        self.clf = LogisticRegression()
        self.fitted = False
        if model_path:
            self.load(model_path)
    
    def train(self, samples: list[tuple[str, bool]]) -> None:
        X = self.vec.fit_transform([s[0] for s in samples])
        y = [s[1] for s in samples]
        self.clf.fit(X, y)
        self.fitted = True
    
    def score(self, text: str) -> float:
        if not self.fitted: return 0.0
        return float(self.clf.predict_proba(self.vec.transform([text]))[0,1])
```
在 `ConversationAgent` 最後送出 response 前：
```python
prob = detector.score(final_text)
if prob > 0.7:
    span.set_attribute("firn.silent_failure.suspected", True)
    span.set_attribute("firn.silent_failure.score", prob)
    logger.warning(f"possible fail-plausible: prob={prob:.2f}")
```
**為什麼重要**：這是 §7.7 / §7.8 的 silent-failure-as-table-stakes pattern 的具體落實。Firn 目前 `firn.cron.silent` attribute 只是「有沒有 silent 失敗」的 boolean，沒抓「**是什麼語言模式讓它 silent**」。TF-IDF 加 sklearn 不需要 GPU，5 MB 模型，free。

### 5.4 Self-host Langfuse + 接上現有 OTel exporter
**難度**：MODERATE｜**耗時**：半天  
**改動**：`src/firn/observability/otel.py` 的 `setup_otel()` 內加一段
```python
if config.observability.langfuse_enabled:
    from langfuse import Langfuse
    Langfuse(
        public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
        secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        host="http://localhost:3000",  # self-host via docker-compose
    )
    # Langfuse 自動接 OTel — 不需額外設定
```
**前置**：`docker compose up langfuse-server langfuse-worker postgres redis`（官方 image）。  
**為什麼重要**：TurnsLogger 是 SQLite，**沒有 UI**——debug 要寫 SQL。Self-host Langfuse 一行 env 就拿到 conversation tree UI，且**完全免費**（只有 Langfuse Cloud 收費）。

### 5.5 補 `gen_ai.conversation.id` attribute
**難度**：TRIVIAL｜**耗時**：< 30 min  
**改動**：`src/firn/observability/otel.py` 的 span setup 處
```python
span.set_attribute("gen_ai.conversation.id", session_id)
```
**為什麼重要**：沒有 `conversation.id`，跨 turn 的 inference span 會在 Langfuse UI 上變成**多筆獨立 trace**，看不到「這是一段對話」。Spec 寫這是 Conditionally Required，意思是「有就該填」。

### 5.6 不要做的事
- **不要自己實作 OTel GenAI exporter**——用現成的 `opentelemetry-instrumentation-openai` / `opentelemetry-instrumentation-anthropic`，2026 年起兩邊都已 stable。
- **不要把 trace 全 push 到 cloud**——token / prompt 可能含 PII，先過 `OTLPSpanExporter(endpoint=...)` 連 local collector。
- **不要把 span 當 audit log**——OTel spec 沒說 span 不能刪，且預設 sampling 會丟。需要 audit log 就另開 SQLite table（我們已有 turns）。
- **不要 chase fail-plausible 的 100% detection rate**——目前 SOTA 是 AUROC 0.83 task-disjoint，跨 domain 會掉；做為「輔助 signal」而非「唯一判準」。

---


### 來源

- 原始報告：2026-06-17-agent-trace-formalization-observability.md
- 類型：
- 連結：
