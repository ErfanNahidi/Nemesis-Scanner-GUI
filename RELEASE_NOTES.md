# Nemesis Scanner GUI 1.3

## What's changed

- Added Windows and Linux GitHub Actions builds for every push and pull request.
- Added version-tagged GitHub Releases containing the Windows EXE and ZIP, Linux DEB, RPM,
  Arch package, and AppImage. The release tag must match the application version.
- Added an **Install new update** action for supported Windows and Linux installations.
- Simplified scan navigation and added assessment presets with clearer descriptions.
- Added real scan-stage status and elapsed time to the scan page.

## Build and release

Pushes and pull requests build platform artifacts and keep them as workflow artifacts for 14 days.
To publish a release, set `nemesis_gui.__version__`, commit the changes, and push a matching tag,
for example `v1.3`. GitHub creates the release only after both platform builds succeed.

Windows automatic replacement requires the portable EXE to be in a folder writable by the current
user. Linux package installs require desktop authorization; AppImage updates require a writable
AppImage directory. macOS builds are not published.

## Previous release

The 1.2.2 patch below fixed Linux window identity and icon setup.

# Nemesis Scanner GUI 1.2.2

This patch fixes the Linux window identity and icon setup so Fedora's desktop taskbar can display
the Nemesis Scanner logo instead of Tk's default X icon.

## What's changed

- Set the Linux Tk application and window class at window creation. This works with Tk 9, where the
  older `wm class` command is unavailable.
- Apply the bundled Nemesis logo as the Linux window icon.
- Match the window class with `StartupWMClass` in the RPM, DEB, Arch, and AppImage desktop launchers
  so GNOME, KDE, and other X11 desktop shells can associate the running window with its app icon.
- Kept Windows icon handling unchanged.

## Updating

Use the **Updates** page to check GitHub and download the package for your system. After installing
this update, close and reopen Nemesis Scanner to refresh the taskbar icon.

Nmap remains a separate system requirement for scans. See `README.md` and `MANUAL.md` for
installation details.
