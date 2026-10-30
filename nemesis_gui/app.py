import shutil
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from core.history import RecentTargetStore

from . import __version__
from .theme import COLORS, apply_theme
from .views.dashboard import DashboardPage
from .views.reports import ReportsPage
from .views.scan import ScanPage


class NemesisApp(tk.Tk):
    def __init__(self):
        super().__init__()
        apply_theme(self)
        self.title(f"Nemesis Scanner GUI {__version__}")
        self.geometry("1440x920")
        self.minsize(1120, 740)
        self.logo_image = None
        self.history = RecentTargetStore()
        self.current_page = None
        self._build_shell()
        self.show_page("dashboard")

    def _build_shell(self):
        shell = tk.Frame(self, bg=COLORS["canvas"])
        shell.pack(fill="both", expand=True)
        sidebar = tk.Frame(shell, bg=COLORS["green_dark"], width=250, padx=20, pady=22)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=COLORS["green_dark"])
        brand.pack(fill="x", pady=(0, 40))
        gui_root = Path(__file__).resolve().parents[1]
        logo_path = next((gui_root / name for name in ("Logo.png", "logo.png") if (gui_root / name).is_file()), None)
        try:
            if logo_path:
                source_image = tk.PhotoImage(file=str(logo_path))
                sample = max(1, (max(source_image.width(), source_image.height()) + 87) // 88)
                self.logo_image = source_image.subsample(sample, sample)
                tk.Label(brand, image=self.logo_image, bg=COLORS["green_dark"], bd=0).pack(side="left", padx=(0, 12))
            else:
                raise tk.TclError("Logo.png not found")
        except tk.TclError:
            tk.Label(brand, text="N", bg=COLORS["green"], fg="#FFFFFF", width=3, height=2, font=("DejaVu Sans", 14, "bold")).pack(side="left", padx=(0, 12))
        brand_copy = tk.Frame(brand, bg=COLORS["green_dark"])
        brand_copy.pack(side="left", anchor="center")
        tk.Label(brand_copy, text="NEMESIS", bg=COLORS["green_dark"], fg="#FFFFFF", font=("DejaVu Sans", 13, "bold")).pack(anchor="w")
        tk.Label(brand_copy, text=f"SCANNER  /  GUI {__version__}", bg=COLORS["green_dark"], fg="#A5B6CE", font=("DejaVu Sans", 7, "bold")).pack(anchor="w", pady=(3, 0))

        tk.Label(sidebar, text="WORKSPACE", bg=COLORS["green_dark"], fg="#8798B1", font=("DejaVu Sans", 8, "bold")).pack(anchor="w", pady=(0, 10))
        self.nav_buttons = {}
        self.nav_rows = {}
        for key, label in (("dashboard", "Overview"), ("scan", "New assessment"), ("reports", "Report library")):
            row = tk.Frame(sidebar, bg=COLORS["green_dark"])
            row.pack(fill="x", pady=2)
            indicator = tk.Frame(row, bg=COLORS["green_dark"], width=3)
            indicator.pack(side="left", fill="y", padx=(0, 7))
            button = tk.Button(
                row,
                text=label,
                anchor="w",
                bg=COLORS["green_dark"],
                fg="#D4DFD9",
                activebackground="#142949",
                activeforeground="#FFFFFF",
                relief="flat",
                padx=13,
                pady=13,
                font=("DejaVu Sans", 10, "bold"),
                command=lambda page=key: self.show_page(page),
            )
            button.pack(side="left", fill="x", expand=True)
            self.nav_buttons[key] = button
            self.nav_rows[key] = (row, indicator)

        spacer = tk.Frame(sidebar, bg=COLORS["green_dark"])
        spacer.pack(fill="both", expand=True)
        tk.Frame(sidebar, bg="#243650", height=1).pack(fill="x", pady=(8, 15))
        nmap_state = "Nmap ready" if shutil.which("nmap") else "Nmap not found"
        state_color = COLORS["lime"] if shutil.which("nmap") else "#F1A78C"
        tk.Label(sidebar, text="LOCAL ENGINE", bg=COLORS["green_dark"], fg="#8798B1", font=("DejaVu Sans", 8, "bold")).pack(anchor="w")
        tk.Label(sidebar, text=f"●  {nmap_state}", bg=COLORS["green_dark"], fg=state_color, font=("DejaVu Sans", 9)).pack(anchor="w", pady=(7, 0))

        main = tk.Frame(shell, bg=COLORS["canvas"])
        main.pack(side="left", fill="both", expand=True)
        topbar = tk.Frame(main, bg=COLORS["panel"], height=66, padx=34, highlightthickness=1, highlightbackground=COLORS["line"])
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        self.page_title = tk.Label(topbar, text="Overview", bg=COLORS["panel"], fg=COLORS["ink"], font=("DejaVu Sans", 10, "bold"))
        self.page_title.pack(side="left", anchor="center")
        tk.Label(topbar, text="LOCAL WORKSPACE   /   AUTHORIZED SCOPE", bg=COLORS["panel"], fg=COLORS["muted"], font=("DejaVu Sans", 8, "bold")).pack(side="right", anchor="center")
        self.status_bar = tk.Label(main, text="Ready", bg=COLORS["canvas"], fg=COLORS["muted"], anchor="w", padx=34, pady=10, font=("DejaVu Sans", 8))
        self.status_bar.pack(side="bottom", fill="x")
        self.content = ttk.Frame(main, padding=(34, 28, 34, 12))
        self.content.pack(fill="both", expand=True)
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        self.pages = {
            "dashboard": DashboardPage(self.content, self),
            "scan": ScanPage(self.content, self),
            "reports": ReportsPage(self.content),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")
            page.grid_remove()
        self.scan_page = self.pages["scan"]

    def show_page(self, name):
        if self.current_page:
            self.current_page.grid_remove()
        self.current_page = self.pages[name]
        self.current_page.grid()
        self.current_page.tkraise()
        self.page_title.configure(text={"dashboard": "Overview", "scan": "New assessment", "reports": "Report library"}[name])
        for key, button in self.nav_buttons.items():
            active = key == name
            color = "#142949" if active else COLORS["green_dark"]
            button.configure(bg=color, fg="#FFFFFF" if active else "#D4DFD9")
            row, indicator = self.nav_rows[key]
            row.configure(bg=color)
            indicator.configure(bg=COLORS["lime"] if active else COLORS["green_dark"])
        refresh = getattr(self.current_page, "refresh", None)
        if refresh:
            refresh()

    def on_scan_complete(self, report, path):
        self.history.add_target(report["target"], source="gui")
        self.status_bar.configure(text=f"Saved {path.name}  |  {len(report.get('raw_services', []))} open services")
        self.pages["dashboard"].refresh()
        self.pages["reports"].refresh()