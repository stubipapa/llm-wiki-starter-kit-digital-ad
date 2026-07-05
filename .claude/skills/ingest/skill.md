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
user-invocable: true
---

# ingest 技能：Inbox & Archive 核心工作流

## 1. 核心目標
將 `raw/` 待處理收件箱中的原始素材（廣告報表 CSV、網頁剪藏、會議記錄、競品資料），
經過**結構化轉換**與**提煉編譯**，網狀化輸出至 `wiki/` 唯讀層，確保知識庫持續增量演進。

> **Karpathy 核心理念**：知識不是每次查詢時重新從原始文件中推導，
> 而是在攝入時**一次性編譯**成持久的、可複合累積的 Wiki 產物。
> 每一次 ingest 都讓 Wiki 變得更豐富，交叉引用已經建立，矛盾已經標記，
> 綜合分析已經反映了你讀過的一切。

## 2. 觸發邏輯
| 指令 | 行為 |
|---|---|
| `/ingest` | 掃描 `raw/` 所有子目錄（嚴格排除 `09-archive/` 與 `03-json/`），找出待處理檔案。優先處理 `raw/02-csv/ad_reports` 中的 CSV 廣告報表。 |
| `/ingest <路徑>` | 僅處理指定檔案或目錄。若路徑指向 `.csv` 則走 Phase A 流程；若為 `.md`/`.pdf` 則走 Phase B 流程。 |
| 隱式觸發 | 用戶提及「攝取」、「導入」、「收入資料」、「轉換報表」時自動觸發。 |

## 3. 資料流架構

```
raw/02-csv/ad_reports/*.csv
        │
        ▼  Phase A: ad_report_ingest.py（自動轉換）
raw/03-json/ad_reports/*.json
        │
        ▼  Phase B: LLM 編譯流水線（提煉 → 摘要 → 網絡化）
wiki/sources/     ← 來源摘要頁
wiki/entities/    ← 實體頁（廣告平台、品牌…）
wiki/concepts/    ← 概念頁（CPM、CTR、行銷目標…）
wiki/index.md     ← 總目錄更新
wiki/log.md       ← 操作日誌追加
        │
        ▼  Phase C: 歸檔
raw/09-archive/   ← 原始 CSV 移入歸檔
```

---

## 4. Phase A：廣告報表 CSV → JSON 結構化轉換

### 觸發條件
當待處理檔案位於 `raw/02-csv/ad_reports/` 或指定路徑為 `.csv` 檔案時，自動執行此階段。

### 操作步驟

#### 步驟 A1：執行轉換腳本
在專案根目錄執行以下命令：
```bash
python3 .claude/skills/ingest/ad_report_ingest.py raw/02-csv/ad_reports raw/03-json/ad_reports
```
- 若 `python3` 不可用，改用 `python`。
- 若用戶指定了單一 CSV 檔案路徑，改為：
```bash
python3 .claude/skills/ingest/ad_report_ingest.py <輸入CSV路徑> <輸出JSON路徑>
```
- 腳本會自動建立輸出目錄（若不存在）。
- 腳本處理邏輯：解析 CSV 中的活動基本資訊（Campaign 名稱、媒體、走期、預算、KPI）以及各區段明細（DATE / 受眾 / 年齡），輸出標準化 JSON。

#### 步驟 A2：驗證轉換結果
- 確認 `raw/03-json/ad_reports/` 下已產生對應的 `.json` 檔案。
- 讀取 JSON 並做基本健全性檢查：`campaign_name` 非空、`cost` 有值。
- 若腳本回報錯誤，在終端顯示錯誤訊息並**暫停**，等待用戶決定是否繼續。

#### 步驟 A3：進入 Phase B
轉換成功後，以 `raw/03-json/ad_reports/*.json` 作為 Phase B 的輸入源檔案，進入 LLM 編譯流水線。

---

## 5. Phase B：LLM 編譯流水線 (SOP)

