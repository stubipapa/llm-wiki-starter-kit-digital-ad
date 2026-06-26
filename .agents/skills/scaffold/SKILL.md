---
name: scaffold
description: >
  在當前目錄初始化完整的 LLM Wiki Obsidian Vault 結構。建立所有必要的目錄（raw、wiki、assets）、
  規則檔案（CLAUDE.md、WIKI_SCHEMA.md、.agyrules）以及 Claude Code / Antigravity 的 Skills
  （ingest、lint、query）。當用戶要求「初始化知識庫」、「建立新 Vault」、「scaffold」、
  「設定 LLM Wiki」時觸發。
---

# scaffold 技能：LLM Wiki Vault 一鍵初始化

## 1. 核心目標
在用戶指定的空目錄（或當前工作目錄）中，建立一個完整的、遵循 Karpathy 規範的 LLM Wiki Obsidian Vault 結構，包括所有目錄、規則檔案、技能檔案和初始模板。

## 2. 觸發條件
- 用戶要求「初始化知識庫」、「建立新 Vault」、「scaffold」、「設定 LLM Wiki」

## 3. 操作流程
請參閱 `.claude/skills/scaffold/skill.md` 中的完整 SOP。兩者邏輯完全一致。

## 4. 硬約束
- 若目標目錄已有 `WIKI_SCHEMA.md` 等核心檔案，必須警告用戶並詢問是否覆蓋
- 所有模板內容使用繁體中文
- 不覆蓋 `.obsidian/` 目錄
