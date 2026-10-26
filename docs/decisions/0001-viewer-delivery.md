# 0001 — Viewer delivery

**Status:** open (2026-10-26). Desktop and AnkiDroid (both study screens) are measured; AnkiMobile is left (see
the end). · **Spike code:** [`spikes/0001-viewer-delivery/`](../../spikes/0001-viewer-delivery/)

## Question

Can the viewer load from a versioned media file (`_radscroll-vN.js`) as reliably as from a block inside the
templates, on Anki desktop, AnkiDroid (old and new study screen) and AnkiMobile?

Forum reports say a script loaded from the media folder works on desktop and fails on AnkiMobile, probably
because of timing: an inline script that calls the file's functions runs before the file has loaded
([1](https://forums.ankiweb.net/t/loading-external-javascript-file/67719),
[2](https://forums.ankiweb.net/t/loading-mathjax-configuration-from-external-script-doesnt-work/53643)). The
PRD's default is the inline block, because the author's own viewer already works that way on his iPhone.

## Three ways to deliver it

| | In the template | What a template update means |
|---|---|---|
| **A inline** | the whole viewer (≈ 47 KB) in a marked `<script>` block, front and back | rewrite every template |
| **B src** | `<script src="_radscroll-vN.js"></script>` | add a new file, change one line |
| **C loader** | ≈ 12 lines: call the viewer if this version is loaded, else add a `<script>` for the file | add a new file, change one line |

In B and C the file runs its own scan when it loads, so no inline code has to wait for it. That removes the
timing problem the forum reports describe, if it is the cause.

## Method

- **The probe** stands in for the viewer and is shaped like it: one guarded IIFE, no top-level `let` / `const`,
  listeners only on the stack, padded to the real bundle's 47 KB. Each card carries a red badge,
  `NOT RUN · <delivery>`, in the template's own HTML. When the probe runs it turns the badge green and writes
  `RAN · <delivery> · probe vN · runs K`, and binds a drag / wheel scroll to the stack.
- **The deck:** three throw-away note types (one per delivery), 20 cards each, a 12-slice synthetic stack per
  card (numbered rings; no anatomy). Built with Anki's own Python package in a sandbox profile, never a real
  one.
- **A failure** is a card side whose badge is still red 1 s after it shows, and again 3 s later. A badge that turns
  green between the two reads counts as a late run.
- **Hosts:** Anki desktop 26.9.2 on macOS, driven by a sandbox-only add-on that reads each badge from the page.
  AnkiDroid 2.25.3 on an Android 15 emulator (system WebView 124), driven over adb: it reads the badge through
  Android's accessibility tree, or OCR of a screenshot (macOS Vision) when the tree doesn't hold the card's text
  yet (the new study screen at first), drags once on the stack, shows the answer, reads again and answers Easy.
- **Sync:** the deck was uploaded to a separate test AnkiWeb account, and AnkiDroid was wiped and filled from that
  account before the new-screen run.

Each deck of 20 cards gives 40 shown sides (question and answer), so each row below is 40 renders.

## Results

| Host | Delivery | Sides shown | Viewer ran | Not run | Late | Drags that scrolled |
|---|---|---|---|---|---|---|
| Desktop 26.9.2, macOS | A inline | 40 | 40 | 0 | 0 | – |
| | B src | 40 | 40 | 0 | 0 | – |
| | C loader | 40 | 40 | 0 | 0 | – |
| AnkiDroid 2.25.3, old screen | A inline | 40 | 40 | 0 | 0 | 20 / 20 |
| | B src | 40 | 40 | 0 | 0 | 20 / 20 |
| | C loader | 40 | 40 | 0 | 0 | 20 / 20 |
| AnkiDroid 2.25.3, new screen | A inline | 40 | 40 | 0 | 0 | 20 / 20 |
| | B src | 40 | 40 | 0 | 0 | 20 / 20 |
| | C loader | 40 | 40 | 0 | 0 | 20 / 20 |
| AnkiMobile (iPad) | A, B, C | not run yet | | | | |

**Media sync carries the file.** After the upload, a wiped AnkiDroid logged in to the test account received
`_radscroll-v1.js` byte for byte (same checksum) with the slices, in the same sync.

## Findings that hold for any delivery

- **The back side runs the viewer twice.** `{{FrontSide}}` carries the front's script, and the back template
  has its own block, so every back side showed `runs 2` on every host. The viewer must stay safe to run twice
  (it is: one guarded IIFE, a stack is bound once).
- **An export only carries an underscore file that a template names in full.** Anki's `.apkg` export included
  `_radscroll-v1.js` because the `src` note type names it. A loader that builds the name in code
  (`"_radscroll-" + v + ".js"`) would ship decks without the viewer; the loader must spell the name out.

## Decision

Pending the AnkiMobile rows.

## Still open

- AnkiMobile on the author's iPad: the three decks, 20 cards each, through the test account.
- The update test: a page that already ran probe v1 gets the v2 note types and file; every card must then say
  v2.
