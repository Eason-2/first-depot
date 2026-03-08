from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

TASK_API = "AI-Blog-API-OnLogon"
TASK_CYCLE = "AI-Blog-RunCycle"


def _run(cmd: list[str], tolerate_error: bool = False) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0 and not tolerate_error:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{out}")
    return out.strip()


def _write_wrapper_scripts(project_root: Path, python_exe: str) -> tuple[Path, Path]:
    runtime_dir = project_root / "runtime"
    log_dir = runtime_dir / "logs"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    api_cmd = runtime_dir / "start_api.cmd"
    cycle_cmd = runtime_dir / "run_cycle.cmd"

    api_cmd.write_text(
        "\n".join(
            [
                "@echo off",
                "set BLOG_HOST=0.0.0.0",
                "set BLOG_PORT=8088",
                f'cd /d "{project_root}"',
                f'"{python_exe}" -m scripts.start_api >> "{log_dir / "api.log"}" 2>&1',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    cycle_cmd.write_text(
        "\n".join(
            [
                "@echo off",
                "set AUTO_PUBLISH_MODE=auto",
                "set BLOG_HOST=0.0.0.0",
                "set BLOG_PORT=8088",
                f'cd /d "{project_root}"',
                f'"{python_exe}" -m scripts.run_once >> "{log_dir / "run_cycle.log"}" 2>&1',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return api_cmd, cycle_cmd


def install_tasks(interval_minutes: int, run_now: bool) -> None:
    if interval_minutes < 5:
        raise ValueError("interval_minutes must be >= 5")

    project_root = Path(__file__).resolve().parents[2]
    python_exe = sys.executable

    api_cmd, cycle_cmd = _write_wrapper_scripts(project_root, python_exe)
    api_task_cmd = f'cmd.exe /c "{api_cmd}"'
    cycle_task_cmd = f'cmd.exe /c "{cycle_cmd}"'

    _run([
        "schtasks",
        "/Create",
        "/TN",
        TASK_API,
        "/SC",
        "ONLOGON",
        "/TR",
        api_task_cmd,
        "/RL",
        "LIMITED",
        "/F",
    ])

    _run([
        "schtasks",
        "/Create",
        "/TN",
        TASK_CYCLE,
        "/SC",
        "MINUTE",
        "/MO",
        str(interval_minutes),
        "/TR",
        cycle_task_cmd,
        "/RL",
        "LIMITED",
        "/F",
    ])

    if run_now:
        _run(["schtasks", "/Run", "/TN", TASK_CYCLE], tolerate_error=True)
        _run(["schtasks", "/Run", "/TN", TASK_API], tolerate_error=True)

    print("Installed scheduled tasks:")
    print(f"- {TASK_API} (on logon)")
    print(f"- {TASK_CYCLE} (every {interval_minutes} minutes)")
    print(f"- API wrapper: {api_cmd}")
    print(f"- Cycle wrapper: {cycle_cmd}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Windows tasks for auto blog operations.")
    parser.add_argument("--interval", type=int, default=30, help="Run cycle every N minutes (>=5), default 30")
    parser.add_argument("--run-now", action="store_true", help="Run both tasks immediately after install")
    args = parser.parse_args()

    install_tasks(interval_minutes=args.interval, run_now=args.run_now)


if __name__ == "__main__":
    main()
