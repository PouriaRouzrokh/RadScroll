# 0001 — Viewer delivery

**Status:** open (2026-10-26). Desktop and AnkiDroid (both study screens, and an update from v1 to v2) are
measured: no delivery failed once. AnkiMobile is left (see the end). · **Spike code:** [`spikes/0001-viewer-delivery/`](../../spikes/0001-viewer-delivery/)

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

**The update reaches a page that already ran the old version.** On AnkiDroid's new study screen, the first card
of each deck ran probe v1; then the v2 package (new note-type blocks, `_radscroll-v2.js`) was imported over it, and
every deck was flipped again in the same app session:

| Host | Delivery | Sides shown | Viewer ran | Ran v2 | Not run | Drags that scrolled |
|---|---|---|---|---|---|---|
| AnkiDroid 2.25.3, new screen, after v1 → v2 | A inline | 40 | 40 | 40 | 0 | 20 / 20 |
| | B src | 40 | 40 | 40 | 0 | 20 / 20 |
| | C loader | 40 | 40 | 40 | 0 | 20 / 20 |

**Media sync carries the file.** After the upload, a wiped AnkiDroid logged in to the test account received
`_radscroll-v1.js` byte for byte (same checksum) with the slices, in the same sync.

**Limits of this evidence.** One Android emulator (Android 15, system WebView 124, no Play Store updates), not a
phone; one AnkiDroid release (2.25.3); desktop on macOS only. WebView 124 is older than most phones run, which
is the harder case for an ES2017 bundle, not the easier one.

## Findings that hold for any delivery

- **The back side runs the viewer twice.** `{{FrontSide}}` carries the front's script, and the back template
  has its own block, so every back side showed `runs 2` on every host. The viewer must stay safe to run twice
  (it is: one guarded IIFE, a stack is bound once).
- **An export only carries an underscore file that a template names in full.** Anki's `.apkg` export included
  `_radscroll-v1.js` because the `src` note type names it. A loader that builds the name in code
  (`"_radscroll-" + v + ".js"`) would ship decks without the viewer; the loader must spell the name out.
- **A versioned file still changes the templates on every update.** The template has to name `-v2` instead of
  `-v1`, so the media file saves the size of the block, not the template edit. An unversioned name would avoid
  the edit but risks a cached old copy (a forum add-on deletes and re-adds its file for that reason).

## Decision

Pending the AnkiMobile rows. **Leaning: keep the inline block (A) as the default**, even if AnkiMobile passes B
and C, because on the hosts measured so far the three are equally reliable (0 failures in 480 renders each,
counting the update test), so reliability doesn't separate them; and the media file gains little:

- Every update still edits the templates (see above), which is the step that needs the template manager's care.
- It adds ways to fail that the inline block doesn't have: a card synced before its media (the viewer is missing
  until media sync ends), a deck shared without the file, a user cleaning out underscore files.
- What it saves is ≈ 47 KB per template, which is small next to one stack's slices.

If AnkiMobile fails B or C, the decision is A without question. If it passes, the record closes on A with the
loader (C) noted as the tested fallback, should template size ever matter.

## Still open

- **AnkiMobile on the author's iPad**, through the test account: the three decks, 20 cards each (40 sides), then
  the v1 → v2 update by sync. Steps: sync the iPad with the real account; log out; log in to the test account and
  download; review "RS spike 1::A inline", "B src", "C loader" (front and back of each card), noting any red
  badge and the last badge text in each deck; then the update sync and one more pass; finally log out, log in to
  the real account and choose **Download from AnkiWeb** (never Upload).
- A real Android phone with a current WebView: comes with milestone 1's device checklist (the borrowed Android).
