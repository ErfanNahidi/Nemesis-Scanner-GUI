import asyncio
import unittest
from unittest.mock import patch

from core.core import NemesisScanner, QUICK_TCP, QUICK_UDP


class ScanModeTests(unittest.TestCase):
    def test_quick_mode_uses_fast_common_ports(self):
        scanner = NemesisScanner("127.0.0.1", scan_mode="quick", vuln_check=True)
        port_spec = scanner._build_port_spec()

        self.assertIn(f"T:{','.join(map(str, QUICK_TCP))}", port_spec)
        self.assertIn(f"U:{','.join(map(str, QUICK_UDP))}", port_spec)
        self.assertNotIn("T:1-1000", port_spec)

    def test_quick_mode_keeps_fast_scan_profile(self):
        scanner = NemesisScanner("127.0.0.1", scan_mode="quick", vuln_check=True)
        args = scanner._nmap_arguments()

        self.assertIn("-sV", args)
        self.assertIn("--script vuln", args)
        self.assertIn("-T5", args)
        self.assertNotIn("-p T:1-1000", args)

    def test_online_cve_lookup_is_independent_of_nmap_scripts(self):
        scanner = NemesisScanner(
            "127.0.0.1",
            scan_mode="quick",
            vuln_check=False,
            vuln_source="online",
            cve_lookup=True,
        )

        self.assertTrue(scanner.cve_lookup)
        self.assertNotIn("--script vuln", scanner._nmap_arguments())

    def test_online_correlation_queries_nvd_without_nse_scripts(self):
        scanner = NemesisScanner(
            "127.0.0.1",
            scan_mode="quick",
            vuln_check=False,
            vuln_source="online",
            cve_lookup=True,
        )
        service = {"proto": "tcp", "port": 443, "name": "https", "product": "Example", "version": "1.0"}
        nvd_result = {"cve": "CVE-2026-1234", "description": "Example", "severity": "HIGH"}

        with patch("core.core.lookup_nvd_vulnerabilities", return_value=[nvd_result]) as lookup:
            findings = asyncio.run(scanner._correlate_cves(service))

        lookup.assert_called_once()
        self.assertIn(nvd_result, findings)


if __name__ == "__main__":
    unittest.main()
