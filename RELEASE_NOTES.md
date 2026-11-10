# Nemesis Scanner GUI 1.3.0

- Redesigned the scan page with simpler navigation, clearer assessment presets, and optional
  settings that stay out of the way until needed.
- Added scan-stage status and elapsed time to make longer scans easier to follow.
- Added an **Install new update** action for supported Windows and Linux installations.
- Added automatic Windows and Linux package builds. The release includes the Windows EXE and ZIP,
  Linux DEB, RPM, Arch package, and AppImage.

## Installation notes

- Windows updates replace the portable EXE and restart the application. Keep it in a folder writable
  by your account.
- Linux package updates request desktop authorization. AppImage updates require the current
  AppImage folder to be writable.
- Nmap remains a separate system requirement for scanning.
