import unittest

from nemesis_gui import __version__
from nemesis_gui.services.scanner import flatten_findings, summarize_report, validate_target


class GuiVersionTests(unittest.TestCase):
    def test_gui_has_independent_version(self):
        self.assertEqual(__version__, "0.1.0")


class TargetValidationTests(unittest.TestCase):
    def test_accepts_single_ip_and_hostname(self):
        self.assertTrue(validate_target("192.0.2.10"))
        self.assertTrue(validate_target("scanner.example.org"))
        self.assertTrue(validate_target("2001:db8::1"))

    def test_rejects_ranges_and_multiple_targets(self):
        self.assertFalse(validate_target("192.0.2.0/24"))
        self.assertFalse(validate_target("host.example 192.0.2.1"))
        self.assertFalse(validate_target("bad..host"))


class ReportSummaryTests(unittest.TestCase):
    def test_counts_services_and_findings(self):
        report = {
            "raw_services": [{"port": 80}, {"port": 443}],
            "vulnerabilities": {
                "tcp/80 http": [{"severity": "HIGH"}, {"severity": "LOW"}],
                "tcp/443 https": [{"severity": "CRITICAL"}],
            },
        }
        self.assertEqual(summarize_report(report), {
            "services": 2,
            "findings": 3,
            "critical": 1,
            "high": 1,
        })

    def test_findings_are_flattened_for_the_results_view(self):
        report = {
            "vulnerabilities": {
                "tcp/443 https": [{"severity": "high", "cve": "CVE-2026-1234", "description": "Example finding"}],
            },
        }
        self.assertEqual(flatten_findings(report), [{
            "service": "tcp/443 https",
            "severity": "HIGH",
            "cve": "CVE-2026-1234",
            "description": "Example finding",
        }])


if __name__ == "__main__":
    unittest.main()