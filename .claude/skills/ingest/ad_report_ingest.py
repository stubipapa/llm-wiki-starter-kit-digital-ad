import csv
import json
import os
import sys
import re

# ============================================================================
# LLM Wiki Starter Kit — ad_report_ingest.py
# 將標準化廣告報表 CSV 轉換為結構化 JSON 與視覺化 Markdown 歸檔
# ============================================================================

def strip_template_wrapper(val):
    """
    剝除模板包裝格式，例如：
    '（範例：300000）' → '300000'
    '（範例：300,000）' → '300,000'
    '（範例：meta）' → 'meta'
    '（範例：3%）' → '3%'
    如果不是模板格式，原樣返回。
    """
    if not val:
        return val
    val = val.strip()
    # 匹配 （範例：XXX） 或 (範例：XXX) 格式
    match = re.match(r'^[（(]範例[：:](.+?)[）)]$', val)
    if match:
        return match.group(1).strip()
    return val

def clean_int(val):
    """清洗整數值，移除千分位逗號與空白"""
    if not val or val.strip() in ['-', '', '—']:
        return None
    val = strip_template_wrapper(val)
    val = val.replace(',', '').replace(' ', '')
    try:
        return int(float(val))
    except ValueError:
        return None

def clean_float(val):
    """清洗浮點數值，移除貨幣符號"""
    if not val or val.strip() in ['-', '', '—']:
        return None
    val = strip_template_wrapper(val)
    val = val.replace(',', '').replace('NT$', '').replace('$', '').replace(' ', '')
    try:
        return float(val)
    except ValueError:
        return None

def clean_percent(val):
    """清洗百分比值，轉為小數 (例如 13.19% → 0.1319)"""
    if not val or val.strip() in ['-', '', '—']:
        return None
    val = strip_template_wrapper(val)
    val = val.replace('%', '').replace(' ', '').replace(',', '')
    try:
        return round(float(val) / 100.0, 4)
    except ValueError:
        return None

def clean_text(val):
    """清洗文字值，剝除模板包裝"""
    if not val:
        return ''
    return strip_template_wrapper(val.strip())

def safe_get(row, idx, default=''):
    """安全取值，避免 index out of range"""
    if idx < len(row):
        return row[idx].strip()
    return default

def get_value(row, col_map, key, default=None):
    """從 col_map 對應的欄位取值"""
    if key in col_map and col_map[key] < len(row):
        return row[col_map[key]]
    return default

def format_val(val, is_percent=False, is_float=False):
    """格式化數值用於 Markdown 輸出"""
    if val is None:
        return "-"
    if is_percent:
        return f"{val*100:.2f}%"
    if is_float:
        return f"{val:,.2f}"
    return f"{val:,}"

# ============================================================================
# 1. Header 區解析 (Row 1-12)
# ============================================================================

