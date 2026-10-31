# Nemesis Scanner GUI

[برای زبان فارسی اینجا کلیک کنید](README-fa.md)

Nemesis Scanner is a desktop interface for assessing one authorized host at a time. It uses Nmap
to discover ports and services, can correlate findings with local or online vulnerability data,
and saves each completed assessment as a JSON report.

The GUI release version is **1.0.0**. It is independent of the scanner engine version.

## Install

Download an asset from the [GitHub Releases page](https://github.com/ErfanNahidi/Nemesis-Scanner-GUI/releases).

| Platform | Asset | Install / run |
| --- | --- | --- |
| Windows x64 | `NemesisScanner.exe` | Download and open. Install Nmap separately for scans. |
| Fedora-compatible Linux x86_64 | `nemesis-scanner-gui-1.0.0-1.x86_64.rpm` | Open in Software, or run `sudo dnf install ./nemesis-scanner-gui-1.0.0-1.x86_64.rpm`. |
| Debian or Ubuntu | `nemesis-scanner-gui_1.0.0_all.deb` | Open in the package installer, or run `sudo apt install ./nemesis-scanner-gui_1.0.0_all.deb`. |
| Arch Linux | `nemesis-scanner-gui-1.0.0-1-any.pkg.tar.zst` | Run `sudo pacman -U ./nemesis-scanner-gui-1.0.0-1-any.pkg.tar.zst`. |
| Portable Linux x86_64 | `NemesisScanner-1.0.0-x86_64.AppImage` | Mark executable, then open it. Nmap must be installed on the host. |

On Linux, launch the GUI with `nemesis-scanner-gui`; the CLI keeps the separate `nemesis-scanner` command. The DEB and Arch packages use the platform's Python/Tk libraries and let `apt` or `pacman`
install declared dependencies. The Windows executable bundles Python and the GUI's Python
libraries. Nmap is a separate system program and is required for scanning on every platform.

## Start from source

Install Python 3.10 or newer, Tkinter, Nmap, and the Python requirements, then run:

```bash
python -m pip install -r requirements.txt
python main.py
```

On Debian/Ubuntu, Tkinter may need to be installed as `python3-tk`; on Fedora it is commonly
provided by `python3-tkinter`. Use the same Python environment for installation and launch. Do not
launch the source application with `sudo python main.py`.

## First scan

1. Open **Network scan**.
2. Enter one IPv4 address, IPv6 address, or hostname.
3. Choose **Quick**, **Common**, or **Full TCP**.
4. Select optional Nmap vulnerability scripts, active service checks, and a vulnerability data
   source as needed.
5. Confirm that you are authorized to assess the host, then select **Run scan**.
6. Review detected services and findings. Completed scans appear in **Scan reports** and on the
   dashboard.

Only scan systems you own or have explicit permission to assess. See [MANUAL.md](MANUAL.md) for
installation details, scan options, report handling, API keys, privacy, and troubleshooting.

## Build packages

On Fedora x86_64, install PyInstaller, `rpmbuild`, and `appimagetool`, then run
`./build-linux.sh`. To build the DEB and Arch packages, run `./build-deb-arch.sh` on a system with
`dpkg-deb`, `tar`, and `zstd`. Run `build-windows.ps1` on Windows to make the single-file EXE.
Build outputs go into `dist/` and are excluded from Git.

Linux binary packages are built on Fedora 44 and use the system's native libraries. Use the DEB
on Debian-family systems and the Arch package on Arch Linux; those packages use the target
distribution's Python and native libraries.

## Data and privacy

Reports, recent-target history, and online vulnerability caches are stored in the user's data
directory:

- Linux: `~/.local/share/nemesis-scanner/` (or `$XDG_DATA_HOME/nemesis-scanner/`)
- Windows: the path selected by the `XDG_DATA_HOME` setting, otherwise `~/.local/share` under the
  Windows user profile

Reports contain the target, detected services, timestamps, and vulnerability findings. API keys
are masked in the interface and are used for the current scan only; they are not written to a
report or application settings. `NVD_API_KEY` and `VULNERS_API_KEY` can prefill the key fields.

Online lookups send service/product information to NVD and, when selected, Vulners. The local
database option does not need those online providers. Network scans still contact the target
directly through Nmap.
