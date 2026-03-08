from __future__ import annotations

import json
import socket
from pathlib import Path


def _local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    runtime = project_root / "runtime"
    port = 8088

    last_run = runtime / "last_run.json"
    tunnel_url = runtime / "public_tunnel_url.txt"

    print("Blog access info:")
    print(f"- Local: http://127.0.0.1:{port}/blog")
    print(f"- LAN:   http://{_local_ip()}:{port}/blog")

    if tunnel_url.exists():
        url = tunnel_url.read_text(encoding="utf-8").strip()
        if url:
            print(f"- Tunnel: {url}/blog")

    if last_run.exists():
        try:
            payload = json.loads(last_run.read_text(encoding="utf-8"))
            print(f"- Last cycle status: {payload.get('status', 'unknown')}")
        except json.JSONDecodeError:
            pass


if __name__ == "__main__":
    main()
