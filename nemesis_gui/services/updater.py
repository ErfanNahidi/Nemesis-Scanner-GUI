"""Check GitHub Releases and download the update asset for this platform."""

import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import requests


REPOSITORY = "ErfanNahidi/Nemesis-Scanner-GUI"
LATEST_RELEASE_API = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"


def version_tuple(value):
    match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", str(value))
    if not match:
        raise ValueError(f"Unsupported version format: {value}")
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch or 0)


def fetch_latest_release():
    response = requests.get(
        LATEST_RELEASE_API,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "Nemesis-Scanner-GUI"},
        timeout=(8, 20),
    )
    response.raise_for_status()
    release = response.json()
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("GitHub did not return a stable published release.")
    release["version"] = str(release.get("tag_name", "")).lstrip("vV")
    version_tuple(release["version"])
    release["assets"] = [
        asset
        for asset in release.get("assets", [])
        if asset.get("name") and asset.get("browser_download_url")
    ]
    return release


def recommended_asset_name(assets):
    names = {asset["name"] for asset in assets}
    system = platform.system()
    if system == "Windows":
        preferred = ("NemesisScanner.exe", "windows-x64-portable.zip", "windows-x64.zip")
    elif system == "Linux":
        try:
            distro = platform.freedesktop_os_release().get("ID", "").lower()
        except (AttributeError, OSError):
            distro = ""
        if distro in {"arch", "manjaro", "endeavouros"}:
            preferred = ("-any.pkg.tar.zst", ".AppImage")
        elif distro in {"debian", "ubuntu", "linuxmint", "pop"}:
            preferred = ("_all.deb", ".AppImage")
        elif distro in {"fedora", "rhel", "centos", "rocky", "almalinux", "opensuse-leap", "opensuse-tumbleweed"}:
            preferred = (".x86_64.rpm", ".AppImage")
        else:
            preferred = (".AppImage",)
    else:
        preferred = ()

    for suffix in preferred:
        match = next((name for name in sorted(names) if name.endswith(suffix)), None)
        if match:
            return match
    return None


def download_release_asset(asset, progress_callback=None):
    """Download an official release asset into Downloads without overwriting files."""
    name = asset.get("name", "")
    if not name or Path(name).name != name or "/" in name or "\\" in name or name in {".", ".."}:
        raise ValueError("The release contains an invalid asset filename.")

    downloads = Path.home() / "Downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    destination = downloads / name
    suffix = 1
    while destination.exists():
        extensions = "".join(Path(name).suffixes)
        stem = name[:-len(extensions)] if extensions else name
        destination = downloads / f"{stem} ({suffix}){extensions}"
        suffix += 1
    partial = destination.with_name(destination.name + ".part")
    expected_size = int(asset.get("size", 0) or 0)
    received = 0

    try:
        with requests.get(asset["browser_download_url"], stream=True, timeout=(10, 60)) as response:
            response.raise_for_status()
            header_size = int(response.headers.get("Content-Length", 0) or 0)
            total = expected_size or header_size
            with partial.open("wb") as output:
                for chunk in response.iter_content(chunk_size=256 * 1024):
                    if not chunk:
                        continue
                    output.write(chunk)
                    received += len(chunk)
                    if progress_callback:
                        progress_callback(received, total)
        if expected_size and received != expected_size:
            raise IOError(f"Download was incomplete ({received} of {expected_size} bytes).")
        os.replace(partial, destination)
    except Exception:
        partial.unlink(missing_ok=True)
        raise

    if destination.suffix.lower() == ".appimage":
        destination.chmod(destination.stat().st_mode | 0o111)
    return destination


def is_installable_asset(asset_name, system=None, frozen=None):
    system = system or platform.system()
    name = str(asset_name).lower()
    if system == "Windows":
        is_frozen = getattr(sys, "frozen", False) if frozen is None else frozen
        return is_frozen and name.endswith((".exe", "windows-x64-portable.zip", "windows-x64.zip"))
    if system == "Linux":
        return name.endswith((".appimage", ".deb", ".rpm", ".pkg.tar.zst"))
    return False


