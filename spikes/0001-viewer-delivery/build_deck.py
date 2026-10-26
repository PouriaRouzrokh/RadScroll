"""Build the spike 1 test deck in a sandbox Anki profile and export it as an .apkg.

Three throw-away note types, one per way of delivering the viewer, each with its own deck of 20 cards:

- ``inline``: the probe inside the templates, in a marked ``<script>`` block (today's default).
- ``src``: ``<script src="_radscroll-vN.js">`` pointing at a media file.
- ``loader``: a short inline script that calls the probe if it is already loaded, else injects the media file.

The cards hold no anatomy: the "slices" are numbered rings drawn with Qt. The probe is padded to the real viewer's
size (about 47 KB) so the inline block weighs what the real one does.

Run with a plain CPython 3.13 that borrows Anki's packages, never on a real profile:

    PYTHONPATH=/Applications/Anki.app/Contents/Resources/app_packages python3.13 -I build_deck.py <profile-dir> v1

``<profile-dir>`` is a profile folder inside a sandbox base (``<base>/User 1``). Run again with ``v2`` to move the
note types to a new probe version (the update test); notes are added only on the first run.
"""

import os
import sys
from pathlib import Path

PACKAGES = os.environ.get("RADSCROLL_ANKI_PACKAGES", "/Applications/Anki.app/Contents/Resources/app_packages")
if PACKAGES:
    sys.path.insert(0, PACKAGES)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from anki.collection import Collection, DeckIdLimit, ExportAnkiPackageOptions  # noqa: E402
from PyQt6.QtCore import QBuffer, QByteArray, QIODevice, Qt  # noqa: E402
from PyQt6.QtGui import QColor, QFont, QGuiApplication, QImage, QPainter, QPen  # noqa: E402

HERE = Path(__file__).resolve().parent
DELIVERIES = ("inline", "src", "loader")
CARDS = 20
SLICES = 12
SIZE = 47_000  # bytes, the real viewer bundle's size

CSS = """\
.card { font-family: system-ui, -apple-system, sans-serif; text-align: center; background: #fff; color: #111; }
.rs-status { display: block; margin: 8px auto; padding: 18px 8px; border-radius: 6px;
  font: bold 20px/1.2 system-ui, sans-serif; color: #fff !important; }
.rs-fail { background: #d50000 !important; }
.rs-ok { background: #00a040 !important; }
.rs-label { margin: 6px; font-size: 16px; }
.ra-stack { position: relative; display: inline-block; width: 280px; height: 280px; outline: 1px solid #888;
  touch-action: none; }
.ra-stack img { display: none; width: 100%; height: 100%; }
.ra-stack img:first-of-type { display: block; }
.ra-stack.rs-live img { display: none; }
.ra-stack.rs-live img.rs-on { display: block; }
.rs-at { position: absolute; top: 4px; right: 6px; color: #ff0; font: 12px monospace; }
"""

LOADER = """\
<script>
(function () {
  var want = "@VERSION@";
  var R = window.RadScrollProbe;
  if (R && R.version === want) { R.scan(); return; }
  var s = document.createElement("script");
  s.src = "_radscroll-@VERSION@.js";  // the full name, so exports and Check Media see the file
  s.onerror = function () {
    var b = document.querySelectorAll(".rs-status");
    for (var i = 0; i < b.length; i++) b[i].textContent = "LOAD ERROR · loader";
  };
  document.head.appendChild(s);
})();
</script>"""


def probe_js(version: str) -> str:
    """The probe for `version`, padded with a comment to the real viewer's size."""
    js = (HERE / "probe.js").read_text().replace("@VERSION@", version)
    pad = SIZE - len(js.encode()) - 8
    return js + "\n/* " + "." * max(0, pad) + " */\n"


def block(delivery: str, version: str) -> str:
    """The template text that delivers the probe."""
    if delivery == "inline":
        body = "<script>\n" + probe_js(version) + "</script>"
    elif delivery == "src":
        body = f'<script src="_radscroll-{version}.js"></script>'
    else:
        body = LOADER.replace("@VERSION@", version)
    return f"<!-- RadScroll spike {version} begin -->\n{body}\n<!-- RadScroll spike end -->"


