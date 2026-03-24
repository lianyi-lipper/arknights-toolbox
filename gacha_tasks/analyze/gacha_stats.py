"""
明日方舟寻访数据分析脚本
========================
读取 raw_data/gacha_records.json，生成统计报告。

输出：
  - reports/gacha_summary.txt   纯文本摘要
  - reports/gacha_summary.json  结构化数据
"""

import os, json
from collections import Counter, defaultdict

# ─── 路径配置 ──────────────────────────────────────────────────
GACHA_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_FILE   = os.path.join(GACHA_DIR, "raw_data", "gacha_records.json")
REPORT_DIR = os.path.join(GACHA_DIR, "analyze", "reports")
# ──────────────────────────────────────────────────────────────

RARITY_MAP = {5: "★6", 4: "★5", 3: "★4", 2: "★3", 1: "★2", 0: "★1"}


def load_records() -> list:
    if not os.path.exists(RAW_FILE):
        print(f"❌ 数据文件不存在: {RAW_FILE}")
        print(f"   请先运行 gacha_tasks/fetch/get_gacha_records.py")
        return []
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze(records: list) -> dict:
    """分析寻访记录，返回统计数据"""

    # 1. 基础统计
    total = len(records)
    rarity_count = Counter(r.get("rarity") for r in records)

    # 2. 分类统计
    category_count = Counter(r.get("_category", "未知") for r in records)
    pool_count = Counter(r.get("poolName", "未知") for r in records)

    # 3. 六星干员列表
    six_stars = [r for r in records if r.get("rarity") == 5]
    six_star_detail = []
    for r in six_stars:
        six_star_detail.append({
            "name": r.get("charName", "?"),
            "pool": r.get("poolName", "?"),
            "category": r.get("_category", "?"),
            "isNew": r.get("isNew", False),
            "gachaTs": r.get("gachaTs", ""),
        })

    # 4. 六星出货间隔（保底计数）
    # 按时间正序（从早到晚）计算每次六星之间的抽数
    sorted_records = sorted(records, key=lambda r: int(r.get("gachaTs", "0")))
    pity_list = []  # 每次六星的间隔抽数
    count_since_last = 0
    for r in sorted_records:
        count_since_last += 1
        if r.get("rarity") == 5:
            pity_list.append({
                "name": r.get("charName", "?"),
                "pool": r.get("poolName", "?"),
                "pulls": count_since_last,
            })
            count_since_last = 0

    # 5. 五星干员列表
    five_stars = [r for r in records if r.get("rarity") == 4]

    return {
        "total": total,
        "rarity_distribution": {RARITY_MAP.get(k, f"稀有度{k}"): v
                                 for k, v in sorted(rarity_count.items(), reverse=True)},
        "category_distribution": dict(category_count.most_common()),
        "pool_distribution": dict(pool_count.most_common()),
        "six_stars": six_star_detail,
        "six_star_pity": pity_list,
        "five_star_count": len(five_stars),
        "current_pity": count_since_last,  # 距离上次六星的抽数
    }


def format_report(stats: dict) -> str:
    """生成纯文本报告"""
    lines = []
    lines.append("=" * 50)
    lines.append("  明日方舟寻访记录统计报告")
    lines.append("=" * 50)
    lines.append(f"\n总抽数: {stats['total']}")
    lines.append(f"当前保底计数: {stats['current_pity']} (距上次★6)")

    lines.append("\n── 稀有度分布 ──")
    for rarity, count in stats["rarity_distribution"].items():
        pct = count / stats["total"] * 100
        bar = "█" * int(pct / 2)
        lines.append(f"  {rarity}: {count:>4} ({pct:5.1f}%) {bar}")

    lines.append("\n── 分类统计 ──")
    for cat, count in stats["category_distribution"].items():
        lines.append(f"  {cat}: {count} 次")

    lines.append("\n── 卡池统计 ──")
    for pool, count in stats["pool_distribution"].items():
        lines.append(f"  {pool}: {count} 次")

    lines.append(f"\n── ★6 干员 ({len(stats['six_stars'])} 次) ──")
    for s in stats["six_stars"]:
        tag = "(新)" if s["isNew"] else "(重复)"
        lines.append(f"  [{s['pool']}] {s['name']}  {tag}")

    lines.append(f"\n── ★6 出货间隔 ──")
    if stats["six_star_pity"]:
        pulls = [p["pulls"] for p in stats["six_star_pity"]]
        avg = sum(pulls) / len(pulls)
        lines.append(f"  平均: {avg:.1f} 抽/★6")
        lines.append(f"  最欧: {min(pulls)} 抽")
        lines.append(f"  最非: {max(pulls)} 抽")
        lines.append("")
        for p in stats["six_star_pity"]:
            bar = "▓" * (p["pulls"] // 5)
            lines.append(f"  {p['name']:>8}: {p['pulls']:>3} 抽 {bar}")

    return "\n".join(lines)


def main():
    records = load_records()
    if not records:
        return

    os.makedirs(REPORT_DIR, exist_ok=True)

    stats = analyze(records)
    report = format_report(stats)

    # 输出到控制台
    print(report)

    # 保存报告
    txt_path = os.path.join(REPORT_DIR, "gacha_summary.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(report)

    json_path = os.path.join(REPORT_DIR, "gacha_summary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"\n💾 报告已保存到:")
    print(f"   {txt_path}")
    print(f"   {json_path}")


if __name__ == "__main__":
    main()
