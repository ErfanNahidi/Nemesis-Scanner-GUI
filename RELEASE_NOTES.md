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
