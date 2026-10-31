# Nemesis Scanner GUI — User Manual

Version 1.0.0

This manual covers installation, the three application screens, scan settings, vulnerability data,
reports, data storage, and common problems. The interface is currently in English.

## 1. What the application does

Nemesis Scanner GUI provides a desktop workflow for examining one host at a time. Nmap identifies
open ports and services. The application can then correlate the discovered service information
with a bundled local vulnerability database or online providers. Completed scans are saved as
JSON reports and can be reviewed or exported later.

The GUI release number (1.0.0) is independent of the scanner engine version. The GUI is not a
general-purpose vulnerability scanner and a reported match is not proof that a host is
exploitable. Verify findings against the affected system and the cited vendor advisories.

## 2. Authorization and safe use

Use the application only against systems you own or are explicitly authorized to assess. A host
name or address must identify a single host; network ranges and CIDR notation are not accepted.
Before a scan starts, the interface requires you to check **I am authorized to assess this host**.
That confirmation is a reminder and does not grant permission by itself.

Scans send network probes to the selected host. Enabling Nmap's vulnerability scripts or active
service checks sends additional requests and may create service logs or affect fragile systems.
Use a short profile first when you are unsure about the host's capacity. Obtain written approval
for production systems and follow the owner's change-control requirements.

## 3. Requirements

### Linux packages

- **DEB:** Debian/Ubuntu systems. Installing the package with the graphical package installer or
  `apt` resolves its declared Python, Tkinter, requests, Pillow, and Nmap dependencies.
- **RPM:** Fedora-compatible x86_64 systems. The RPM includes the Python application runtime and
  libraries, while RPM resolves native library requirements and installs Nmap.
- **Arch:** install the `.pkg.tar.zst` with `pacman -U`; pacman installs the declared Python,
  Tkinter, requests, Pillow, and Nmap dependencies. The small `python-nmap` adapter is included in
  the application package.
- **AppImage:** requires an x86_64 Linux system with compatible native desktop libraries. Nmap is
  not included and must be installed separately.

Linux packages use the native libraries of their target distributions. The Fedora-built RPM and
AppImage are not intended for older Linux releases whose system libraries are incompatible.

### Windows

The Windows EXE bundles Python and the application's Python libraries. Install Nmap for Windows
before scanning. Nmap's packet-capture driver (Npcap) may be required for certain scan types; use
the Nmap installer and follow its driver prompts. The EXE is built by the release workflow when a
GitHub release is published.

### Run from source

Install Python 3.10 or newer, Tkinter, Nmap, and the packages in `requirements.txt`:

```bash
python -m pip install -r requirements.txt
python main.py
```

On Debian/Ubuntu install Tkinter with `python3-tk` if needed; on Fedora, use `python3-tkinter`.
Run the application with the same Python environment used to install its requirements. Do not
start the source application with `sudo python main.py`.

## 4. Installation and first launch

Download the file for your operating system from the repository's [Releases page](https://github.com/ErfanNahidi/Nemesis-Scanner-GUI/releases).

### Windows

1. Download `NemesisScanner.exe` and open it.
2. If Windows SmartScreen prompts you, verify that you downloaded the file from the project's
   release page before choosing whether to continue.
3. Install Nmap separately if it is not already installed.
4. If Nmap reports that a scan needs packet-capture support, install or repair Npcap using the
   official Nmap installer.

### Debian or Ubuntu

Open `nemesis-scanner-gui_1.0.0_all.deb` in the software installer, or run:

```bash
sudo apt install ./nemesis-scanner-gui_1.0.0_all.deb
```

The package manager installs the declared dependencies. Start **Nemesis Scanner** from the
application menu or run `nemesis-scanner-gui`.

### Fedora-compatible Linux

Open `nemesis-scanner-gui-1.0.0-1.x86_64.rpm` in Software, or run:

```bash
sudo dnf install ./nemesis-scanner-gui-1.0.0-1.x86_64.rpm
```

Start the application from the menu or run `nemesis-scanner-gui`.

### Arch Linux

Install the local package:

```bash
sudo pacman -U ./nemesis-scanner-gui-1.0.0-1-any.pkg.tar.zst
```

