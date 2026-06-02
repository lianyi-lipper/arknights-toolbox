# Arknights Toolbox 🎮

明日方舟个人数据工具箱 — 自动获取游戏数据、寻访记录，并生成分析报告。

## 功能

### 📅 每日数据 (`daily_tasks/`)
- 拉取玩家信息（等级/理智/干员/基建等）
- 数据清洗 & 报表导出（CSV/JSON）
- gzip 按日期归档

### 🎰 寻访记录 (`gacha_tasks/`)
- **全自动获取**：Playwright 无头浏览器登录 → 拦截 API → 逐分类翻页
- **追加合并**：每次运行只新增，不重复存储
- **统计分析**：稀有度分布、六星出货间隔（保底计数）、分池统计

### ⏰ 定时任务
- 提供 `run_all.bat` 一键运行所有数据爬取任务
- 支持 Windows 任务计划程序定时执行

## 项目结构

```
arknights-toolbox/
├── daily_tasks/              # 每日数据模块
│   ├── config.json           # 凭证配置（手机号+密码，需从模板复制）
│   ├── config.example.json   # 凭证配置模板
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
└── run_all.bat               # 一键运行脚本
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. 配置凭证

复制 `daily_tasks/config.example.json` 为 `daily_tasks/config.json`，并填入你的手机号和密码：

```json
{
  "phone": "你的手机号",
  "password": "你的密码"
}
```

### 3. 运行

#### 🚀 数据爬取（获取原始数据）

你可以通过手动命令拉取各部分原始数据，或直接双击 `run_all.bat` 一键爬取。**注意：**`run_all.bat` 仅用于自动爬取每日数据和寻访记录的原始 JSON 文件，不包含后续的清洗分析步骤。

```bash
# 一键运行全部原始数据爬取
run_all.bat

# 或者是手动单独执行：
# 获取每日原始数据
python daily_tasks/fetch/get_daily_info.py

# 获取寻访记录原始数据（使用 Playwright 登录）
python gacha_tasks/fetch/get_gacha_records.py
```

#### 📊 数据清洗与分析（生成报表）

在拉取原始数据后，可以手动运行以下脚本生成统计报告和可读的 Excel/CSV 报表：

```bash
# 1. 生成寻访记录分析摘要（报告输出到 gacha_tasks/analyze/reports/）
python gacha_tasks/analyze/gacha_stats.py

# 2. 清洗每日数据（报告输出到 daily_tasks/analyze/reports/）
# 导出干员列表 (cleaned_chars.csv/json)
python daily_tasks/analyze/clean_operator_data.py
# 导出基建排班与心情状态 (cleaned_base_chars.csv/json)
python daily_tasks/analyze/clean_base_data.py
# 导出皮肤记录和进度简报 (cleaned_skins_history.csv, cleaned_progress_report.txt)
python daily_tasks/analyze/clean_records_data.py
```

### 4. 定时任务（可选）

Windows 任务计划程序（请在**管理员权限**下打开 PowerShell 运行该命令，并注意将路径修改为您在本机的**项目实际绝对路径**）：

```powershell
schtasks /create /tn "ArknightsDataFetch" /tr "你的项目实际路径\arknights-toolbox\run_all.bat" /sc daily /st 08:00 /rl highest /f
```

## 致谢

- 森空岛 API SDK 基于 [aynakeya/skland-api](https://github.com/aynakeya/skland-api)