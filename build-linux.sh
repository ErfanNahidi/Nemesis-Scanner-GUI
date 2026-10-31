#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
VERSION="$(python3 -c 'from nemesis_gui import __version__; print(__version__)')"
OUT="${1:-$ROOT/dist}"
OUT="$(mkdir -p "$OUT" && cd "$OUT" && pwd)"

command -v nmap >/dev/null || { echo "Nmap is required on the build host." >&2; exit 1; }
python3 -m pip install --user -r requirements.txt pyinstaller

rm -rf build dist/NemesisScanner dist/NemesisScanner.spec
python3 -m PyInstaller --noconfirm --clean --onedir --windowed \
  --name NemesisScanner --add-data "Logo.png:." --collect-data core \
  --hidden-import=nmap --hidden-import=requests --hidden-import=PIL \
  main.py

APPDIR="$OUT/NemesisScanner.AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/share/applications" "$APPDIR/usr/share/icons/hicolor/256x256/apps"
cp -a dist/NemesisScanner/. "$APPDIR/usr/bin/"
cp Logo.png "$APPDIR/usr/share/icons/hicolor/256x256/apps/nemesis-scanner.png"
cp Logo.png "$APPDIR/nemesis-scanner.png"
cat > "$APPDIR/nemesis-scanner.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Nemesis Scanner
Comment=Network scanner and report viewer
Exec=nemesis-scanner
Icon=nemesis-scanner
Categories=Utility;Network;Security;
Terminal=false
EOF
cp "$APPDIR/nemesis-scanner.desktop" "$APPDIR/usr/share/applications/"
cat > "$APPDIR/AppRun" <<'EOF'
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "$0")")"
export PATH="$HERE/usr/bin:$PATH"
exec "$HERE/usr/bin/NemesisScanner" "$@"
EOF
chmod +x "$APPDIR/AppRun"

RPMROOT="$OUT/rpm-root"
rm -rf "$RPMROOT"
mkdir -p "$RPMROOT/opt/nemesis-scanner" "$RPMROOT/usr/bin" "$RPMROOT/usr/share/applications" "$RPMROOT/usr/share/icons/hicolor/256x256/apps"
cp -a dist/NemesisScanner/. "$RPMROOT/opt/nemesis-scanner/"
cp Logo.png "$RPMROOT/usr/share/icons/hicolor/256x256/apps/nemesis-scanner.png"
cp "$APPDIR/nemesis-scanner.desktop" "$RPMROOT/usr/share/applications/"
cat > "$RPMROOT/usr/bin/nemesis-scanner" <<'EOF'
#!/usr/bin/env bash
exec /opt/nemesis-scanner/NemesisScanner "$@"
EOF
chmod +x "$RPMROOT/usr/bin/nemesis-scanner"
RPMBUILD="$OUT/rpmbuild"
mkdir -p "$RPMBUILD/BUILD" "$RPMBUILD/BUILDROOT" "$RPMBUILD/RPMS" "$RPMBUILD/SOURCES" "$RPMBUILD/SPECS" "$RPMBUILD/SRPMS" "$RPMBUILD/TMP"
tar -C "$RPMROOT" -czf "$RPMBUILD/SOURCES/nemesis-scanner-root.tar.gz" .
cat > "$RPMBUILD/SPECS/nemesis-scanner.spec" <<EOF
%global __requires_exclude ^lib(gfortran|quadmath)-.*
Name:           nemesis-scanner
%global debug_package %{nil}
Version:        $VERSION
Release:        1%{?dist}
Summary:        Nemesis Scanner graphical desktop application
License:        Unknown
BuildArch:      x86_64
Requires:       nmap
Source0:        nemesis-scanner-root.tar.gz

%description
Nemesis Scanner graphical network scanning and report viewer.

%prep
%setup -q -c -T
tar -xzf %{SOURCE0}

%install
mkdir -p %{buildroot}
cp -a . %{buildroot}/

%files
/opt/nemesis-scanner
/usr/bin/nemesis-scanner
/usr/share/applications/nemesis-scanner.desktop
/usr/share/icons/hicolor/256x256/apps/nemesis-scanner.png
EOF
rpmbuild --define "_topdir $RPMBUILD" --define "_tmppath $RPMBUILD/TMP" -bb "$RPMBUILD/SPECS/nemesis-scanner.spec"
cp "$RPMBUILD/RPMS/x86_64/nemesis-scanner-${VERSION}-1"*.rpm "$OUT/nemesis-scanner-${VERSION}-1.x86_64.rpm"

APPIMAGETOOL="${APPIMAGETOOL:-$(command -v appimagetool || true)}"
if [[ -n "$APPIMAGETOOL" ]]; then
  if [[ -n "${APPIMAGE_RUNTIME:-}" ]]; then
    APPIMAGE_EXTRACT_AND_RUN=1 ARCH=x86_64 "$APPIMAGETOOL" --runtime-file "$APPIMAGE_RUNTIME" "$APPDIR" "$OUT/NemesisScanner-${VERSION}-x86_64.AppImage"
  else
    ARCH=x86_64 "$APPIMAGETOOL" "$APPDIR" "$OUT/NemesisScanner-${VERSION}-x86_64.AppImage"
  fi
else
  echo "AppDir created at $APPDIR; appimagetool is missing, so AppImage could not be finalized." >&2
fi
echo "RPM: $OUT/nemesis-scanner-${VERSION}-1.x86_64.rpm"
