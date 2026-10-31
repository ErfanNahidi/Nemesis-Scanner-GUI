from tkinter import ttk


COLORS = {
    "canvas": "#EAF0F6",
    "panel": "#FFFFFF",
    "ink": "#101828",
    "muted": "#66758A",
    "green": "#2563EB",
    "green_dark": "#101B2D",
    "mint": "#DBEAFE",
    "lime": "#22D3EE",
    "coral": "#E17654",
    "gold": "#B7791F",
    "line": "#D7E0EB",
    "soft": "#F4F7FB",
    "red": "#C83B45",
    "blue_light": "#EFF6FF",
    "blue_line": "#C7DAF4",
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
    style.configure("TEntry", padding=(12, 10), fieldbackground=COLORS["panel"], foreground=COLORS["ink"], bordercolor=COLORS["line"])
    style.map("TEntry", bordercolor=[("focus", COLORS["green"])])
    style.configure(
        "TCombobox",
        padding=(10, 9),
        fieldbackground=COLORS["panel"],
        foreground=COLORS["ink"],
        background=COLORS["soft"],
        bordercolor=COLORS["line"],
        lightcolor=COLORS["line"],
        darkcolor=COLORS["line"],
        arrowcolor=COLORS["muted"],
        relief="flat",
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", COLORS["panel"]), ("disabled", COLORS["soft"])],
        foreground=[("readonly", COLORS["ink"]), ("disabled", COLORS["muted"])],
        selectbackground=[("readonly", COLORS["panel"])],
        selectforeground=[("readonly", COLORS["ink"])],
        background=[("active", COLORS["blue_light"])],
        arrowcolor=[("disabled", COLORS["muted"])],
    )
    root.option_add("*TCombobox*Listbox.background", COLORS["panel"])
    root.option_add("*TCombobox*Listbox.foreground", COLORS["ink"])
    root.option_add("*TCombobox*Listbox.selectBackground", COLORS["green"])
    root.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")
    root.option_add("*TCombobox*Listbox.font", ("DejaVu Sans", 9))
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
    style.map("Secondary.TButton", background=[("active", "#C7DDFF")])
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
