from __future__ import annotations

import hashlib
import os
import subprocess
import urllib.request
from pathlib import Path

CLOUDFLARED_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
MIN_BINARY_SIZE_BYTES = 5 * 1024 * 1024


def _validate_binary(target: Path) -> str:
    result = subprocess.run(
        [str(target), "--version"],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    output = (result.stdout or result.stderr).strip()
    if result.returncode != 0:
        raise RuntimeError(f"cloudflared validation failed with code {result.returncode}: {output}")
    if not output:
        raise RuntimeError("cloudflared validation did not return version output")
    return output.splitlines()[0]


def install_cloudflared() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    target = project_root / "runtime" / "tools" / "cloudflared.exe"
    tmp_target = target.with_suffix(".download")
    target.parent.mkdir(parents=True, exist_ok=True)

    sha256 = hashlib.sha256()
    total_size = 0

    with urllib.request.urlopen(CLOUDFLARED_URL, timeout=120) as resp, tmp_target.open("wb") as out:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
            sha256.update(chunk)
            total_size += len(chunk)

    if total_size < MIN_BINARY_SIZE_BYTES:
        tmp_target.unlink(missing_ok=True)
        raise RuntimeError(
            f"Downloaded file is unexpectedly small ({total_size} bytes). Please retry with stable network."
        )

    os.replace(tmp_target, target)
    version_line = _validate_binary(target)

    print(f"Installed cloudflared to: {target}")
    print(f"size_bytes: {total_size}")
    print(f"sha256: {sha256.hexdigest()}")
    print(f"version: {version_line}")
    print("Restart daemon to apply tunnel support.")
    return target


if __name__ == "__main__":
    install_cloudflared()
