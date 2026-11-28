@echo off
chcp 65001 > nul
cd /d D:\User\SignalOrNoise\signal-or-noise
if not exist logs mkdir logs
echo ===== %date% %time% ===== >> logs\fetch.log
"C:\Users\PC\.local\bin\uv.exe" run fetch_prices.py >> logs\fetch.log 2>&1