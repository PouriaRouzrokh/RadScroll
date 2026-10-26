# 0002 — Decoding engine

**Status:** decided (2026-10-26): mpv where Anki ships it, Qt everywhere else and as the fallback. Measured on
macOS, Windows and Linux. Two checks stay open (see the end). · **Spike code:**
[`spikes/0002-decoding/`](../../spikes/0002-decoding/)

## Question

Can RadScroll turn screen recordings into frames using only what Anki already ships (PRD candidate (d)), with no
compiled wheel and no download? Two engines are in the Anki install:

- **Qt:** `QMediaPlayer` + `QVideoSink`, on Qt's FFmpeg media backend (frames arrive as `QImage`).
- **mpv:** the `mpv` binary in the `anki_audio` package, run in encoding mode, so raw frames come out on a pipe.

## What each platform's Anki carries (Anki 26.9.2)

Anki's launcher installs `aqt[qt,audio]==26.9.2` from PyPI. `aqt` asks for `anki-audio` only on macOS and Windows,
and PyPI has `anki-audio` 0.2.3 wheels only for those two (arm64 and x64). PyQt6-Qt6 6.11.2 has wheels for all
three.

| | macOS arm64 | Windows x64 | Linux x64 |
|---|---|---|---|
| Qt media backend | FFmpeg (and Darwin) | FFmpeg (and Windows Media Foundation) | FFmpeg only |
| Qt's FFmpeg | 7.1.5, trimmed: no AV1 decoder | the same build | the same build |
| mpv | 0.41.0, FFmpeg 8.1.2 (60 MB with its libraries) | 0.41.0-dev, one static `mpv.exe`, FFmpeg git f853d12 | **none bundled**; the distribution's mpv if the user installed it (Ubuntu 24.04: 0.37.0, FFmpeg 6.1.1) |
| mpv decoders | all (dav1d for AV1, libvpx) | all (dav1d for AV1, libvpx) | all, in Ubuntu's build |

Qt image plugins read and write WebP, HEIC, TIFF, BMP, JPEG and PNG on macOS (an early answer for record 0003).

**HEVC on Windows needs no paid codec.** The runner is Windows Server 2025 without Microsoft's HEVC Video
Extensions. Both engines decoded HEVC exactly, because each uses its own FFmpeg software decoder, not Media
Foundation.

## Method

There are no patient images and no anatomy. `make_clips.py` draws a synthetic phantom with Anki's own PyQt6: a
viewer frame around a pane showing 60 "slices". The scroll goes down, back up and down again, with uneven holds
and some cross-fade frames. Every frame carries a 12-bit barcode of its own index, so a decoder is checked frame by
frame. FFmpeg 8.1 encodes the frames into 11 variants. Two 3-minute, 2560 × 1600, 60 fps clips (10,800 frames)
test speed.

`bench.py` runs each engine on a plain CPython 3.13 with Anki's packages. It never opens Anki, a profile or a
collection.

- **Pass 1** decodes every frame to ≈ 200 px grayscale and reads its index.
- **Pass 2** decodes five chosen frames at full size and checks that each is the frame asked for.
- Qt runs in two modes. **qt16**: play at 16× and take frames through the event loop (the macOS run's method).
  **qt16d**: the same, but each frame is handled on Qt's decoding thread, so the decoder waits for the reader.

macOS ran on an Apple M5 (macOS 26.6.2). Windows and Linux ran on GitHub's standard runners (4 x64 cores, 16 GB,
no GPU) through a manual workflow, [`spike-0002-decoding.yml`](../../.github/workflows/spike-0002-decoding.yml),
with every platform decoding the same clip files. Raw results:
[`results/`](../../spikes/0002-decoding/results/) (`<platform>.jsonl`, and `<platform>-probe.json` for what the
install carries).

## Results

Correctness is the same on all three platforms:

