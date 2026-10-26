"""Spike 2 bench: decode the synthetic clips with what Anki ships, and check every frame.

Engines:
  mpv      the bundled anki_audio mpv in encoding mode, raw grayscale frames on a pipe
  qt<rate> QMediaPlayer + QVideoSink (Qt's FFmpeg backend) playing at <rate>x, e.g. qt16
  qt<rate>sw the same with Qt's hardware decoding turned off, e.g. qt16sw

Pass 1 decodes every frame at about 200 px wide in grayscale and reads each frame's index barcode.
Pass 2 decodes a few chosen frames at full size and checks each one is the frame asked for.

Usage:
  python -I bench.py <clips_dir> <engine> [clip ...]
  python -I bench.py <clips_dir> <engine> --cycle 265 --frames 10800 <clip>   (a clip that loops the source)

Prints one JSON line per clip. Runs on a plain CPython 3.13 that borrows Anki's packages; it never opens Anki or
a collection.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from itertools import pairwise
from pathlib import Path

# Anki's packages: the macOS app bundle by default. Elsewhere, point RADSCROLL_ANKI_PACKAGES at a folder holding
# them, or install Anki's pinned packages in the running Python and set it to "" (the CI workflow does this).
ANKI_PACKAGES = os.environ.get("RADSCROLL_ANKI_PACKAGES", "/Applications/Anki.app/Contents/Resources/app_packages")
if ANKI_PACKAGES:
    sys.path.insert(0, ANKI_PACKAGES)


def find_mpv() -> str | None:
    """Anki's bundled mpv (macOS, Windows), else RADSCROLL_MPV, else an mpv on PATH (Linux has no bundled one)."""
    if path := os.environ.get("RADSCROLL_MPV"):
        return path
    try:
        import anki_audio
    except ImportError:
        return shutil.which("mpv")
    folder = Path(anki_audio.__file__).parent
    return next((str(p) for p in (folder / "mpv.exe", folder / "mpv") if p.is_file()), None)


MPV = find_mpv()

from PyQt6.QtCore import QEventLoop, QTimer, QUrl  # noqa: E402
from PyQt6.QtGui import QGuiApplication, QImage  # noqa: E402

BITS = 12  # must match make_clips.py
STRIP = 24 / 800  # centre of the index strip, as a fraction of the source height
SMALL_W = 200
PASS2_PICKS = (5, 50, 120, 200, 260)


# ---------------------------------------------------------------- barcode

class Reader:
    """Reads the frame-index barcode. `edge` says where the strip lies once the engine has turned the picture
    upright: top (no turn), left (turned counter-clockwise), right (turned clockwise)."""

    def __init__(self) -> None:
        self.edge = "top"

    def read(self, gray: bytes, w: int, h: int) -> int:
        v = 0
        for i in range(BITS):
            if self.edge == "top":
                x, y = int((i + 0.5) * w / BITS), int(STRIP * h)
            elif self.edge == "left":  # read bottom to top
                x, y = int(STRIP * w), int((BITS - 1 - i + 0.5) * h / BITS)
            else:  # right, read top to bottom
                x, y = min(w - 1, int((1 - STRIP) * w)), int((i + 0.5) * h / BITS)
            v = (v << 1) | (gray[y * w + x] > 128)
        return v

    def detect(self, gray: bytes, w: int, h: int) -> None:
        """Pick the edge for a turned picture from its first frame (index 0)."""
        self.edge = "left"
        if self.read(gray, w, h) != 0:
            self.edge = "right"


def qimage_gray(img: QImage, width: int | None = None) -> tuple[bytes, int, int]:
    if width:
        img = img.scaledToWidth(width)
    img = img.convertToFormat(QImage.Format.Format_Grayscale8)
    w, h, bpl = img.width(), img.height(), img.bytesPerLine()
    raw = bytes(img.constBits().asarray(bpl * h))
    if bpl != w:
        raw = b"".join(raw[r * bpl:r * bpl + w] for r in range(h))
    return raw, w, h


