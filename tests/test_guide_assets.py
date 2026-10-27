from __future__ import annotations

import io
import unittest

from apps.api.guide_assets import ASSET_DIR, ASSET_NAMES, handle_guide_asset


class FakeHandler:
    def __init__(self):
        self.status = None
        self.headers = {}
        self.wfile = io.BytesIO()

    def send_error(self, status):
        self.status = status

    def send_response(self, status):
        self.status = status

    def send_header(self, key, value):
        self.headers[key] = value

    def end_headers(self):
        pass


class GuideAssetTests(unittest.TestCase):
    def test_public_images_are_served_as_images(self):
        for name in ASSET_NAMES:
            handler = FakeHandler()
            self.assertTrue(handle_guide_asset('/tutorials/assets/' + name, handler))
            self.assertEqual(handler.status, 200)
            self.assertEqual(handler.headers['Content-Type'], 'image/webp')
            self.assertEqual(handler.wfile.getvalue(), (ASSET_DIR / name).read_bytes())
            self.assertEqual(handler.wfile.getvalue()[8:12], b'WEBP')

    def test_asset_route_never_serves_unlisted_or_parent_files(self):
        for name in ('../server.py', '%2e%2e/server.py', 'SOURCES.md', 'missing.webp'):
            handler = FakeHandler()
            self.assertTrue(handle_guide_asset('/tutorials/assets/' + name, handler))
            self.assertEqual(handler.status, 404)
            self.assertEqual(handler.wfile.getvalue(), b'')
        self.assertFalse(handle_guide_asset('/tutorials/', FakeHandler()))
