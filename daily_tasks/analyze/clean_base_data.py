"""
基建数据清洗脚本
================
读取 raw_data/player_info.json → 输出基建排班报表到 analyze/reports/
"""

import sys
import os
import json
import csv

# ─── 路径配置 ───────────────────────────────────────────────
DAILY_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INPUT_FILE = os.path.join(DAILY_DIR, "raw_data", "player_info.json")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
OUT_JSON   = os.path.join(REPORTS_DIR, "cleaned_base_chars.json")
OUT_CSV    = os.path.join(REPORTS_DIR, "cleaned_base_chars.csv")
# ────────────────────────────────────────────────────────────

# 森空岛返回的 AP 机制是 放大 360000 倍，即 1 点心情 = 360,000 AP。满心情 24 = 8,640,000 AP
AP_DIVISOR = 360000.0

# 基建产物常见 Item ID 到中文的映射字典
ITEM_TRANSLATOR = {
    "2001": "基础作战记录",
    "2002": "初级作战记录",
    "2003": "中级作战记录",
    "2004": "高级作战记录",
    "3003": "赤金",
    "3401": "源石碎片",
    "32001": "双极纳米片",
    "32002": "D32钢",
    "32003": "聚合剂",
    "31013": "白马醇",
    "31014": "三水锰矿",
    "31023": "改量装置",
    "31024": "全新装置",
}

def extract_room_chars(room_list, room_type_name, char_info_map, current_ts, formula_info_map=None):
    """通用函数，从指定的房间列表中提取上班干员的信息。"""
    results = []
    
    if isinstance(room_list, dict):
        room_list = [room_list]
        
    for room in room_list:
        slot = room.get('slotId', 'default')
        chars = room.get('chars', [])
        
        for char in chars:
            char_id = char.get('charId', '')
            if not char_id:
                continue
                
            info = char_info_map.get(char_id, {})
            name = info.get("name", char_id)
            
            raw_ap = char.get("ap", 0)
            mood = round(raw_ap / AP_DIVISOR, 2)
            
            work_time_sec = char.get("workTime", 0)
            work_time_str = f"{work_time_sec // 3600}小时{(work_time_sec % 3600) // 60}分钟"
            
            product_name = "无"
            stock_info = "无"
            speed = "无"
            
            if room_type_name == "制造站" and formula_info_map:
                formula_id = room.get("formulaId")
                if formula_id:
                    formula_detail = formula_info_map.get(formula_id, {})
                    item_id = formula_detail.get("itemId", "")
                    product_name = ITEM_TRANSLATOR.get(item_id, f"未知物品({item_id})")
                
                complete = room.get("complete", 0)
                capacity = room.get("capacity", 0)
                speed_raw = room.get("speed", 0.0)
                
                stock_info = f"{complete} / {capacity}"
                speed = f"+{round((speed_raw - 1.0) * 100)}%" if speed_raw > 1.0 else "基础速度"
            
            results.append({
                "roomType": room_type_name,
                "roomSlot": slot,
                "charId": char_id,
                "name": name,
                "mood": mood,
                "workTimeSec": work_time_sec,
                "workTimeStr": work_time_str,
                "productName": product_name,
                "stockInfo": stock_info,
                "speed": speed
            })
            
    return results

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 找不到原始数据文件：{INPUT_FILE}")
        print("请先执行 `python -m daily_tasks.fetch.get_daily_info` 生成数据！")
        sys.exit(1)

    os.makedirs(REPORTS_DIR, exist_ok=True)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        try:
            raw_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ 解析 JSON 失败: {e}")
            sys.exit(1)

    current_ts = raw_data.get("currentTs", 0)
    building = raw_data.get("building", {})
    char_info_map = raw_data.get("charInfoMap", {})
    formula_info_map = raw_data.get("manufactureFormulaInfoMap", {})

    print(f"✅ 加载基建数据...")

    all_chars = []
    
    all_chars.extend(extract_room_chars(building.get('manufactures', []), "制造站", char_info_map, current_ts, formula_info_map))
    all_chars.extend(extract_room_chars(building.get('tradings', []), "贸易站", char_info_map, current_ts))
    all_chars.extend(extract_room_chars(building.get('control', {}), "控制中枢", char_info_map, current_ts))
    all_chars.extend(extract_room_chars(building.get('dormitories', []), "宿舍", char_info_map, current_ts))
    all_chars.extend(extract_room_chars(building.get('power', []), "发电站", char_info_map, current_ts))
    all_chars.extend(extract_room_chars(building.get('meeting', {}), "会客室", char_info_map, current_ts))
    all_chars.extend(extract_room_chars(building.get('hire', {}), "人力办公室", char_info_map, current_ts))

    all_chars.sort(key=lambda x: (x["mood"], x["roomType"]))
    
    print(f"💡 共发现 {len(all_chars)} 名在基建上班/休息的干员。")

    # 1. 导出 JSON
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_chars, f, ensure_ascii=False, indent=2)
    print(f"💾 已导出基建JSON: {OUT_JSON}")

    # 2. 导出 CSV
    if all_chars:
        headers = ["name", "mood", "roomType", "roomSlot", "workTimeStr", "productName", "stockInfo", "speed", "charId"]
        headers_map = {
            "name": "干员姓名",
            "mood": "当前心情 (max 24)",
            "roomType": "设施类型",
            "roomSlot": "房间号/槽位",
            "workTimeStr": "连续工作时间",
            "productName": "生产目标 (制造站专属)",
            "stockInfo": "已完成/容量 (制造站专属)",
            "speed": "当前设施效能效率加成",
            "charId": "干员代号"
        }

        with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
            writer.writerow(headers_map)
            writer.writerows(all_chars)
        print(f"💾 已导出基建排班CSV表: {OUT_CSV}")

    print("🎉 基建数据快照清洗完成！低心情的需要注意换班哦！")

if __name__ == '__main__':
    main()
