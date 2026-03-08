from __future__ import annotations

import argparse
import os
import secrets
import subprocess
import sys
from pathlib import Path


def _startup_dir() -> Path:
    appdata = Path(os.environ.get("APPDATA", ""))
    if not appdata:
        raise RuntimeError("APPDATA is not available")
    return appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def install_autostart(interval_minutes: int, run_now: bool, enable_tunnel: bool) -> None:
    if interval_minutes < 5:
        raise ValueError("interval_minutes must be >= 5")

    project_root = Path(__file__).resolve().parents[2]
    runtime_dir = project_root / "runtime"
    log_dir = runtime_dir / "logs"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    token_file = runtime_dir / "admin_token.txt"

    python_exe = sys.executable
    launcher = runtime_dir / "autostart_launcher.cmd"
    startup_entry = _startup_dir() / "AI-Blog-Autostart.cmd"
    daemon_log = log_dir / "daemon.log"
    start_line = (
        "powershell -NoProfile -ExecutionPolicy Bypass -Command "
        f"\"Start-Process -WindowStyle Hidden -FilePath '{python_exe}' "
        f"-ArgumentList '-m scripts.daemon' -WorkingDirectory '{project_root}' "
        f"-RedirectStandardOutput '{daemon_log}' -RedirectStandardError '{log_dir / 'daemon.err.log'}'\""
    )
    admin_token = os.getenv("ADMIN_TOKEN", "").strip() or secrets.token_hex(24)
    token_file.write_text(admin_token + "\n", encoding="utf-8")

    launcher.write_text(
        "\n".join(
            [
                "@echo off",
                f"set AUTO_PUBLISH_MODE=auto",
                "set BLOG_HOST=0.0.0.0",
                "set BLOG_PORT=8088",
                f"set SCHEDULE_INTERVAL_MINUTES={interval_minutes}",
                f"set ENABLE_CLOUDFLARE_TUNNEL={'1' if enable_tunnel else '0'}",
                f"set ADMIN_TOKEN={admin_token}",
                f'cd /d "{project_root}"',
                start_line,
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    startup_entry.write_text(
        "\n".join(
            [
                "@echo off",
                f'call "{launcher}"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    if run_now:
        subprocess.Popen(["cmd", "/c", str(launcher)], cwd=str(project_root))

    print("Installed startup autostart:")
    print(f"- Startup entry: {startup_entry}")
    print(f"- Launcher: {launcher}")
    print(f"- Admin token file: {token_file}")
    print(f"- Interval minutes: {interval_minutes}")
    print(f"- Cloudflare tunnel: {'enabled' if enable_tunnel else 'disabled'}")
    print("- On next login, daemon will auto start API + scheduled publishing")


def main() -> None:
    parser = argparse.ArgumentParser(description="Install startup autostart for AI blog daemon.")
    parser.add_argument("--interval", type=int, default=30, help="Run cycle every N minutes (>=5), default 30")
    parser.add_argument("--run-now", action="store_true", help="Start daemon immediately")
    parser.add_argument("--enable-tunnel", action="store_true", help="Also start cloudflared quick tunnel")
    args = parser.parse_args()

    install_autostart(interval_minutes=args.interval, run_now=args.run_now, enable_tunnel=args.enable_tunnel)


if __name__ == "__main__":
    main()