def score(found: list[int], expected: int, cycle: int | None) -> dict:
    """Frames missing or out of order. For a looped clip, each step must be +1 modulo the cycle."""
    if cycle:
        bad_steps = sum(1 for a, b in pairwise(found) if (b - a) % cycle != 1)
        return {"frames_expected": expected, "frames_got": len(found), "bad_steps": bad_steps}
    seen = set(found)
    return {
        "frames_expected": expected,
        "frames_got": len(found),
        "missing": expected - len(seen & set(range(expected))),
        "out_of_order": sum(1 for a, b in pairwise(found) if b < a),
    }


def peak_memory() -> dict:
    """Peak resident memory so far, in MB, of this process (the Qt engine) and of its children (mpv). None on
    Windows, which has no `resource` module."""
    try:
        import resource
    except ImportError:
        return {}
    unit = 1 if sys.platform == "darwin" else 1024  # ru_maxrss: bytes on macOS, KB on Linux
    return {f"peak_{who}_mb": round(resource.getrusage(r).ru_maxrss * unit / 2**20)
            for who, r in (("self", resource.RUSAGE_SELF), ("children", resource.RUSAGE_CHILDREN))}


# ---------------------------------------------------------------- mpv engine

def mpv_probe(path: Path) -> dict:
    """Display size (after autorotate) and the rotation tag."""
    msg = "RSPROBE ${video-out-params/dw} ${video-out-params/dh} ${video-params/rotate}"
    r = subprocess.run([MPV, "--no-config", "--vo=null", "--ao=null", "--frames=1", f"--term-playing-msg={msg}",
                        str(path)], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=60, check=False)
    line = next((ln for ln in r.stdout.splitlines() if ln.startswith("RSPROBE ")), "")
    parts = line.split()[1:]
    if len(parts) != 3:
        raise RuntimeError(f"mpv probe failed: {r.stdout[-300:]}")
    return {"dw": int(parts[0]), "dh": int(parts[1]), "rotate": parts[2]}


def mpv_frames(path: Path, vf: str, w: int, h: int):
    """Yield raw grayscale frames of w x h from mpv's encoder on stdout."""
    cmd = [MPV, "--no-config", "--msg-level=all=error", "--no-audio", "--o=-", "--of=rawvideo", "--ovc=rawvideo",
           f"--vf=lavfi=[{vf}]", str(path)]
    size = w * h
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as proc:
        while chunk := proc.stdout.read(size):
            if len(chunk) == size:
                yield chunk


def run_mpv(path: Path, reader: Reader) -> dict:
    meta = mpv_probe(path)
    turned = meta["rotate"] in ("90", "270")
    reader.edge = {"270": "left", "90": "right"}.get(meta["rotate"], "top")
    w = SMALL_W
    h = round(meta["dh"] * w / meta["dw"] / 2) * 2
    sw, sh = (h, w) if turned else (w, h)  # mpv's autorotate runs after our filter: scale the stored picture

    t0 = time.perf_counter()
    found = [reader.read(f, w, h) for f in mpv_frames(path, f"scale={sw}:{sh},format=gray", w, h)]
    meta["pass1_s"] = round(time.perf_counter() - t0, 2)

    sel = "+".join(f"eq(n\\,{i})" for i in PASS2_PICKS)
    t0 = time.perf_counter()
    got = [reader.read(f, meta["dw"], meta["dh"])
           for f in mpv_frames(path, f"select='{sel}',format=gray", meta["dw"], meta["dh"])]
    meta["pass2_s"] = round(time.perf_counter() - t0, 2)
    meta["pass2"] = [{"want": i, "got": g} for i, g in zip(PASS2_PICKS, got)]
    meta["found"] = found
    return meta


# ---------------------------------------------------------------- Qt engine

