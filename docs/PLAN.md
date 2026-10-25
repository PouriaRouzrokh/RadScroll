# RadScroll — build and evaluation plan

**Version:** 1.1 · **Date:** 2026-10-25 · **Goes with:** [`PRD.md`](PRD.md) v1.4

This is the plan for turning the PRD into a tool that works for people the author will never meet. It says what
each step delivers, how it is tested, who tests it, and what must be true before the next step starts. It is a
living document: update it when a decision record changes a step.

The one idea behind the order: **one launch, everything in it, nothing half-done** (Pouria, 2026-10-25: "I want
everything to be ready before I launch; a solid product"). The work is still built in milestones, because each
intake has its own engine, test set and failure modes, but the milestones are internal. Nothing is listed on
AnkiWeb or announced until every v1.0 feature passes its gate and a private beta has used the whole product. Testers
before launch get builds by hand, never a public release.

---

## 1. What "useful" and "robust" mean here

**Useful** means a resident makes a card they will actually review, in minutes, from material they already have.
The three jobs, in the order most users meet them:

1. "I have a Radiopaedia case / a set of slices from a lecture or a book; I want to scroll it on my phone."
2. "I recorded myself scrolling a series; I want that as a stack without hand work."
3. "I want the clean stack on the front and the annotated one on the back, in step."

Everything else (DICOM, AI help, twins by colour, sharing polish) is after those three work for strangers.

**Robust** means the add-on holds on machines and Anki versions the author doesn't have, with other add-ons
installed, on recordings he never made, and fails with a sentence a user can act on. Concretely (PRD F17):
nothing compiled, nothing downloaded, no monkey-patching, a compatibility matrix tested every release, "Copy
diagnostics" in every bug report, byte-for-byte template restore, and a note never touched until Insert.

---

## 2. Milestones and gates

Each milestone ends in an internal build (a tagged commit and a `.ankiaddon` from CI, shared only with the
author and the private testers) and a **gate**: a short list of things that must be true, checked by someone
other than the author where it says so. A milestone that misses its gate does not start the next one; it gets a
fix round instead. The only public release is v1.0, after Gate 4.

### Milestone 0 — Spikes (decision records 0001–0004)

| # | Question | How it is answered | Record |
|---|---|---|---|
| 1 | Viewer delivery: inline block vs `_radscroll-vN.js` media file | A throw-away note type with each delivery, synced to AnkiMobile and AnkiDroid (old and new study screen); 20 card flips each; count failures to run | `0001-viewer-delivery.md` |
| 2 | Decoding engine | Candidate (d) first: `QMediaPlayer` + `QVideoSink` and the bundled `mpv` inside Anki's own Python on macOS, Windows and Linux, against the recorder matrix (§4); measure decode time for pass 1 (≈ 200 px) and pass 2 (full size, chosen frames), seek accuracy, rotation metadata, HEVC on Windows. Fall back to (a)–(c) only if (d) fails a row | `0002-decoding-engine.md` |
| 3 | Image I/O | `QImage` WebP read / write (quality, grayscale, size) on all three platforms; TIFF, BMP, HEIC readers present? | `0003-image-io.md` |
| 4 | Minimum Anki version | Run the M1 prototype on the last three releases and the oldest with Qt ≥ 6.5; set `min_point_version` to the oldest that passes | `0004-minimum-anki.md` |

Also in Step 0: write to Radiopaedia (terms, politeness, the credit format, a heads-up that an add-on will do
one-case-at-a-time imports); borrow or buy an Android test device; set up a Windows and a Linux VM; start the
recorder matrix with licensed images only.

**Gate 0:** four records with numbers; an engine that decodes every row of the matrix on all three platforms (or a
named fallback per failing row); Radiopaedia asked.

### Milestone 1 — "Scroll": viewer, template manager, image sets

Delivers: the viewer moved from the author's site as the single source (TypeScript, its tests, one IIFE build);
the board schema (`ra-board v1`) as a JSON schema with fixtures; the template manager (create "RadScroll Case",
enable on an existing note type, update, remove, with backup and byte-for-byte restore); Add stack from images
(one stack / side by side / separate; natural name order; the review strip's basics: order, reverse, key slice,
delete, label); layout (same-height rows, ≤ 3 per row); the privacy notice (F11) and the disclaimer string;
diagnostics (F17); CI that builds `.ankiaddon` on three platforms and runs pytest + vitest + Playwright.

Tests: viewer unit tests (input maths, linked groups, parts labels, idempotent setup); Playwright gesture tests on
WebKit and Chromium at phone and desktop sizes; template-manager tests on a real collection through the `anki`
package (markers, scm unchanged, scheduling snapshot identical, restore byte-identical, a template edited by hand
inside the markers, two card types, a note type with other scripts); schema fixtures shared with the author's
site; the device checklist (§5) on real phones.

**Gate 1:** the author's 400+ cards render and scroll under the add-on's block with no conversion; two private
testers (one Windows, one macOS, one of them on AnkiDroid) each install the build by hand and make an image-set card
in ≤ 10 min with no help; the device checklist passes; "Copy diagnostics" works; no open P0 issue.

### Milestone 2 — "Record": recordings

Delivers: the clip → slices pipeline ported onto the engine from record 0002 (runs, repeats, blur / tear drop,
recorder outline, end trim, re-assembly); the recorder matrix test set with ground truth; adaptive thresholds
(the clip's own noise floor); the full review strip (what was removed, with Restore; thin only on click; size
against budget; the manual crop box and mask; the automatic viewport only if it passes its bar); slice order
(recorded order, Reverse); progress and cancel; the first beta programme (§6).

Tests: pytest on synthetic clips with known answers (slice count, a scroll back, blurred frames, a cursor, a
constant-rate recorder, a cross-fade, a 2×2 layout) and on every matrix clip (slices kept exactly once ≥ 95 %;
no blurred frame kept; no stray frame at the ends; the viewport box right or absent, never cutting anatomy);
speed on the reference laptop; memory ceiling on a 3-minute clip; cancel mid-way leaves no temp files and no
note change.

**Gate 2:** ≥ 5 private testers across the three platforms and both phones; each makes a card from their
own recording; every clip they send that fails is added to the matrix and fixed or given a plain message; median
install-to-first-stack ≤ 10 min; no crash; no silent empty stack; the automatic viewport shipped only with its
measurement in a decision record.

### Milestone 3 — "Import": Radiopaedia

Delivers (only with Radiopaedia's answer in hand; if the answer is no, F10 is cut from v1.0 and the launch goes
ahead without it): paste a case link → choose series → a filled note; politeness
(robots.txt read and honoured, one request at a time, ≥ 10 s apart, `Retry-After`, stop for hours on 403 / 429 /
503 / a challenge, a bounded cache, an honest User-Agent naming the add-on and its repo); the credit with the
licence on the back; nothing naming the case on the front; the stray-picture rule with Restore; a first-use
notice.

Tests: parser fixtures from cached case JSON (no network in CI); a fake server that counts requests and asserts
the gap and the stop; a front-leak check (the case title's words must not appear in the Question or Image field);
the credit present whenever any Radiopaedia content is on the card, boards or not.

**Gate 3:** a fake Radiopaedia server proves the gap, the stop and the cache; the front-leak check passes on
every fixture case; the credit is present on every fixture card; private testers import three cases each.

### Milestone 4 — v1.0: the whole product, then the launch

Delivers: the "Prepare for sharing" basics the masking tools need (sizes, credits present, the disclaimer); the
docs site; issue templates; the AnkiWeb listing text; the full private beta on the complete product (§6); every
earlier gate re-run on the current Anki; the fix rounds from the beta closed.

**Gate 4 (launch):** every earlier gate green on the current Anki release; the compatibility matrix run by hand on
the three desktops and both phones; no open P0 or P1 issue from the beta; a fresh tester follows the README alone
and succeeds with images, a recording and a Radiopaedia case; the AnkiWeb listing text carries the disclaimer.
Only then: the AnkiWeb listing, the GitHub Release, the blog post, the subreddits, the support thread.

### After v1.0 — v1.1+ and convergence

DICOM (F12, pydicom pure Python, uncompressed and the syntaxes pure Python can read); the AI tier (F13) with its
cost display; twins and marks by colour (F14); the rest of sharing polish (F15); the author's site adopts the
add-on's viewer, schema and pipeline packages (the site keeps its agents, tagging and sync server).

---

## 3. What is ported, and how

The original code lives on the author's site. Most of it is already pure; the rest is tied to that site's
database, agents and server. The port is a copy into this repo with the site-specific parts replaced by
interfaces, never a fork of the shared pieces.

| Piece | Source today | Port |
|---|---|---|
| Viewer | `web/src/components/stacks/viewer.ts` (v19) + `styles.ts` + `build-stack-viewer.mjs` | Copied as-is into `viewer/`; the site then imports the package from here. Fixes found in review (listener lifetime, re-run safety) land here first |
| Board format | written / parsed in `stack_board.py`, the editor's `ankiHtml.ts` | A JSON schema + fixtures in `schema/`; one writer and one parser in the add-on; the parser keeps unknown attributes |
| Clip → slices | `stack_video.py` (numpy + ffmpeg) | The rules (runs, repeats, blur, trim, re-assembly) rewritten over the engine from record 0002: Qt frames, Python arithmetic on ≈ 200 px grayscale, chosen frames decoded once at full size |
| Margin, layout, encoding | `stack_board.py`, `pack.ts` (same height) | Pure arithmetic: port with the fixtures; WebP through `QImage` |
| Pairing, marks by colour | `stack_pairing.py`, `stack_store.marks_by_colour` | Step 4 (F14); pure arithmetic |
| Radiopaedia | `radiopaedia.py` (parser, politeness), `radiopaedia_import.py` (plan, fields), `slice_rules.py` | The pure parts port as-is; fetching rewritten sync / threaded with a file-based rate limit and robots.txt; no local index |
| Template manager | `stacks_template.py`, `viewer_rollout.py` | Same marker scheme; the checks (scm, scheduling snapshot, render) become the add-on's tests and its pre-update guard |

A review of that code (2026-10-25, recorded on the author's site as its own design record) found bugs that the
port must not carry over; the ones that matter for strangers are listed in §7.

---

## 4. The recorder matrix (the test set)

Every clip shows public-domain, synthetic or licensed images (never patient data); the licence is recorded next
to each file. Ground truth per clip: the number of distinct slices, their order, which frames are blurred or
stray, the true image box.

| Recorder / source | Clips | What it stresses |
|---|---|---|
| macOS Screenshot (⌘⇧5), QuickTime | 2 + 2 | variable frame rate, the dashed outline, Retina |
| Windows Snipping Tool, Xbox Game Bar | 2 + 2 | constant 30 / 60 fps, HiDPI scaling, the cursor |
| OBS (30 and 60 fps), ShareX (MP4 and GIF) | 2 + 2 | many identical frames per slice, GIF palette noise |
| Loom, Zoom, Teams | 2 each | heavy compression, webcam picture-in-picture, slide with a video |
| GNOME / KDE recorders | 1 each | VP8 / VP9 WebM |
| iPhone, Android screen recordings | 2 + 2 | HEVC, portrait, rotation metadata, status bar, notch |
| PACS cine export, a browser tab of a teaching site, a 2×2 PACS layout | 2 each | letterboxing, still UI around a changing pane, two panes |
| Scrolled down, up, back and forth; a fast flick; a cross-fade | 1 each | ordering, blur, transitions |

The matrix is the acceptance test for Step 2 and the measurement behind the automatic viewport's on / off.

---

## 5. The device checklist (every release)

Run by hand on: Anki desktop on macOS, Windows and Linux (current release and the two before it); AnkiMobile on
an iPhone and an iPad; AnkiDroid on a phone with the old and with the new study screen. Dark and light themes.

1. A card with one stack opens on slice 1; the still shows with scripts off.
2. Desktop: wheel, trackpad, drag, ↑ ↓, click → full screen, zoom and pan, Esc closes; the next card is clean
   (no stale listeners: scroll the second card's stack 50 times, no drift).
3. Phone: tap → full screen; quick drag scrolls the card; hold-then-drag scrolls slices; pinch zooms the stack
   only; one finger pans when zoomed; flick slows to a stop; double tap in and out; nothing answers the card by
   accident (AnkiMobile swipes set as the docs say; AnkiDroid gestures on both study screens).
4. Three stacks on one board, each on its own; linked twins in step; ◀ ▶ visits marks; a joined stack names its
   part.
5. A card made on desktop appears on the phone after one sync with every slice (Check Media reports nothing
   missing).
6. Template manager: enable, update, remove on a note type with two card types; the other card type unchanged;
   the templates byte-identical after remove; no full-sync prompt on any device.
7. "Copy diagnostics" produces a block with versions, platform, engine and no personal paths.

---

## 6. The beta programme (who tests, how we learn)

- **Who:** 5–10 residents and students found through the author's network (not a public call, since nothing is
  announced before launch); at least one each on Windows, macOS, Linux, AnkiMobile and AnkiDroid; none who know
  the author's site. Two of them start at Gate 1, the rest at Gate 2; all of them run the full product at Milestone 4.
- **What they do:** a one-page script: install the build they were sent, enable stacks on a note type they
  already use (or create the RadScroll Case type), make one card from images, one from their own recording and
  one from a Radiopaedia case, review them on their phone, run Remove. They time the first card.
- **What we collect:** the script's checkboxes, the time, the diagnostics block, and any clip that failed (they
  send it only if it holds no patient data; the form says so in the disclaimer's words).
- **What we do with it:** every failure becomes a fixture or a plain message; the matrix grows; findings are
  closed in a fix round before the gate they belong to is called.
- **No telemetry, ever:** the add-on sends nothing; the beta is forms and e-mail.

---

## 7. Known problems in the original code that the port must fix

From the 2026-10-25 review of the author's implementation (the full list is in that site's design record). The
ones that would hurt strangers:

- **Radiopaedia politeness is per process** and a request already waiting can go out after a 429; robots.txt is
  never read; the User-Agent names another project. The add-on uses a file-based rate limit, reads robots.txt,
  honours `Retry-After`, and sends `RadScroll/<version> (+repo URL)`.
- **A failed study fetch is cached as an empty study for 30 days.** Never cache a non-200; write caches atomically.
- **No credit when a case has no annotated study** (the credit was tied to a back board). The credit goes on the
  back whenever any Radiopaedia content is on the card, with the licence named.
- **An annotated series can be sent to the front through the API** (only the dialog stopped it). A code gate.
- **Double thinning** when "keep every Nth" meets the 300-slice cap. One thinning step.
- **Network errors reach the UI as "Internal Server Error".** Every intake error becomes a sentence.
- The viewer and pipeline findings (listener lifetime, re-run safety, fixed thresholds, end-trim rule, pairing
  indices after thinning) are tracked in the same record and become tests here before the port.

---

## 8. Working rules for this repo

- One decision record per design question before the code for it; the record carries the measurements.
- Commit and push to `main` often; every milestone ends with a tagged internal build and a short changelog in
  plain words; the first public release is v1.0.
- Tests run on three platforms in CI; the device checklist is run by hand and recorded in the release notes.
- The author reviews at each gate on his own devices; outsiders test before Gates 1, 2 and 3.
- The viewer and pipelines have one source, here; the author's site imports them.
- Live AI calls (Step 4) state their cost before running; the MVP makes none.
