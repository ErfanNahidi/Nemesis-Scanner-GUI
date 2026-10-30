from tkinter import ttk


COLORS = {
    "canvas": "#F3F5F7",
    "panel": "#FFFFFF",
    "ink": "#17233B",
    "muted": "#738096",
    "green": "#1267D6",
    "green_dark": "#07152B",
    "mint": "#E2EEFF",
    "lime": "#56C8F2",
    "coral": "#D66A4A",
    "gold": "#C78B24",
    "line": "#DEE5EF",
    "soft": "#F5F7FA",
    "red": "#C64949",
    "blue_light": "#F0F6FF",
    "blue_line": "#D7E6FB",
}


def apply_theme(root):
    root.configure(background=COLORS["canvas"])
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background=COLORS["canvas"])
    style.configure("Panel.TFrame", background=COLORS["panel"])
    style.configure("TLabel", background=COLORS["canvas"], foreground=COLORS["ink"], font=("DejaVu Sans", 10))
    style.configure("Panel.TLabel", background=COLORS["panel"], foreground=COLORS["ink"])
    style.configure("Muted.TLabel", background=COLORS["panel"], foreground=COLORS["muted"])
    style.configure("Title.TLabel", font=("DejaVu Sans", 24, "bold"), foreground=COLORS["ink"])
    style.configure("Subtitle.TLabel", font=("DejaVu Sans", 10), foreground=COLORS["muted"])
    style.configure("Metric.TLabel", font=("DejaVu Sans", 25, "bold"), foreground=COLORS["ink"])
    style.configure("TEntry", padding=(12, 10), fieldbackground=COLORS["soft"], bordercolor=COLORS["line"])
    style.map("TEntry", bordercolor=[("focus", COLORS["green"])])
    style.configure("TCombobox", padding=(10, 9), fieldbackground=COLORS["soft"], bordercolor=COLORS["line"])
    style.configure("TCheckbutton", background=COLORS["panel"], foreground=COLORS["ink"], font=("DejaVu Sans", 10))
    style.configure("TNotebook", background=COLORS["panel"], borderwidth=0, tabmargins=(0, 0, 0, 0))
    style.configure("TNotebook.Tab", background=COLORS["soft"], foreground=COLORS["muted"], padding=(17, 11), font=("DejaVu Sans", 9, "bold"))
    style.map("TNotebook.Tab", background=[("selected", COLORS["panel"])], foreground=[("selected", COLORS["green"])])
    style.configure(
        "Primary.TButton",
        background=COLORS["green"],
        foreground="#FFFFFF",
        padding=(18, 12),
        font=("DejaVu Sans", 10, "bold"),
        borderwidth=0,
    )
    style.map("Primary.TButton", background=[("active", "#0D55B8"), ("disabled", "#AAB6C7")])
    style.configure(
        "Secondary.TButton",
        background=COLORS["mint"],
        foreground=COLORS["green_dark"],
        padding=(13, 9),
        borderwidth=0,
    )
    style.map("Secondary.TButton", background=[("active", "#C9E0D3")])
    style.configure(
        "Treeview",
        background=COLORS["panel"],
        fieldbackground=COLORS["panel"],
        foreground=COLORS["ink"],
        rowheight=34,
        borderwidth=0,
        font=("DejaVu Sans", 9),
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["soft"],
        foreground=COLORS["muted"],
        font=("DejaVu Sans", 9, "bold"),
        padding=(8, 8),
        relief="flat",
    )
    style.map("Treeview", background=[("selected", COLORS["mint"])], foreground=[("selected", COLORS["ink"])])