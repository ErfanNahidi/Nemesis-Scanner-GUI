# Nemesis Scanner GUI 1.2.0

This release improves scan cancellation and reliability, refreshes the desktop interface, and uses
native file selection dialogs when exporting reports.

## What's changed

- Added a working **Cancel scan** action that stops the active Nmap process and discards incomplete
  scan results.
- Improved Nmap process handling, output parsing, and cancellation behavior, including Linux
  administrator-authorized scans.
- Updated scan presets and bounded HTTP response-header reads to avoid unnecessary delays.
- Replaced the dated cream-colored controls with a cooler blue-gray palette and clearer comboboxes.
- Report export now opens the desktop's native file chooser: KDE's picker on KDE, GNOME's picker on
  GNOME, and the platform-native Tk dialog on Windows and macOS.
- Refreshed the English and Persian installation instructions and the complete user manual.
- Prepared release packaging for Fedora/RPM, Debian/Ubuntu, Arch Linux, AppImage, and Windows x64.

## Platform notes

Nmap remains a system dependency. Install Nmap separately before scanning; on Windows, install it
with the official Nmap installer, which can also provide Npcap for scan types that need it. On
Linux, package managers install the declared Nmap dependency. AppImage users need Nmap installed on
the host.

Linux scans that need raw packet access can request desktop administrator authorization. Only the
Nmap process is elevated; the GUI and report files remain under the signed-in user.

## Downloads

Choose the installer for your operating system from the GitHub release assets. See `README.md` for
quick installation and `MANUAL.md` for detailed setup and usage instructions.
