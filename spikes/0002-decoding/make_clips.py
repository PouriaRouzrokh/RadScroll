"""Make synthetic test clips for spike 2 (decoding engine).

Each clip imitates a screen recording of someone scrolling a stack in a viewer: a still UI frame around a pane
that shows one "slice" at a time. Slices are geometric shapes (no anatomy). Every frame carries a barcode of its
own index (top strip) and its slice id (bottom strip), so a decoder can be checked frame by frame.

Frames are drawn with Anki's bundled PyQt6; Homebrew ffmpeg only encodes the test clips.

Usage: python -I make_clips.py <out_dir>   (also writes <out_dir>/long/: two 3-minute 2560 x 1600 60 fps clips that
loop the 60 fps clip, for speed; the bench reads them with --cycle 265 --frames 10800)
"""

import json
import math
import random
import subprocess
import sys
from pathlib import Path

ANKI_PACKAGES = "/Applications/Anki.app/Contents/Resources/app_packages"
sys.path.insert(0, ANKI_PACKAGES)

from PyQt6.QtCore import QPointF, QRectF, Qt  # noqa: E402
from PyQt6.QtGui import QColor, QFont, QGuiApplication, QImage, QPainter, QRadialGradient  # noqa: E402

W, H = 1280, 800
BITS = 12  # barcode bits: up to 4096 frames / slices
PANE = QRectF(240, 90, 800, 620)


def barcode(p: QPainter, value: int, y: float, h: float) -> None:
    """Draw `value` as BITS black / white blocks across the full width (robust to scaling and compression)."""
    bw = W / BITS
    for i in range(BITS):
        on = (value >> (BITS - 1 - i)) & 1
        p.fillRect(QRectF(i * bw, y, bw, h), QColor(255, 255, 255) if on else QColor(0, 0, 0))


def draw_slice(p: QPainter, s: int, n: int) -> None:
    """A phantom slice: a sphere cut at height s, rings and a few dots that move with s."""
    p.fillRect(PANE, QColor(0, 0, 0))
    t = (s + 0.5) / n
    cx, cy = PANE.center().x(), PANE.center().y()
    r = 280 * math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2)) + 6
    g = QRadialGradient(QPointF(cx, cy), r)
    g.setColorAt(0, QColor(200, 200, 200))
    g.setColorAt(1, QColor(90, 90, 90))
    p.setBrush(g)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(cx, cy), r, r * 0.85)
    p.setBrush(QColor(40, 40, 40))
    for k in range(5):
        a = 2 * math.pi * (k / 5 + t)
        p.drawEllipse(QPointF(cx + 0.6 * r * math.cos(a), cy + 0.5 * r * math.sin(a)), 14, 14)
    p.setPen(QColor(230, 230, 230))
    p.setFont(QFont("Helvetica", 22))
    p.drawText(QRectF(PANE.left() + 10, PANE.bottom() - 40, 200, 30), 0, f"Im: {s + 1}/{n}")


def slice_image(s: int, n: int) -> QImage:
    img = QImage(W, H, QImage.Format.Format_RGB32)
    img.fill(QColor(48, 52, 60))
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QColor(200, 200, 200))
    p.setFont(QFont("Helvetica", 18))
    p.drawText(QRectF(20, 60, 200, 30), 0, "SYNTHETIC")
    p.drawText(QRectF(20, 100, 200, 30), 0, "Series 3")
    draw_slice(p, s, n)
    p.end()
    return img


def frame(base: QImage, idx: int, sid: int) -> QImage:
    img = base.copy()
    p = QPainter(img)
    barcode(p, idx, 0, 48)
    barcode(p, sid, H - 48, 48)
    p.end()
    return img


def blend(a: QImage, b: QImage, w: float) -> QImage:
    out = a.copy()
    p = QPainter(out)
    p.setOpacity(w)
    p.drawImage(0, 0, b)
    p.end()
    return out


def scroll_plan(n: int, seed: int) -> list[tuple[int, int | None]]:
    """(slice, blend_to) per frame: down through the stack, back up a little, down again; random holds;
    some single cross-fade frames between neighbours (blend_to is the next slice)."""
    rnd = random.Random(seed)
    order = list(range(n)) + list(range(n - 2, n - 8, -1)) + list(range(n - 7, n))
    plan: list[tuple[int, int | None]] = []
    for i, s in enumerate(order):
        for _ in range(rnd.choice([1, 2, 3, 4, 6])):
            plan.append((s, None))
        if i + 1 < len(order) and rnd.random() < 0.15:
            plan.append((s, order[i + 1]))
    return [(order[0], None)] * 10 + plan + [(order[-1], None)] * 10