def templates(delivery: str, version: str) -> tuple[str, str]:
    status = f'<div class="rs-status rs-fail" data-delivery="{delivery}">NOT RUN · {delivery}</div>'
    front = f'{status}\n<div class="rs-label">{{{{Label}}}}</div>\n{{{{Board}}}}\n{block(delivery, version)}'
    back = f'{{{{FrontSide}}}}\n<hr id="answer">\n<div class="rs-label">answer side</div>\n{block(delivery, version)}'
    return front, back


def slice_webp(i: int) -> bytes:
    """One synthetic slice: a ring whose size changes with `i`, and the slice number. No anatomy."""
    img = QImage(256, 256, QImage.Format.Format_Grayscale8)
    img.fill(QColor(20, 20, 20))
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(QColor(220, 220, 220), 6))
    r = 20 + i * 8
    p.drawEllipse(128 - r, 128 - r, 2 * r, 2 * r)
    p.setFont(QFont("Helvetica", 40))
    p.drawText(img.rect(), Qt.AlignmentFlag.AlignCenter, str(i + 1))
    p.end()
    data = QByteArray()
    buf = QBuffer(data)
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    img.save(buf, "WEBP", 80)
    return bytes(data)


def board(names: list[str]) -> str:
    imgs = "".join(f'<img src="{n}">' for n in names)
    return (f'<div class="ra-board" data-ra-board="v1"><div class="ra-stack" data-ra-label="Phantom">'
            f'<span class="rs-at">1 / {len(names)}</span>{imgs}</div></div>')


def write_media(col: Collection, name: str, data: bytes) -> None:
    got = col.media.write_data(name, data)
    if got != name:  # a different file already has this name: never overwrite silently
        raise SystemExit(f"media name taken by other content: {name} (written as {got})")


def build(profile: Path, version: str) -> Path:
    profile.mkdir(parents=True, exist_ok=True)
    col = Collection(str(profile / "collection.anki2"))
    try:
        write_media(col, f"_radscroll-{version}.js", probe_js(version).encode())
        names = []
        for i in range(SLICES):
            name = f"rs-spike1-s{i + 1:02d}.webp"
            write_media(col, name, slice_webp(i))
            names.append(name)

        mm = col.models
        for letter, delivery in zip("ABC", DELIVERIES):
            name = f"RS spike 1 · {delivery}"
            front, back = templates(delivery, version)
            m = mm.by_name(name)
            if m:  # the update test: same note type, new block
                m["tmpls"][0]["qfmt"], m["tmpls"][0]["afmt"] = front, back
                mm.update_dict(m)
                continue
            m = mm.new(name)
            for field in ("Label", "Board"):
                mm.add_field(m, mm.new_field(field))
            t = mm.new_template("Card 1")
            t["qfmt"], t["afmt"] = front, back
            mm.add_template(m, t)
            m["css"] = CSS
            mm.add_dict(m)
            m = mm.by_name(name)

            did = col.decks.id(f"RS spike 1::{letter} {delivery}")
            conf = col.decks.config_dict_for_deck_id(did)
            conf["new"]["perDay"] = 200
            col.decks.update_config(conf)
            for n in range(CARDS):
                note = col.new_note(m)
                note["Label"] = f"{delivery} · card {n + 1:02d} / {CARDS}"
                note["Board"] = board(names)
                col.add_note(note, did)

        out = profile.parent / f"rs-spike1-{version}.apkg"
        top = col.decks.id("RS spike 1")
        opts = ExportAnkiPackageOptions(with_scheduling=False, with_deck_configs=True, with_media=True,
                                        legacy=False)
        col.export_anki_package(out_path=str(out), options=opts, limit=DeckIdLimit(deck_id=top))
        return out
    finally:
        col.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    app = QGuiApplication(sys.argv[:1])
    print(build(Path(sys.argv[1]).expanduser(), sys.argv[2]))