def parse_header_area(rows):
    """
    解析 CSV 的前 12 行 Header 區，提取活動概覽資訊。
    模板格式為每行 8 欄，左半部 (col 0-1) 與右半部 (col 3-4) 各放一對 key-value。
    """
    campaign = {
        "advertiser": "",
        "campaign_name": "",
        "platform": "",
        "ad_objective": "",
        "funnel_stage": "",
        "creative_type": "",
        "creative_style": "",
        "period_start": "",
        "period_end": "",
        "period": "",
        "cost": None,
        "ad_unit_price": None,
        "pricing_unit": "",
        "guaranteed_impressions": None,
        "actual_impressions": None,
        "estimated_ctr": None,
        "estimated_clicks": None,
        "actual_clicks": None,
        "kpi_target_value": None,
        "kpi_actual_value": None,
        "kpi_achievement_rate": None,
        "ga4_page_entries": None,
        "ga4_avg_duration": None,
        "gtm_events": None,
        "date": {},
        "target_audience": {},
        "target_age": {}
    }

    # 逐行解析 Header 區 (最多前 17 行，因為後面可能有空行)
    for row in rows[:17]:
        if not row or not row[0].strip():
            continue

        left_key = row[0].strip() if len(row) > 0 else ''
        left_val = safe_get(row, 1)
        right_key = safe_get(row, 3)
        right_val = safe_get(row, 4)

        # --- 左半部解析 ---
        if left_key == '廣告商':
            campaign['advertiser'] = clean_text(left_val)
        elif left_key == 'Campaign 名稱':
            campaign['campaign_name'] = clean_text(left_val).replace('\n', '')
        elif left_key == '廣告總預算':
            campaign['cost'] = clean_float(left_val)
        elif left_key == '投放平台':
            campaign['platform'] = clean_text(left_val)
        elif left_key == '媒體':
            # 向後相容舊模板
            if not campaign['platform']:
                campaign['platform'] = clean_text(left_val)
        elif left_key == '廣告開始':
            campaign['period_start'] = clean_text(left_val)
        elif left_key == '廣告結束':
            campaign['period_end'] = clean_text(left_val)
        elif left_key == '廣告走期':
            # 向後相容舊模板
            campaign['period'] = clean_text(left_val)
        elif left_key == '漏斗階段':
            campaign['funnel_stage'] = clean_text(left_val)
        elif left_key == '廣告目標':
            campaign['ad_objective'] = clean_text(left_val)
        elif left_key == '廣告單價':
            campaign['ad_unit_price'] = clean_float(left_val)
        elif left_key == 'GA4_有效頁面進站':
            campaign['ga4_page_entries'] = clean_int(left_val)
        elif left_key == 'GA4_平均停留時間':
            campaign['ga4_avg_duration'] = clean_float(left_val)
        elif left_key == 'GTM_實際觸發事件':
            campaign['gtm_events'] = clean_int(left_val)

        # --- 右半部解析 ---
        if right_key == '保證曝光數':
            campaign['guaranteed_impressions'] = clean_int(right_val)
        elif right_key == '實際曝光數':
            campaign['actual_impressions'] = clean_int(right_val)
        elif right_key == '預估 CTR':
            campaign['estimated_ctr'] = clean_percent(right_val)
        elif right_key == '預估點擊數':
            campaign['estimated_clicks'] = clean_int(right_val)
        elif right_key == '實際點擊數':
            campaign['actual_clicks'] = clean_int(right_val)
        elif right_key == '素材種類':
            campaign['creative_type'] = clean_text(right_val)
        elif right_key == '素材風格':
            campaign['creative_style'] = clean_text(right_val)
        elif right_key == '計價單位':
            campaign['pricing_unit'] = clean_text(right_val)
        elif right_key == 'KPI 目標值':
            campaign['kpi_target_value'] = clean_int(right_val) or clean_float(right_val)
        elif right_key == 'KPI 實際值':
            campaign['kpi_actual_value'] = clean_int(right_val) or clean_float(right_val)
        elif right_key == 'KPI 達成率':
            campaign['kpi_achievement_rate'] = clean_percent(right_val)
        # 向後相容舊模板中的 KPI 目前達成率
        elif right_key == 'KPI 目前達成率':
            campaign['kpi_achievement_rate'] = clean_percent(right_val)
        elif right_key == '預估曝光數':
            campaign['guaranteed_impressions'] = clean_int(right_val)

    # 組合走期
    if campaign['period_start'] and campaign['period_end']:
        campaign['period'] = f"{campaign['period_start']} ~ {campaign['period_end']}"

    return campaign

# ============================================================================
# 2. 數據表區解析 (DATE / 年齡 / 受眾)
# ============================================================================

