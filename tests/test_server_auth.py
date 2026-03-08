from __future__ import annotations

import unittest

from apps.api.server import is_run_once_authorized, resolve_client_ip


class ServerAuthTests(unittest.TestCase):
    def test_loopback_always_allowed(self) -> None:
        self.assertTrue(is_run_once_authorized("127.0.0.1", None, ""))
        self.assertTrue(is_run_once_authorized("::1", None, ""))

    def test_remote_denied_without_token(self) -> None:
        self.assertFalse(is_run_once_authorized("10.0.0.2", None, ""))

    def test_remote_allowed_with_correct_token(self) -> None:
        self.assertTrue(is_run_once_authorized("10.0.0.2", "abc123", "abc123"))
        self.assertFalse(is_run_once_authorized("10.0.0.2", "abc123", "wrong"))

    def test_cf_connecting_ip_takes_priority(self) -> None:
        resolved = resolve_client_ip("127.0.0.1", {"CF-Connecting-IP": "203.0.113.8"})
        self.assertEqual("203.0.113.8", resolved)

    def test_x_forwarded_for_uses_first_hop(self) -> None:
        resolved = resolve_client_ip("127.0.0.1", {"X-Forwarded-For": "198.51.100.2, 10.0.0.8"})
        self.assertEqual("198.51.100.2", resolved)


if __name__ == "__main__":
    unittest.main()
