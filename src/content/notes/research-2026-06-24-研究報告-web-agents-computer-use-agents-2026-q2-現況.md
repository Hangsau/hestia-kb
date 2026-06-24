---
_slug: research-2026-06-24-研究報告-web-agents-computer-use-agents-2026-q2-現況
_vault_path: research/2026-06-24-研究報告-web-agents-computer-use-agents-2026-q2-現況.md
tags:
- research
- knowledge
- ai-agent
created: '2026-06-24'
version: 1
source_report: 2026-06-24-web-agents-browser-use-state-of-art.md
source_url: ''
type: research
fingerprint: action, self, agent, anthropic, mythos, https, claude, raw, screenshot,
  osworld
title: 研究報告：Web Agents / Computer-Use Agents — 2026 Q2 現況
status: seedling
updated: '2026-06-24'
---

# 研究報告：Web Agents / Computer-Use Agents — 2026 Q2 現況

## Version 1 — 2026-06-24

### 核心觀念
**問題**：Web/computer-use agents 是 2024-2026 唯一從研究 demo 進入企業部署的 agent 類別。三大廠（Anthropic / OpenAI / Google）各自有 production-grade 系統，前線使用者實際付費使用，但： - **能力天梯仍陡峭**：OSWorld-Verified 從 2024 Q4 的 ~38% (GPT-4V) 爬到 2026 Q2 的 80.4% (Holo3)，但 19.6% 差距代表仍有 1/5 任務人類可用而頂級 AI 失敗。 - **安全暴露面爆炸**：當 agent 可以「做任何桌面動作」，prompt inje…

**洞見**：三個獨立領域同個結論： - **browser-use 0.13**：刪抽象層、讓模型直接看 raw screenshot。 - **Claude Code safe-mode**：禁用所有 Skills/Plugins，讓模型裸跑。 - **Apple Siri WWDC 2026**：撤掉 intermediate orchestration layer，直接讀 raw screen。 **理論依據**：當 base model 達到某個能力閾值，harness 的引導 prompt / action mapping / DOM parsing 反而會： 1. 限制 action spac…

### 架構 / 機制
## 2. Core Mechanism

### 2.1 三種主流架構（2026 Q2）

```
┌─────────────────────────────────────────────────────────────────┐
│                  Computer-Use Agent 三大家族                       │
├──────────────────┬──────────────────┬───────────────────────────┤
│  Anthropic CU    │  OpenAI CUA      │  Google Project Mariner  │
│  (Claude 4.x)    │  (Operator+BG)   │  (Gemini 2.5 Computer)   │
├──────────────────┼──────────────────┼───────────────────────────┤
│ API + SDK +      │ macOS native +   │ Browser extension +       │
│ Hosted agent     │ Swift localhost  │ Chrome-only +              │
│ (browser-based)  │ API + Windows VM │ server-side execution     │
├──────────────────┼──────────────────┼───────────────────────────┤
│ Screenshots +    │ macOS SkyLight   │ DOM observation +         │
│ accessibility    │ private APIs +   │ action space via          │
│ tree (a11y)      │ focus-without-   │ extension                 │
│ + cursor + keybd │ raise            │                           │
├──────────────────┼──────────────────┼───────────────────────────┤
│ Opus 4.8:        │ Codex BG:        │ Gemini 2.5:               │
│ OSWorld-V 82.8%  │ 未公布 OSWorld   │ OSWorld-V 77.2%           │
│ Mythos 5:        │ 平行多 agent     │ Studio 模式可同時多任務    │
│ (內部 85% 估計)  │ 各有虛擬游標     │                           │
└──────────────────┴──────────────────┴───────────────────────────┘
```

### 2.2 Codex Background Computer Use 的關鍵創新（2026-04-16）

來源：BuildMVPFast 詳細分析。

OpenAI 沒有使用 OS-level accessibility APIs（OSX 上不夠即時），改用 **SkyLight**——macOS 內部未公開的 private APIs：

```python
# 概念性程式碼（逆向工程出來的 Cua-Driver 開源版）
from cua_driver import SkyLightSession

async def background_agent(task: str):
    # 1. focus-without-raise: 不搶 focus 就能控制視窗
    session = await SkyLightSession.create(focus_steal=False)
    
    # 2. 每個 agent 一個獨立 virtual cursor
    cursor_a = session.create_virtual_cursor("agent-A")
    cursor_b = session.create_virtual_cursor("agent-B")
    
    # 3. 並行多個 agent，每個讀自己 cursor 附近的 framebuffer 區域
    results = await asyncio.gather(
        run_agent(task, cursor_a),
        run_agent(task, cursor_b),
    )
    
    # 4. localhost Swift API 橋接，比 IPC 快 ~10x
    return results
```

