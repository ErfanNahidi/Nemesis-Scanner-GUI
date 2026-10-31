import os
import platform
import shutil
import subprocess
import tkinter as tk
from pathlib import Path
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
        ttk.Label(header, text="Scan reports", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Review and export stored host scan reports.", style="Subtitle.TLabel").pack(anchor="w", pady=(5, 0))

        body = ttk.Frame(self)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=3)
        body.rowconfigure(0, weight=1)
        list_panel = ttk.Frame(body, style="Panel.TFrame", padding=15)
        list_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        detail_panel = ttk.Frame(body, style="Panel.TFrame", padding=17)
        detail_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ttk.Label(list_panel, text="REPORT ARCHIVE", style="Muted.TLabel", font=("DejaVu Sans", 8, "bold")).pack(anchor="w", pady=(0, 10))
        self.tree = ttk.Treeview(list_panel, columns=("target", "date"), show="headings", height=14)
        self.tree.heading("target", text="TARGET")
        self.tree.heading("date", text="DATE")
        self.tree.column("target", width=180, anchor="w")
        self.tree.column("date", width=130, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._select_report)
        ttk.Button(list_panel, text="Export report...", style="Secondary.TButton", command=self._export).pack(anchor="w", pady=(12, 0))

        detail_panel.columnconfigure(0, weight=1)
        detail_panel.rowconfigure(2, weight=1)
        self.detail_title = ttk.Label(detail_panel, text="Select a report", style="Panel.TLabel", font=("DejaVu Sans", 14, "bold"))
        self.detail_title.grid(row=0, column=0, sticky="w")
        self.detail_subtitle = ttk.Label(detail_panel, text="Report metadata and findings are displayed here.", style="Muted.TLabel")
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
        lines = ["DETECTED SERVICES"]
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
            messagebox.showinfo("Export report", "Select a report to export.", parent=self)
            return
        report_path = self.selected_path
        documents = Path.home() / "Documents"
        initial_file = documents / report_path.name if documents.is_dir() else Path.home() / report_path.name
        desktop = " ".join((os.environ.get("XDG_CURRENT_DESKTOP", ""), os.environ.get("DESKTOP_SESSION", ""))).lower()

        destination = None
        chooser_opened = False
        if platform.system() == "Linux":
            if "kde" in desktop:
                chooser_order = ("kdialog", "zenity")
            elif "gnome" in desktop:
                chooser_order = ("zenity", "kdialog")
            else:
                chooser_order = ("kdialog", "zenity")

            for chooser in chooser_order:
                executable = shutil.which(chooser)
                if not executable:
                    continue
                if chooser == "kdialog":
                    command = [executable, "--title", "Export scan report", "--getsavefilename", str(initial_file), "JSON reports (*.json)"]
                else:
                    command = [
                        executable, "--file-selection", "--save", "--confirm-overwrite",
                        f"--filename={initial_file}", "--title=Export scan report",
                        "--file-filter=JSON reports | *.json",
                    ]
                try:
                    result = subprocess.run(command, capture_output=True, text=True, check=False)
                except OSError:
                    continue
                chooser_opened = True
                if result.returncode == 0 and result.stdout.strip():
                    destination = result.stdout.strip()
                break

        if destination is None and platform.system() != "Linux":
            destination = filedialog.asksaveasfilename(
                parent=self,
                title="Export report",
                initialfile=report_path.name,
                initialdir=str(initial_file.parent),
                defaultextension=".json",
                filetypes=(("JSON report", "*.json"),),
            )
        elif destination is None and not chooser_opened:
            destination = filedialog.asksaveasfilename(
                parent=self,
                title="Export report",
                initialfile=report_path.name,
                initialdir=str(initial_file.parent),
                defaultextension=".json",
                filetypes=(("JSON report", "*.json"),),
            )

        if destination:
            try:
                shutil.copy2(report_path, destination)
            except OSError as error:
                messagebox.showerror("Export report", f"Could not export the report:\n{error}", parent=self)
            else:
                self.detail_subtitle.configure(text=f"Report exported to {destination}")
