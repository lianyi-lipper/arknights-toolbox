@echo off
chcp 65001 >nul

:: Arknights Toolbox - Auto Run
cd /d "%~dp0"

:: Activate conda
call "C:\ProgramData\miniconda3\Scripts\activate.bat" base

echo.
echo [1/3] Daily data fetch...
python daily_tasks\fetch\get_daily_info.py
if %errorlevel% neq 0 echo FAILED: daily data

echo.
echo [2/3] Gacha records fetch...
python gacha_tasks\fetch\get_gacha_records.py
if %errorlevel% neq 0 echo FAILED: gacha fetch

echo.
echo [3/3] Gacha analysis...
python gacha_tasks\analyze\gacha_stats.py
if %errorlevel% neq 0 echo FAILED: gacha analysis

echo.
echo === All done ===
>> "%~dp0run_log.txt" echo [%date% %time%] run completed