四個關鍵設計：
1. **Focus-without-raise**：不把視窗彈到前面，避免干擾用戶當前工作。
2. **Multiple virtual cursors**：多個 agent 可以同時操作，互相看不見對方 cursor。
3. **localhost Swift API**：直接通過 Swift ↔ Python 橋，比一般 IPC（gRPC/HTTP）延遲低 10x。
4. **Cua-Driver 開源**：整個 SkyLight 層被 reverse-engineered 出來並以 MIT 開源，browser-use 等第三方可直接整合。

### 2.3 browser-use 0.13 的 Rust Rewrite（2026-06-09）

來源：clawblog 分析文章。

```python
# 0.12 架構（被丟棄）
class BrowserAgent:
    def __init__(self):
        self.browser = PlaywrightChrome()       # 瀏覽器抽象
        self.dom_parser = DOMTreeParser()       # DOM 抽象
        self.action_mapper = ActionMapper()     # 動作映射抽象
        self.screenshot_encoder = Encoder()     # 截圖抽象
        # 6 層 abstraction，model 只能看到 action_mapper 給的有限動作
    
    def step(self):
        action = self.model.predict(self.encoded_state)
        return self.action_mapper.execute(action)  # 50% 動作沒對應

# 0.13 架構（Rust + thin helpers）
class BrowserAgent:
    def __init__(self):
        self.rust_core = RustBrowserCore()      # 一個薄的 Rust 層
        # 只暴露：mouse_click(x, y), keypress(k), screenshot() 
        #          + optional a11y tree dump
    
    def step(self):
        # 模型直接拿到 raw screenshot + 可選 a11y tree
        # 動作就是 (x, y, button) + (key, modifiers)
        # 模型完全控制，沒有抽象層卡住
        action = self.model.predict(self.raw_screenshot, self.a11y_tree)
        return self.rust_core.execute(action)
```

**刪掉的不是性能、是抽象**：模型已經知道瀏覽器是什麼，不需要 Playwright 把語意翻譯成模型看得懂的東西。

### 2.4 OSWorld-Verified Benchmark 真相

os-world.github.io 官方榜（截至 2026-06-23）：

| Rank | Model | OSWorld-V | Notes |
|------|-------|-----------|-------|
| 1 | Holo3-35B-A3B | **80.4%** | Bytedance Seed, 專用模型 |
| 2 | Claude Opus 4.7 | 79.3% | Anthropic, 2026-04 |
| 3 | Claude Opus 4.8 | 82.8% | 2026-05-28（含 zoom-tool bug fix 後重算） |
| 4 | MiniMax M3 | 75.2% | **疑慮：是否名稱巧合？需確認** |
| 5 | Sonnet 4.6 | 72.1% | |
| 6 | Kimi K2.5/K2.6 | 73.1% | |
| 7 | Gemini 2.5 | 77.2% | |
| 8 | GPT-5.6 (rumored) | n/a | 數據未公開提交 |
| 9 | Mythos 5 | n/a | **不在官方榜** |
| 10 | Fable 5 | n/a | **不在官方榜** |

**Mythos 5 / Fable 5 不在 OSWorld 官方榜**——這是 Steel.dev / DigitalApplied 等二手報導引用「Anthropic 內部公告」的 85% 數字時的關鍵警訊。Anthropic 公開 system card 數字是內部評估條件（不同 max_steps / 不同 scaffolding），不應與 OSWorld-Verified 直接比較。

---

### 思考
## 4. Limitations / Honest Assessment

### 4.1 為什麼 OSWorld 還沒到 90%

Holo3 80.4% 看起來高，但細看類別分數：
- Chrome: ~32-40/46
- GIMP: ~17-20/26
- LibreOffice Calc: ~15-20/47
- Multi-apps: ~17-23/93 ← 最大瓶頸

**真實問題是「跨應用工作流」**。讓 agent 打開瀏覽器複製資料、切到 LibreOffice 貼上並格式化——這類任務的成功率仍 <25%。Holo3 的高分主要是 OS 系統操作和單一應用，不是我們想像的「AI 秘書」。

### 4.2 Mythos 5 「85%」數字的迷思

Anthropic 內部 system card 報告的 85.4% 數字（被 Steel.dev / DigitalApplied 引用為「OSWorld-Verified 榜首」）實際上是：
- **內部 evaluation suite**，不是 OSWorld-Verified 官方榜
- 使用 100 max_steps，OSWorld-Verified 標準是 50
- 用 Anthropic 自家 scaffolding，不是各家統一介面
- **未提交 OSWorld 官方榜**——這是關鍵