def parse_data_sections(rows, campaign):
    """
    解析 CSV 中的數據區段。
    偵測 section header (DATE / 年齡 / 受眾)，動態建立 col_map，
    然後逐行解析直到遇到空行或下一個 section。
    """
    current_section = None
    col_map = {}

    for row in rows:
        if not row:
            continue
        col0 = row[0].strip()

        # 跳過完全空的行
        if not col0:
            continue

        # 偵測 section header
        if col0 in ['DATE', '年齡', '受眾']:
            if col0 == 'DATE':
                current_section = 'date'
            elif col0 == '年齡':
                current_section = 'target_age'
            elif col0 == '受眾':
                current_section = 'target_audience'

            col_map = {name.strip(): idx for idx, name in enumerate(row) if name.strip()}
            continue

        # 跳過非數據行
        if current_section is None:
            continue

        # 判斷是否為合法的數據行
        is_date_row = '/' in col0 and any(c.isdigit() for c in col0)
        is_total_row = col0 == 'TOTAL'
        is_named_row = current_section in ['target_audience', 'target_age'] and col0 not in ['DATE', '年齡', '受眾', '']

        if not (is_date_row or is_total_row or is_named_row):
            # 遇到不認識的行，重設 section
            current_section = None
            col_map = {}
            continue

        key_name = 'Total' if is_total_row else col0

        # 通用指標提取 — 用 col_map 動態對應
        impressions = clean_int(get_value(row, col_map, 'Impression'))
        clicks = clean_int(get_value(row, col_map, 'Click'))
        engagement = clean_int(get_value(row, col_map, 'Engagement'))
        cost = clean_float(get_value(row, col_map, 'Cost'))
        ctr = clean_percent(get_value(row, col_map, 'CTR'))
        etr = clean_percent(get_value(row, col_map, 'ETR'))
        cpe = clean_float(get_value(row, col_map, 'CPE'))

        # 向後相容舊模板欄位名
        if impressions is None:
            impressions = clean_int(get_value(row, col_map, 'IMPRESSION'))
        if cost is None:
            cost = clean_float(get_value(row, col_map, 'COST'))
        if clicks is None:
            clicks = clean_int(get_value(row, col_map, 'Link Click'))

        # 舊模板額外指標
        view = clean_int(get_value(row, col_map, 'View'))
        vtr = clean_percent(get_value(row, col_map, 'VTR'))
        cpm = clean_float(get_value(row, col_map, 'CPM'))
        cpv = clean_float(get_value(row, col_map, 'CPV'))
        button = clean_int(get_value(row, col_map, '點擊 (查詢經銷商)'))

        # 自動計算衍生指標
        cpc = None
        if cost is not None and clicks is not None and clicks > 0:
            cpc = round(cost / clicks, 2)
        if cpm is None and cost is not None and impressions is not None and impressions > 0:
            cpm = round(cost / impressions * 1000, 2)
        if cpv is None and cost is not None and view is not None and view > 0:
            cpv = round(cost / view, 2)

        metrics = {
            "cost": cost,
            "impressions": impressions,
            "clicks": clicks,
            "engagement": engagement,
            "ctr": ctr,
            "etr": etr,
            "cpc": cpc,
            "cpe": cpe,
            "cpm": cpm,
            "view": view,
            "vtr": vtr,
            "cpv": cpv,
            "button": button,
        }

        campaign[current_section][key_name] = metrics

    return campaign

# ============================================================================
# 3. Markdown 歸檔生成
# ============================================================================

