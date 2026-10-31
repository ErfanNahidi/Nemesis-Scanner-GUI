#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
VERSION="$(python3 -c 'from nemesis_gui import __version__; print(__version__)')"
OUT="${1:-$ROOT/dist}"
OUT="$(mkdir -p "$OUT" && cd "$OUT" && pwd)"
STAGE="$OUT/packages-stage"
rm -rf "$STAGE"

copy_app() {
  local root="$1"
  mkdir -p "$root/usr/share/nemesis-scanner-gui" \
    "$root/usr/share/applications" "$root/usr/share/icons/hicolor/256x256/apps" "$root/usr/bin"
  cp -a main.py core nemesis_gui Logo-small.png "$root/usr/share/nemesis-scanner-gui/"
  local nmap_python_dir
  nmap_python_dir="$(python3 -c 'import nmap; from pathlib import Path; print(Path(nmap.__file__).parent)')"
  cp -a "$nmap_python_dir" "$root/usr/share/nemesis-scanner-gui/nmap"
  find "$root/usr/share/nemesis-scanner-gui" -type d -name __pycache__ -prune -exec rm -rf {} +
  find "$root/usr/share/nemesis-scanner-gui" -type f -name '*.pyc' -delete
  cp README.md README-fa.md MANUAL.md "$root/usr/share/nemesis-scanner-gui/"
  cp Logo.png "$root/usr/share/icons/hicolor/256x256/apps/nemesis-scanner.png"
  cat > "$root/usr/bin/nemesis-scanner-gui" <<'EOF'
#!/usr/bin/env sh
cd /usr/share/nemesis-scanner-gui
exec python3 /usr/share/nemesis-scanner-gui/main.py "$@"
EOF
  chmod 755 "$root/usr/bin/nemesis-scanner-gui"
  cat > "$root/usr/share/applications/nemesis-scanner.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Nemesis Scanner
Comment=Network scanner and report viewer
Exec=nemesis-scanner-gui
Icon=nemesis-scanner
StartupWMClass=NemesisScanner
Categories=Utility;Network;Security;
Terminal=false
EOF
}

# Debian package: platform Python and libraries are resolved by apt.
DEB="$STAGE/deb"
mkdir -p "$DEB/DEBIAN"
copy_app "$DEB"
cat > "$DEB/DEBIAN/control" <<EOF
Package: nemesis-scanner-gui
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Maintainer: Nemesis Scanner contributors
Depends: python3, python3-tk, python3-requests, nmap
Description: Nemesis Scanner graphical desktop application
 Network scanner GUI with local reports and vulnerability review.
EOF
dpkg-deb --build --root-owner-group "$DEB" "$OUT/nemesis-scanner-gui_${VERSION}_all.deb"

# Build an Arch package archive; pacman resolves the declared dependencies.
ARCH="$STAGE/arch"
copy_app "$ARCH"
cat > "$ARCH/.PKGINFO" <<EOF
pkgname = nemesis-scanner-gui
pkgbase = nemesis-scanner-gui
pkgver = ${VERSION}-1
pkgdesc = Nemesis Scanner graphical desktop application
url = https://github.com/ErfanNahidi/Nemesis-Scanner-GUI
builddate = $(date +%s)
packager = Nemesis Scanner contributors
size = $(du -sb "$ARCH" | cut -f1)
arch = any
license = unknown
depend = python
depend = python-requests
depend = tk
depend = nmap
EOF
tar --zstd --format=gnu --owner=0 --group=0 --numeric-owner -C "$ARCH" \
  -cf "$OUT/nemesis-scanner-gui-${VERSION}-1-any.pkg.tar.zst" .

# Include a standard makepkg recipe and source snapshot for Arch rebuilds.
SRCROOT="$OUT/arch-src"
rm -rf "$SRCROOT"
mkdir -p "$SRCROOT/nemesis-scanner-gui-$VERSION"
tar --exclude='*/__pycache__' --exclude='*.pyc' -cf - main.py core nemesis_gui Logo.png Logo-small.png README.md README-fa.md MANUAL.md | \
  tar -xf - -C "$SRCROOT/nemesis-scanner-gui-$VERSION"
NMAP_PYTHON_DIR="$(python3 -c 'import nmap; from pathlib import Path; print(Path(nmap.__file__).parent)')"
cp -a "$NMAP_PYTHON_DIR" "$SRCROOT/nemesis-scanner-gui-$VERSION/nmap"
find "$SRCROOT/nemesis-scanner-gui-$VERSION/nmap" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$SRCROOT/nemesis-scanner-gui-$VERSION/nmap" -type f -name '*.pyc' -delete
tar -C "$SRCROOT" -czf "$OUT/nemesis-scanner-gui-$VERSION.tar.gz" "nemesis-scanner-gui-$VERSION"
SUM="$(sha256sum "$OUT/nemesis-scanner-gui-$VERSION.tar.gz" | cut -d' ' -f1)"
cat > "$OUT/PKGBUILD" <<EOF
pkgname=nemesis-scanner-gui
pkgver=$VERSION
pkgrel=1
pkgdesc='Nemesis Scanner graphical desktop application'
arch=('any')
license=('unknown')
depends=('python' 'python-requests' 'tk' 'nmap')
source=("\$pkgname-\$pkgver.tar.gz")
sha256sums=('$SUM')

package() {
  cd "\$srcdir/\$pkgname-\$pkgver"
  install -d "\$pkgdir/usr/share/nemesis-scanner-gui" "\$pkgdir/usr/bin" \\
    "\$pkgdir/usr/share/applications" "\$pkgdir/usr/share/icons/hicolor/256x256/apps"
  cp -a main.py core nemesis_gui nmap Logo-small.png README.md README-fa.md MANUAL.md "\$pkgdir/usr/share/nemesis-scanner-gui/"
  cat > "\$pkgdir/usr/bin/nemesis-scanner-gui" <<'LAUNCHER'
#!/usr/bin/env sh
cd /usr/share/nemesis-scanner-gui
exec python3 /usr/share/nemesis-scanner-gui/main.py "\$@"
LAUNCHER
  chmod 755 "\$pkgdir/usr/bin/nemesis-scanner-gui"
  cat > "\$pkgdir/usr/share/applications/nemesis-scanner.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=Nemesis Scanner
Comment=Network scanner and report viewer
Exec=nemesis-scanner-gui
Icon=nemesis-scanner
Categories=Utility;Network;Security;
Terminal=false
DESKTOP
  install -Dm644 Logo.png "\$pkgdir/usr/share/icons/hicolor/256x256/apps/nemesis-scanner.png"
}
EOF

echo "DEB: $OUT/nemesis-scanner-gui_${VERSION}_all.deb"
echo "Arch: $OUT/nemesis-scanner-gui-${VERSION}-1-any.pkg.tar.zst"
echo "Arch recipe: $OUT/PKGBUILD (with source tarball beside it)"