誠實比較時，官方榜的 Anthropic 最高分是 **Opus 4.8 @ 82.8%**。

### 4.3 Browser-Use 0.13 Rust 重建的代價

- **學習曲線陡峭**：之前 developer 寫 Python action mapping 即可，現在要直接寫 Rust helper 或承受 raw action 帶來的錯誤率上升。
- **截圖解析成本**：每步都要 model 重新 parse raw screenshot，token 用量上升。
- **a11y tree 還是必要**：純 visual 在「看不見的元素」（hidden input, modal 後的 background）上仍失敗。

### 4.4 Codex Background Computer Use 的可行性

- 目前 **macOS only**（SkyLight 是 macOS 私 API）
- Windows 版本據報導是透過 VM + 截圖驅動，效能差很多
- 多 agent 並行會「打架」（virtual cursor 不互相感知，會 click 同一個地方）
- **未公開 OSWorld benchmark 分數**——這是主要疑慮

---

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

### 5.1 firn firefox/dev 自動化

**核心建議**：採用 **「薄 harness + 開放 a11y 輔助」** 模式。

```python
# firn_desktop/agent.py (建議)
class FirnDesktopAgent:
    """對齊 browser-use 0.13 哲學：薄介面 + 開放 a11y"""
    def __init__(self, llm: LLM):
        self.llm = llm
        self.firefox = FirefoxCDP()           # 直接用 CDP，不包 Playwright
        self.a11y_dump = A11yTreeDumper()     # optional 輔助
    
    async def step(self, task: str) -> Action:
        # 1. 拿 raw screenshot + 可選 a11y tree
        screenshot = await self.firefox.screenshot()
        a11y = await self.a11y_dump.dump() if self.config.use_a11y else None
        
        # 2. 讓 LLM 決定（給 raw，不給抽象）
        action = await self.llm.predict(
            task=task, 
            screenshot=screenshot, 
            a11y=a11y,
            action_space=["click(x,y)", "type(text)", "key(k)", "scroll(dx,dy)"]
        )
        
        # 3. 執行 raw action
        return await self.firefox.execute(action)
```

**實作難度：MODERATE**
- 把現有 Playwright 抽象層拆開：~2 週
- 寫 Rust helper 取代 Python 熱路徑（如果需要效能）：~1 月
- 對齊現有 browser-use 0.13 介面（互通）：~1 週

**成本**：本地跑 Firefox headless 不需要 API 費；LLM 推理是最大成本（每步約 $0.01-0.05 with GPT-4V/Claude）。

### 5.2 firn 的安全加固

對齊 Claude Code Action RCE 教訓：

```python
# firn_desktop/sandbox.py (必須)
class DesktopSandbox:
    """所有 computer-use agent 必須跑在這層後面"""
    def __init__(self):
        self.firejail = FirejailProfile(
            allow_network=False,           # 預設斷網
            allow_clipboard=False,        # 預設禁剪貼簿
            allow_filesystem=Path("/tmp/firn-sandbox"),
            seccomp_policy="computer-use-strict"
        )
    
    def validate_action(self, action: Action) -> bool:
        # 攔截可疑 pattern
        if action.type == "key" and "ctrl+l ctrl+c" in action.value:
            return False  # 阻擋地址欄複製
        if action.type == "type" and "rm -rf" in action.value:
            return False  # 阻擋危險命令
        if action.type == "click" and not self.is_visible(action.x, action.y):
            return False  # 阻擋 click 看不見的元素
        return True
```

**實作難度：TRIVIAL**（已經有基礎設施，主要是 policy 設計）

### 5.3 managed-agents 系統：對齊 Mythos 的「雙模型 + classifier fallback」

```yaml
# 對齊 Fable 5 設計
research_pipeline:
  primary_model: opus-4.8       # 大多數任務
  escalation_model: sonnet-4.6  # 容量不足 fallback
  classifier:                   # 風險檢測
    high_risk_categories:
      - "刪除 firn 資料"
      - "推送 GitHub commit"
      - "外寄 email"
    action: "fallback to escalation_model + 通知 owner"
```

**實作難度：TRIVIAL**——只是 routing logic。

### 5.4 不該做的事

- ❌ 直接重現 OSWorld 80%+ 分數（要在 firefox 真實場景跑，需要幾個月 fine-tune）
- ❌ 嘗試 Mythos 5 級 fallback classifier（太複雜，firn 風險面比 Mythos 小）
- ❌ 用 raw SkyLight private API（macOS only，license 不明，Cua-Driver 雖 MIT 但 SkyLight 本身仍是 Apple proprietary）

---


### 來源

- 原始報告：2026-06-24-web-agents-browser-use-state-of-art.md
- 類型：
- 連結：
