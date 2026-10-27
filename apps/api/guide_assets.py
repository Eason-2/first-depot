"""Public, explicitly listed lesson images shared by the server and export."""

from pathlib import Path


ASSET_DIR = Path(__file__).with_name("guide_assets")
ASSET_NAMES = frozenset({
    "node-windows-download.webp", "node-macos-download.webp",
    "node-windows-mobile.webp", "node-macos-mobile.webp",
})
ASSET_URL = "/tutorials/assets/"


def handle_guide_asset(path: str, handler) -> bool:
    if not path.startswith(ASSET_URL):
        return False
    name = path[len(ASSET_URL):]
    if name not in ASSET_NAMES:
        handler.send_error(404)
        return True
    try:
        data = (ASSET_DIR / name).read_bytes()
    except FileNotFoundError:
        handler.send_error(404)
        return True
    handler.send_response(200)
    handler.send_header("Content-Type", "image/webp")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "no-cache")
    handler.end_headers()
    handler.wfile.write(data)
    return True
