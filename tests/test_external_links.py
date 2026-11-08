"""No-network regression tests for the external documentation URL checker."""

import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from scripts.check_external_links import probe


class ExternalLinkTests(unittest.TestCase):
    def setUp(self):
        self.item = {"id": "example", "url": "https://example.org/docs"}

    @staticmethod
    def fake_response():
        response = MagicMock()
        response.__enter__.return_value.status = 200
        response.__enter__.return_value.url = "https://example.org/docs"
        return response

    @staticmethod
    def http_error(code):
        return urllib.error.HTTPError(
            "https://example.org/docs", code, "Test response", {}, None
        )

    def test_ok_on_head(self):
        with patch("scripts.check_external_links.urllib.request.urlopen",
                   return_value=self.fake_response()) as mocked:
            self.assertEqual(probe(self.item)[1], "ok")
        self.assertEqual(mocked.call_count, 1)
        self.assertEqual(mocked.call_args.args[0].get_method(), "HEAD")

    def test_retry_get_after_head_404(self):
        with patch("scripts.check_external_links.urllib.request.urlopen",
                   side_effect=[self.http_error(404), self.fake_response()]) as mocked:
            self.assertEqual(probe(self.item)[1], "ok")
        self.assertEqual(mocked.call_count, 2)
        self.assertEqual(mocked.call_args.args[0].get_method(), "GET")

    def test_broken_only_after_get_confirms_404(self):
        with patch("scripts.check_external_links.urllib.request.urlopen",
                   side_effect=[self.http_error(404), self.http_error(404)]):
            self.assertEqual(probe(self.item)[1], "broken")

    def test_429_means_manual_review(self):
        with patch("scripts.check_external_links.urllib.request.urlopen",
                   side_effect=self.http_error(429)) as mocked:
            self.assertEqual(probe(self.item)[1], "review")
        self.assertEqual(mocked.call_count, 1)

    def test_head_network_error_can_fall_back_to_get(self):
        with patch("scripts.check_external_links.urllib.request.urlopen",
                   side_effect=[urllib.error.URLError("HEAD blocked"),
                                self.fake_response()]):
            self.assertEqual(probe(self.item)[1], "ok")


if __name__ == "__main__":
    unittest.main()
