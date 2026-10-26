# Spike 1 — viewer delivery on phones

Throw-away test code for [decision record 0001](../../docs/decisions/0001-viewer-delivery.md). Nothing here ships
in the add-on.

The question: does the viewer run as reliably from a versioned media file (`_radscroll-vN.js`) as from a block
inside the templates, on desktop, AnkiDroid (old and new study screen) and AnkiMobile?

## What's here

- `probe.js`: a stand-in for the viewer, shaped like it (one guarded IIFE, no top-level `let` / `const`, listeners
  only on the stack, safe to run twice). It scrolls the synthetic stack and turns each card's red "NOT RUN" badge
  green: `RAN · <delivery> · probe vN · runs K`. It is padded to the real viewer's size (≈ 47 KB).
- `build_deck.py`: builds a sandbox profile with three note types and a deck of 20 cards each, then exports an
  `.apkg`. Run it again with `v2` to move the note types to a new probe version (the update test).
  - **A inline**: the probe in a marked `<script>` block in both templates.
  - **B src**: `<script src="_radscroll-vN.js"></script>` in both templates.
  - **C loader**: a short inline script that calls the probe if this version is already loaded, else adds a
    `<script>` element for `_radscroll-vN.js`. It spells the file name out in full, so exports and Check Media
    see it.
- `make_base.py`: turns the sandbox folder into an Anki base folder that opens without first-run dialogs, and can
  install an add-on into it.
- `desktop_driver/`: an add-on for the sandbox only; reviews every spike deck in Anki desktop and logs each badge.
- `android_flip.py`: drives AnkiDroid in the emulator through adb (wipe, import, pick the study screen, then flip
  every card, read each badge from the accessibility tree and drag once on the stack).
- `ocr.swift`: prints the text macOS's Vision framework reads in a screenshot; the driver uses it when Android's
  accessibility tree doesn't hold the card's text (AnkiDroid's new study screen, at first).
- `sync_up.py`: uploads the sandbox profile to the separate test AnkiWeb account, media included. The login comes
  from the environment and is never written to disk.
- `summarize.py`: turns the result logs into the table in the record.
- `results/`: one JSON line per card side.

The slices are numbered rings drawn with Qt: no anatomy, no patient data.

## Running it

Never on a real profile. Everything lives in a sandbox base folder (here `~/RadScrollSandbox`).

```sh
PY=python3.13   # any CPython 3.13; the scripts borrow Anki's bundled packages
$PY -I build_deck.py "~/RadScrollSandbox/spike1-base/User 1" v1      # also writes rs-spike1-v1.apkg

# desktop baseline, on a copy so the sync copy keeps its cards new
cp -R ~/RadScrollSandbox/spike1-base/"User 1" ~/RadScrollSandbox/spike1-desktop/
$PY -I make_base.py ~/RadScrollSandbox/spike1-desktop desktop_driver
/Applications/Anki.app/Contents/MacOS/Anki -b ~/RadScrollSandbox/spike1-desktop  # closes itself when done

# AnkiDroid in the emulator (Android command-line tools from Homebrew, AnkiDroid from its GitHub release)
$PY -I android_flip.py --reset ~/RadScrollSandbox/spike1-base/rs-spike1-v1.apkg old old "A inline" "B src" "C loader"
$PY -I android_flip.py --reset ~/RadScrollSandbox/spike1-base/rs-spike1-v1.apkg new new "A inline" "B src" "C loader"
```

Sync and AnkiMobile:

```sh
$PY -I make_base.py ~/RadScrollSandbox/spike1-base
RADSCROLL_TEST_USER=... RADSCROLL_TEST_PW=... $PY -I sync_up.py ~/RadScrollSandbox/spike1-base
```

AnkiMobile can't be driven from a computer: the iPad logs in to the test account, downloads, and the cards are
flipped by hand. Update test on AnkiDroid: `android_flip.py --update <v1.apkg> <v2.apkg> old|new <deck> ...`, with
the v2 package built by `build_deck.py <copy of the profile> v2`.
