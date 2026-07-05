---
name: ingest
description: >
  將 raw/ 目錄下的原始資料編譯到 wiki/ 中。支援兩種資料流：
  (A) 廣告報表 CSV — 自動執行 ad_report_ingest.py 將 raw/02-csv/ad_reports 的 CSV 轉換為
      raw/03-json/ad_reports 的 JSON，再據 JSON 編譯摘要與知識頁面至 wiki/。
  (B) 一般素材（.md / .pdf）— 直接讀取、提煉並編譯至 wiki/。
  處理完成後，將源檔案自動移動到 raw/09-archive/ 歸檔。
  支援 /ingest（掃描 raw/ 下所有未處理檔案）或 /ingest <path>（處理指定檔案或目錄）。
  當用戶提到「攝取」、「導入」、「收入」資料，或要求將檔案加入知識庫時，也應該觸發此技能。
  絕對忽略 raw/09-archive/ 與 raw/03-json/ 目錄作為待處理的掃描來源。
---

# ingest 技能：Inbox & Archive 核心工作流

## 操作流程
請參閱 `.claude/skills/ingest/skill.md` 中的完整 SOP。兩者邏輯完全一致。

## 硬約束
- `raw/` 為不可變層（Immutable），禁止修改或刪除原始檔案內容
- 絕對不讀取 `raw/09-archive/` 下的任何檔案，且嚴禁將 `raw/03-json/` 作為新的待處理掃描來源
- 所有 wiki 頁面必須包含 `## 關聯連接` 區域，不能產生孤島頁面
- 使用繁體中文編寫所有內容
