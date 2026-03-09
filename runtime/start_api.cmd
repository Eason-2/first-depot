@echo off
cd /d "C:\Users\32025\projects\ai-blog-autopublisher"
"C:\Users\32025\python-sdk\python3.13.2\python.exe" -m scripts.start_api >> "C:\Users\32025\projects\ai-blog-autopublisher\runtime\logs\api.log" 2>&1