對每個待處理的源檔案（`.json`、`.md`、`.pdf`），嚴格執行以下六大步驟：

### 步驟 B1：讀取源檔案
- **`.json` 檔案**（廣告報表）：讀取 JSON 內容，解析 `campaigns` 陣列中的每個活動物件。
- **`.md` 檔案**：使用讀取工具完整讀取內容。
- **`.pdf` 檔案**：嘗試提取文本。若無法提取或內容為空，則改為在 sources 頁面中僅記錄檔案元資訊（檔名、頁數）。

### 步驟 B2：提煉核心並翻譯
從源檔案中提取出：
- **核心主旨**：這段資料的核心在講什麼（1-2 句話精確總結）。
- **實體 (Entities)**：人物、公司、工具、產品、廣告平台等具體名詞。
- **概念 (Concepts)**：框架、方法論、理論、廣告指標（CPM、CTR、CPC、VTR 等）等抽象名詞。

針對**廣告報表 JSON** 特別提煉：
- 活動名稱、投放平台、走期、預算與 KPI 達成率。
- 各日期/受眾/年齡段的成效指標比較與趨勢洞察。
- 表現最佳與最差的維度及可能原因。
- **素材與策略維度**：從活動名稱或數據特徵中，嘗試推斷或提取「投放素材類型」（如影片、圖文）、「投放素材風格」（如促銷、感性、理性規格）、「行銷漏斗階段」（曝光、考慮、轉換）以及「關鍵轉換事件」（如查詢經銷商）。

> *若原始素材為英文或其他非繁體中文內容，在此步驟必須自動翻譯並提煉為台灣繁體中文。*

### 步驟 B3：創建來源摘要 (Source Page)
在 `wiki/sources/` 下建立 Markdown 檔案，檔名嚴格使用 kebab-case。

**一般素材範本：**
```markdown
---
title: "摘要-{檔案slug}"
type: source
tags: [來源, 原始檔案]
sources: [raw/對應目錄/xxx.md]
last_updated: YYYY-MM-DD
---
## 核心摘要
[3-5 句話的核心觀點總結]

## 關聯連接
- [[EntityName]] — 關聯實體
- [[ConceptName]] — 關聯概念
```

**廣告報表專用範本：**
```markdown
---
title: "摘要-{campaign-name-slug}"
type: source
tags: [來源, 廣告報表, {平台名稱}]
sources: [raw/02-csv/ad_reports/{原始檔名}.csv]
last_updated: YYYY-MM-DD
---
## 活動概覽
| 欄位 | 數值 |
|---|---|
| 活動名稱 | {campaign_name} |
| 投放平台 | {platform} |
| 廣告走期 | {period} |
| 總預算 | {cost} |
| KPI 目標值 | {kpi_target_value} |
| KPI 實際值 | {kpi_actual_value} |
| KPI 達成率 | {kpi_achievement_rate} |
| 投放素材類型 | {例如：影片 / 圖文 / 輪播} |
| 投放素材風格 | {例如：理性規格 / 感性訴求 / 節慶促銷} |
| 行銷漏斗階段 | {Top-Funnel / Mid-Funnel / Bottom-Funnel} |

## 成效分析
[基於 date、target_audience、target_age 各維度的數據，撰寫 3-5 句成效洞察]

## 關鍵發現
- [表現最佳的維度/日期及其指標]
- [表現最差的維度/日期及需改善之處]
- [整體趨勢與建議]

## 關聯連接
- [[{平台實體頁}]] — 投放平台
- [[{投放素材類型}]] — 素材格式
- [[{投放素材風格}]] — 素材調性
- [[{行銷漏斗階段}]] — 策略定位
- [[{關鍵轉換事件}]] — 核心轉換指標 (如：查詢經銷商)
- [[CPM]] / [[CTR]] — 相關指標
```

