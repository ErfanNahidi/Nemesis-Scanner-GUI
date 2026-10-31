import queue
import threading
import tkinter as tk
import webbrowser
from tkinter import ttk

from .. import __version__
from ..services.updater import (
    download_release_asset,
    fetch_latest_release,
    recommended_asset_name,
    reveal_in_file_manager,
    version_tuple,
)
from ..theme import COLORS


class UpdatesPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.release = None
        self.selected_asset = None
        self.downloaded_path = None
        self.events = queue.Queue()
        self.columnconfigure(0, weight=1)
        self._build()
        self.after(120, self._process_events)

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 18))
        ttk.Label(header, text="Updates", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Check for a published version and download the installer for this computer.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(5, 0))

        developer = tk.Frame(self, bg=COLORS["green_dark"], padx=20, pady=15)
        developer.pack(fill="x", pady=(0, 14))
        credit = tk.Frame(developer, bg=COLORS["green_dark"])
        credit.pack(side="left", anchor="w")
        tk.Label(
            credit,
            text="DEVELOPED BY",
            bg=COLORS["green_dark"],
            fg=COLORS["lime"],
            font=("DejaVu Sans", 8, "bold"),
        ).pack(anchor="w")
        tk.Label(
            credit,
            text="Erfan Nahidi",
            bg=COLORS["green_dark"],
            fg="#FFFFFF",
            font=("DejaVu Sans", 16, "bold"),
        ).pack(anchor="w", pady=(2, 0))
        github_link = tk.Label(
            credit,
            text="GitHub  ·  ErfanNahidi",
            bg=COLORS["green_dark"],
            fg=COLORS["lime"],
            cursor="hand2",
            font=("DejaVu Sans", 10, "underline"),
        )
        github_link.pack(anchor="w", pady=(4, 0))
        github_link.bind("<Button-1>", lambda _event: webbrowser.open("https://github.com/ErfanNahidi"))

        version_card = ttk.Frame(self, style="Panel.TFrame", padding=20)
        version_card.pack(fill="x", pady=(0, 14))
        version_card.columnconfigure(1, weight=1)
        ttk.Label(version_card, text="INSTALLED VERSION", style="Muted.TLabel", font=("DejaVu Sans", 8, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(version_card, text=__version__, style="Panel.TLabel", font=("DejaVu Sans", 18, "bold")).grid(row=1, column=0, sticky="w", pady=(3, 0))
        self.latest_label = ttk.Label(version_card, text="Latest version: not checked", style="Muted.TLabel")
        self.latest_label.grid(row=1, column=1, sticky="e", padx=(20, 0))

        self.status_label = ttk.Label(self, text="Check GitHub to see whether a newer release is available.", style="Subtitle.TLabel", wraplength=700)
        self.status_label.pack(fill="x", pady=(0, 12))

        controls = ttk.Frame(self, style="Panel.TFrame", padding=18)
        controls.pack(fill="x", pady=(0, 14))
        controls.columnconfigure(0, weight=1)
        ttk.Label(controls, text="Update file for this system", style="Panel.TLabel", font=("DejaVu Sans", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.asset_box = ttk.Combobox(controls, state="readonly", values=())
        self.asset_box.grid(row=1, column=0, sticky="ew", pady=(9, 12))
        self.asset_box.bind("<<ComboboxSelected>>", self._asset_selected)
        actions = ttk.Frame(controls, style="Panel.TFrame")
        actions.grid(row=2, column=0, sticky="ew")
        self.check_button = ttk.Button(actions, text="Check for updates", style="Primary.TButton", command=self._check)
        self.check_button.pack(side="left")
        self.download_button = ttk.Button(actions, text="Download update", style="Secondary.TButton", command=self._download, state="disabled")
        self.download_button.pack(side="left", padx=(9, 0))
        self.release_button = ttk.Button(actions, text="Release details", style="Secondary.TButton", command=self._open_release, state="disabled")
        self.release_button.pack(side="left", padx=(9, 0))
        self.folder_button = ttk.Button(actions, text="Show downloaded file", style="Secondary.TButton", command=self._reveal_download, state="disabled")
        self.folder_button.pack(side="left", padx=(9, 0))

        self.progress = ttk.Progressbar(self, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(0, 14))

        notes = ttk.Frame(self, style="Panel.TFrame", padding=18)
        notes.pack(fill="both", expand=True, pady=(0, 14))
        ttk.Label(notes, text="RELEASE NOTES", style="Muted.TLabel", font=("DejaVu Sans", 8, "bold")).pack(anchor="w")
        self.notes_label = ttk.Label(notes, text="Release information will appear here after checking for updates.", style="Muted.TLabel", wraplength=700, justify="left")
        self.notes_label.pack(fill="both", expand=True, anchor="nw", pady=(9, 0))

    def _check(self):
        self._set_busy(True, "Checking GitHub for the latest stable release…")
        threading.Thread(target=self._check_worker, daemon=True).start()

    def _check_worker(self):
        try:
            release = fetch_latest_release()
            self.events.put(("check_done", release))
        except Exception as error:
            self.events.put(("error", f"Could not check for updates: {error}"))

    def _download(self):
        if not self.selected_asset:
            return
        asset = self.selected_asset
        self.folder_button.configure(state="disabled")
        self._set_busy(True, f"Downloading {asset['name']}…")
        self.progress.configure(mode="determinate", value=0)
        threading.Thread(target=self._download_worker, args=(asset,), daemon=True).start()

    def _download_worker(self, asset):
        try:
            path = download_release_asset(asset, lambda received, total: self.events.put(("progress", received, total)))
            self.events.put(("download_done", path))
        except Exception as error:
            self.events.put(("error", f"Download failed: {error}"))

    def _process_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]
                if kind == "check_done":
                    self._show_release(event[1])
                elif kind == "progress":
                    _, received, total = event
                    if total:
                        self.progress.configure(value=min(100, received * 100 / total))
                        self.status_label.configure(text=f"Downloading update… {received / 1048576:.1f} / {total / 1048576:.1f} MB")
                    else:
                        self.status_label.configure(text=f"Downloading update… {received / 1048576:.1f} MB")
                elif kind == "download_done":
                    self.downloaded_path = event[1]
                    self._set_busy(False, f"Update downloaded to {self.downloaded_path}")
                    self.folder_button.configure(state="normal")
                    self.progress.configure(value=100)
                elif kind == "error":
                    self._set_busy(False, event[1])
                    if self.release and self.selected_asset:
                        self.download_button.configure(state="normal")
                self.events.task_done()
        except queue.Empty:
            pass
        self.after(120, self._process_events)

    def _show_release(self, release):
        self.release = release
        latest = release["version"]
        self.latest_label.configure(text=f"Latest version: {latest}")
        current_tuple = version_tuple(__version__)
        latest_tuple = version_tuple(latest)
        if latest_tuple > current_tuple:
            message = f"Version {latest} is available. Choose the matching file and download it below."
        elif latest_tuple == current_tuple:
            message = "You are using the latest published version."
        else:
            message = f"This build ({__version__}) is newer than the latest public release ({latest})."
        self.status_label.configure(text=message)

        assets = release.get("assets", [])
        names = [asset["name"] for asset in assets]
        self.asset_box.configure(values=names)
        recommended = recommended_asset_name(assets)
        if recommended:
            self.asset_box.set(recommended)
            self.selected_asset = next(asset for asset in assets if asset["name"] == recommended)
        elif names:
            self.asset_box.set(names[0])
            self.selected_asset = assets[0]
        else:
            self.asset_box.set("No downloadable files were attached to this release")
            self.selected_asset = None

        notes = (release.get("body") or "No release notes were provided.").strip()
        if len(notes) > 1400:
            notes = notes[:1397].rstrip() + "…"
        self.notes_label.configure(text=notes)
        self.release_button.configure(state="normal")
        may_download = latest_tuple > current_tuple and self.selected_asset is not None
        self.download_button.configure(state="normal" if may_download else "disabled")
        self._set_busy(False, message)

    def _asset_selected(self, _event=None):
        if self.release:
            name = self.asset_box.get()
            self.selected_asset = next((asset for asset in self.release["assets"] if asset["name"] == name), None)
            can_download = bool(self.selected_asset and version_tuple(self.release["version"]) > version_tuple(__version__))
            self.download_button.configure(state="normal" if can_download else "disabled")

    def _open_release(self):
        if self.release:
            webbrowser.open(self.release.get("html_url", "https://github.com/ErfanNahidi/Nemesis-Scanner-GUI/releases"))

    def _reveal_download(self):
        if self.downloaded_path:
            try:
                reveal_in_file_manager(self.downloaded_path)
            except Exception as error:
                self.status_label.configure(text=f"Could not open the download folder: {error}")

    def _set_busy(self, busy, message):
        self.status_label.configure(text=message)
        self.check_button.configure(state="disabled" if busy else "normal")
        if busy:
            self.download_button.configure(state="disabled")
            self.progress.configure(mode="indeterminate")
            self.progress.start(12)
        else:
            self.progress.stop()
            self.progress.configure(mode="determinate")
