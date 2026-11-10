# Nemesis Scanner GUI 1.3.1

- Fixed the Windows one-file build to bundle Tcl/Tk runtime data and avoid the startup crash.
- Added a Windows CI smoke test that launches the packaged app before publishing it.
- Enabled Windows high-DPI rendering and the native Segoe UI font for clearer text.
- Published the portable Windows ZIP with an explicit `portable` filename and documented it.

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
