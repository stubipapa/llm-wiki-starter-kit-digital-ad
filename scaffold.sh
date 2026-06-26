#!/usr/bin/env bash
# ============================================================================
# LLM Wiki Starter Kit — scaffold.sh
# 一鍵初始化符合 Karpathy 規範的 Obsidian LLM Wiki 知識庫
# 用法：bash scaffold.sh [目標目錄]
# ============================================================================

set -euo pipefail

# --- 顏色定義 ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- 取得腳本所在目錄（模板來源） ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- 目標目錄 ---
TARGET_DIR="${1:-.}"
TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd || mkdir -p "$TARGET_DIR" && cd "$TARGET_DIR" && pwd)"

echo -e "${CYAN}🧠 LLM Wiki Starter Kit — 初始化中...${NC}"
echo -e "   目標目錄：${YELLOW}${TARGET_DIR}${NC}"
echo ""

# --- 檢查是否已存在核心檔案 ---
if [[ -f "${TARGET_DIR}/WIKI_SCHEMA.md" ]]; then
    echo -e "${RED}⚠️  偵測到 ${TARGET_DIR}/WIKI_SCHEMA.md 已存在！${NC}"
    read -p "   是否覆蓋現有檔案？(y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo -e "${YELLOW}已取消初始化。${NC}"
        exit 0
    fi
fi

# --- 建立目錄結構 ---
echo -e "${GREEN}📁 建立目錄結構...${NC}"

directories=(
    "raw/01-articles"
    "raw/02-papers"
    "raw/03-transcripts"
    "raw/04-clipper"
    "raw/09-archive"
    "wiki/concepts"
    "wiki/entities"
    "wiki/sources"
    "wiki/syntheses"
    "assets"
    ".claude/skills/ingest"
    ".claude/skills/lint"
    ".claude/skills/query"
    ".agents/skills/scaffold"
)

for dir in "${directories[@]}"; do
    mkdir -p "${TARGET_DIR}/${dir}"
    echo -e "   ✅ ${dir}/"
done

# --- 複製模板檔案 ---
echo ""
echo -e "${GREEN}📄 建立規則與模板檔案...${NC}"

template_files=(
    "CLAUDE.md"
    "WIKI_SCHEMA.md"
    ".agyrules"
    ".claude/skills/ingest/skill.md"
    ".claude/skills/lint/skill.md"
    ".claude/skills/query/skill.md"
    ".agents/skills/scaffold/SKILL.md"
    "wiki/index.md"
    "wiki/log.md"
)

for file in "${template_files[@]}"; do
    if [[ -f "${SCRIPT_DIR}/${file}" ]]; then
        cp "${SCRIPT_DIR}/${file}" "${TARGET_DIR}/${file}"
        echo -e "   ✅ ${file}"
    else
        echo -e "   ${YELLOW}⚠️  模板不存在，跳過: ${file}${NC}"
    fi
done

# --- 建立 .gitkeep（讓空目錄能被 Git 追蹤） ---
echo ""
echo -e "${GREEN}📌 建立 .gitkeep 佔位檔...${NC}"

gitkeep_dirs=(
    "raw/01-articles"
    "raw/02-papers"
    "raw/03-transcripts"
    "raw/04-clipper"
    "raw/09-archive"
    "wiki/concepts"
    "wiki/entities"
    "wiki/sources"
    "wiki/syntheses"
    "assets"
)

for dir in "${gitkeep_dirs[@]}"; do
    touch "${TARGET_DIR}/${dir}/.gitkeep"
done
echo -e "   ✅ 已建立 ${#gitkeep_dirs[@]} 個 .gitkeep"

# --- 更新 log.md 中的日期 ---
TODAY=$(date +%Y-%m-%d)
if [[ -f "${TARGET_DIR}/wiki/log.md" ]]; then
    sed -i '' "s/YYYY-MM-DD/${TODAY}/g" "${TARGET_DIR}/wiki/log.md" 2>/dev/null || \
    sed -i "s/YYYY-MM-DD/${TODAY}/g" "${TARGET_DIR}/wiki/log.md" 2>/dev/null || true
fi

# --- 初始化 Git（可選） ---
echo ""
if [[ ! -d "${TARGET_DIR}/.git" ]]; then
    read -p "是否初始化 Git 儲存庫？(y/N): " init_git
    if [[ "$init_git" == "y" || "$init_git" == "Y" ]]; then
        cd "${TARGET_DIR}" && git init
        echo -e "   ✅ Git 儲存庫已初始化"
    fi
fi

# --- 完成報告 ---
echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ LLM Wiki Vault 初始化完成！${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo -e "📁 已建立的目錄結構："
echo -e "   ${CYAN}raw/${NC}          — 原始素材收件箱（唯讀）"
echo -e "   ${CYAN}wiki/${NC}         — 知識編譯輸出區"
echo -e "   ${CYAN}assets/${NC}       — 媒體資產存放區"
echo ""
echo -e "📄 已建立的規則檔案："
echo -e "   ${CYAN}CLAUDE.md${NC}     — Agent 全局系統提示"
echo -e "   ${CYAN}WIKI_SCHEMA.md${NC} — Wiki 架構規範"
echo -e "   ${CYAN}.agyrules${NC}     — Antigravity 路由規則"
echo ""
echo -e "🛠️  已建立的技能："
echo -e "   ${CYAN}/ingest${NC}       — 原始素材攝取與編譯"
echo -e "   ${CYAN}/query${NC}        — 本地知識檢索與回答"
echo -e "   ${CYAN}/lint${NC}         — 知識庫健康度巡檢"
echo ""
echo -e "🚀 下一步："
echo -e "   1. 用 Obsidian 開啟 ${YELLOW}${TARGET_DIR}${NC} 作為 Vault"
echo -e "   2. 將原始素材放入 ${CYAN}raw/${NC} 對應子目錄"
echo -e "   3. 使用 AI Agent 執行 ${CYAN}/ingest${NC} 開始建構知識網絡"
echo ""
