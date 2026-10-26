# Spike 2 — decoding engine

Throw-away measurement code for [decision record 0002](../../docs/decisions/0002-decoding-engine.md). Nothing here
ships in the add-on.

The scripts run on a plain CPython 3.13 that borrows Anki's bundled packages (PyQt6, Qt's FFmpeg plugin,
`anki_audio/mpv`). They never start Anki or open a collection. The path to Anki is set at the top of each script
(macOS default).

```sh
PY=python3.13   # any CPython 3.13; Anki's PyQt6 uses the stable ABI
$PY -I make_clips.py clips        # synthetic clips, clips/long/, truth.json (ffmpeg with x264, x265, vpx, svt-av1)
$PY -I bench.py clips mpv         # or qt16 (Qt at 16x playback)
$PY -I bench.py clips/long mpv --cycle 265 --frames 10800 h264_3min_2560.mp4
```

Each line of output is the JSON result for one clip. The clips are git-ignored; `make_clips.py` makes them again.
`probe.py` prints what the install carries (Qt's media backends and FFmpeg, the mpv in use and its decoders).

Engines: `mpv`, `qt<rate>` (frames through the event loop), `qt<rate>d` (frames on Qt's decoding thread) and a `sw`
suffix for Qt with hardware decoding off, e.g. `qt16dsw`.

Off macOS, install Anki's packages in the Python that runs the scripts (`pip install "aqt[qt,audio]==26.9.2"`) and
set `RADSCROLL_ANKI_PACKAGES=""`; `RADSCROLL_MPV` picks an mpv. The manual GitHub workflow
[`spike-0002-decoding.yml`](../../.github/workflows/spike-0002-decoding.yml) runs the whole bench on Windows and
Linux x64 runners (`gh workflow run spike-0002-decoding.yml`, optionally `-f clips_run=<run id>` to reuse clips).