def wait(ms: int) -> None:
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def run_qt(path: Path, reader: Reader, rate: float) -> dict:
    from PyQt6.QtMultimedia import QMediaPlayer, QVideoSink

    meta: dict = {}
    found: list[int] = []
    starts: list[int] = []
    player, sink, loop = QMediaPlayer(), QVideoSink(), QEventLoop()
    player.setVideoSink(sink)

    def on_frame(fr) -> None:
        if not fr.isValid():
            return
        img = fr.toImage()
        if img.isNull():  # seen on large clips: the frame arrives but cannot be read back
            meta["null_images"] = meta.get("null_images", 0) + 1
            meta.setdefault("null_handle", fr.handleType().name)
            return
        g, w, h = qimage_gray(img, SMALL_W)
        if not found:
            turned = (img.width() < img.height()) != (fr.width() < fr.height())
            meta.update(frame_size=[fr.width(), fr.height()], image_size=[img.width(), img.height()],
                        rotation=fr.surfaceFormat().rotation().name, upright=turned)
            if turned:
                reader.detect(g, w, h)
        found.append(reader.read(g, w, h))
        starts.append(fr.startTime())

    def on_status(st) -> None:
        if st in (QMediaPlayer.MediaStatus.EndOfMedia, QMediaPlayer.MediaStatus.InvalidMedia):
            meta["status"] = st.name
            loop.quit()

    def on_error(_err, msg: str) -> None:
        meta["error"] = msg
        loop.quit()

    sink.videoFrameChanged.connect(on_frame)
    player.mediaStatusChanged.connect(on_status)
    player.errorOccurred.connect(on_error)
    player.setSource(QUrl.fromLocalFile(str(path)))
    player.setPlaybackRate(rate)
    t0 = time.perf_counter()
    player.play()
    QTimer.singleShot(600_000, loop.quit)
    loop.exec()
    meta["pass1_s"] = round(time.perf_counter() - t0, 2)

    player.stop()

    # Pass 2 on a fresh player: pause, seek to each picked frame's start time (ms), take the frame that arrives.
    picks = [(i, starts[found.index(i)]) for i in PASS2_PICKS if i in found]
    latest: list = []
    player, sink = QMediaPlayer(), QVideoSink()
    player.setVideoSink(sink)
    # Convert inside the callback: a QVideoFrame kept for later can lose its buffer and read back empty.
    sink.videoFrameChanged.connect(lambda fr: fr.isValid() and latest.append(fr.toImage()))
    player.setSource(QUrl.fromLocalFile(str(path)))
    player.pause()
    wait(300)
    t0 = time.perf_counter()
    meta["pass2"] = []
    for idx, start_us in picks:
        latest.clear()
        player.setPosition(start_us // 1000 + 1)  # +1 ms so rounding lands inside the frame
        for _ in range(600):  # up to 3 s
            if latest:
                break
            wait(5)
        got = None
        img = latest[-1] if latest else None
        if img is not None and not img.isNull():
            g, w, h = qimage_gray(img)
            got = reader.read(g, w, h)
        meta["pass2"].append({"want": idx, "got": got})
    meta["pass2_s"] = round(time.perf_counter() - t0, 2)
    player.stop()
    meta["found"] = found
    return meta


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", type=Path)
    ap.add_argument("engine", help="mpv, or qt<rate> such as qt16")
    ap.add_argument("names", nargs="*")
    ap.add_argument("--cycle", type=int, help="the clip loops a source of this many frames")
    ap.add_argument("--frames", type=int, help="frames in a looped clip")
    args = ap.parse_args()
    if args.engine == "mpv" and not MPV:
        sys.exit("no mpv: Anki ships none on this platform and none is on PATH")
    if args.engine.endswith("sw"):  # Qt with hardware decoding off: an empty list of hardware device types
        os.environ["QT_FFMPEG_DECODING_HW_DEVICE_TYPES"] = ","

    truth = None if args.cycle else json.loads((args.clips / "truth.json").read_text())
    expected = args.frames if args.cycle else truth["frames"]
    names = args.names or sorted(p.name for p in args.clips.iterdir() if p.is_file() and p.suffix != ".json")
    _app = QGuiApplication(["bench"])
    for name in names:
        reader = Reader()
        row: dict = {"clip": name, "engine": args.engine}
        try:
            if args.engine == "mpv":
                meta = run_mpv(args.clips / name, reader)
            else:
                meta = run_qt(args.clips / name, reader, float(args.engine.removeprefix("qt").removesuffix("sw") or 1))
            found = meta.pop("found")
            row.update(meta)
            row.update(score(found, expected, args.cycle))
            row["pass2_exact"] = f"{sum(p['got'] == p['want'] for p in meta['pass2'])}/{len(meta['pass2'])}"
            row.update(peak_memory())
        except Exception as e:  # noqa: BLE001 - a spike reports a failure and moves on
            row["exception"] = repr(e)
        print(json.dumps(row), flush=True)


if __name__ == "__main__":
    main()
