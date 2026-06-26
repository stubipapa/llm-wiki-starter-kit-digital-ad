---
name: scaffold
description: 在當前目錄初始化完整的 LLM Wiki Obsidian Vault 結構。建立所有必要的目錄（raw、wiki、assets）、規則檔案（CLAUDE.md、WIKI_SCHEMA.md、.agyrules）以及 Claude Code / Antigravity 的 Skills（ingest、lint、query）。當用戶要求「初始化知識庫」、「建立新 Vault」、「scaffold」、「設定 LLM Wiki」時觸發。
user-invocable: true
---

# scaffold 技能：LLM Wiki Vault 一鍵初始化

## 1. 核心目標
在用戶指定的空目錄（或當前工作目錄）中，建立一個完整的、遵循 Karpathy 規範的 LLM Wiki Obsidian Vault 結構，包括所有目錄、規則檔案、技能檔案和初始模板。

## 2. 觸發條件
- 用戶要求「初始化知識庫」、「建立新 Vault」、「scaffold」、「設定 LLM Wiki」
- 用戶提供一個空目錄路徑，要求在其中建立知識庫

## 3. 初始化流水線 (SOP)

### 步驟 1：確認目標目錄
確認目標目錄存在且為空（或用戶明確同意在非空目錄中建立）。若目錄不存在則建立。

### 步驟 2：建立目錄結構
建立以下完整目錄樹：
- `.claude/skills/ingest/`
- `.claude/skills/lint/`
- `.claude/skills/query/`
- `assets/`
- `raw/01-articles/`
- `raw/02-papers/`
- `raw/03-transcripts/`
- `raw/04-clipper/`
- `raw/09-archive/`
- `wiki/concepts/`
- `wiki/entities/`
- `wiki/sources/`
- `wiki/syntheses/`

### 步驟 3：建立規則檔案
依照本 skill 同層目錄中的模板建立以下檔案：
- `CLAUDE.md` — Agent 全局系統提示（見同倉庫模板）
- `WIKI_SCHEMA.md` — Wiki 架構規範（見同倉庫模板）
- `.agyrules` — Antigravity 路由規則（見同倉庫模板）

### 步驟 4：建立技能檔案
從同倉庫的模板複製以下技能：
- `.claude/skills/ingest/skill.md`
- `.claude/skills/lint/skill.md`
- `.claude/skills/query/skill.md`

### 步驟 5：建立 Wiki 初始檔案

`wiki/index.md`：
```markdown
# Wiki Index
本檔案記錄所有 wiki 內的知識節點。每次新增頁面後，必須將其按分類加入目錄中。
格式要求： `<頁面名稱>` — 一句話描述。

## Sources

## Entities

## Concepts

## Syntheses
```

`wiki/log.md`：
```markdown
# Wiki Log
只能追加寫入（Append-only）。每次操作後記錄：`## [YYYY-MM-DD] <動作> | <操作簡述>`。

## [YYYY-MM-DD] scaffold | 初始化 LLM Wiki 知識庫結構
```

### 步驟 6：完成確認
建立完成後打印結構化的成功報告，列出所有已建立的目錄、檔案和可用技能。

## 4. 硬約束
- 若目標目錄已有 `WIKI_SCHEMA.md` 等核心檔案，必須警告用戶並詢問是否覆蓋
- 所有模板內容使用繁體中文
- 不覆蓋 `.obsidian/` 目錄（保留用戶的 Obsidian 個人設定）