Start it from the menu or run `nemesis-scanner-gui`. The release also includes `PKGBUILD` and a source
tarball for rebuilding with `makepkg`.

### AppImage

Make the file executable, then launch it:

```bash
chmod +x NemesisScanner-1.0.0-x86_64.AppImage
./NemesisScanner-1.0.0-x86_64.AppImage
```

Install Nmap separately. Depending on the Linux desktop, a compatible FUSE/AppImage runtime may
also be required.

## 5. The application window

The left sidebar opens three pages:

### Dashboard

The dashboard summarizes saved reports, service count and finding count from the latest report. It
also lists recent reports and the five most recently used targets. Double-click a recent target to
put it back in the scan form; double-click a recent report to open the reports page.

### Network scan

This page accepts one host, scan settings and authorization confirmation. When a scan starts, it
runs in a worker thread so the interface remains responsive. The progress bar and status line show
the current stage. The result area has separate **Detected services** and **Vulnerability
findings** tabs.

### Scan reports

The report archive lists reports saved by this application. Select a row to see the target,
timestamp, operating-system estimate, detected services and vulnerability findings. Select
**Export report...** to copy the selected JSON report to a location of your choice.

## 6. Configure a scan

### Target

Enter one IP address (IPv4 or IPv6) or a hostname, for example `192.0.2.10` or `server.example`.
Whitespace, slash notation, ranges and multiple hosts are rejected. Use a hostname only when you
intend to assess the host to which it resolves.

### Port scan profile

| Profile | Ports and behavior | Typical use |
| --- | --- | --- |
| **Quick** | A curated set of commonly used TCP and UDP ports. It uses an aggressive timing template and a shorter host timeout. | Initial, short assessment. |
| **Common** | TCP ports 1–1000 plus a curated set of common UDP ports. Identifies service versions and attempts OS detection. | Broader routine assessment. |
| **Full TCP** | All TCP ports (1–65535) plus common UDP ports. Identifies service versions and attempts OS detection. | Thorough port coverage; can take substantially longer. |

Timing depends on host response, filtering, retries, network conditions and enabled checks. Full
TCP does not mean every UDP port; it scans the application's configured common UDP list.

### Nmap vulnerability scripts

**Run Nmap vulnerability scripts** asks Nmap to run its NSE checks in addition to port/service
discovery. The scripts make additional requests and can lengthen a scan. The selected script set
depends on the profile. This option is independent of the vulnerability data source below: script
results and database/provider matches are different kinds of evidence.

Nmap scripts and data are supplied by the system's Nmap installation, not by the AppImage or
Windows EXE. Keep Nmap updated through the appropriate system installer or package manager.

### Active service checks

**Enable active service checks** runs additional checks against some discovered TCP services. The
checks include basic FTP anonymous-login probing, selected HTTP security-header checks and TLS
certificate/protocol checks. They do not cover every protocol or configuration. A missing finding
does not establish that a service is secure.

### Vulnerability data source

| Source | What it does | Credentials/network |
| --- | --- | --- |
| **Local database** | Matches services against vulnerability information shipped with the application. | No provider key or provider request required. |
| **NVD online** | Queries NIST NVD for matching vulnerability information. | Internet required; NVD API key is optional and can improve rate limits. |
| **NVD + Vulners** | Uses NVD and requests exploit-reference enrichment from Vulners. | Internet required; a Vulners API key is required. An NVD key remains optional. |

Online lookup and Nmap NSE checks are independent. You can use online vulnerability data without
selecting the Nmap vulnerability-script option.

### API keys

The key fields are masked. Keys are used only for the current scan and are not saved in reports or
application settings. `NVD_API_KEY` and `VULNERS_API_KEY` environment variables can prefill the
fields when the application starts. The GUI never displays the full key after entry.

## 7. Read scan results

### Detected services

The table shows protocol/port, service name, product and version when Nmap can identify them. A
blank product or version means the probe did not identify it; it does not mean the service is
absent. Filtered ports and closed ports may not appear as open services.

### Vulnerability findings

