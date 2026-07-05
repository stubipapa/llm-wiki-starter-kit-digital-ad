---
name: scaffold
description: LLM Wiki 互動式安裝精靈。當用戶要求「初始化知識庫」、「建立新 Vault」、「scaffold」、「安裝 LLM Wiki」時觸發。引導用戶指定 Obsidian 實際路徑，並精準將核心架構與規則複製過去，不污染目標資料夾。
user-invocable: true
---

# scaffold 技能：LLM Wiki 互動式安裝精靈

## 1. 核心目標
作為一個純淨的安裝精靈，將當前 Starter Kit (安裝包) 內的「核心架構與規則檔案」精準部署到用戶真實的 Obsidian Vault 目錄中。絕對不複製與 Obsidian 運行無關的 Git 安裝包檔案 (如 README, .git)。

## 2. 觸發條件
- 用戶要求「初始化知識庫」、「建立新 Vault」、「scaffold」、「安裝 LLM Wiki」

## 3. 互動式安裝流水線 (SOP)

### 步驟 1：詢問與確認目標路徑 (互動)
- **暫停並詢問**：要求用戶提供 Obsidian Vault 的「絕對路徑」。
  > 「請問您想將 LLM Wiki 架構安裝到哪裡？請提供您 Obsidian Vault 的絕對路徑（例如：\`/Users/username/Documents/MyWiki\`）。如果您還沒建立該資料夾，請直接告訴我理想的路徑，我會幫您建立。」
- **等待回覆**：在用戶回覆具體路徑之前，**絕對不能執行任何檔案操作**。

### 步驟 2：路徑最終確認 (互動)
- 收到用戶提供的路徑後，向用戶進行最後確認：
  > 「收到，即將在 \`[使用者提供的路徑]\` 部署 LLM Wiki 架構。請確認是否開始安裝？」
- **等待同意**：獲得用戶明確同意後再繼續。

### 步驟 3：建立目錄結構
在用戶指定的目標路徑 (\`$TARGET_DIR\`) 內，建立以下完整目錄樹（若目錄不存在則建立）：
- \`$TARGET_DIR/.claude/skills/ingest/\`
- \`$TARGET_DIR/.claude/skills/lint/\`
- \`$TARGET_DIR/.claude/skills/query/\`
- \`$TARGET_DIR/.claude/skills/scaffold/\`
- \`$TARGET_DIR/.agents/skills/scaffold/\`
- \`$TARGET_DIR/.agents/skills/ingest/\`
- \`$TARGET_DIR/.agents/skills/lint/\`
- \`$TARGET_DIR/.agents/skills/query/\`
- \`$TARGET_DIR/assets/\`
- \`$TARGET_DIR/raw/01-articles/\`
- \`$TARGET_DIR/raw/02-csv/ad_reports/\`
- \`$TARGET_DIR/raw/03-json/ad_reports/\`
- \`$TARGET_DIR/raw/04-clipper/\`
- \`$TARGET_DIR/raw/09-archive/\`
- \`$TARGET_DIR/wiki/concepts/\`
- \`$TARGET_DIR/wiki/entities/\`
- \`$TARGET_DIR/wiki/sources/\`
- \`$TARGET_DIR/wiki/syntheses/\`

### 步驟 4：精準複製核心大腦檔案
從**當前所在目錄 (Starter Kit 安裝包)**，將以下核心檔案複製到 \`$TARGET_DIR\` 中：
- \`CLAUDE.md\`
- \`WIKI_SCHEMA.md\`
- \`.agyrules\`
- \`.claude/skills/ingest/skill.md\`
- \`.claude/skills/ingest/ad_report_ingest.py\`
- \`.claude/skills/lint/skill.md\`
- \`.claude/skills/query/skill.md\`
- \`.claude/skills/scaffold/skill.md\`
- \`.agents/skills/scaffold/SKILL.md\`
- \`.agents/skills/ingest/SKILL.md\`
- \`.agents/skills/lint/SKILL.md\`
- \`.agents/skills/query/SKILL.md\`

### 步驟 5：初始化 Wiki 基礎檔案
在 \`$TARGET_DIR\` 中建立或覆寫以下檔案：

\`$TARGET_DIR/wiki/index.md\`：
```markdown
# Wiki Index
本檔案記錄所有 wiki 內的知識節點。每次新增頁面後，必須將其按分類加入目錄中。
格式要求： \`<頁面名稱>\` — 一句話描述。

## Sources

## Entities

## Concepts

## Syntheses
```

\`$TARGET_DIR/wiki/log.md\`：
```markdown
# Wiki Log
只能追加寫入（Append-only）。每次操作後記錄：\`## [YYYY-MM-DD] <動作> | <操作簡述>\`。

## [YYYY-MM-DD] scaffold | 初始化 LLM Wiki 知識庫結構
```
*(請將 YYYY-MM-DD 替換為今日日期)*

### 步驟 6：完成報告
安裝完成後，在終端機打印結構化的成功報告，提醒用戶：「安裝已完成，您可以直接用 Obsidian 開啟該資料夾，並在該資料夾啟動 AI Agent 開始使用了！當前的 Git 安裝包目錄可以刪除。」

## 4. 硬約束 (嚴格遵守)
- **禁止污染目標目錄**：絕對**不可以**將當前安裝包目錄下的 \`README.md\`、\`.git/\` 目錄、\`scaffold.sh\` 或其他無關檔案複製到使用者的 Obsidian Vault 裡。
- **不可預設當前目錄**：除非用戶非常明確要求「裝在現在這個資料夾」，否則預設必須詢問路徑。
- **保留用戶設定**：絕對不可覆蓋目標目錄中原有的 \`.obsidian/\` 隱藏目錄。
