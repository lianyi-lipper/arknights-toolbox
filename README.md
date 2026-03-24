# Arknights Toolbox 🎮

明日方舟个人数据工具箱 — 自动获取游戏数据、寻访记录，并生成分析报告。

## 功能

### 📅 每日数据 (`daily_tasks/`)
- 自动签到 & 获取签到日历
- 拉取玩家信息（等级/理智/干员/基建）
- 数据清洗 & 报表导出（CSV/JSON）
- gzip 按日期归档

### 🎰 寻访记录 (`gacha_tasks/`)
- **全自动获取**：Playwright 无头浏览器登录 → 拦截 API → 逐分类翻页
- **追加合并**：每次运行只新增，不重复存储
- **统计分析**：稀有度分布、六星出货间隔（保底计数）、分池统计

### ⏰ 定时任务
- 提供 `run_all.bat` 一键运行所有任务
- 支持 Windows 任务计划程序定时执行

## 项目结构

```
arknights-toolbox/
├── daily_tasks/              # 每日数据模块
│   ├── config.json           # 凭证配置（手机号+密码）
│   ├── fetch/                # 数据获取
│   │   └── get_daily_info.py
│   ├── analyze/              # 数据分析
│   │   ├── clean_operator_data.py
│   │   ├── clean_base_data.py
│   │   ├── clean_records_data.py
│   │   └── reports/
│   ├── raw_data/             # 原始 JSON
│   └── archive/              # gzip 归档
├── gacha_tasks/              # 寻访记录模块
│   ├── fetch/
│   │   └── get_gacha_records.py
│   ├── analyze/
│   │   ├── gacha_stats.py
│   │   └── reports/
│   └── raw_data/             # 追加式存储
├── skland/                   # 森空岛 API SDK
├── run_all.bat               # 一键运行脚本
└── pyproject.toml
```

## 快速开始

### 1. 安装依赖

```bash
pip install httpx playwright
python -m playwright install chromium
```

### 2. 配置凭证

编辑 `daily_tasks/config.json`：

```json
{
  "phone": "你的手机号",
  "password": "你的密码"
}
```

### 3. 运行

```bash
# 获取每日数据
python daily_tasks/fetch/get_daily_info.py

# 获取寻访记录
python gacha_tasks/fetch/get_gacha_records.py

# 生成寻访分析报告
python gacha_tasks/analyze/gacha_stats.py

# 或者一键运行全部
run_all.bat
```

### 4. 定时任务（可选）

Windows 任务计划程序（管理员 PowerShell）：

```powershell
schtasks /create /tn "ArknightsDataFetch" /tr "C:\work\skland-api\run_all.bat" /sc daily /st 08:00 /rl highest /f
```

## 致谢

- 森空岛 API SDK 基于 [xxyz30/skland-api](https://github.com/xxyz30/skland-api)