---
_slug: 30-Areas-swimming-digests-PMID-42267983-arm-propulsive-force-kinematics-digest
_vault_path: 30-Areas/swimming/digests/PMID-42267983-arm-propulsive-force-kinematics-digest.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 4, column 80:\n     ... e and arm kinematics in swimming: experimental and numerical\
  \ study.\n                                         ^"
_raw_fm: '

  uid: PMID-42267983

  type: digest

  title: Relationship between arm propulsive force and arm kinematics in swimming:
  experimental and numerical study.

  date: 2026-06-13

  pmid: 42267983

  status: completed

  tags: [swimming, freestyle, biomechanics, propulsion, CFD, robotic]

  created: 2026-06-13

  updated: 2026-06-15

  '
title: PMID-42267983-arm-propulsive-force-kinematics-digest
type: area
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

## 研究問題
在受控條件下，划手旋轉頻率如何決定上肢產生的推進力？實驗與數值方法能否在同樣的時間解析運動學下得到一致結果？

## 方法
- **雙方法驗證**：robotic arm 實驗 + unsteady CFD 模擬
- **關鍵設計**：兩種方法採用**相同的時間解析運動學**（time-resolved kinematics imposed identically），這是文獻首次做到的直接對比
- **變因**：arm rotational frequency 0.46–0.76 Hz
- **對照頻率**：0.70 Hz 為「競技游泳代表頻率」

## 結論
1. **推進力隨頻率二次方增長**（quadratic increase）：從 27.45 N（0.46 Hz）升至 120.48 N（0.76 Hz）
2. **0.70 Hz 時實驗 vs CFD 差異僅 8%**——驗證了計算模型的可靠度
3. 提供了「划手運動學 → 推進力」的實驗驗證框架

## 教練觀點
- **頻率-推進力曲線確認「為何划頻那麼重要」**：0.30 Hz 區間內推進力增加約 4.4 倍（27→120 N），這不是線性而是加速
- **0.70 Hz 為「競技代表頻率」**：與男子精英 50m 自由式划頻（80–100 cycle/min ≈ 1.3–1.7 Hz）有差距，提示**模型測試頻段偏慢**——可能不直接覆蓋衝刺情境
- **CFD 驗證意涵**：robo-arm + CFD 對齊的框架，未來可以用 CFD 模擬教練想嘗試的「划手路徑修改」，預測推進力變化，節省實驗成本
- **不該過度詮釋**：本研究是**單一臂的孤立實驗**，未涉及水流場、體幹耦合、踢水耦合——真實划手是全身系統，這是「局部力學上限的量化」而非「實際表現預測」

## 整合層備註
歸入 1.11 對照表：量化了「划手旋轉頻率 → 推進力」的非線性關係，可作為 1.7「划頻 vs 划距」章節的力學基礎（SR 上限為何不是無限——是推進力增長曲線 + 神經徵召速度的乘積）。
