# Nemesis Scanner GUI 0.1.0

The GUI is version 0.1.0, a modular Tkinter desktop application that uses the scanner engine in `core/`.
The GUI release number is independent of the scanner engine version.
The branded sidebar loads `logo.png` or `Logo.png` from this directory.
It keeps scan work off the UI thread, stores JSON reports under `reports/`, and reuses the
recent-target history service.

## Run

Install the system Nmap binary and the Python dependencies, then run from this directory:

```bash
python -m pip install -r requirements.txt
python main.py
````

Run both commands with the same Python environment that installed the dependencies. Do not use
`sudo python main.py`; it can select a different system Python with missing packages.

Tkinter is included with most Python desktop distributions. Linux distributions may package it
separately as `python3-tk`.

Only scan a single host you own or are explicitly authorized to assess. The GUI requires an
authorization confirmation before starting a scan.

## CVE Providers

- `Local database` uses the bundled offline vulnerability data.
- `NVD online` queries the NVD API; an API key is optional but recommended for higher rate limits.
- `NVD + Vulners` queries NVD and enriches CVEs with Vulners exploit references. A Vulners API key is required.

Online CVE matching is independent from the Nmap vulnerability-script option. API keys entered in
the GUI are masked and used for the current scan only; they are not saved to reports or settings.
You can prefill them with `NVD_API_KEY` and `VULNERS_API_KEY` environment variables. Provider
request failures are shown in the scan status and included in the JSON report.