def render(out: Path, n: int, seed: int) -> dict:
    frames_dir = out / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    plan = scroll_plan(n, seed)
    cache: dict[int, QImage] = {}
    truth = []
    for idx, (s, to) in enumerate(plan):
        base = cache.setdefault(s, slice_image(s, n))
        if to is not None:
            base = blend(base, cache.setdefault(to, slice_image(to, n)), 0.5)
        frame(base, idx, s).save(str(frames_dir / f"{idx:05d}.png"))
        truth.append({"frame": idx, "slice": s, "blend": to is not None})
    return {"slices": n, "frames": len(plan), "plan": truth}


# name: (ffmpeg output args, file suffix, fps)
VARIANTS = {
    "h264_30cfr": (["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18"], "mp4", 30),
    "h264_60cfr": (["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18"], "mp4", 60),
    "hevc_30": (["-c:v", "libx265", "-tag:v", "hvc1", "-pix_fmt", "yuv420p", "-crf", "20"], "mp4", 30),
    "vp9_30": (["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "30", "-row-mt", "1"], "webm", 30),
    "vp8_30": (["-c:v", "libvpx", "-b:v", "4M"], "webm", 30),
    "av1_30": (["-c:v", "libsvtav1", "-crf", "35", "-preset", "8"], "mp4", 30),
    "prores_30": (["-c:v", "prores_ks", "-profile:v", "0"], "mov", 30),
    "mjpeg_30": (["-c:v", "mjpeg", "-q:v", "3"], "avi", 30),
    "gif_15": (["-vf", "split[a][b];[a]palettegen[p];[b][p]paletteuse"], "gif", 15),
}


def encode(src: Path, out: Path) -> list[str]:
    made = []
    pattern = str(src / "frames" / "%05d.png")
    for name, (args, suffix, fps) in VARIANTS.items():
        dst = out / f"{name}.{suffix}"
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(fps), "-i", pattern, *args, str(dst)]
        subprocess.run(cmd, check=True)
        made.append(dst.name)
    # Variable frame rate: same frames, uneven timestamps (as macOS / phone recorders write them).
    vfr = out / "h264_vfr.mov"
    concat = src / "vfr.txt"
    rnd = random.Random(7)
    lines = []
    for f in sorted((src / "frames").iterdir()):
        lines += [f"file '{f.resolve()}'", f"duration {rnd.choice([1 / 60, 1 / 30, 1 / 20, 1 / 12]):.5f}"]
    concat.write_text("\n".join(lines) + "\n")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
                    "-fps_mode", "passthrough", "-enc_time_base", "1:600", "-video_track_timescale", "600",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(vfr)], check=True)
    made.append(vfr.name)
    # Phone-style rotation metadata: pixels stored landscape, display matrix says rotate 90.
    rot = out / "h264_rot90.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-display_rotation", "90",
                    "-i", str(out / "h264_30cfr.mp4"), "-c", "copy", str(rot)], check=True)
    made.append(rot.name)
    return made


def encode_long(out: Path) -> list[str]:
    """3 minutes at 2560 x 1600, 60 fps (a Retina screen recording's size), H.264 and HEVC."""
    (out / "long").mkdir(exist_ok=True)
    codecs = {
        "h264": ["-c:v", "libx264", "-crf", "20", "-preset", "veryfast"],
        "hevc": ["-c:v", "libx265", "-tag:v", "hvc1", "-crf", "22", "-preset", "veryfast",
                 "-x265-params", "log-level=error"],
    }
    made = []
    for name, args in codecs.items():
        dst = out / "long" / f"{name}_3min_2560.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-stream_loop", "45", "-i", str(out / "h264_60cfr.mp4"),
                        "-vf", "scale=2560:1600:flags=neighbor", "-frames:v", "10800", "-pix_fmt", "yuv420p",
                        *args, str(dst)], check=True)
        made.append(f"long/{dst.name}")
    return made


def main() -> None:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    _app = QGuiApplication(["x", "-platform", "offscreen"])
    truth = render(out / "src", n=60, seed=1)
    (out / "truth.json").write_text(json.dumps(truth))
    made = encode(out / "src", out) + encode_long(out)
    print(json.dumps({"frames": truth["frames"], "slices": truth["slices"], "clips": made}))


if __name__ == "__main__":
    main()
