---
name: scaffold
description: >
  LLM Wiki 互動式安裝精靈。當用戶要求「初始化知識庫」、「建立新 Vault」、
  「scaffold」、「安裝 LLM Wiki」時觸發。引導用戶指定 Obsidian 實際路徑，
  並精準將核心架構與規則複製過去，不污染目標資料夾。
---

# scaffold 技能：LLM Wiki 互動式安裝精靈

## 操作流程
請參閱 `.claude/skills/scaffold/skill.md` 中的完整 SOP。兩者邏輯完全一致。

## 硬約束
- **禁止污染目標目錄**：絕對**不可以**將當前安裝包目錄下的 `README.md`、`.git/` 目錄、`scaffold.sh` 或其他無關檔案複製到使用者的 Obsidian Vault 裡。
- **不可預設當前目錄**：除非用戶非常明確要求「裝在現在這個資料夾」，否則預設必須詢問路徑。
- **保留用戶設定**：絕對不可覆蓋目標目錄中原有的 `.obsidian/` 隱藏目錄。
