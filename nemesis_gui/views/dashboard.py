import tkinter as tk
from tkinter import ttk

from ..services.scanner import load_reports, summarize_report
from ..theme import COLORS


class DashboardPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 24))
        ttk.Label(header, text="Workspace", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Your saved assessments and recent network activity.", style="Subtitle.TLabel").pack(anchor="w", pady=(5, 0))

        hero = tk.Frame(self, bg=COLORS["green_dark"], padx=30, pady=28, highlightthickness=1, highlightbackground="#182D4C")
        hero.pack(fill="x", pady=(0, 20))
        hero.columnconfigure(0, weight=1)
        tk.Label(hero, text="NETWORK ASSESSMENT", bg=COLORS["green_dark"], fg=COLORS["lime"], font=("DejaVu Sans", 8, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(hero, text="Understand your exposed surface.", bg=COLORS["green_dark"], fg="#FFFFFF", font=("DejaVu Sans", 20, "bold"), justify="left").grid(row=1, column=0, sticky="w", pady=(9, 6))
        tk.Label(hero, text="Scan one authorized host, review services, and keep findings in one place.", bg=COLORS["green_dark"], fg="#B7C7DC", font=("DejaVu Sans", 10)).grid(row=2, column=0, sticky="w")
        ttk.Button(hero, text="Configure assessment", style="Primary.TButton", command=lambda: self.app.show_page("scan")).grid(row=1, column=1, rowspan=2, padx=(25, 0), sticky="e")

        metrics = ttk.Frame(self)
        metrics.pack(fill="x", pady=(0, 18))
        for column in range(3):
            metrics.columnconfigure(column, weight=1, uniform="metric")
        self.metric_values = {}
        for column, (key, title, accent) in enumerate((
            ("assessments", "REPORTS SAVED", COLORS["green"]),
            ("services", "SERVICES IN LATEST", COLORS["gold"]),
            ("findings", "FINDINGS IN LATEST", COLORS["coral"]),
        )):
            card = tk.Frame(metrics, bg=COLORS["panel"], padx=20, pady=17, highlightthickness=1, highlightbackground=COLORS["line"])
            card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 9, 9 if column < 2 else 0))
            marker = tk.Frame(card, bg=accent, width=4)
            marker.pack(side="left", fill="y", padx=(0, 15))
            value_block = tk.Frame(card, bg=COLORS["panel"])
            value_block.pack(side="left", fill="both", expand=True)
            tk.Label(value_block, text=title, bg=COLORS["panel"], fg=COLORS["muted"], font=("DejaVu Sans", 8, "bold")).pack(anchor="w")
            value = tk.Label(value_block, text="0", bg=COLORS["panel"], fg=COLORS["ink"], font=("DejaVu Sans", 25, "bold"))
            value.pack(anchor="w", pady=(6, 0))
            self.metric_values[key] = value

        lower = ttk.Frame(self)
        lower.pack(fill="both", expand=True)
        lower.columnconfigure(0, weight=3)
        lower.columnconfigure(1, weight=2)
        recent_box = ttk.Frame(lower, style="Panel.TFrame", padding=20)
        recent_box.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        history_box = ttk.Frame(lower, style="Panel.TFrame", padding=20)
        history_box.grid(row=0, column=1, sticky="nsew", padx=(9, 0))
        ttk.Label(recent_box, text="Recent assessments", style="Panel.TLabel", font=("DejaVu Sans", 12, "bold")).pack(anchor="w")
        ttk.Label(recent_box, text="Your latest saved scan reports", style="Muted.TLabel").pack(anchor="w", pady=(4, 13))
        self.recent_tree = ttk.Treeview(recent_box, columns=("target", "services", "date"), show="headings", height=5)
        for column, title, width in (("target", "TARGET", 180), ("services", "SERVICES", 85), ("date", "DATE", 145)):
            self.recent_tree.heading(column, text=title)
            self.recent_tree.column(column, width=width, anchor="w")
        self.recent_tree.pack(fill="both", expand=True)
        self.recent_tree.bind("<Double-1>", lambda _event: self.app.show_page("reports"))

        ttk.Label(history_box, text="Recent targets", style="Panel.TLabel", font=("DejaVu Sans", 12, "bold")).pack(anchor="w")
        ttk.Label(history_box, text="Pick up where you left off", style="Muted.TLabel").pack(anchor="w", pady=(4, 13))
        self.target_list = tk.Listbox(history_box, height=5, bg=COLORS["soft"], fg=COLORS["ink"], selectbackground=COLORS["mint"], selectforeground=COLORS["ink"], relief="flat", highlightthickness=0, font=("DejaVu Sans", 10), activestyle="none")
        self.target_list.pack(fill="both", expand=True)
        self.target_list.bind("<Double-1>", self._use_recent_target)

    def _use_recent_target(self, _event=None):
        selected = self.target_list.curselection()
        if selected:
            self.app.scan_page.set_target(self.target_list.get(selected[0]))
            self.app.show_page("scan")

    def refresh(self):
        reports = load_reports()
        self.recent_tree.delete(*self.recent_tree.get_children())
        for path, report in reports[:8]:
            summary = summarize_report(report)
            timestamp = str(report.get("timestamp", ""))[:10]
            self.recent_tree.insert("", "end", values=(report.get("target", path.stem), summary["services"], timestamp))
        if not reports:
            self.recent_tree.insert("", "end", values=("No saved reports yet", "-", "-"))
            latest = {"services": 0, "findings": 0}
        else:
            latest = summarize_report(reports[0][1])
        self.metric_values["assessments"].configure(text=str(len(reports)))
        self.metric_values["services"].configure(text=str(latest["services"]))
        self.metric_values["findings"].configure(text=str(latest["findings"]))
        self.target_list.delete(0, "end")
        for target in self.app.history.get_recent():
            self.target_list.insert("end", target)