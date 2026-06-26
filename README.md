# 🧠 LLM Wiki Starter Kit

> 一鍵初始化符合 [Karpathy LLM Wiki 規範](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 的 Obsidian 知識庫，內建 AI Agent 自動化工作流（Claude Code / Antigravity / 通用 Agent）。

---

## ✨ 這是什麼？

這是一個**開箱即用的 Obsidian Vault 初始化模板**（懶人包）。它包含：

- 📁 **完整的目錄架構**：raw（原始素材）/ wiki（知識編譯）/ assets（媒體資產）
- 📜 **AI Agent 規則檔案**：讓任何 AI Agent 理解你的知識庫結構與操作規範
- 🛠️ **三大核心 Skills**：ingest（攝取）/ query（查詢）/ lint（巡檢）
- 🔗 **雙鏈知識網絡**：自動維護 Obsidian 雙向連結，杜絕孤島頁面

### 設計哲學

```
raw/（不可變層）──→ AI Agent 編譯 ──→ wiki/（知識輸出層）
     唯讀                                  你擁有這裡
```

你只需將原始素材丟進 `raw/`，AI Agent 就會自動提煉、翻譯、建立實體與概念頁面、維護索引與日誌。

---

## 🚀 快速開始

> **重要觀念**：`llm-wiki-starter-kit/` 是「安裝包」，不是最終使用位置。
> 你需要把內容**展開到 Vault 根目錄**，因為所有 AI Agent 都從 Vault 根目錄開始掃描。

### 方法一：Shell 腳本（推薦）

```bash
# 1. Clone 此儲存庫到任意位置
git clone https://github.com/YOUR_USERNAME/llm-wiki-starter-kit.git

# 2. 建立你的 Vault 目錄
mkdir -p ~/Documents/My-Wiki-Vault

# 3. 執行初始化腳本（將所有內容展開到 Vault 根目錄）
bash llm-wiki-starter-kit/scaffold.sh ~/Documents/My-Wiki-Vault

# 4. 用 Obsidian 開啟 ~/Documents/My-Wiki-Vault 作為 Vault
```

### 方法二：已下載到 Vault 中

如果你已經把 `llm-wiki-starter-kit/` 下載到 Vault 裡面：

```bash
# 在 Vault 根目錄執行
cd ~/Documents/My-Wiki-Vault
bash llm-wiki-starter-kit/scaffold.sh .

# 初始化完成後，安裝包可以刪除或保留
# rm -rf llm-wiki-starter-kit/  ← 可選
```

### 方法三：手動複製

```bash
# 將所有檔案複製到 Vault 根目錄
cp -r llm-wiki-starter-kit/{CLAUDE.md,WIKI_SCHEMA.md,raw,wiki,assets} ~/Documents/My-Wiki-Vault/
cp llm-wiki-starter-kit/.agyrules ~/Documents/My-Wiki-Vault/
cp -r llm-wiki-starter-kit/.claude ~/Documents/My-Wiki-Vault/
cp -r llm-wiki-starter-kit/.agents ~/Documents/My-Wiki-Vault/
```

---

## 🏗️ 架構原理

### 檔案載入鏈

AI Agent 不會自己知道你的知識庫規則。它靠**入口檔**引導，一步步讀取：

```
Claude Code 啟動
  └→ 自動讀取 CLAUDE.md（平台硬編碼行為）
       └→ CLAUDE.md 裡寫著「讀 WIKI_SCHEMA.md」
            └→ Agent 讀取 WIKI_SCHEMA.md，理解全部規則

Antigravity 啟動
  └→ 自動讀取 .agyrules（平台硬編碼行為）
       └→ .agyrules 裡寫著「遵守 WIKI_SCHEMA.md」
            └→ Agent 讀取 WIKI_SCHEMA.md，理解全部規則
```

### 為什麼規則放在 WIKI_SCHEMA.md 而不是入口檔？

```
CLAUDE.md ─────┐
               ├──→ WIKI_SCHEMA.md（共用規範，改一處全局生效）
.agyrules ─────┘
```

入口檔各平台不同，但規則是通用的。抽出來放 `WIKI_SCHEMA.md`，兩邊都只需一行「去讀它」。

### 初始化後的 Vault 結構

```
My-Vault/                          ← Vault 根目錄
├── CLAUDE.md                      ← Claude Code 入口（自動讀取）
├── .agyrules                      ← Antigravity 入口（自動讀取）
├── WIKI_SCHEMA.md                 ← 核心規範（被上面兩個引用）
├── .claude/skills/                ← Claude Code 的 Skills
│   ├── ingest/skill.md
│   ├── lint/skill.md
│   └── query/skill.md
├── .agents/skills/                ← Antigravity 的 Skills
│   └── scaffold/SKILL.md
├── raw/                           ← 原始素材收件箱（唯讀）
│   ├── 01-articles/
│   ├── 02-papers/
│   ├── 03-transcripts/
│   ├── 04-clipper/
│   └── 09-archive/
├── wiki/                          ← 知識編譯輸出區
│   ├── concepts/
│   ├── entities/
│   ├── sources/
│   ├── syntheses/
│   ├── index.md
│   └── log.md
└── assets/                        ← 媒體資產存放區
```

---

## 🛠️ 內建 Skills

| 指令 | 功能 | 觸發方式 |
|------|------|----------|
| `/ingest` | 將 raw/ 原始素材編譯為 wiki/ 知識頁面 | `/ingest` 或 `/ingest <路徑>` |
| `/query` | 在本地知識庫中精準檢索並回答 | `/query <問題>` |
| `/lint` | 知識庫健康度全面巡檢 | `/lint` |

### Ingest 工作流
```mermaid
graph LR
    A[raw/ 原始素材] --> B[讀取 & 提煉]
    B --> C[建立 Source 摘要]
    C --> D[建立/更新 Entity & Concept]
    D --> E[更新 index.md & log.md]
    E --> F[歸檔至 raw/09-archive/]
```

### Lint 巡檢項目
- ✅ 索引一致性（index.md 與實體檔案同步）
- ✅ 雙鏈健康（死鏈偵測）
- ✅ 孤兒頁面偵測
- ✅ 知識衝突審查

---

## ➕ 如何新增 Skill

### 第 1 步：建立 Skill 檔案

以新增 `export` skill 為例，建立兩份（Claude Code + Antigravity）：

```bash
# Claude Code 版
mkdir -p .claude/skills/export
touch .claude/skills/export/skill.md

# Antigravity 版（內容相同，檔名不同）
mkdir -p .agents/skills/export
touch .agents/skills/export/SKILL.md
```

### 第 2 步：撰寫 Skill 內容

```markdown
---
name: export
description: 將 wiki/ 中的知識頁面匯出為 PDF 或簡報格式。當用戶提到"匯出"、"輸出報告"、"轉 PDF" 時觸發。
user-invocable: true
---

# export 技能：知識匯出

## 1. 核心目標
[描述這個 skill 要做什麼]

## 2. 觸發條件
[什麼時候該觸發]

## 3. 操作流程 (SOP)
[步驟化的執行指南]
```

> **關鍵**：`description` 寫得好不好，直接決定 AI 能不能自動找到你的 skill。
> 把所有可能的觸發詞（匯出、輸出、轉 PDF……）都寫進去。

### 第 3 步：在入口檔登記路由

編輯 `CLAUDE.md`，新增一行：
```markdown
   - `/export` -> 調用 `.claude/skills/export/skill`
```

### 第 4 步：同步到另一個平台

```bash
# 一鍵同步：從 .claude 複製到 .agents
for dir in .claude/skills/*/; do
  name=$(basename "$dir")
  mkdir -p ".agents/skills/$name"
  cp "$dir/skill.md" ".agents/skills/$name/SKILL.md"
done
```

### Skill 觸發機制總結

| 觸發方式 | 運作原理 | 你要做什麼 |
|----------|---------|-----------|
| **自動觸發** | 平台比對 `description` 與用戶意圖 | 把 `description` 寫清楚完整 |
| **斜線指令** | 用戶輸入 `/export`，Agent 查路由表 | 在 `CLAUDE.md` 登記路由 |
| **自然語言** | 用戶說「幫我匯出報告」 | 同自動觸發（靠 description） |

### Skill 存放路徑對照

| 平台 | Skill 路徑 | 檔名 |
|------|-----------|------|
| Claude Code | `.claude/skills/<名稱>/` | `skill.md` |
| Antigravity | `.agents/skills/<名稱>/` | `SKILL.md` |

兩份檔案的**內容可以 100% 一樣**，只是路徑和檔名不同。

---

## 📝 自訂指南

### 品牌與語意設定
編輯 `WIKI_SCHEMA.md` 中的 **§3.D 核心語意與品牌特例守則**：

```markdown
### D. 核心語意與品牌特例守則 (Custom Constraints)
- **品牌概念**：[填入你的品牌核心概念]
- **產品感受**：[填入你希望產出的風格與調性]
```

### 新增 raw/ 子分類
在 `raw/` 下新增你需要的分類目錄（如 `05-meetings/`、`06-bookmarks/`），並在 ingest skill 中更新說明。

### 語言設定
預設使用**台灣繁體中文 (zh-TW)**。若需變更，修改 `WIKI_SCHEMA.md` 的 §1 語言指令。

---

## 🤝 相容性

| AI Agent | 支援狀態 | 入口檔 | Skill 路徑 |
|----------|----------|--------|-----------|
| Claude Code | ✅ 完整支援 | `CLAUDE.md` | `.claude/skills/` |
| Antigravity IDE | ✅ 完整支援 | `.agyrules` | `.agents/skills/` |
| Cursor / Windsurf | ⚡ 相容 | 手動餵入 `WIKI_SCHEMA.md` | 不支援原生 Skill |
| 其他 Agent | ⚡ 相容 | 手動餵入 `WIKI_SCHEMA.md` | 不支援原生 Skill |

---

## 📜 License

MIT License — 自由使用、修改與分享。

---

## 🙏 致謝

- [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — LLM Wiki 原始概念
- [Obsidian](https://obsidian.md/) — 本地 Markdown 知識管理
- [Anthropic](https://www.anthropic.com/) — Claude Code Skills 架構
- [Google](https://google.com/) — Antigravity IDE Agent Skills
