---
_slug: 99-Templates-_archive-software-development-transcription-pipeline
_vault_path: 99-Templates/_archive/software-development/transcription-pipeline.md
tags:
- skill
- transcription
- audio
- ffmpeg
- pipeline
source: multi
created: '2026-05-13'
title: Transcription Pipeline Skill
updated: '2026-06-15'
type: template
status: budding
---

# Transcription Pipeline Skill

> 完整技能檔見 `~/.hermes/skills/transcription-pipeline/SKILL.md`

## 簡介

語音轉寫管線技能，支援多格式音檔轉換、段落分割、批量處理。

## 安裝前置

- Python 3.12.10+
- ffmpeg
- uv (用於環境管理)

## 步骟

1. 準備音檔檔案
2. 使用 ffmpeg 轉換格式
3. 分割為適合轉寫的段落
4. 執行轉寫
5. 整合結果

## 常見問題

- 大檔案處理時需注意記憶體使用
- 批量處理建議使用佇列系統

## 參見

- [[ciby-transcription-pipeline]] — 專案案例
- [[project-map-index]] — 專案總索引
