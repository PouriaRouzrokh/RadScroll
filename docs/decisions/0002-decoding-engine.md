# 0002 — Decoding engine

**Status:** in progress. macOS measured (2026-10-26); Windows and Linux still to run. · **Spike code:**
[`spikes/0002-decoding/`](../../spikes/0002-decoding/)

## Question

Can RadScroll turn screen recordings into frames using only what Anki already ships (PRD candidate (d)), with no
compiled wheel and no download? Two engines are in the Anki bundle:

- **Qt:** `QMediaPlayer` + `QVideoSink`, on Qt's FFmpeg media backend (frames arrive as `QImage`).
- **mpv:** the `mpv` binary in the `anki_audio` package, run in encoding mode, so raw frames come out on a pipe.

## What was checked in the Anki bundle (Anki 26.9.2, macOS arm64)

- Qt 6.11.0 / PyQt 6.11.0. Qt's FFmpeg is **7.1.5, a trimmed build**: software decoders for H.264, HEVC, GIF,
  MJPEG, ProRes, WebP and APNG; VP9 only through Apple's VideoToolbox; no AV1 decoder.
- `anki_audio` ships **mpv 0.41.0 with its own FFmpeg 8.1.2** (dav1d for AV1, libvpx for VP8 / VP9, x264, x265),
  60 MB in all.
- Qt image plugins read and write WebP, HEIC, TIFF, BMP, JPEG and PNG (an early answer for record 0003).

## Method

There are no patient images and no anatomy. `make_clips.py` draws a synthetic phantom with Anki's own PyQt6: a
viewer frame around a pane showing 60 "slices". The scroll goes down, back up and down again, with uneven holds
and some cross-fade frames. Every frame carries a 12-bit barcode of its own index, so a decoder is checked frame by
frame. Homebrew ffmpeg encodes the frames into 11 variants. Two 3-minute, 2560 × 1600, 60 fps clips (10,800 frames)
test speed.

`bench.py` runs each engine on a plain CPython 3.13 that borrows Anki's packages. It never opens Anki, a profile or
a collection.

- **Pass 1** decodes every frame to ≈ 200 px grayscale and reads its index.
- **Pass 2** decodes five chosen frames at full size and checks that each is the frame asked for.

Raw results: [`spikes/0002-decoding/results/macos-arm64.jsonl`](../../spikes/0002-decoding/results/macos-arm64.jsonl).

## Results (Apple M5, macOS 26.6.2)

| Clip | mpv: frames / seeks | Qt (16×): frames / seeks |
|---|---|---|
| H.264 30 fps, 60 fps | 265 / 5 of 5 | 265 / 5 of 5 |
| H.264 variable frame rate | 265 / 5 of 5 | 265 / **3 of 5** (two seeks one frame early) |
| H.264 with rotation tag (phone style) | 265, turned upright / 5 of 5 | 265, turned upright / 5 of 5 |
| HEVC | 265 / 5 of 5 | 265 / 5 of 5 |
| VP8, VP9 (WebM) | 265 / 5 of 5 | 265 / 5 of 5 |
| AV1 | 265 / 5 of 5 | **0 frames, and no error** |
| GIF, ProRes, MJPEG | 265 / 5 of 5 | 265 / 5 of 5 |

Pass 1 speed on the 3-minute, 2560 × 1600, 60 fps clips:

| Clip | mpv | Qt (16×) |
|---|---|---|
| H.264 | 22.8 s | 35–42 s |
| HEVC | 25.7 s | 37–151 s (varies between runs) |

mpv's pass 2 took 8–17 s on the long clips. Its `select` filter decodes the whole clip to reach the chosen frames,
so this can be sped up later with exact seeks (`--hr-seek`). Qt's pass 2 took about 2 s.

Bench pitfalls worth keeping:
- mpv's autorotate filter runs after the user filter, so scale the stored (unturned) size.
- Qt: convert a `QVideoFrame` to `QImage` inside the callback; a frame kept for later can read back empty.

## Leaning (macOS only)

**mpv as the primary engine, Qt as the fallback.**
- mpv decoded every codec, every frame and every seek exactly, and it was the fastest and steadiest.
- Qt misses AV1 silently and lands one frame early on variable-frame-rate seeks. When Qt is used, pass 2 should
  pick frames by count during a second play, not by time.
- Neither engine needs anything bundled or downloaded.

## Still to answer before this record closes

1. **Windows:** does `anki_audio` carry mpv with the same FFmpeg? Does Qt decode HEVC without Microsoft's paid
   codec? Run the same bench.
2. **Linux:** the PRD expects no bundled mpv there (the system mpv, if any). Check, and measure Qt as the
   primary engine if mpv is absent.
3. Real recordings from the recorder matrix (PLAN §4), once collected: so far only synthetic clips.
4. Inside Anki itself (a sandbox base folder, `Anki -b <folder>`): run pass 1 on a background thread with Anki's
   own event loop, and confirm the UI stays responsive.