### 步驟 B4：知識網絡化（實體與概念增量合併）
針對步驟 B2 提取出的每個實體（移至 `wiki/entities/`）與概念（移至 `wiki/concepts/`）執行以下邏輯：
1. **頁面不存在**：依據 `WIKI_SCHEMA.md` 的 Frontmatter 規範建立新頁面。
2. **頁面已存在**：讀取現有內容，進行**增量合併**，將新獲取的關鍵資訊補進去，絕對不可覆蓋舊有脈絡。
3. **發現衝突**：**立即觸發衝突處理流程**（見下方第 7 節說明），暫停執行。

頁面格式範本：
```markdown
---
title: "頁面名稱"
type: entity | concept
tags: [標籤]
sources: [關聯的源檔案相對路徑]
last_updated: YYYY-MM-DD
---
## 定義
[對該實體/概念的核心定義描述]

## 關鍵資訊
[從源檔案中提取的詳細結構化內容]

## 關聯連接
- [[摘要-source-slug]] — 來源
- [[RelatedPage]] — 相關知識節點
```

### 步驟 B5：更新全局註冊表
- **更新 `wiki/index.md`**：將新創立或更新的頁面，按照 `WIKI_SCHEMA.md` 的分類契約與命名規範（TitleCase 或 kebab-case）加入目錄中。
- **更新 `wiki/log.md`**：追加寫入一筆操作日誌：`## [YYYY-MM-DD] ingest | <操作簡述>`，明列變更與衝突狀態。

### 步驟 B6：自動歸檔源檔案
當且僅當上述五個步驟皆完美完成、無任何報錯後：
- **廣告報表**：將原始 CSV 由 `raw/02-csv/ad_reports/` 移動至 `raw/09-archive/`。JSON 中間產物保留在 `raw/03-json/ad_reports/` 不移動（作為結構化資料供後續查詢使用）。
- **一般素材**：將原檔案由 `raw/` 原目錄移動至 `raw/09-archive/`。

**硬約束：絕對禁止修改、污染或刪除源檔案內部的原始文字。**

---

## 6. Phase C：完整流程摘要輸出

每次 ingest 完成後，在終端輸出以下摘要：
```
═══════════════════════════════════════════
  INGEST 完成報告
═══════════════════════════════════════════
  處理檔案數：X
  CSV → JSON 轉換：Y 個檔案
  Wiki 頁面新增：Z 個
  Wiki 頁面更新：W 個
  衝突發現：N 個
  歸檔檔案：M 個
═══════════════════════════════════════════
```

---

## 7. 衝突處理流程 (Conflict Resolution Loop)
當在步驟 B4 發現新攝入的資訊與舊頁面存在認知或事實衝突時：
1. **暫停**：立即中斷當前的 ingest 流程。
2. **報告**：在終端機或 Chat 視窗向用戶明確展示衝突點（哪個頁面、新舊說法有何矛盾）。
3. **詢問**：請用戶手動選擇處理路徑：
   - **A)** 保留新舊兩者，在該頁面新建 `## 知識衝突` 區塊進行對比。
   - **B)** 用新知識覆蓋/修正舊知識。
   - **C)** 終止本次 ingest 任務。
4. **繼續**：接收到用戶指令後，方可解凍並繼續執行後續步驟。

---

## 8. 硬約束與注意事項

- 絕對不讀取 `raw/09-archive/` 下的任何檔案，且嚴禁將 `raw/03-json/` 作為新的待處理掃描來源
- 所有 wiki 頁面必須包含 `## 關聯連接` 區域，不能產生孤島頁面
- 使用繁體中文編寫所有內容
- 實體命名使用 TitleCase，概念和來源使用 kebab-case
- `raw/` 為不可變層（Immutable），禁止修改或刪除原始檔案內容
- JSON 中間產物（`raw/03-json/`）保留不歸檔，作為結構化查詢來源
- 執行 Python 腳本時優先使用 `python3`，若不可用則退回 `python`