def install_downloaded_update(downloaded_path):
    path = Path(downloaded_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Update file was not found: {path}")
    if not is_installable_asset(path.name):
        raise RuntimeError("This update file cannot be installed automatically on this system.")

    system = platform.system()
    if system == "Windows":
        if path.name.lower().endswith(".zip"):
            extracted = _extract_windows_executable(path)
            try:
                return _start_windows_update(extracted, cleanup_source=True)
            except Exception:
                extracted.unlink(missing_ok=True)
                raise
        return _start_windows_update(path)
    if system == "Linux":
        if path.name.lower().endswith(".appimage"):
            return _replace_running_appimage(path)
        return _start_linux_package_install(path)
    raise RuntimeError("Automatic updates are available only for the published Windows and Linux builds.")


def _ensure_writable_directory(directory, error_message):
    try:
        with tempfile.NamedTemporaryFile(prefix=".nemesis-update-", dir=directory, delete=True):
            pass
    except OSError as error:
        raise PermissionError(error_message) from error


def _powershell_literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def _extract_windows_executable(bundle_path):
    with zipfile.ZipFile(bundle_path) as bundle:
        candidates = [
            item for item in bundle.infolist()
            if not item.is_dir() and item.filename.replace("\\", "/").rsplit("/", 1)[-1].lower() == "nemesisscanner.exe"
        ]
        if len(candidates) != 1:
            raise RuntimeError("The Windows update bundle must contain exactly one NemesisScanner.exe.")
        executable = candidates[0]
        if executable.file_size > 500 * 1024 * 1024:
            raise RuntimeError("The Windows update executable is unexpectedly large.")
        descriptor, extracted_name = tempfile.mkstemp(prefix="nemesis-update-", suffix=".exe")
        extracted = Path(extracted_name)
        try:
            with os.fdopen(descriptor, "wb") as destination, bundle.open(executable) as source:
                shutil.copyfileobj(source, destination)
        except Exception:
            extracted.unlink(missing_ok=True)
            raise
    return extracted


def _start_windows_update(downloaded_path, cleanup_source=False):
    if not getattr(sys, "frozen", False):
        raise RuntimeError("Automatic Windows updates require the portable NemesisScanner.exe build.")

    target = Path(sys.executable).resolve()
    if downloaded_path == target:
        raise RuntimeError("The downloaded update is already the running application.")
    _ensure_writable_directory(
        target.parent,
        "The application folder is protected. Move NemesisScanner.exe to a writable folder and try again.",
    )
    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if not powershell:
        raise RuntimeError("PowerShell was not found. Open the downloaded update manually instead.")

    staged = target.with_name(target.name + ".update")
    backup = target.with_name(target.name + ".previous")
    script = f"""$ErrorActionPreference = 'Stop'
$targetPid = {os.getpid()}
$source = {_powershell_literal(downloaded_path)}
$target = {_powershell_literal(target)}
$staged = {_powershell_literal(staged)}
$backup = {_powershell_literal(backup)}
$cleanupSource = ${str(cleanup_source).lower()}
try {{
  while (Get-Process -Id $targetPid -ErrorAction SilentlyContinue) {{ Start-Sleep -Milliseconds 300 }}
  Copy-Item -LiteralPath $source -Destination $staged -Force
  Remove-Item -LiteralPath $backup -Force -ErrorAction SilentlyContinue
    $moved = $false
    for ($attempt = 0; $attempt -lt 40; $attempt++) {{
        try {{
            Move-Item -LiteralPath $target -Destination $backup -Force
            $moved = $true
            break
        }} catch {{
            Start-Sleep -Milliseconds 250
        }}
    }}
    if (-not $moved) {{ throw 'Windows is still using the application file.' }}
  Move-Item -LiteralPath $staged -Destination $target -Force
  Start-Process -FilePath $target
  Remove-Item -LiteralPath $backup -Force -ErrorAction SilentlyContinue
}} catch {{
  Remove-Item -LiteralPath $staged -Force -ErrorAction SilentlyContinue
  if (Test-Path -LiteralPath $backup) {{
    Remove-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue
    Move-Item -LiteralPath $backup -Destination $target -Force
  }}
  Add-Type -AssemblyName System.Windows.Forms
  [System.Windows.Forms.MessageBox]::Show(
    "The update could not be installed:`n$($_.Exception.Message)",
    'Nemesis Scanner update'
  ) | Out-Null
}} finally {{
    if ($cleanupSource) {{ Remove-Item -LiteralPath $source -Force -ErrorAction SilentlyContinue }}
  Remove-Item -LiteralPath $PSCommandPath -Force -ErrorAction SilentlyContinue
}}
"""
    descriptor, script_path = tempfile.mkstemp(prefix="nemesis-update-", suffix=".ps1")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as script_file:
            script_file.write(script)
        creationflags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        subprocess.Popen(
            [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-STA", "-WindowStyle", "Hidden", "-File", script_path],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
    except Exception:
        Path(script_path).unlink(missing_ok=True)
        raise
    return "restart"


def _replace_running_appimage(downloaded_path):
    running_image = os.environ.get("APPIMAGE")
    if not running_image:
        raise RuntimeError("Start the application from its AppImage file to install an AppImage update.")

    target = Path(running_image).expanduser().resolve()
    _ensure_writable_directory(
        target.parent,
        "The AppImage folder is not writable. Move the AppImage to a folder you can edit and try again.",
    )
    descriptor, staged_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".update", dir=target.parent)
    staged = Path(staged_name)
    try:
        with os.fdopen(descriptor, "wb") as staged_file, downloaded_path.open("rb") as source:
            shutil.copyfileobj(source, staged_file)
            staged_file.flush()
            os.fsync(staged_file.fileno())
        staged.chmod(0o755)
        os.replace(staged, target)
    except Exception:
        staged.unlink(missing_ok=True)
        raise

    subprocess.Popen([str(target)], cwd=str(target.parent), start_new_session=True)
    return "restart"


def _linux_package_command(package_path):
    package_name = package_path.name.lower()
    if package_name.endswith(".deb"):
        manager = shutil.which("apt-get")
        if not manager:
            raise RuntimeError("apt-get was not found. Install this update with your system package manager.")
        return [manager, "install", "-y", str(package_path)]

    if package_name.endswith(".pkg.tar.zst"):
        manager = shutil.which("pacman")
        if not manager:
            raise RuntimeError("pacman was not found. Install this update with your system package manager.")
        return [manager, "-U", "--noconfirm", str(package_path)]

    if package_name.endswith(".rpm"):
        try:
            distro = platform.freedesktop_os_release().get("ID", "").lower()
        except (AttributeError, OSError):
            distro = ""
        if distro.startswith("opensuse"):
            manager = shutil.which("zypper")
            if manager:
                return [manager, "--non-interactive", "install", str(package_path)]
        manager = shutil.which("dnf")
        if manager:
            return [manager, "install", "-y", str(package_path)]
        raise RuntimeError("No supported RPM package manager was found. Install this update manually.")

    raise RuntimeError("This Linux package type is not supported for automatic installation.")


def _start_linux_package_install(package_path):
    polkit = shutil.which("pkexec")
    if not polkit:
        raise RuntimeError("pkexec was not found. Install this update with your system package manager.")
    command = _linux_package_command(package_path)
    return subprocess.Popen(
        [polkit, *command],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )


def reveal_in_file_manager(path):
    path = Path(path)
    if platform.system() == "Windows":
        os.startfile(str(path.parent))
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", "-R", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path.parent)])
