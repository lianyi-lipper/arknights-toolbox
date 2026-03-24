"""
皮肤与进度数据清洗脚本
========================
读取 raw_data/player_info.json → 输出皮肤记录和进度简报到 analyze/reports/
"""

import sys
import os
import json
import csv
from datetime import datetime

# ─── 路径配置 ───────────────────────────────────────────────
DAILY_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INPUT_FILE = os.path.join(DAILY_DIR, "raw_data", "player_info.json")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
OUT_SKINS_CSV    = os.path.join(REPORTS_DIR, "cleaned_skins_history.csv")
OUT_PROGRESS_TXT = os.path.join(REPORTS_DIR, "cleaned_progress_report.txt")
# ────────────────────────────────────────────────────────────

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

    print(f"✅ 加载玩家成就与皮肤数据...")
    
    skin_info_map = raw_data.get("skinInfoMap", {})
    char_info_map = raw_data.get("charInfoMap", {})
    campaign_info_map = raw_data.get("campaignInfoMap", {})

    status = raw_data.get("status", {})
    campaign = raw_data.get("campaign", {})
    routine = raw_data.get("routine", {})

    # ==========================
    # 1. 皮肤数据提取与清洗
    # ==========================
    skins_list = raw_data.get("skins", [])
    cleaned_skins = []

    for skin in skins_list:
        skin_id = skin.get("id")
        ts = skin.get("ts", 0)
        
        skin_detail = skin_info_map.get(skin_id, {})
        skin_name = skin_detail.get("name", "默认服装/未命名")
        
        char_id = skin_detail.get("charId", "")
        if not char_id and "#" in skin_id:
            char_id = skin_id.split("#")[0]
        elif not char_id and "@" in skin_id:
            char_id = skin_id.split("@")[0]
            
        char_name = char_info_map.get(char_id, {}).get("name", char_id)
        
        acquire_time = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') if ts > 0 else "初始获得"
        
        cleaned_skins.append({
            "skinName": skin_name,
            "charName": char_name,
            "acquireTime": acquire_time,
            "ts": ts,
            "skinId": skin_id
        })

    cleaned_skins.sort(key=lambda x: x["ts"], reverse=True)

    if cleaned_skins:
        headers = ["skinName", "charName", "acquireTime", "skinId"]
        headers_map = {
            "skinName": "皮肤名称",
            "charName": "所属干员",
            "acquireTime": "获取时间",
            "skinId": "系统代号"
        }

        with open(OUT_SKINS_CSV, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
            writer.writerow(headers_map)
            writer.writerows(cleaned_skins)
        print(f"👕 成功导出 {len(cleaned_skins)} 款皮肤获取记录至: {OUT_SKINS_CSV}")

    # ==========================
    # 2. 游戏进度核心简报
    # ==========================
    main_stage = status.get("mainStageProgress", "暂无数据")
    
    campaign_records = campaign.get("records", [])
    perfect_campaigns = 0
    detailed_campaigns = []
    
    if campaign_records and isinstance(campaign_records, list):
        for record in campaign_records:
            c_id = record.get("campaignId", "")
            kills = record.get("maxKills", 0)
            
            c_name = campaign_info_map.get(c_id, {}).get("name", c_id)
            
            if kills >= 400:
                perfect_campaigns += 1
                status_str = "● 已达成 (400)"
            else:
                status_str = f"○ 未达成 ({kills}/400)"
            
            detailed_campaigns.append(f"- {c_name:<15} {status_str}")

    daily_ap = routine.get("daily", {}).get("current", 0)
    weekly_ap = routine.get("weekly", {}).get("current", 0)

    report_lines = [
        "==========================",
        "🏆 森空岛玩家进度与成就快照",
        "==========================",
        "",
        f"📅 数据提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "【主线推进】",
        f"📍 当前主线最高进度：{main_stage}",
        "",
        "【剿灭作战】",
        f"🔰 已剿灭满 400 杀的战役数量：{perfect_campaigns} 场",
        "",
        "【剿灭详情清单】",
        *detailed_campaigns,
        "",
        "【活跃度】",
        f"☀️ 本日日常进度 (活跃度): {daily_ap}",
        f"🌟 本周周常进度 (活跃度): {weekly_ap}",
        "",
        "【外观收藏】",
        f"👗 总计已收集皮肤 (含原皮换色等): {len(cleaned_skins)} 件"
    ]

    with open(OUT_PROGRESS_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"🏆 成功导出进度简报至: {OUT_PROGRESS_TXT}")
    print("🎉 皮肤和进度分析脚本执行完成！")

if __name__ == '__main__':
    main()
