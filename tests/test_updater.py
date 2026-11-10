import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from nemesis_gui.services import updater


class UpdaterTests(unittest.TestCase):
    def test_installable_assets_are_limited_to_published_platforms(self):
        self.assertTrue(updater.is_installable_asset("NemesisScanner.exe", "Windows", frozen=True))
        self.assertTrue(updater.is_installable_asset("NemesisScanner-windows-x64.zip", "Windows", frozen=True))
        self.assertFalse(updater.is_installable_asset("NemesisScanner.exe", "Windows", frozen=False))
        self.assertTrue(updater.is_installable_asset("nemesis-scanner.deb", "Linux"))
        self.assertTrue(updater.is_installable_asset("NemesisScanner.AppImage", "Linux"))
        self.assertFalse(updater.is_installable_asset("NemesisScanner.exe", "Linux"))
        self.assertFalse(updater.is_installable_asset("NemesisScanner.dmg", "Darwin"))

    def test_deb_update_uses_apt_get(self):
        package = Path("/tmp/nemesis-scanner.deb")
        with patch.object(updater.shutil, "which", return_value="/usr/bin/apt-get"):
            self.assertEqual(
                updater._linux_package_command(package),
                ["/usr/bin/apt-get", "install", "-y", str(package)],
            )

    def test_arch_update_uses_pacman(self):
        package = Path("/tmp/nemesis-scanner.pkg.tar.zst")
        with patch.object(updater.shutil, "which", return_value="/usr/bin/pacman"):
            self.assertEqual(
                updater._linux_package_command(package),
                ["/usr/bin/pacman", "-U", "--noconfirm", str(package)],
            )

    def test_appimage_replacement_relaunches_updated_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "installed.AppImage"
            downloaded = Path(directory) / "update.AppImage"
            target.write_bytes(b"old")
            downloaded.write_bytes(b"new")
            with patch.dict(os.environ, {"APPIMAGE": str(target)}), patch.object(updater.subprocess, "Popen") as launch:
                self.assertEqual(updater._replace_running_appimage(downloaded), "restart")

            self.assertEqual(target.read_bytes(), b"new")
            self.assertTrue(target.stat().st_mode & 0o111)
            launch.assert_called_once()

    def test_windows_bundle_extracts_only_the_expected_executable(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "windows-x64.zip"
            with zipfile.ZipFile(bundle, "w") as archive:
                archive.writestr("docs/README.md", "release notes")
                archive.writestr("app/NemesisScanner.exe", b"portable app")
            extracted = updater._extract_windows_executable(bundle)
            try:
                self.assertEqual(extracted.read_bytes(), b"portable app")
            finally:
                extracted.unlink(missing_ok=True)

    def test_windows_update_starts_helper_for_running_executable(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "NemesisScanner.exe"
            downloaded = Path(directory) / "NemesisScanner-new.exe"
            target.write_bytes(b"old")
            downloaded.write_bytes(b"new")
            script_path = None
            with (
                patch.object(updater.sys, "frozen", True, create=True),
                patch.object(updater.sys, "executable", str(target)),
                patch.object(updater.shutil, "which", return_value="powershell.exe"),
                patch.object(updater.subprocess, "Popen") as launch,
            ):
                self.assertEqual(updater._start_windows_update(downloaded), "restart")
                script_path = Path(launch.call_args.args[0][-1])
                script = script_path.read_text(encoding="utf-8")
                self.assertIn(str(os.getpid()), script)
                self.assertIn(str(downloaded), script)
                self.assertIn(str(target), script)
            script_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()