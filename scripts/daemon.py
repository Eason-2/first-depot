from __future__ import annotations

import os
import re
import subprocess
import threading
import time
from pathlib import Path

from apps.api.server import run_api_server
from core.config import Settings
from scripts.git_auto_sync import sync_from_env
from workers.publishing.scheduler import AutopublishScheduler


def _write_tunnel_error(err_file: Path, message: str) -> None:
    err_file.write_text(message.rstrip() + "\n", encoding="utf-8")


def _run_cloudflare_tunnel(project_root: Path, api_port: int) -> None:
    runtime_dir = project_root / "runtime"
    log_dir = runtime_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "tunnel.log"
    url_file = runtime_dir / "public_tunnel_url.txt"
    err_file = runtime_dir / "public_tunnel_error.txt"

    if url_file.exists():
        url_file.unlink()
    if err_file.exists():
        err_file.unlink()

    local_cloudflared = runtime_dir / "tools" / "cloudflared.exe"
    cloudflared_cmd = str(local_cloudflared) if local_cloudflared.exists() else "cloudflared"

    tunnel_token = os.getenv("CLOUDFLARE_TUNNEL_TOKEN", "").strip()
    public_base_url = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")
    is_named_tunnel = bool(tunnel_token)

    if is_named_tunnel:
        cmd = [
            cloudflared_cmd,
            "tunnel",
            "--no-autoupdate",
            "run",
            "--token",
            tunnel_token,
        ]
        if public_base_url:
            url_file.write_text(public_base_url + "\n", encoding="utf-8")
    else:
        cmd = [
            cloudflared_cmd,
            "tunnel",
            "--url",
            f"http://127.0.0.1:{api_port}",
            "--no-autoupdate",
        ]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(project_root),
        )
    except FileNotFoundError:
        _write_tunnel_error(
            err_file,
            "cloudflared not found. Install cloudflared and restart daemon with ENABLE_CLOUDFLARE_TUNNEL=1.",
        )
        return
    except OSError as exc:
        _write_tunnel_error(
            err_file,
            f"Failed to start cloudflared ({cloudflared_cmd}): {exc}. Reinstall cloudflared and restart daemon.",
        )
        return

    pattern = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com", re.IGNORECASE)
    found_url = False

    with log_path.open("a", encoding="utf-8") as logf:
        for line in proc.stdout or []:
            logf.write(line)
            if not is_named_tunnel:
                match = pattern.search(line)
                if match and not found_url:
                    found_url = True
                    url_file.write_text(match.group(0) + "\n", encoding="utf-8")

    return_code = proc.wait()
    if return_code != 0:
        message = f"cloudflared exited with code {return_code}. See runtime/logs/tunnel.log for details."
        if is_named_tunnel and not public_base_url:
            message += " Set PUBLIC_BASE_URL so tools can show your fixed blog URL."
        if (not is_named_tunnel) and (not found_url):
            _write_tunnel_error(err_file, message)
        elif is_named_tunnel:
            _write_tunnel_error(err_file, message)


def _run_git_sync_loop(project_root: Path, interval_seconds: int) -> None:
    runtime_dir = project_root / "runtime"
    log_dir = runtime_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "git_sync.log"

    while True:
        changed, detail = sync_from_env(project_root)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with log_path.open("a", encoding="utf-8") as logf:
            logf.write(f"[{timestamp}] changed={str(changed).lower()} detail={detail}\n")
        time.sleep(max(30, interval_seconds))


def main() -> None:
    os.environ.setdefault("AUTO_PUBLISH_MODE", "auto")
    settings = Settings.from_env()

    api_thread = threading.Thread(
        target=run_api_server,
        kwargs={"host": settings.api_host, "port": settings.api_port},
        daemon=True,
    )
    api_thread.start()

    if os.getenv("ENABLE_CLOUDFLARE_TUNNEL", "0").strip() == "1":
        tunnel_thread = threading.Thread(
            target=_run_cloudflare_tunnel,
            kwargs={"project_root": settings.project_root, "api_port": settings.api_port},
            daemon=True,
        )
        tunnel_thread.start()

    if os.getenv("ENABLE_GIT_AUTO_SYNC", "0").strip() == "1":
        try:
            sync_interval_seconds = int(os.getenv("GIT_SYNC_INTERVAL_SECONDS", "120"))
        except ValueError:
            sync_interval_seconds = 120
        sync_thread = threading.Thread(
            target=_run_git_sync_loop,
            kwargs={"project_root": settings.project_root, "interval_seconds": sync_interval_seconds},
            daemon=True,
        )
        sync_thread.start()

    scheduler = AutopublishScheduler(settings)
    scheduler.run_forever(max_items_per_source=10)


if __name__ == "__main__":
    main()
