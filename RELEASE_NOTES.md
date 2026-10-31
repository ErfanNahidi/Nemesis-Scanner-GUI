# Nemesis Scanner GUI 1.1.0

This release adds a desktop authorization flow for Linux scans that need elevated Nmap privileges
and refreshes all Linux installers with that feature.

## What's changed

- Added **Request administrator access for Nmap (Linux)** to the scan form. When selected, the
  system opens its polkit authentication dialog for Nmap.
- Only the Nmap process runs elevated. The GUI and report writing remain under the signed-in user,
  so reports are not saved into root's home directory.
- Added clearer status and error messages when administrator authorization is requested or when
  `pkexec` is unavailable.
- Kept the GUI launcher name `nemesis-scanner-gui`, allowing the GUI to coexist with the CLI
  package and its `nemesis-scanner-cli` command.
- Updated the English and Persian README files and the full manual with the new option and
  installation filenames.

## Linux scan authorization requirements

Elevated scans need `pkexec` and an active polkit authentication agent provided by the desktop
environment. The option is available on Linux only and is optional for scans that work with the
current user's permissions. Nmap remains a separately installed system dependency on all
platforms.

## Installers

- Fedora-compatible RPM
- Debian/Ubuntu DEB
- Arch Linux package
- x86_64 AppImage
- Windows x64 executable (the Linux-specific authorization option is unavailable on Windows)

Use the application only for systems you own or are explicitly authorized to assess. See
`MANUAL.md` for installation, scan settings, report storage, and troubleshooting.