Findings include a severity label, associated service, CVE identifier when available, and a short
description. Some active checks do not produce a CVE identifier. Severity is an aid for triage,
not a complete risk rating: business exposure, configuration, reachability, compensating controls
and vendor advisories matter.

A failed online provider may produce a warning while still allowing a report to be saved. Check
the status line and report before treating an empty provider result as confirmation that no
vulnerabilities exist.

## 8. Reports and stored data

Each completed scan is saved as a JSON file. Reports include the target, timestamp, detected
services, OS estimate, vulnerability findings and scan-related metadata. They do not include the
API keys entered in the GUI.

Default user-data location:

- Linux: `~/.local/share/nemesis-scanner/`
- Linux with `XDG_DATA_HOME`: `$XDG_DATA_HOME/nemesis-scanner/`
- Windows: `.local/share/nemesis-scanner` under the current user's home directory unless
  `XDG_DATA_HOME` is set

The `reports/` subdirectory contains JSON reports. `recent_targets.json` stores the recent-target
list. Online query cache files are also stored in this user-data directory. Reports are local
files; protect, back up or delete them according to your organization's data-handling policy.

The application does not upload saved reports. When online providers are selected, service and
product details needed for matching are sent to those providers. Nmap itself communicates with the
target during the scan.

## 9. Troubleshooting

### “Nmap not found” or the scan cannot start

Install Nmap and make sure `nmap` (Windows: `nmap.exe`) is on the system PATH. Close and reopen
the GUI after changing PATH. The Linux AppImage does not bundle Nmap. On Windows, install Nmap and
Npcap using the Nmap installer.

### A scan returns no services

Confirm the address is correct and reachable, inspect host firewalls and network ACLs, and try a
Quick scan before Full TCP. A host that drops probes or permits access only from selected sources
may appear to have no open services. Do not interpret an empty result as proof that the host is
safe.

### OS detection or a scan type needs privileges

Some Nmap probes require raw-packet privileges. The GUI does not elevate itself and should not be
started as root just to bypass this. Use the operating system's approved Nmap permission/capability
setup, or run a profile that works with the current user's permissions. On Windows, check Npcap
installation and driver status.

### Online lookup fails

Confirm Internet access, check the selected provider's API key, and retry later if the provider is
rate-limiting or unavailable. NVD lookup can be used without an API key, but limits may be lower.
Vulners mode requires a Vulners key. The local database remains available offline.

### Reports are missing or cannot be written

Check the user-data directory above and confirm it is writable and has free space. Avoid launching
the GUI with `sudo`, which would save files under a different account and home directory. If
`XDG_DATA_HOME` is customized, look under that location.

### The window or logo does not render correctly

Update the platform's Tk/Tcl packages and graphics drivers. For a source install, confirm that the
Tkinter module is available in the Python environment used to launch the application.

## 10. Uninstall

- Debian/Ubuntu: `sudo apt remove nemesis-scanner-gui`
- Fedora-compatible: `sudo dnf remove nemesis-scanner-gui`
- Arch: `sudo pacman -R nemesis-scanner-gui`
- AppImage: delete the AppImage file.
- Windows: delete the downloaded EXE; the one-file program does not install itself.

Uninstalling does not remove reports or recent-target history in the user's data directory. Delete
that directory yourself if you no longer need the stored data.

## 11. Build from source

- Fedora Linux x86_64: `./build-linux.sh` builds the RPM and AppImage. PyInstaller,
  `rpmbuild`, and `appimagetool` are required. `APPIMAGETOOL` and `APPIMAGE_RUNTIME` can point to
  local AppImage build tools.
- Debian/Arch packages: `./build-deb-arch.sh` builds the DEB, a pacman package archive, a `PKGBUILD`
  and a source tarball. It requires `dpkg-deb`, `tar`, `zstd` and the Python nmap module on the
  build host.
- Windows x64: run `build-windows.ps1` in PowerShell with Python available. The published GitHub
  release workflow runs this script and attaches the resulting EXE.

Generated files are written to `dist/`, which is excluded from Git. Linux binary outputs are tied
to the platform libraries on the build host; distribution packages should be built on their
respective target distributions for the broadest compatibility.
