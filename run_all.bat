@echo off
chcp 65001 >nul
echo ============================================
echo   明日方舟数据自动获取 - %date% %time%
echo ============================================

:: 设置工作目录为脚本所在目录
cd /d "%~dp0"

:: 激活 conda 环境
call "C:\ProgramData\miniconda3\Scripts\activate.bat" base

echo.
echo [1/3] 获取每日数据（森空岛）...
python daily_tasks\fetch\get_daily_info.py
if %errorlevel% neq 0 (
    echo ❌ 每日数据获取失败
) else (
    echo ✅ 每日数据获取成功
)

echo.
echo [2/3] 获取寻访记录...
python gacha_tasks\fetch\get_gacha_records.py
if %errorlevel% neq 0 (
    echo ❌ 寻访记录获取失败
) else (
    echo ✅ 寻访记录获取成功
)

echo.
echo [3/3] 生成寻访分析报告...
python gacha_tasks\analyze\gacha_stats.py
if %errorlevel% neq 0 (
    echo ❌ 分析报告生成失败
) else (
    echo ✅ 分析报告生成成功
)

echo.
echo ============================================
echo   全部完成 - %time%
echo ============================================

:: 将日志追加到文件
>> "%~dp0\run_log.txt" echo [%date% %time%] 自动运行完成