| Clip | mpv: frames / seeks | Qt: frames / seeks |
|---|---|---|
| H.264 30 fps, 60 fps | 265 / 5 of 5 | 265 / 5 of 5 |
| H.264 variable frame rate | 265 / 5 of 5 | 265 / **3 of 5** (two seeks one frame early) |
| H.264 with rotation tag (phone style) | 265, turned upright / 5 of 5 | 265, turned upright / 5 of 5 |
| HEVC | 265 / 5 of 5 | 265 / 5 of 5 |
| VP8, VP9 (WebM) | 265 / 5 of 5 | 265 / 5 of 5 |
| AV1 | 265 / 5 of 5 | **0 frames, and no error** |
| GIF, ProRes, MJPEG | 265 / 5 of 5 | 265 / 5 of 5 |

On Linux, "mpv" is Ubuntu's mpv, not one Anki ships.

Pass 1 on the 3-minute, 2560 × 1600, 60 fps clips (H.264 / HEVC), with peak memory:

| Engine | macOS (M5) | Windows runner | Linux runner |
|---|---|---|---|
| mpv | 22.8 s / 25.7 s | 27.1 s / 40.3 s | 24.3 s / 36.7 s, mpv 175–200 MB |
| qt16 (event loop) | 35–42 s / 37–151 s | **stopped at 4 GB** after 1,255 / 928 frames | **stopped at 4 GB** after 789 / 880 frames |
| qt16d (decoding thread) | 58 s / 137 s, 430–550 MB | 441 s / 448 s, 350–370 MB | 131 s / 131 s, 260–280 MB |

**Qt's frame queue has no limit.** In qt16, Qt hands each frame to the event loop and goes on decoding. When the
reader is slower than the decoder, frames pile up. On the runners memory passed 4 GB within 40 seconds. Earlier
runs without the 4 GB guard crashed on Windows and took down the whole Linux runner. The fast M5 kept up, which
is why macOS never showed it. In qt16d, all 10,800 frames arrived in order every time, with memory flat at
260–550 MB.

Qt is slow on the Windows runner (24 fps for qt16d). Its FFmpeg tries DirectX video acceleration first, finds no
GPU, and decodes in software. A Windows PC with a GPU may be faster; this was not measured. Windows has mpv, so Qt
there is only the fallback.

mpv's pass 2 took 13–29 s on the long clips. Its `select` filter decodes the whole clip to reach the chosen frames;
exact seeks (`--hr-seek`) can speed this up later. Qt's pass 2 took 1–2 s.

Bench pitfalls worth keeping:
- mpv's autorotate filter runs after the user filter, so scale the stored (unturned) size.
- Qt: convert a `QVideoFrame` to `QImage` inside the callback; a frame kept for later can read back empty.
- Read mpv's console output as UTF-8; Windows' default code page fails on it.
- `QT_FFMPEG_DECODING_HW_DEVICE_TYPES=","` turns Qt's hardware decoding off (bench engine suffix `sw`).

## Decision

1. **Engine order:** Anki's bundled mpv on macOS and Windows; on Linux, an mpv found on `PATH`; otherwise Qt. If
   mpv fails on a clip, retry with Qt.
2. **Qt must handle frames on its decoding thread** (a direct connection on `videoFrameChanged`), never queue them
   on the event loop. Do the ≈ 200 px grayscale reduction there and keep only that.
3. **With Qt, pass 2 picks frames by count during a second play, not by time.** Seeks by time land one frame
   early on variable-frame-rate clips.
4. **AV1 without mpv** (Linux with no mpv installed): Qt returns no frames and no error. Treat zero frames as
   "this format can't be read here" and say so plainly: install mpv, or record again as H.264.
5. Nothing extra is bundled or downloaded on any platform.

## Still open

These don't change the decision. They are checks for when the pipeline is built (PLAN milestone 1):

1. **Real recordings** from the recorder matrix (PLAN §4): so far only synthetic clips.
2. **Inside Anki itself** (a sandbox base folder, `Anki -b <folder>`): run pass 1 on a background thread with
   Anki's own event loop, confirm the UI stays responsive, and time Qt on a Windows PC with a GPU.
