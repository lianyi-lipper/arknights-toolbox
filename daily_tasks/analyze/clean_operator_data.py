"""
干员数据清洗脚本
================
读取 raw_data/player_info.json → 输出干员报表到 analyze/reports/
"""

import sys
import os
import json
import csv

# ─── 路径配置 ───────────────────────────────────────────────
DAILY_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INPUT_FILE = os.path.join(DAILY_DIR, "raw_data", "player_info.json")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
OUT_JSON   = os.path.join(REPORTS_DIR, "cleaned_chars.json")
OUT_CSV    = os.path.join(REPORTS_DIR, "cleaned_chars.csv")
# ────────────────────────────────────────────────────────────

PROFESSION_TRANSLATOR = {
    "PIONEER": "先锋",
    "WARRIOR": "近卫",
    "SNIPER": "狙击",
    "TANK": "重装",
    "MEDIC": "医疗",
    "SUPPORT": "辅助",
    "CASTER": "术师",
    "SPECIAL": "特种"
}

def extract_mod_info(equip_list, equipment_info_map):
    """提取非默认模组信息并翻译为中文名称"""
    mods = []
    for eq in equip_list:
        eq_id = eq.get("id", "")
        if "uniequip_001_" in eq_id or "uniequip_002_" in eq_id and eq.get("level") == 1 and eq.get("locked"):
             if eq.get("locked"):
                 continue
             if "uniequip_001_" in eq_id:
                 continue
                 
        if not eq.get("locked"):
            eq_name = equipment_info_map.get(eq_id, {}).get("name", eq_id)
            mods.append(f"{eq_name} (Lv.{eq.get('level')})")
    return " | ".join(mods) if mods else "无"

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

    chars = raw_data.get("chars", [])
    char_info_map = raw_data.get("charInfoMap", {})
    equipment_info_map = raw_data.get("equipmentInfoMap", {})

    print(f"✅ 成功加载原始数据，共 {len(chars)} 名干员。")
    print("⏳ 正在进行数据清洗和合并...")

    cleaned_data = []

    for char in chars:
        char_id = char.get("charId", "")
        info = char_info_map.get(char_id, {})
        
        name = info.get("name", char_id)
        rarity = info.get("rarity", 0)
        
        raw_profession = info.get("profession", "UNKNOWN")
        profession = PROFESSION_TRANSLATOR.get(raw_profession, raw_profession)
        
        sub_profession = info.get("subProfessionName", "未知")

        level = char.get("level", 1)
        evolve_phase = char.get("evolvePhase", 0)
        potential_rank = char.get("potentialRank", 0)
        favor_percent = char.get("favorPercent", 0)
        
        skills = char.get("skills", [])
        spec_skills = []
        for i, sk in enumerate(skills):
            spec_lvl = sk.get("specializeLevel", 0)
            if spec_lvl > 0:
                spec_skills.append(f"技能{i+1}:专{spec_lvl}")
                
        spec_str = " | ".join(spec_skills) if spec_skills else "无"
        
        equip_list = char.get("equip", [])
        mods_str = extract_mod_info(equip_list, equipment_info_map)

        cleaned_data.append({
            "charId": char_id,
            "name": name,
            "rarity": rarity,
            "profession": profession,
            "subProfession": sub_profession,
            "evolvePhase": evolve_phase,
            "level": level,
            "potentialRank": potential_rank,
            "favorPercent": favor_percent,
            "specializations": spec_str,
            "modules": mods_str
        })

    cleaned_data.sort(key=lambda x: (
        x["rarity"], 
        x["evolvePhase"], 
        x["level"], 
        x["potentialRank"]
    ), reverse=True)

    # 1. 导出 JSON
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    print(f"💾 已导出清洗后的 JSON 报表: {OUT_JSON}")

    # 2. 导出 CSV
    if cleaned_data:
        keys = ["name", "rarity", "profession", "subProfession", "evolvePhase", "level", 
                "potentialRank", "favorPercent", "specializations", "modules", "charId"]
        
        headers_map = {
            "name": "干员名",
            "rarity": "星级",
            "profession": "大职业",
            "subProfession": "子职业分支",
            "evolvePhase": "精英化",
            "level": "等级",
            "potentialRank": "潜能",
            "favorPercent": "信赖值(%)",
            "specializations": "技能专精状态",
            "modules": "装备模组",
            "charId": "内部代号"
        }

        with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writerow(headers_map)
            writer.writerows(cleaned_data)
        print(f"💾 已导出清洗后的 CSV 报表: {OUT_CSV}")

    print("🎉 干员数据快照清洗完成！")

if __name__ == '__main__':
    main()
