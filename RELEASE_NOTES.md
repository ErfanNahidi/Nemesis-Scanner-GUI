# Nemesis Scanner GUI 1.0.0

First stable release of the Nemesis Scanner desktop interface.

The Linux GUI package is named `nemesis-scanner-gui` and installs the `nemesis-scanner-gui`
command. The CLI package keeps the separate `nemesis-scanner` command so both can be installed
side by side.

## Highlights

- Desktop dashboard, single-host network scans and a searchable local JSON report archive.
- Quick, Common and Full TCP scan profiles.
- Optional Nmap vulnerability scripts and active checks for selected services.
- Local vulnerability matching, NVD online lookup, and optional Vulners enrichment.
- Reports, recent-target history and online query cache stored in the user's data directory.
- Linux installers for Fedora-compatible RPM, Debian/Ubuntu DEB, Arch Linux, and a portable
  x86_64 AppImage.
- Windows x64 executable is built and attached by the release workflow after publication.

## Requirements to note

Nmap is a separate system program and must be installed for scans on all platforms. The AppImage
does not install Nmap. Online vulnerability lookup needs internet access; NVD's key is optional,
while Vulners mode requires a Vulners API key.

Use only against hosts you own or have explicit permission to assess. See `MANUAL.md` for full
installation, scan, privacy and troubleshooting instructions. `README-fa.md` contains the Persian
overview.
