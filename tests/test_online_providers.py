import unittest
from unittest.mock import Mock, patch

from core.vulnerability.online import fetch_nvd_keyword, search_exploits_vulners


class OnlineProviderTests(unittest.TestCase):
    @patch("core.vulnerability.online.requests.get")
    def test_nvd_query_uses_key_and_maps_results(self, request_get):
        response = Mock()
        response.json.return_value = {
            "vulnerabilities": [{
                "cve": {
                    "id": "CVE-2026-1234",
                    "descriptions": [{"lang": "en", "value": "Example issue"}],
                    "metrics": {},
                    "references": [],
                },
            }],
        }
        request_get.return_value = response

        results = fetch_nvd_keyword("example-product-unique-test", api_key="test-nvd-key")

        self.assertEqual(results[0]["cve"], "CVE-2026-1234")
        self.assertEqual(results[0]["description"], "Example issue")
        self.assertEqual(request_get.call_args.kwargs["headers"], {"apiKey": "test-nvd-key"})

    @patch("core.vulnerability.online.requests.post")
    def test_vulners_query_uses_key_and_returns_exploits(self, request_post):
        response = Mock()
        response.json.return_value = {"data": {"search": [{"title": "Example", "href": "https://example.test/advisory"}]}}
        request_post.return_value = response

        results = search_exploits_vulners("CVE-2026-1234", api_key="test-vulners-key")

        self.assertEqual(results[0]["title"], "Example")
        self.assertEqual(request_post.call_args.kwargs["json"]["apiKey"], "test-vulners-key")


if __name__ == "__main__":
    unittest.main()