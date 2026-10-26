"""Spike 2 probe: what decoders does this platform's Anki install carry?

Prints one JSON object: the platform, the Qt version and its media backend files (with the FFmpeg libraries Qt
ships), and the mpv that bench.py would use (its version and the FFmpeg inside it).

Usage: python -I probe.py   (same RADSCROLL_ANKI_PACKAGES / RADSCROLL_MPV settings as bench.py)
"""

import json
import os
import platform
import subprocess
import sys
from pathlib import Path

ANKI_PACKAGES = os.environ.get("RADSCROLL_ANKI_PACKAGES", "/Applications/Anki.app/Contents/Resources/app_packages")
if ANKI_PACKAGES:
    sys.path.insert(0, ANKI_PACKAGES)

from PyQt6.QtCore import QLibraryInfo, qVersion  # noqa: E402


def mpv_info(mpv: str | None) -> dict:
    if not mpv:
        return {"path": None}

    def run(*args: str) -> str:
        return subprocess.run([mpv, "--no-config", *args], capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=60, check=False).stdout

    lines = run("--version").splitlines()
    decoders = {ln.split()[0] for ln in run("--vd=help").splitlines()[1:] if ln.strip()}
    return {
        "path": mpv,
        "version": lines[0] if lines else None,
        "ffmpeg": next((ln.strip() for ln in lines if "FFmpeg version" in ln), None),
        "decoders": [d for d in ("h264", "hevc", "vp8", "vp9", "av1", "libdav1d", "prores", "mjpeg", "gif")
                     if d in decoders],
        "files": sorted(p.name for p in Path(mpv).parent.iterdir()),
    }


def main() -> None:
    sys.path.insert(1, str(Path(__file__).parent))  # -I leaves the script's folder off the path
    import bench  # noqa: PLC0415 - reuse its mpv lookup; importing it does not run the bench

    plugins = Path(QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath))
    libs = Path(QLibraryInfo.path(QLibraryInfo.LibraryPath.LibrariesPath))
    bins = Path(QLibraryInfo.path(QLibraryInfo.LibraryPath.BinariesPath))
    ffmpeg_libs = sorted({p.name for d in (libs, bins) if d.is_dir() for p in d.iterdir()
                          if p.name.startswith(("av", "libav", "sw", "libsw"))})
    print(json.dumps({
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "qt": qVersion(),
        "qt_media_backends": sorted(p.name for p in (plugins / "multimedia").glob("*")) if plugins.is_dir() else [],
        "qt_ffmpeg_libs": ffmpeg_libs,
        "mpv": mpv_info(bench.MPV),
    }, indent=1))


if __name__ == "__main__":
    main()
