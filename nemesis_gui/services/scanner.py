import asyncio
import ipaddress
import json
import logging
import os
import re
import threading
from datetime import datetime
from pathlib import Path
from queue import Queue


REPORTS_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "nemesis-scanner" / "reports"


def validate_target(value):
    target = str(value or "").strip()
    if not target or len(target) > 253 or "/" in target or any(char.isspace() for char in target):
        return False
    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        pass
    if not re.fullmatch(r"[A-Za-z0-9.-]+", target):
        return False
    labels = target.rstrip(".").split(".")
    return all(
        label and len(label) <= 63
        and re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", label)
        for label in labels
    )


def summarize_report(report):
    vulnerabilities = report.get("vulnerabilities", {})
    all_findings = [finding for entries in vulnerabilities.values() for finding in entries]
    return {
        "services": len(report.get("raw_services", [])),
        "findings": len(all_findings),
        "critical": sum(finding.get("severity", "").upper() == "CRITICAL" for finding in all_findings),
        "high": sum(finding.get("severity", "").upper() == "HIGH" for finding in all_findings),
    }


def flatten_findings(report):
    findings = []
    for service, entries in report.get("vulnerabilities", {}).items():
        for entry in entries:
            findings.append({
                "service": service,
                "severity": str(entry.get("severity", "UNKNOWN")).upper(),
                "cve": entry.get("cve", ""),
                "description": entry.get("description", ""),
            })
    return findings


def load_reports():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    reports = []
    for path in REPORTS_DIR.glob("*.json"):
        try:
            with path.open("r", encoding="utf-8") as report_file:
                data = json.load(report_file)
            if isinstance(data, dict) and "target" in data:
                reports.append((path, data))
        except (OSError, json.JSONDecodeError):
            continue
    return sorted(reports, key=lambda item: item[1].get("timestamp", ""), reverse=True)


class ScanWorker(threading.Thread):
    def __init__(self, target, scan_mode, vuln_check, vuln_source, deep_inspect, nvd_api_key="", vulners_api_key=""):
        super().__init__(daemon=True)
        self.target = target
        self.scan_mode = scan_mode
        self.vuln_check = vuln_check
        self.vuln_source = vuln_source
        self.deep_inspect = deep_inspect
        self.nvd_api_key = nvd_api_key
        self.vulners_api_key = vulners_api_key
        self.events = Queue()

    def run(self):
        provider_warnings = []

        class ProviderWarningHandler(logging.Handler):
            def emit(self, record):
                message = record.getMessage()
                if "lookup failed" in message.lower():
                    provider_warnings.append(message)

        warning_handler = ProviderWarningHandler(level=logging.WARNING)
        scanner_logger = logging.getLogger("NemesisScanner")
        scanner_logger.addHandler(warning_handler)
        try:
            from core.core import NemesisScanner

            provider_names = "NVD" if self.vuln_source == "online" else "local vulnerability database"
            if self.vulners_api_key and self.vuln_source == "online":
                provider_names += " + Vulners"
            self.events.put(("status", f"Scanning and querying {provider_names}..."))
            scanner = NemesisScanner(
                self.target,
                scan_mode=self.scan_mode,
                vuln_check=self.vuln_check,
                vuln_source=self.vuln_source,
                deep_inspect=self.deep_inspect,
                nvd_api_key=self.nvd_api_key or None,
                vulners_api_key=self.vulners_api_key or None,
                cve_lookup=self.vuln_source == "online",
            )
            report = asyncio.run(scanner.full_analysis())
            if report is None:
                raise RuntimeError("The target did not return a scan report. Check reachability and Nmap output.")
            if provider_warnings:
                report["provider_warnings"] = list(dict.fromkeys(provider_warnings))

            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_target = re.sub(r"[^A-Za-z0-9_.-]+", "_", self.target)
            report_path = REPORTS_DIR / f"{safe_target}_{stamp}.json"
            with report_path.open("w", encoding="utf-8") as report_file:
                json.dump(report, report_file, indent=2, ensure_ascii=False)
                report_file.write("\n")
            self.events.put(("complete", report, report_path))
        except Exception as error:
            self.events.put(("error", str(error)))
        finally:
            scanner_logger.removeHandler(warning_handler)
