@echo off
set AUTO_PUBLISH_MODE=auto
set BLOG_HOST=0.0.0.0
set BLOG_PORT=8088
set SCHEDULE_INTERVAL_MINUTES=30
set ENABLE_CLOUDFLARE_TUNNEL=1
set ADMIN_TOKEN=1991f9147c45ec0824696843387008ffc38d85bbe0c836cb
cd /d "C:\Users\32025\projects\ai-blog-autopublisher"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -WindowStyle Hidden -FilePath 'C:\Users\32025\python-sdk\python3.13.2\python.exe' -ArgumentList '-m scripts.daemon' -WorkingDirectory 'C:\Users\32025\projects\ai-blog-autopublisher' -RedirectStandardOutput 'C:\Users\32025\projects\ai-blog-autopublisher\runtime\logs\daemon.log' -RedirectStandardError 'C:\Users\32025\projects\ai-blog-autopublisher\runtime\logs\daemon.err.log'"
