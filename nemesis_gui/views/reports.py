import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from ..services.scanner import load_reports, summarize_report
from ..theme import COLORS


class ReportsPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.reports = []
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 19))
        ttk.Label(header, text="Report library", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Browse and export saved assessment results.", style="Subtitle.TLabel").pack(anchor="w", pady=(5, 0))

        body = ttk.Frame(self)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=3)
        body.rowconfigure(0, weight=1)
        list_panel = ttk.Frame(body, style="Panel.TFrame", padding=15)
        list_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        detail_panel = ttk.Frame(body, style="Panel.TFrame", padding=17)
        detail_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ttk.Label(list_panel, text="SAVED REPORTS", style="Muted.TLabel", font=("DejaVu Sans", 8, "bold")).pack(anchor="w", pady=(0, 10))
        self.tree = ttk.Treeview(list_panel, columns=("target", "date"), show="headings", height=14)
        self.tree.heading("target", text="TARGET")
        self.tree.heading("date", text="DATE")
        self.tree.column("target", width=180, anchor="w")
        self.tree.column("date", width=130, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._select_report)
        ttk.Button(list_panel, text="Export selected report", style="Secondary.TButton", command=self._export).pack(anchor="w", pady=(12, 0))

        detail_panel.columnconfigure(0, weight=1)
        detail_panel.rowconfigure(2, weight=1)
        self.detail_title = ttk.Label(detail_panel, text="Select a report", style="Panel.TLabel", font=("DejaVu Sans", 14, "bold"))
        self.detail_title.grid(row=0, column=0, sticky="w")
        self.detail_subtitle = ttk.Label(detail_panel, text="Assessment details will appear here.", style="Muted.TLabel")
        self.detail_subtitle.grid(row=1, column=0, sticky="w", pady=(5, 12))
        self.detail_text = tk.Text(detail_panel, wrap="word", bg=COLORS["soft"], fg=COLORS["ink"], relief="flat", padx=12, pady=12, font=("DejaVu Sans", 9), state="disabled")
        self.detail_text.grid(row=2, column=0, sticky="nsew")
        self.selected_path = None
        self.refresh()

    def refresh(self):
        self.reports = load_reports()
        self.tree.delete(*self.tree.get_children())
        for index, (path, report) in enumerate(self.reports):
            self.tree.insert("", "end", iid=str(index), values=(report.get("target", path.stem), str(report.get("timestamp", ""))[:10]))
        self.selected_path = None

    def _select_report(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        path, report = self.reports[int(selected[0])]
        self.selected_path = path
        summary = summarize_report(report)
        self.detail_title.configure(text=report.get("target", "Unknown target"))
        self.detail_subtitle.configure(text=f"{report.get('os', 'Unknown OS')}    |    {report.get('timestamp', '')[:19].replace('T', ' ')}    |    {summary['services']} services    |    {summary['findings']} findings")
        lines = ["OPEN SERVICES"]
        lines.extend(f"  {service}" for service in report.get("services", []))
        lines.extend(("", "VULNERABILITY FINDINGS"))
        vulnerabilities = report.get("vulnerabilities", {})
        if vulnerabilities:
            for service, findings in vulnerabilities.items():
                lines.append(f"\n{service}")
                for finding in findings:
                    severity = finding.get("severity", "UNKNOWN").upper()
                    cve = finding.get("cve", "")
                    suffix = f" ({cve})" if cve else ""
                    lines.append(f"  [{severity}]{suffix} {finding.get('description', '')}")
        else:
            lines.append("  No vulnerability findings in this report.")
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", "\n".join(lines))
        self.detail_text.configure(state="disabled")

    def _export(self):
        if not self.selected_path:
            messagebox.showinfo("Export report", "Select a report first.", parent=self)
            return
        destination = filedialog.asksaveasfilename(
            parent=self,
            title="Export report",
            initialfile=self.selected_path.name,
            defaultextension=".json",
            filetypes=(("JSON report", "*.json"),),
        )
        if destination:
            shutil.copy2(self.selected_path, destination)