def generate_markdown(campaign, output_md):
    """將 campaign dict 轉換為排版精美的 Markdown 報表，存入 raw/09-archive/"""
    lines = []
    lines.append(f"# 廣告報表原始數據歸檔: {campaign.get('campaign_name', '未命名活動')}")
    lines.append("")

    # --- 活動概覽表格 ---
    lines.append("## 活動概覽")
    lines.append("| 欄位 | 數值 |")
    lines.append("|---|---|")

    overview_fields = [
        ("廣告商", campaign.get('advertiser')),
        ("活動名稱", campaign.get('campaign_name')),
        ("投放平台", campaign.get('platform')),
        ("廣告走期", campaign.get('period')),
        ("廣告目標", campaign.get('ad_objective')),
        ("漏斗階段", campaign.get('funnel_stage')),
        ("素材種類", campaign.get('creative_type')),
        ("素材風格", campaign.get('creative_style')),
        ("廣告單價", format_val(campaign.get('ad_unit_price'), is_float=True)),
        ("計價單位", campaign.get('pricing_unit')),
        ("總預算", format_val(campaign.get('cost'), is_float=True)),
        ("保證曝光數", format_val(campaign.get('guaranteed_impressions'))),
        ("實際曝光數", format_val(campaign.get('actual_impressions'))),
        ("預估 CTR", format_val(campaign.get('estimated_ctr'), is_percent=True)),
        ("預估點擊數", format_val(campaign.get('estimated_clicks'))),
        ("實際點擊數", format_val(campaign.get('actual_clicks'))),
        ("KPI 目標值", format_val(campaign.get('kpi_target_value'))),
        ("KPI 實際值", format_val(campaign.get('kpi_actual_value'))),
        ("KPI 達成率", format_val(campaign.get('kpi_achievement_rate'), is_percent=True)),
    ]

    # GA4 / GTM 欄位只在有值時顯示
    if campaign.get('ga4_page_entries') is not None:
        overview_fields.append(("GA4 有效頁面進站", format_val(campaign.get('ga4_page_entries'))))
    if campaign.get('ga4_avg_duration') is not None:
        overview_fields.append(("GA4 平均停留時間 (秒)", format_val(campaign.get('ga4_avg_duration'), is_float=True)))
    if campaign.get('gtm_events') is not None:
        overview_fields.append(("GTM 實際觸發事件", format_val(campaign.get('gtm_events'))))

    for label, value in overview_fields:
        display = value if value else "-"
        lines.append(f"| {label} | {display} |")
    lines.append("")

    # --- 數據維度表格 ---
    sections = [
        ("日期維度成效 (Date)", "date"),
        ("年齡維度成效 (Target Age)", "target_age"),
        ("受眾維度成效 (Target Audience)", "target_audience"),
    ]

    for title, key in sections:
        data = campaign.get(key, {})
        if not data:
            continue

        # 動態決定要顯示哪些指標欄
        all_metric_keys = [
            ("花費", "cost", True, False),
            ("曝光", "impressions", False, False),
            ("點擊", "clicks", False, False),
            ("互動", "engagement", False, False),
            ("CTR", "ctr", False, True),
            ("ETR", "etr", False, True),
            ("CPC", "cpc", True, False),
            ("CPE", "cpe", True, False),
            ("CPM", "cpm", True, False),
            ("觀看", "view", False, False),
            ("VTR", "vtr", False, True),
            ("CPV", "cpv", True, False),
            ("按鈕點擊", "button", False, False),
        ]

        # 只顯示至少有一行有值的指標欄
        active_cols = []
        for label, mkey, is_float, is_pct in all_metric_keys:
            has_data = any(
                row_metrics.get(mkey) is not None
                for row_metrics in data.values()
            )
            if has_data:
                active_cols.append((label, mkey, is_float, is_pct))

        if not active_cols:
            continue

        lines.append(f"## {title}")
        header = "| 項目 | " + " | ".join(c[0] for c in active_cols) + " |"
        separator = "|---" + "|---" * len(active_cols) + "|"
        lines.append(header)
        lines.append(separator)

        for item_name, metrics in data.items():
            vals = []
            for _, mkey, is_f, is_p in active_cols:
                v = metrics.get(mkey)
                if is_p:
                    vals.append(format_val(v, is_percent=True))
                elif is_f:
                    vals.append(format_val(v, is_float=True))
                else:
                    vals.append(format_val(v))
            lines.append(f"| {item_name} | " + " | ".join(vals) + " |")
        lines.append("")

    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"SUCCESS: Markdown archive generated at {output_md}.")

# ============================================================================
# 4. 主流程
# ============================================================================

def process_csv(input_csv, output_json, output_md=None):
    """主處理函數：讀取 CSV → 解析 Header + 數據 → 輸出 JSON + MD"""
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.reader(f))

    # Step 1: 解析 Header 區
    campaign = parse_header_area(rows)

    # Step 2: 解析數據表區
    campaign = parse_data_sections(rows, campaign)

    # Step 3: 輸出 JSON
    output_data = {"campaigns": [campaign]}
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"SUCCESS: CSV data parsed and exported to {output_json}.")

    # Step 4: 輸出 Markdown 歸檔
    if output_md:
        generate_markdown(campaign, output_md)

def process_directory(input_dir, output_dir, archive_dir="raw/09-archive"):
    """批次處理整個目錄下的所有 CSV 檔案"""
    if not os.path.exists(input_dir):
        print(f"Directory {input_dir} does not exist.")
        return

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

    csv_files_processed = 0
    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, filename.replace('.csv', '.json'))
            archive_file = os.path.join(archive_dir, filename.replace('.csv', '.md'))

            print(f"Processing {input_file}...")
            try:
                process_csv(input_file, output_file, archive_file)
                csv_files_processed += 1
            except Exception as e:
                print(f"Error processing {input_file}: {e}")

    print(f"Finished processing {csv_files_processed} files.")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        if os.path.isdir(input_path):
            process_directory(input_path, output_path)
        else:
            archive_path = sys.argv[3] if len(sys.argv) > 3 else None
            process_csv(input_path, output_path, archive_path)
    else:
        default_input = "raw/02-csv/ad_reports"
        default_output = "raw/03-json/ad_reports"
        process_directory(default_input, default_output)
