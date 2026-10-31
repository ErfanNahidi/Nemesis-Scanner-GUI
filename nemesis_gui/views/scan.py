import os
import tkinter as tk
from tkinter import ttk

from ..services.scanner import ScanWorker, flatten_findings, summarize_report, validate_target
from ..theme import COLORS


class ScanPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.worker = None
        self._render_generation = 0
        self.target_var = tk.StringVar()
        self.profile_var = tk.StringVar(value="Quick")
        self.source_var = tk.StringVar(value="Local database")
        self.nvd_key_var = tk.StringVar(value=os.environ.get("NVD_API_KEY", ""))
        self.vulners_key_var = tk.StringVar(value=os.environ.get("VULNERS_API_KEY", ""))
        self.vuln_var = tk.BooleanVar(value=False)
        self.deep_var = tk.BooleanVar(value=False)
        self.authorized_var = tk.BooleanVar(value=False)
        self.profile_hint = tk.StringVar()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1, minsize=360)
        self._build()
        self.profile_var.trace_add("write", self._update_profile_hint)
        self.vuln_var.trace_add("write", self._update_source_state)
        self.source_var.trace_add("write", self._update_source_state)
        self.target_var.trace_add("write", self._update_button)
        self.after(120, self._drain_events)

    def _build(self):
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ttk.Label(header, text="Network scan", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Host, port, service, and vulnerability assessment.", style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))

        form = ttk.Frame(self, style="Panel.TFrame", padding=10)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 7))
        form.columnconfigure(0, weight=3)
        form.columnconfigure(1, weight=2)
        ttk.Label(form, text="TARGET HOST / IP", style="Muted.TLabel", font=("DejaVu Sans", 8, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="PORT SCAN PROFILE", style="Muted.TLabel", font=("DejaVu Sans", 8, "bold")).grid(row=0, column=1, sticky="w", padx=(14, 0))
        self.target_entry = ttk.Entry(form, textvariable=self.target_var)
        self.target_entry.grid(row=1, column=0, sticky="ew", pady=(5, 8))
        self.target_entry.bind("<Return>", lambda _event: self._start_scan())
        self.profile_combo = ttk.Combobox(form, textvariable=self.profile_var, values=("Quick", "Common", "Full TCP"), state="readonly", width=17)
        self.profile_combo.grid(row=1, column=1, sticky="ew", padx=(14, 0), pady=(5, 8))
        ttk.Label(form, textvariable=self.profile_hint, style="Muted.TLabel").grid(row=2, column=1, sticky="w", padx=(14, 0), pady=(0, 4))

        options = ttk.Frame(form, style="Panel.TFrame")
        options.grid(row=2, column=0, sticky="ew")
        options.columnconfigure(0, weight=1)
        ttk.Checkbutton(options, text="Run Nmap vulnerability scripts", variable=self.vuln_var).grid(row=0, column=0, sticky="w", pady=4)
        ttk.Checkbutton(options, text="Enable active service checks", variable=self.deep_var).grid(row=1, column=0, sticky="w", pady=4)
        ttk.Label(options, text="VULNERABILITY DATA SOURCE", style="Muted.TLabel", font=("DejaVu Sans", 8, "bold")).grid(row=0, column=1, sticky="e", padx=(10, 7))
        self.source_combo = ttk.Combobox(options, textvariable=self.source_var, values=("Local database", "NVD online", "NVD + Vulners"), state="readonly", width=19)
        self.source_combo.grid(row=1, column=1, sticky="e", padx=(10, 0), pady=4)

        self.api_keys = ttk.Frame(form, style="Panel.TFrame")
        self.api_keys.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.api_keys.columnconfigure(0, weight=1)
        self.api_keys.columnconfigure(1, weight=1)
        ttk.Label(self.api_keys, text="NVD API KEY (OPTIONAL)", style="Muted.TLabel", font=("DejaVu Sans", 8, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(self.api_keys, text="VULNERS API KEY (REQUIRED FOR VULNERS)", style="Muted.TLabel", font=("DejaVu Sans", 8, "bold")).grid(row=0, column=1, sticky="w", padx=(14, 0))
        self.nvd_key_entry = ttk.Entry(self.api_keys, textvariable=self.nvd_key_var, show="•")
        self.nvd_key_entry.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.vulners_key_entry = ttk.Entry(self.api_keys, textvariable=self.vulners_key_var, show="•")
        self.vulners_key_entry.grid(row=1, column=1, sticky="ew", padx=(14, 0), pady=(6, 0))

        consent = tk.Frame(form, bg=COLORS["soft"], padx=8, pady=5)
        consent.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(5, 5))
        tk.Checkbutton(consent, text="I am authorized to assess this host.", variable=self.authorized_var, bg=COLORS["soft"], activebackground=COLORS["soft"], fg=COLORS["ink"], selectcolor=COLORS["mint"], font=("DejaVu Sans", 9, "bold"), command=self._update_button).pack(anchor="w")

        footer = ttk.Frame(form, style="Panel.TFrame")
        footer.grid(row=5, column=0, columnspan=2, sticky="ew")
        footer.columnconfigure(0, weight=1)
        self.status_label = ttk.Label(footer, text="Awaiting scan configuration.", style="Muted.TLabel")
        self.status_label.grid(row=0, column=0, sticky="w")
        self.scan_button = ttk.Button(footer, text="Run scan", style="Primary.TButton", command=self._start_scan)
        self.scan_button.grid(row=0, column=1, sticky="e")
        self._update_button()

        result = ttk.Frame(self, style="Panel.TFrame", padding=12)
        result.grid(row=2, column=0, sticky="nsew")
        result.columnconfigure(0, weight=1)
        result.rowconfigure(2, weight=1)
        title_row = ttk.Frame(result, style="Panel.TFrame")
        title_row.grid(row=0, column=0, sticky="ew")
        title_row.columnconfigure(0, weight=1)
        ttk.Label(title_row, text="Scan results", style="Panel.TLabel", font=("DejaVu Sans", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.result_summary = ttk.Label(title_row, text="No scan results", style="Muted.TLabel")
        self.result_summary.grid(row=0, column=1, sticky="e")
        self.progress = ttk.Progressbar(result, mode="indeterminate", maximum=100)
        self.progress.grid(row=1, column=0, sticky="ew", pady=(13, 12))
        self.progress.grid_remove()
        self.results_tabs = ttk.Notebook(result)
        self.results_tabs.grid(row=2, column=0, sticky="nsew")
        services_tab = ttk.Frame(self.results_tabs, style="Panel.TFrame", padding=(0, 8, 0, 0))
        findings_tab = ttk.Frame(self.results_tabs, style="Panel.TFrame", padding=(0, 8, 0, 0))
        services_tab.columnconfigure(0, weight=1)
        services_tab.rowconfigure(0, weight=1)
        findings_tab.columnconfigure(0, weight=1)
        findings_tab.rowconfigure(0, weight=1)
        self.results_tabs.add(services_tab, text="Detected services")
        self.results_tabs.add(findings_tab, text="Vulnerability findings")
        self.service_tree = ttk.Treeview(services_tab, columns=("port", "service", "product", "version"), show="headings", height=20)
        for column, title, width in (("port", "PORT / PROTOCOL", 130), ("service", "SERVICE", 180), ("product", "PRODUCT", 250), ("version", "VERSION", 180)):
            self.service_tree.heading(column, text=title)
            self.service_tree.column(column, width=width, anchor="w")
        self.service_tree.grid(row=0, column=0, sticky="nsew")
        service_scrollbar = ttk.Scrollbar(services_tab, orient="vertical", command=self.service_tree.yview)
        service_scrollbar.grid(row=0, column=1, sticky="ns")
        self.service_tree.configure(yscrollcommand=service_scrollbar.set)
        self.service_tree.tag_configure("open", foreground=COLORS["green"])
        self.finding_tree = ttk.Treeview(findings_tab, columns=("severity", "service", "cve", "description"), show="headings", height=20)
        for column, title, width in (("severity", "SEVERITY", 110), ("service", "SERVICE / PORT", 210), ("cve", "CVE ID", 130), ("description", "DESCRIPTION", 500)):
            self.finding_tree.heading(column, text=title)
            self.finding_tree.column(column, width=width, anchor="w", stretch=column == "description")
        self.finding_tree.grid(row=0, column=0, sticky="nsew")
        finding_scrollbar = ttk.Scrollbar(findings_tab, orient="vertical", command=self.finding_tree.yview)
        finding_scrollbar.grid(row=0, column=1, sticky="ns")
        self.finding_tree.configure(yscrollcommand=finding_scrollbar.set)
        self.finding_tree.tag_configure("CRITICAL", foreground=COLORS["red"])
        self.finding_tree.tag_configure("HIGH", foreground=COLORS["coral"])
        self.finding_tree.tag_configure("MEDIUM", foreground=COLORS["gold"])
        self.finding_tree.tag_configure("LOW", foreground=COLORS["green"])
        self._update_profile_hint()
        self._update_source_state()

    def set_target(self, target):
        self.target_var.set(target)
        self.target_entry.focus_set()
        self._update_button()

    def _update_button(self, *_args):
        can_scan = self.authorized_var.get() and self.worker is None and validate_target(self.target_var.get())
        self.scan_button.configure(state="normal" if can_scan else "disabled")

    def _update_profile_hint(self, *_args):
        descriptions = {
            "Quick": "Common TCP and UDP ports; optimized for short scans.",
            "Common": "TCP ports 1-1000 and commonly used UDP ports.",
            "Full TCP": "All TCP ports and commonly used UDP ports; longer runtime.",
        }
        self.profile_hint.set(descriptions.get(self.profile_var.get(), "Select a port scan profile."))

    def _update_source_state(self, *_args):
        provider = self.source_var.get()
        if provider == "Local database":
            self.api_keys.grid_remove()
        else:
            self.api_keys.grid()
        self.nvd_key_entry.configure(state="normal" if provider in {"NVD online", "NVD + Vulners"} else "disabled")
        self.vulners_key_entry.configure(state="normal" if provider == "NVD + Vulners" else "disabled")

    def _start_scan(self):
        if self.worker is not None:
            return
        target = self.target_var.get().strip()
        if not validate_target(target):
            self.status_label.configure(text="Enter one valid IP address or hostname.", foreground=COLORS["red"])
            self.target_entry.focus_set()
            return
        if not self.authorized_var.get():
            self.status_label.configure(text="Confirm authorization before scanning this host.", foreground=COLORS["red"])
            return

        mode = {"Quick": "quick", "Common": "common", "Full TCP": "full"}[self.profile_var.get()]
        provider = self.source_var.get()
        if provider == "NVD + Vulners" and not self.vulners_key_var.get().strip():
            self.status_label.configure(text="Provide a Vulners API key or select NVD.", foreground=COLORS["red"])
            self.vulners_key_entry.focus_set()
            return
        source = "offline" if provider == "Local database" else "online"
        vulners_key = self.vulners_key_var.get().strip() if provider == "NVD + Vulners" else ""
        self.worker = ScanWorker(
            target,
            mode,
            self.vuln_var.get(),
            source,
            self.deep_var.get(),
            nvd_api_key=self.nvd_key_var.get().strip(),
            vulners_api_key=vulners_key,
        )
        self.scan_button.configure(state="disabled")
        self.progress.grid()
        self.progress.start(12)
        self.status_label.configure(text=f"Scanning target {target}...", foreground=COLORS["green"])
        self.result_summary.configure(text=f"Data source: {provider}")
        self.worker.start()

    def _drain_events(self):
        worker = self.worker
        if worker is not None:
            while not worker.events.empty():
                event = worker.events.get()
                if event[0] == "status":
                    self.status_label.configure(text=event[1], foreground=COLORS["green"])
                elif event[0] == "error":
                    self.progress.stop()
                    self.progress.grid_remove()
                    self.status_label.configure(text=f"Scan error: {event[1]}", foreground=COLORS["red"])
                    self.result_summary.configure(text="Report not generated")
                    self.worker = None
                    self._update_button()
                    break
                elif event[0] == "complete":
                    _, report, path = event
                    self.progress.stop()
                    self.progress.grid_remove()
                    self._show_report(report)
                    warnings = report.get("provider_warnings", [])
                    if warnings:
                        self.status_label.configure(text=f"Report saved; provider warning: {warnings[0]}", foreground=COLORS["red"])
                    else:
                        self.status_label.configure(text=f"Report saved: {path.name}", foreground=COLORS["green"])
                    self.app.on_scan_complete(report, path)
                    self.worker = None
                    self._update_button()
                    break
        self.after(120, self._drain_events)

    def _show_report(self, report):
        self.service_tree.delete(*self.service_tree.get_children())
        self.finding_tree.delete(*self.finding_tree.get_children())
        services = report.get("raw_services", [])
        findings = flatten_findings(report)
        summary = summarize_report(report)
        self.result_summary.configure(text=f"{summary['services']} services  |  {summary['findings']} findings")
        self.results_tabs.tab(0, text=f"Detected services ({summary['services']})")
        self.results_tabs.tab(1, text=f"Vulnerability findings ({summary['findings']})")
        self._render_generation += 1
        self._insert_result_batch(self._render_generation, services, findings)

    def _insert_result_batch(self, generation, services, findings, service_index=0, finding_index=0):
        if generation != self._render_generation:
            return

        inserted = 0
        batch_size = 200
        while inserted < batch_size and service_index >= 0 and service_index < len(services):
            service = services[service_index]
            self.service_tree.insert(
                "", "end",
                values=(f"{service.get('proto', '').upper()}/{service.get('port', '')}", service.get("name", ""), service.get("product", ""), service.get("version", "")),
                tags=("open",),
            )
            service_index += 1
            inserted += 1
        while inserted < batch_size and finding_index >= 0 and finding_index < len(findings):
            finding = findings[finding_index]
            description = finding["description"].replace("\n", " ")
            self.finding_tree.insert(
                "", "end",
                values=(finding["severity"], finding["service"], finding["cve"], description),
                tags=(finding["severity"],),
            )
            finding_index += 1
            inserted += 1

        if not services and service_index == 0:
            self.service_tree.insert("", "end", values=("No open ports detected", "", "", ""))
            service_index = -1
        if not findings and finding_index == 0:
            self.finding_tree.insert("", "end", values=("No findings detected", "", "", ""))
            finding_index = -1
        if (service_index >= 0 and service_index < len(services)) or (finding_index >= 0 and finding_index < len(findings)):
            self.after_idle(self._insert_result_batch, generation, services, findings, service_index, finding_index)