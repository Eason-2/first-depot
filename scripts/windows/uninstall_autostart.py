from __future__ import annotations

import os
from pathlib import Path


def _startup_dir() -> Path:
    appdata = Path(os.environ.get("APPDATA", ""))
    if not appdata:
        raise RuntimeError("APPDATA is not available")
    return appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def uninstall_autostart() -> None:
    project_root = Path(__file__).resolve().parents[2]
    startup_entry = _startup_dir() / "AI-Blog-Autostart.cmd"
    launcher = project_root / "runtime" / "autostart_launcher.cmd"

    if startup_entry.exists():
        startup_entry.unlink()
        print(f"Removed: {startup_entry}")
    else:
        print(f"Not found: {startup_entry}")

    if launcher.exists():
        launcher.unlink()
        print(f"Removed: {launcher}")
    else:
        print(f"Not found: {launcher}")


if __name__ == "__main__":
    uninstall_autostart()
