from __future__ import annotations

import argparse
import subprocess

RULE_NAME = "AI Blog Public 8088"


def _run(cmd: list[str], tolerate_error: bool = False) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0 and not tolerate_error:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{out}")
    return out.strip()


def open_port(port: int) -> None:
    _run(
        [
            "netsh",
            "advfirewall",
            "firewall",
            "add",
            "rule",
            f"name={RULE_NAME}",
            "dir=in",
            "action=allow",
            "protocol=TCP",
            f"localport={port}",
        ]
    )
    print(f"Opened Windows Firewall inbound TCP port {port} ({RULE_NAME}).")


def close_port() -> None:
    _run(
        [
            "netsh",
            "advfirewall",
            "firewall",
            "delete",
            "rule",
            f"name={RULE_NAME}",
        ],
        tolerate_error=True,
    )
    print(f"Removed firewall rule: {RULE_NAME}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Open or close Windows Firewall port for blog service")
    parser.add_argument("action", choices=["open", "close"], help="open or close rule")
    parser.add_argument("--port", type=int, default=8088, help="TCP port, default 8088")
    args = parser.parse_args()

    if args.action == "open":
        open_port(args.port)
    else:
        close_port()


if __name__ == "__main__":
    main()
