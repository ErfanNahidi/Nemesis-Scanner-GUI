"""Check GitHub Releases and download the update asset for this platform."""

import os
import platform
import re
import subprocess
from pathlib import Path

import requests


REPOSITORY = "ErfanNahidi/Nemesis-Scanner-GUI"
LATEST_RELEASE_API = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"


def version_tuple(value):
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", str(value))
    if not match:
        raise ValueError(f"Unsupported version format: {value}")
    return tuple(int(part) for part in match.groups())


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
        preferred = ("NemesisScanner.exe", "windows-x64.zip")
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


def reveal_in_file_manager(path):
    path = Path(path)
    if platform.system() == "Windows":
        os.startfile(str(path.parent))
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", "-R", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path.parent)])
