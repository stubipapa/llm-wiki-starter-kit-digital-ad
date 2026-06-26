# Claude Code Global System Prompt

你正在維護一個遵循最高規格的 LLM Wiki 知識庫。

## 最高指令
1. 執行任何動作前，必須嚴格讀取並遵守根目錄下的 `WIKI_SCHEMA.md`。
2. 當使用者在終端機輸入特定斜線指令時，請直接調用並執行 `.claude/skills/` 對應目錄下的 `skill` 檔案，將其視為當前任務的最高 SOP 執行指南。
   - `/ingest` -> 調用 `.claude/skills/ingest/skill`
   - `/query` -> 調用 `.claude/skills/query/skill`
   - `/lint` -> 調用 `.claude/skills/lint/skill`
