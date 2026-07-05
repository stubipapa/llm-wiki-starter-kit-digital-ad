import csv
import json
import os
import sys

def clean_int(val):
    if not val or val.strip() == '-' or val.strip() == '': return None
    return int(val.replace(',', '').replace(' ', ''))

def clean_float(val):
    if not val or val.strip() == '-' or val.strip() == '': return None
    val = val.replace(',', '').replace('NT$', '').replace('$', '').replace(' ', '')
    return float(val)

def clean_percent(val):
    if not val or val.strip() == '-' or val.strip() == '': return None
    val = val.replace('%', '').replace(' ', '')
    return round(float(val) / 100.0, 4)

def get_value(row, col_map, key, default=None):
    if key in col_map and col_map[key] < len(row):
        return row[col_map[key]]
    return default

def process_csv(input_csv, output_json):
    campaign = {
        "campaign_name": "",
        "platform": "",
        "marketing_objective": "",
        "period": "",
        "cost": None,
        "kpi_target_value": None,
        "kpi_actual_value": None,
        "kpi_achievement_rate": None,
        "date": {},
        "target_audience": {},
        "target_age": {}
    }

    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = list(csv.reader(f))

    current_section = None
    col_map = {}
    
    # Parse headers and find sections
    for i, row in enumerate(reader):
        if not row: continue
        col0 = row[0].strip()
        
        # 1. Parse Global Info
        if col0 == "Campaign 名稱":
            campaign["campaign_name"] = row[1].replace('\n', '')
            # Look for 預估曝光數 or 保證曝光數
            for idx, cell in enumerate(row):
                if cell.strip() in ["保證曝光數", "預估曝光數"] and idx + 1 < len(row):
                    campaign["kpi_target_value"] = clean_int(row[idx+1])
        elif col0 == "媒體":
            campaign["platform"] = row[1]
        elif col0 == "廣告走期":
            campaign["period"] = row[1]
        elif col0 == "廣告總預算":
            campaign["cost"] = clean_float(row[1])
            for idx, cell in enumerate(row):
                if cell.strip() == "實際曝光數" and idx + 1 < len(row):
                    campaign["kpi_actual_value"] = clean_int(row[idx+1])
        elif col0 == "KPI":
            for idx, cell in enumerate(row):
                if cell.strip() == "計價單位" and idx + 1 < len(row):
                    campaign["marketing_objective"] = row[idx+1]
        elif col0 == "廣告單價":
            for idx, cell in enumerate(row):
                if cell.strip() == "KPI 目前達成率" and idx + 1 < len(row):
                    kpi_rate = row[idx+1]
                    if '%' in kpi_rate:
                        campaign["kpi_achievement_rate"] = round(float(kpi_rate.replace('%', '')) / 100.0, 4)
                    else:
                        try:
                            campaign["kpi_achievement_rate"] = float(kpi_rate)
                        except:
                            pass
                            
        # 2. Identify Sections and Map Columns dynamically
        elif col0 in ["DATE", "受眾", "素材", "年齡"]:
            if col0 == "DATE":
                current_section = "date"
            elif col0 == "受眾":
                current_section = "target_audience"
            elif col0 in ["素材", "年齡"]:
                current_section = "target_age"
                
            # Build column map for this section
            col_map = {name.strip(): idx for idx, name in enumerate(row)}
            continue
            
        elif col0 == "Estimate" or col0.startswith("KPI") or "finding" in col0:
            continue
            
        # 3. Parse Data Rows
        elif current_section and (col0.replace('/', '').isdigit() or col0 == "TOTAL" or col0 in ["興趣貼標", "線上足跡追蹤", "線下足跡追蹤", "自定義關鍵字", "電子發票數據", "全家零售數據", "25-34", "35-44", "45-54"]):
            
            key_name = "Total" if col0 == "TOTAL" else col0
            
            click_str = get_value(row, col_map, "Click") or get_value(row, col_map, "Link Click")
            button_str = get_value(row, col_map, "點擊 (查詢經銷商)")
            cpm_str = get_value(row, col_map, "CPM")
            cpv_str = get_value(row, col_map, "CPV")
            
            impressions = clean_int(get_value(row, col_map, "IMPRESSION"))
            clicks = clean_int(click_str)
            ctr = clean_percent(get_value(row, col_map, "CTR"))
            view = clean_int(get_value(row, col_map, "View"))
            vtr = clean_percent(get_value(row, col_map, "VTR"))
            cpm = clean_float(cpm_str)
            raw_cpv = clean_float(cpv_str)
            button = clean_int(button_str)
            cost = clean_float(get_value(row, col_map, "COST"))
            
            cpc = None
            if cost is not None and clicks is not None and clicks > 0:
                cpc = round(cost / clicks, 2)
                
            cpv = raw_cpv
            if cpv is None and cost is not None and view is not None and view > 0:
                cpv = round(cost / view, 2)
                
            metrics = {
                "cost": cost,
                "impressions": impressions,
                "clicks": clicks,
                "all_click": None,
                "link_click": None,
                "button": button,
                "ctr": ctr,
                "cpc": cpc,
                "cpm": cpm,
                "view": view,
                "vtr": vtr,
                "cpv": cpv,
                "conversions": None,
                "cpa": None,
                "cap": None
            }
            
            campaign[current_section][key_name] = metrics

    output_data = { "campaigns": [campaign] }
    
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        
    print(f"SUCCESS: CSV data parsed and exported to {output_json}.")

def process_directory(input_dir, output_dir):
    if not os.path.exists(input_dir):
        print(f"Directory {input_dir} does not exist.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    csv_files_processed = 0
    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, filename.replace('.csv', '.json'))
            
            print(f"Processing {input_file}...")
            try:
                process_csv(input_file, output_file)
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
            process_csv(input_path, output_path)
    else:
        # Default behavior: process raw/02-csv/ad_reports to raw/03-json/ad_reports
        # Ensure we use an absolute path based on the current working directory.
        default_input = "raw/02-csv/ad_reports"
        default_output = "raw/03-json/ad_reports"
        process_directory(default_input, default_output)
