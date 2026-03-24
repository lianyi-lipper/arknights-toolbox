"""
森空岛每日数据获取脚本
========================
从森空岛 API 拉取玩家数据，同时：
  1. 保存原始 JSON 到 raw_data/（每次覆盖，供分析脚本读取）
  2. 保存 gzip 压缩归档到 archive/YYYY-MM-DD/（按日期长期存储）
"""

import sys
import os
import json
import gzip
from datetime import datetime

# 添加根目录到环境变量以便于引入 skland 模块
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT_DIR)

from skland.api.v1 import SklandApiV1

# ─── 路径配置 ───────────────────────────────────────────────
DAILY_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_FILE = os.path.join(DAILY_DIR, "config.json")
RAW_DIR     = os.path.join(DAILY_DIR, "raw_data")
ARCHIVE_DIR = os.path.join(DAILY_DIR, "archive")
# ────────────────────────────────────────────────────────────


def save_json(name, data):
    """同时保存原始 JSON 和 gzip 归档"""
    os.makedirs(RAW_DIR, exist_ok=True)

    # 1. 原始 JSON（美化格式，方便调试查看）
    raw_path = os.path.join(RAW_DIR, f"{name}.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    raw_size = os.path.getsize(raw_path)

    # 2. gzip 归档（紧凑格式，按日期存储）
    today = datetime.now().strftime("%Y-%m-%d")
    day_dir = os.path.join(ARCHIVE_DIR, today)
    os.makedirs(day_dir, exist_ok=True)

    gz_path = os.path.join(day_dir, f"{name}.json.gz")
    compact = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode("utf-8")
    with gzip.open(gz_path, "wb") as f:
        f.write(compact)
    gz_size = os.path.getsize(gz_path)

    ratio = (1 - gz_size / raw_size) * 100 if raw_size > 0 else 0
    print(f"💾 {name}.json: {raw_size/1024:.1f}KB → {gz_size/1024:.1f}KB (压缩{ratio:.0f}%)")


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"配置文件不存在，请在 {CONFIG_FILE} 中填写你的账号密码！")
        sys.exit(1)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            print("配置文件格式错误，请确保其为有效的 JSON 格式。")
            sys.exit(1)
    return config


def main():
    config = load_config()
    phone = config.get("phone")
    password = config.get("password")

    if not phone or not password:
        print(f"账号或密码未配置，请打开 {CONFIG_FILE} 填写你的手机号和密码。")
        sys.exit(1)

    print("⏳ 正在获取登录凭证...")
    api = SklandApiV1()
    try:
        token = api.account.token_by_phone_password(phone, password)
        code = api.account.grant_code(token)
        cred = api.auth.generate_cred_by_code(code)
        api.init(cred.cred, cred.token)
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        sys.exit(1)

    print("✅ 登录成功！\n")

    # 获取绑定角色
    try:
        raw_binding = api.client.get("/api/v1/game/player/binding").data
        save_json("player_binding", raw_binding)

        bindings = api.game.player_binding()
        uid = bindings[0].binding_list[0].uid
        name = bindings[0].binding_list[0].nick_name
        print(f"🔖 当前角色: {name}  |  UID: {uid}")
    except Exception as e:
        print(f"❌ 获取绑定角色失败: {e}")
        sys.exit(1)

    # 1. 玩家信息
    print("\n" + "=" * 40)
    print("🌟 玩家基础数据展示 🌟")
    print("=" * 40)

    try:
        raw_info = api.client.get(f"/api/v1/game/player/info?uid={uid}").data
        save_json("player_info", raw_info)

        info = api.game.player_info(uid)
        s = info.status
        print(f"📋 账号状态:")
        print(f"   ► 等级      : Lv.{s.level}  ({s.exp.current}/{s.exp.max} exp)")
        print(f"   ► 主线进度  : {s.main_stage_progress}")
        print(f"   ► 理智情况  : {s.ap.current} / {s.ap.max}")
        print(f"   ► 拥有干员数: {len(info.chars)} 位")
        print(f"   ► 设置助战数: {len(info.assist_chars)} 位")

        elite2 = [c for c in info.chars if c.evolve_phase == 2]
        print(f"\n⭐ 精英2干员 (共 {len(elite2)} 位):")
        for c in elite2[:5]:
            print(f"   - 干员ID: {c.char_id} | Lv.{c.level} | 潜能 {c.potential_rank}")
        if len(elite2) > 5:
            print(f"   ... (以下省略其余 {len(elite2) - 5} 个精二干员)")
    except Exception as e:
        print(f"❌ 获取玩家信息数据失败: {e}")

    # 2. 签到信息
    print("\n" + "=" * 40)
    print("📅 签到情况展示 📅")
    print("=" * 40)

    try:
        raw_att = api.client.get(f"/api/v1/game/attendance?uid={uid}&gameId=1").data
        save_json("attendance", raw_att)

        att = api.game.attendance(uid)
        today_rewards = att.today_rewards

        if today_rewards:
            print(f"🎁 今日【可以】签到，奖励预览:")
            for item in today_rewards:
                name_map = att.resource_info_map.get(item.resource_id, {})
                item_name = name_map.get("name", item.resource_id)
                print(f"   - {item_name}  x{item.count}")
        else:
            print("✅ 今日已完成签到！")

        print(f"\n💡 本月签到日历共计 {len(att.calendar)} 天")
    except Exception as e:
        print(f"❌ 获取签到数据失败: {e}")

    # 完成
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*50}")
    print(f"🎉 数据获取完成！")
    print(f"   原始 JSON → daily_tasks/raw_data/")
    print(f"   gzip 归档 → daily_tasks/archive/{today}/")


if __name__ == '__main__':
    main()
