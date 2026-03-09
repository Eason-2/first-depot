@echo off
set AUTO_PUBLISH_MODE=auto
cd /d "C:\Users\32025\projects\ai-blog-autopublisher"
"C:\Users\32025\python-sdk\python3.13.2\python.exe" -m scripts.run_once >> "C:\Users\32025\projects\ai-blog-autopublisher\runtime\logs\run_cycle.log" 2>&1
