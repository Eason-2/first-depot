from __future__ import annotations

import argparse
import subprocess

TASKS = ["AI-Blog-API-OnLogon", "AI-Blog-RunCycle"]


def _run(cmd: list[str], tolerate_error: bool = False) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0 and not tolerate_error:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{out}")
    return out.strip()


def uninstall_tasks() -> None:
    for task in TASKS:
        _run(["schtasks", "/Delete", "/TN", task, "/F"], tolerate_error=True)
        print(f"Removed (if existed): {task}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Uninstall Windows tasks for auto blog operations.")
    _ = parser.parse_args()
    uninstall_tasks()


if __name__ == "__main__":
    main()
