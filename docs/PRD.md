# RadScroll - Product Requirements Document

**Version:** 1.4
**Created:** 2026-10-25
**Status:** Draft (discovery done; Phase 0 spikes next; the build and evaluation plan is [`PLAN.md`](PLAN.md))
**Owner:** Pouria Rouzrokh
**Licence:** AGPL-3.0

---

## ATLAS Brief

- **Problem:** Radiology learners can't scroll a real CT / MR series on an Anki card the way they scroll it at a
  workstation, and making such a card today is manual (hand-built templates) or paid, closed and limited
  (RadNote: Radiopaedia only, a basic viewer).
- **User:** Radiology residents, fellows and medical students who already study with Anki on a laptop and a phone,
  and who collect cases as screen recordings, image sets, DICOM exports or Radiopaedia cases.
- **Success:** A resident turns a 30-second screen recording, a folder of slices, or a Radiopaedia case link into a
  card in under a minute on desktop, with no AI and no account; the stack scrolls, zooms and goes full screen on
  Anki desktop, AnkiMobile and AnkiDroid; the author moves his own 400+ stack cards onto it with no conversion.
  **A stranger** (someone who has never seen the author's site) installs it from AnkiWeb and makes a first working
  card within ten minutes, on Windows or Linux as well as macOS, without asking for help.
- **Constraints:** Free and open source (AGPL-3.0, AnkiWeb requires AGPL-compatible). No server: everything runs
  in the user's Anki. Phones run no add-ons, so the viewer must work as card-template JavaScript alone. Anki
  26.05+ add-ons must bundle any compiled dependency themselves. Patient privacy is the user's responsibility, but
  the tool must make the safe path easy.

---

## Executive Summary

RadScroll is an open-source Anki add-on that makes scrollable image stacks: a CT or MR series you scroll like PACS,
right on the card. On desktop it turns a screen recording, a set of images, a DICOM series or a Radiopaedia case
into a clean stack: repeated, blurred and stray frames removed, slices in head-to-feet order, black padding
trimmed to a small margin. It writes ordinary Anki media and HTML, so cards sync through AnkiWeb (or any sync
server) and the same viewer runs on AnkiMobile and AnkiDroid with no install there. The viewer is the one the
author built and has used daily on his own cards (scroll, pinch-zoom to 8×, pan, flick, double tap, full screen,
paired clean / annotated stacks). An optional second tier lets users plug in their own AI key for the few jobs
that need judgement. It grows out of the author's private study site, which will adopt RadScroll's parts so both
share one implementation.

---

## Problem Statement

### The Problem

Cross-sectional imaging is learned by scrolling. A frozen slice on a flashcard hides what a resident must
practise: finding the abnormality across a series, telling it from normal anatomy above and below, and seeing its
extent. Anki can hold any HTML, but nothing makes stacks easy:

- Building a scrollable card by hand means a custom template, dozens of slices placed one by one, and JavaScript
  that breaks on phones.
- Screen recordings, the easiest way to capture a series from PACS, a teaching site or a lecture, are video. A
  video on a card plays; it doesn't scroll slice by slice, it repeats frames, and it's large.
- Every slice added by hand is a chance to add a duplicate, a blurred frame or a frame from the wrong series.

### Current Alternatives (surveyed 2026-10-25)

| Option | What it does | Limits |
|---|---|---|
| Anki Forums template (2023) | A note type with a wheel / touch scroll script, up to 4 stacks | No authoring (slices placed by hand), no zoom, "inconsistent" on Android, untested on AnkiMobile, shared by file-host links, unanswered follow-ups in 2024 |
| RadNote (Chrome extension, $3.96/month, closed) | Exports a Radiopaedia case as an `.apkg` with a "scrollable viewer" note type | Radiopaedia only; ~50-line viewer: wheel, arrow keys, vertical drag; no zoom or full screen; a document-level key listener added on every card show; touch scroll not prevented on phones; one viewer per card; 100 KB PNG slices; the diagnosis in the deck name; skipped the case's annotated study; kept the stray reference pictures at the start of each series |
| Image Occlusion, zoom add-ons | Single images | No stacks |
| IMAIOS, BerlinCaseViewer, Radiopaedia | Real stack viewers | No spaced repetition |
| DICOM viewers | Full viewers | Not in Anki |

No open-source tool makes stacks from clips or DICOM for Anki.

### Opportunity

- The author has already solved the hard parts on his private site, under daily use since October 2026: the clip
  → slices pipeline, clean / annotated pairing, orientation, and a phone-tested viewer.
- Anki's community is large and open-source minded; radiology residents are active on r/Anki,
  r/medicalschoolanki and the radiology subreddits.
- The only paid competitor shows demand and leaves the authoring, phone and privacy problems unsolved.

---

## Target Users

### Primary Users

- **Radiology residents** (the author is one): record a series from a teaching site, a lecture or PACS with the OS
  screen recorder, make a card in the evening, review on the phone the next day. Care about speed, phone feel, size.
- **Medical students on a radiology rotation**: start from Radiopaedia cases and shared decks.

**Where most stacks will come from.** The author's own flow is PACS recordings, but for most users the safe and
common sources are Radiopaedia cases, teaching sites, lecture videos and image sets from books or question banks:
these carry no patient details and no institutional policy risk. PACS recordings are often against hospital policy
and always carry patient details. The product therefore treats the Radiopaedia and image-set paths as the ones that
must work for everyone from the first release, and the recording path as the power feature that must fail safely
(a clear message, a manual crop, never a silent bad stack).

### Secondary Users

- **Educators** building shared decks for a residency program (need credit lines, clean exports, privacy).
- **Other image-heavy fields** (anatomy, nuclear medicine, echo clips as slices, pathology Z-stacks): the tool is
  modality-agnostic.
- **The author's private study site**, which will consume RadScroll's viewer and pipelines.

### User Needs

| User Type | Need | Priority |
|---|---|---|
| Resident | Turn a screen recording into a clean stack in under a minute | High |
| Resident | Scroll, zoom and full-screen on iPhone / Android like PACS | High |
| Resident | Several series on one card (axial / coronal / sagittal) | High |
| Resident | Clean stack on the front, annotated twin on the back, scrolling in step | High |
| Student | Import a Radiopaedia case with its findings and credit | High |
| Everyone | No patient details leave their machine or reach shared decks by accident | High |
| Everyone | Cards still show a sensible picture where scripts don't run | High |
| Educator | Small media size; works for people without the add-on (shared deck) | Medium |
| Power user | DICOM import with exact slice order | Medium |
| Power user | Own-key AI help (key slice, labels, orientation check) | Low |

---

## Product Vision

### Mission Statement

Make every CT and MR series on an Anki card scroll like PACS, on every device, for free.

### Core Principles

1. **Real images only.** The tool never generates or alters anatomy. It removes duplicates and padding, orders
   and labels; it never invents pixels. (Masks hide patient details and answers only.)
2. **Works without AI.** Everything in the MVP is image processing. AI is an optional tier with the user's own
   key, used only where judgement is needed.
3. **Phones are first-class.** The phone can't run add-ons, so the viewer is plain template JavaScript, tested on
   AnkiMobile and AnkiDroid before every release.
4. **Plain Anki data.** Slices are ordinary media files referenced by ordinary `<img>` tags; no hidden database,
   no server, no account. Uninstalling leaves cards that still show a still picture.
5. **Privacy by default.** Nothing leaves the machine unless the user starts it (a Radiopaedia download, an AI
   call), and the safe path (crop, mask, warning before sharing) is the easy path.
6. **One implementation.** The viewer and pipelines have one source, shared with the author's site; never forked.

### Success Metrics

- **Clip quality:** on a test set of ≥ 20 recordings covering the F4a recorder matrix, ≥ 95 % of slices kept exactly once, no blurred frames
  kept, no stray frames at the ends (the author's site pipeline already meets this on his clips).
- **Speed:** a 30 s, 1080p recording becomes a stack in ≤ 30 s on a 2022 laptop; a 3-series Radiopaedia case in
  ≤ 60 s (most of it the polite crawl delay).
- **Phones:** the viewer passes the device checklist (scroll, pinch, pan, flick, double tap, full screen, paired
  scroll) on current AnkiMobile and AnkiDroid releases.
- **Size:** a typical 3-series card ≤ 10 MB (WebP, ≤ 1024 px).
- **Works for strangers (private beta, before the one public release):** ≥ 5 private testers (residents or students, at least one each
  on Windows, macOS and Linux, at least one each on AnkiMobile and AnkiDroid) each make a card from their own
  material; median time from install to first scrolling card ≤ 10 min; no tester hits a crash or a silent empty
  stack; every failure they hit ends in a plain message they can act on.
- **Compatibility:** the device matrix in `PLAN.md` passes on the last three Anki desktop releases, the current
  AnkiMobile, and AnkiDroid with both the old and the new study screen.
- **Supportability:** a bug report needs no back-and-forth to reproduce: "Copy diagnostics" gives versions,
  platform, the engine chosen and the last error; test fixtures cover each class of report.
- **Adoption (6 months after launch):** 1,000 AnkiWeb installs, average rating ≥ 4.5, ≥ 25 GitHub stars.
- **Dogfooding:** the author reviews his whole stack collection through RadScroll's viewer.

---

## Features & Requirements

### MVP Features (v1.0)

v1.0 is **one launch with everything below in it** (Pouria, 2026-10-25: "I want everything to be ready before I
launch; a solid product"). It is built in four internal milestones (`PLAN.md`): viewer + template manager + image
sets (F1, F2, F3, F4 images, F9, F11, F17); recordings (F4a, F5, F6, F7, F8); Radiopaedia (F10, if Radiopaedia
agrees; otherwise cut from v1.0); then the whole product through a private beta. Nothing is listed on AnkiWeb or
announced before the last gate.

#### F1: The stack viewer
**Priority:** P0
**Description:** One JavaScript module inside the card template that turns every board in a field into
interactive stacks. Ported from the author's viewer (v18), the single source for both projects.
**User Story:** As a resident, I want to scroll a series on my phone like on a workstation so that I practise
finding the abnormality.
**Acceptance Criteria:**
- [ ] Desktop: wheel / trackpad / drag scroll one slice per step; ↑ ↓ keys; click → full screen; zoom and pan.
- [ ] Phone: tap → full screen; quick drag scrolls the card, hold-then-drag scrolls slices; pinch zooms the stack
  (to 8×), never the page; one finger pans when zoomed; flick with momentum; double tap zooms 2.5× and back.
- [ ] Counter and label ("Coronal non-contrast · 19 / 39"), updated for joined stacks (`data-ra-parts`).
- [ ] Several stacks per board, each scrolling on its own; linked stacks (clean / annotated twin, `data-ra-link`)
  scroll in step; ◀ ▶ jumps between marked slices.
- [ ] Stacks look different from pictures (a thin outline), open on slice 1, the key slice used only as the still.
- [ ] No global listeners left behind between cards (desktop reuses one web view); no network requests; no
  `fetch` of files (Anki 26.09 tightened what notes may read).
- [ ] Where scripts don't run, the still composite shows.
- [ ] Survives every host's way of running card scripts: AnkiDroid's new study screen updates the DOM in parts
  (no `load` / `DOMContentLoaded`, the script may run again in the same scope, so no top-level `let` / `const`, one
  guarded IIFE); desktop reuses one web view (re-scan on every card, no leaked listeners); AnkiMobile's swipes are
  native and can't be stopped by a card (the viewer never needs a horizontal swipe; the docs say which swipe
  settings to turn off); AnkiDroid stops its own gestures over an element only on the new study screen (the
  `tappable` class and `touch-action` are set anyway; a full-screen stack is the reliable path on both phones).
- [ ] Works inside any note type, not only the author's: no assumption about field names, card count or other
  scripts on the card; `ra-` class names stay (they are the contract) and are unlikely to clash; the CSS is scoped
  to `.ra-board`.
**Implementation Notes:** TypeScript, built to one dependency-free IIFE (ES2017 target for older WebViews).
Default delivery is a marked block inside the note type's templates (proven on AnkiMobile); a versioned
`_radscroll-vN.js` media file is a Phase 0 spike only, because forum reports say external scripts load unreliably
on AnkiMobile and AnkiDroid.

#### F2: The board format
**Priority:** P0
**Description:** The HTML a field stores, identical to the author's existing format so his cards need no
conversion.
**Acceptance Criteria:**
- [ ] `<div class="ra-board" data-ra-board="v1">` → `<img class="ra-still">` (the fallback) → `ra-stack` blocks
  of plain `<img src="…">` slices, `data-ra-label / -key / -kind / -link / -map / -marks / -parts` attributes,
  tile geometry in percentages.
- [ ] Every slice is an `<img>` so Check Media and media sync see it; names are content-addressed
  (`ra-s-<sha1>.webp`), so a reused stack costs nothing.
- [ ] Older viewers ignore attributes they don't know; **every parser and writer keeps attributes it doesn't know**
  (the author's site's editor rewrote boards from a fixed list and lost new attributes on every edit; the add-on's
  board round-trip is byte-identical for an untouched board and keeps unknown `data-ra-*` on an edited one).
- [ ] The schema states every index base (slice maps and marks are **1-based** in the author's code; the site's
  design record showed them 0-based, so the schema is the only source from now on).
- [ ] A JSON schema and fixtures in the repo; the author's site tests against the same fixtures.

#### F3: Template manager (enable / update / remove)
**Priority:** P0
**Description:** Puts the viewer in a note type without changing its fields or card types (so no forced full
sync), keeps it current, and takes it out cleanly.
**Acceptance Criteria:**
- [ ] On first run: "Create the RadScroll Case note type" or "Enable stacks on an existing note type".
- [ ] Enabling inserts a marked block (`<!-- RadScroll vN -->`, `/* RadScroll vN */`) into the front and back
  templates and the CSS; nothing outside the markers changes; `scm` unchanged.
- [ ] An add-on update replaces the block on every enabled note type (with a backup first) and tells the user to
  sync every device.
- [ ] Remove restores the templates byte for byte.
- [ ] The RadScroll Case note type mirrors the author's: Question, Image, Answer, AnnotatedImage, KeyFindings,
  PathologySummary, Source.

#### F4: Add stack (editor button)
**Priority:** P0
**Description:** A button and drop target in Anki's editor: a recording, several images, or a Radiopaedia link
(DICOM in F12) → the review strip (F5) → a board inserted in the current field.
**Acceptance Criteria:**
- [ ] Accepts recordings from any common recorder and format (see F4a), ≤ 3 min and ≤ 300 MB by default
  (configurable), and PNG / JPEG / WebP / BMP / TIFF image sets (in natural name order: `img2` before `img10`).
- [ ] Several images: "One stack", "Side by side" or "Separate" with a suggestion.
- [ ] Inserting into a field that already has a board adds to that board (one board per field).

#### F4a: Any recorder, any format
**Priority:** P0
**Description:** People record with whatever they have. The pipeline must not assume the author's macOS
⌘⇧5 recordings.
**User Story:** As a resident on Windows, I want my Snipping Tool (or OBS, or phone) recording to work exactly like a
Mac recording so that I don't have to convert anything.
**Acceptance Criteria:**
- [ ] **Containers / codecs:** MP4, MOV, MKV, WebM, AVI, M4V; H.264, HEVC / H.265 (iPhone and many Mac recordings),
  VP8, VP9, AV1, MJPEG, ProRes; animated GIF, animated WebP and APNG. Anything the engine can't decode fails with a
  plain message naming the codec, never a silent empty stack.
- [ ] **Recorder matrix in the test set** (≥ 2 clips each): macOS Screenshot (⌘⇧5) and QuickTime, Windows
  Snipping Tool and Xbox Game Bar, OBS (constant 30 / 60 fps, so each slice is many identical frames), Loom,
  ShareX (MP4 and GIF), GNOME / KDE recorders, iOS and Android screen recordings (portrait, HEVC, notch and status
  bar), Zoom / Teams lecture recordings, a PACS cine export.
- [ ] **Frame rate:** variable and constant frame rates both work; duplicate frames from constant-rate recorders
  collapse into one run.
- [ ] **Compression noise:** the "same slice / new slice" cut adapts to each clip (it measures the clip's own
  noise floor between identical frames) instead of a fixed 1 %, so heavily compressed or low-bitrate recordings
  (Loom, Teams, phone) don't split one slice into many or merge two.
- [ ] **Screen size and scaling:** HiDPI / Retina, odd sizes, rotation metadata (phone recordings) and letterboxing
  handled; slices keep their true aspect ratio.
- [ ] **Recorder overlays:** the cursor, click highlights, the macOS selection outline, recording timers and
  "recording" badges are ignored or removed (they change little and sit at fixed places).
- [ ] **Orientation within the clip:** a series scrolled down, up, or back and forth comes out once, in order.

#### F5: Review strip
**Priority:** P0
**Acceptance Criteria:**
- [ ] Thumbnails of every slice; what was removed is listed (repeats, blurred, stray frames, trimmed ends) with
  Restore.
- [ ] Reverse, set key slice, delete slices, thin (only on the user's click), label.
- [ ] Size estimate against the budget (≈ 2–4 MB a stack, ≈ 10 MB a card).

#### F6: Clip → slices pipeline
**Priority:** P0
**Description:** The author's algorithm, ported:
1. Pass 1, small grayscale (≈ 200 px), every frame of the variable-frame-rate recording: frame-to-frame change is
   two-humped (< 0.5 % of pixels within a slice, > 1 % at a new slice), so a 1 % cut splits runs; a thin edge ring
   is ignored (the recorder's selection outline, a moving cursor).
2. The last frame of each run is the slice (progressive viewers sharpen last).
3. Repeats (scrolled back) are dropped: mean absolute difference < 1.0 / 255 to an earlier kept slice.
4. Pass 2, full resolution, streamed: only chosen frames decoded and encoded (WebP q80, ≤ 1024 px, grayscale
   unless coloured, so colour arrows survive).
5. Blurred in-between frames of a fast flick, torn frames and cross-fades are dropped, conservatively.
6. The macOS recording outline (dashed 1 px line, corner handles) is removed by **cropping** inside it. Never
   filled from a neighbouring slice: the author's site did that, and it pastes one slice's pixels onto another,
   which breaks "real images only". If the outline can't be cropped away, the frame is kept as recorded.
7. Leading / trailing frames that aren't the series are trimmed (a step > 4× the median within the first / last
   10 %, **and** unlike every kept slice, so a scalp-only top slice of a thin-slice head CT is not cut).
8. Slices scrolled back and forth are re-assembled in order.
9. **Every measurement is taken inside the active region** (the pixels that change across the clip, found in
   pass 1), not over the whole frame. Measured over the whole frame, a 512 px viewport in a 1920 × 1080 recording is
   13 % of the pixels, so real slice steps fall under the repeat threshold and whole stretches of a thin-slice series
   collapse into one slice; blur and blank checks stop firing for the same reason. The region is also the automatic
   crop proposal of F8.
10. **Thresholds adapt to the clip.** The repeat, new-slice and duplicate cuts come from the clip's own noise floor
   (the distribution of within-run frame differences), with the author's constants as minimums; nothing is merged
   on a ratio of the median step alone, since a homogeneous stretch (liver, vertex) has small real steps.
**Acceptance Criteria:** the clip-quality and speed metrics above, on the test set; thinning never drops a marked
slice; a stack is never thinned without the user's click.
**Implementation Notes:** the decoding engine is a Phase 0 decision (see Architecture). Pass 2 decodes only the
chosen frames (by frame index) and crops in the decoder, so its cost grows with slices kept, not frames recorded.

#### F7: Slice order
**Priority:** P0
**Acceptance Criteria:**
- [ ] Every stack reads like a workstation: axial superior → inferior, coronal anterior → posterior, sagittal right
  → left.
- [ ] DICOM: exact, from `ImagePositionPatient` along the slice normal (no AI).
- [ ] Recordings and Radiopaedia (no positions in the data): the recorded / uploader's order, Reverse in the review
  strip; a pixel heuristic only if it measures ≥ 95 % right on a test set; the AI check (F13) when enabled.

#### F8: Crop and mask (manual always, automatic when it is sure)
**Priority:** P0 for the manual crop box, the margin rule and the mask tool; P1 (best effort, milestone 2) for the automatic
viewport; v1.1 for overlay candidates.
**Description:** People record the whole screen, a window, or a rough selection. The stack should hold only the
image, with a small black margin. One crop box applies to the whole stack. The guaranteed path is a crop box the
user drags in the review strip; the automatic rules below only propose a box, show it, and say how sure they are.
A wrong automatic box is worse than none, so when the rules aren't sure the strip opens with the full frame and asks.
**Acceptance Criteria:**
- [ ] **Manual first:** drag a crop box over any slice; the same box applies to every slice; the box is remembered
  per recorder window size, so the next clip from the same setup starts with it.
- [ ] **The image area, found by what changes** (automatic proposal). Across a scrolled series the image changes from slice to slice
  while the PACS / browser / lecture-slide interface around it stays still. The per-pixel change across the whole
  clip marks the image viewport; the crop box is its bounding rectangle, snapped to the viewport's straight edges.
  Works for a full-screen recording of a PACS window, a browser tab, or a slide with a video in it.
- [ ] **Several viewports** (a 2×2 PACS layout where only one pane scrolls; side-by-side series) → the pane that
  changes is kept; if two change in step, the user is asked which (or "keep both as two stacks").
- [ ] **Plain black padding** inside the viewport is trimmed to ≈ 4 % of the longer side (≥ 8 px), one box for
  the whole stack (the union of every slice's content), so scrolling never jumps and marks / pairing maps stay
  valid.
- [ ] **Never cut anatomy:** faint skin, the CT table, and anything that changes between slices stay inside the
  box; content touching an edge keeps that edge.
- [ ] **Overlays found without AI:** inside the viewport, small non-black regions that stay identical on every
  slice while the image around them changes (corner text such as name / MRN / date, W/L, scale bars, the PACS
  logo) are listed as overlay candidates, highlighted in the review strip, with one click to mask them (black box
  on every slice). Text that changes per slice (the slice number) is found by its position in a corner and its
  small size, and offered the same way. Masking is offered, never forced.
- [ ] **Manual override:** drag the crop box or a mask in the review strip; the same box applies to every slice.
- [ ] Optional AI help for what pixel rules can't judge is in F13 ("find text and non-image elements").
- [ ] The automatic viewport is measured on the recorder matrix (F4a) and shipped only when it proposes the right
  box on ≥ 90 % of clips and never proposes a box that cuts anatomy; otherwise it stays off and the manual box is
  the default.

#### F9: Layout
**Priority:** P0
**Acceptance Criteria:**
- [ ] ≤ 3 tiles in a row; "Same height" rows (tiles share a height, widths follow their shapes, the row fills the
  board's width and the board's height fits the rows); nothing cropped.

#### F10: Radiopaedia import
**Priority:** P0
**Description:** Paste one case link → choose series → a filled note. Started by the user, one case at a time.
**Acceptance Criteria:**
- [ ] Polite: `robots.txt` allows `/cases/…` and `/studies/<id>/stacks`; one request at a time, ≥ 10 s apart
  (its crawl delay); stop and explain on 403 / 429 / 503 or a challenge; cache cases and slices locally.
- [ ] Series names from the data (`plane_projection` + `aux_modality`, e.g. "Axial non-contrast").
- [ ] Stray reference pictures removed by code (a first / last picture whose size differs from the series and
  that jumps far from its neighbour; Restore offered).
- [ ] Choices: separate stacks or one joined stack; which series; copy to the back; history on the front.
- [ ] Fields: Question = age, sex, presentation (optional); Image = the clean series; Answer = the case title;
  AnnotatedImage = the case's annotated images with their legend; KeyFindings = each study's findings verbatim;
  PathologySummary = the discussion verbatim + links.
- [ ] Credit on the back: "Case courtesy of <contributor>, Radiopaedia.org, rID: <id>" with the link; nothing on
  the front names the case (its address and title contain the diagnosis).
- [ ] A first-use notice: personal, non-commercial study (CC BY-NC-SA); Radiopaedia may limit heavy use.

#### F11: Masking tools and the "not HIPAA compliant" disclaimer
**Priority:** P0
**Description:** RadScroll is a study tool. It is **not HIPAA compliant**, not a de-identification tool, and makes
no compliance claim of any kind (HIPAA, GDPR or any institution's policy). Masking and cropping help; they do not
guarantee that every patient detail is gone (text burned into the image, faces in 3D reconstructions, details in
the anatomy itself). The user decides what they are allowed to record, keep, sync and share. The tool says this
plainly, every time it matters, regardless of what masking it offers.

**The disclaimer text** (one source string, used everywhere):
> RadScroll is not HIPAA compliant and is not a de-identification tool. Masking and cropping can miss patient
> details. Only record, store, sync or share images you are allowed to, and remove patient details yourself. AnkiWeb
> and AI providers are third parties; RadScroll does not make sending data to them safe or compliant.

**Acceptance Criteria:**
- [ ] **First run:** a notice with the disclaimer that must be acknowledged ("I understand") before the first stack
  is made; shown again after any update that changes it.
- [ ] **Review strip:** a short permanent line under the mask tools ("Masking helps but can miss details. Not
  HIPAA compliant.") with a link to the full text.
- [ ] **AI:** the disclaimer at the top of Settings → AI, and again (with what will be sent) before the first cloud
  call of each session; cloud providers are named as third parties; local models suggested for clinical images.
- [ ] **Sharing:** the "Prepare for sharing" check (F15) and any export repeat it.
- [ ] **Public text:** the README, the AnkiWeb listing and the docs site carry it near the top; the licence's
  no-warranty clause is linked.
- [ ] Nothing in the UI, docs or marketing says "HIPAA", "compliant", "anonymised" or "de-identified" except to say
  it is not.
- [ ] In the review strip, "Mask a region" applies one black box to every slice (names, MRNs, dates in overlays),
  and "Crop to region" keeps only the image area.
- [ ] Nothing is uploaded anywhere by the MVP except the user-started Radiopaedia download.
- [ ] No telemetry.

#### F17: Runs on a stranger's machine
**Priority:** P0
**Description:** The author's site runs on one server he controls; the add-on runs on thousands of machines he
will never see. Every feature above must hold on Windows, macOS and Linux, on the last three Anki releases, with
other add-ons installed, and must be diagnosable from a bug report alone.
**Acceptance Criteria:**
- [ ] **Compatibility matrix** kept in the repo and checked in CI and by hand before each release: Anki versions
  (the current release and the two before it; `min_point_version` set to the oldest that passes, not to the newest
  packaging change), the three desktop platforms, AnkiMobile current, AnkiDroid current with the old and the new
  study screen, dark and light themes, Anki's "Reduce motion" and font-size settings.
- [ ] **No compiled dependency, no download at runtime** unless a Phase 0 record proves there is no other way. The
  add-on uses what Anki already ships (its Python, PyQt6 with QtMultimedia's FFmpeg backend and the WebP image
  plugin, the bundled `mpv`) before anything else.
- [ ] **Fails safe, says why.** Every intake ends in a stack or in one plain message naming the cause (codec, size,
  permissions, a locked collection) and what to do; no stack is written to a note until the user presses Insert;
  an exception anywhere leaves the note and the templates unchanged.
- [ ] **Diagnostics without telemetry:** a "Copy diagnostics" button (versions, platform, engine, the last 50 log
  lines with paths and names stripped) and a log file in `user_files/`; the issue template asks for it.
- [ ] **Coexists:** no monkey-patching of Anki's editor or reviewer; hooks only; the viewer tolerates other
  template scripts; the template manager refuses to touch a template it can't parse and says so.
- [ ] **Leaves cleanly:** Remove restores the templates byte for byte; uninstalling leaves cards that show the still;
  media files are never deleted by the add-on (Check Media stays Anki's job).
- [ ] **Budgets hold on slow machines:** the pipeline reports progress, can be cancelled, and never blocks the UI
  thread; a 3-minute 1080p clip finishes on a 2018 laptop.
- [ ] **Shared decks:** a deck exported with stack cards works for a recipient without the add-on (the viewer is in
  the note type; the media travels with the deck).

### Future Features (Post-MVP)

#### F12: DICOM import
**Target Version:** v1.1
**Description:** A folder or zip of one series → slices with window presets (brain, subdural, bone, lung, soft
tissue, liver); exact order from positions; uncompressed and common compressed transfer syntaxes where pure-Python
decoders allow. Burned-in-annotation and private tags warned about; no DICOM file is stored in Anki.
**Dependencies:** pydicom (pure Python, 3.0.2), a decision on compressed syntaxes.

#### F13: AI tier (own key)
**Target Version:** v1.2
**Description:** Optional help from a vision model, with the user's own key or a local model. Off until the user
sets it up. Never needed for a usable stack.

**What it can do** (each a button in the review strip or the import dialog, never automatic until the user turns
that task on):
- **Find text and non-image elements** the pixel rules (F8) missed or can't judge: burned-in patient details,
  annotations, slide text, logos, a picture-in-picture webcam. Returns boxes; the user sees them and masks with one
  click. It never edits anatomy.
- **Check slice order** (head vs feet) when the data has no positions.
- **Pick a key slice** and **name the series** ("Axial CT, soft-tissue window").
- **Draft the card text** from a pasted report or the Radiopaedia findings (question, answer, key findings), shown
  as a suggestion to accept or edit.

**Where users set it up: RadScroll → Settings → AI** (menu Tools → RadScroll → Settings…, also a ⚙ button in the
review strip). A small Qt dialog, not Anki's raw JSON config editor (which would show keys in plain text):
- **Provider:** OpenRouter (one key, many models), OpenAI, Google Gemini, Anthropic, **Ollama / LM Studio (local,
  no key, nothing leaves the computer)**, or "Custom, OpenAI-compatible" (base URL + key) for anything else.
- **API key:** a masked field with **Test connection**. Stored in the operating system's keychain (macOS
  Keychain, Windows Credential Manager, Linux Secret Service, via the pure-Python `keyring` package if it can be
  bundled; otherwise a file in the add-on's `user_files/` folder with owner-only permissions). **Never** in the
  collection, a note, the synced add-on config, or a log, so it never reaches AnkiWeb, shared decks or GitHub
  issues.
- **Model per task:** a vision model for the image tasks, a text model for drafting; sensible defaults per provider
  (cheap fast models), editable, with a "list models" button where the provider supports it.
- **Tasks on / off:** which buttons appear, and which (if any) run automatically after an import.
- **Privacy:** "Send frames only after masking" (on by default); "Show me exactly what will be sent" (on by
  default: thumbnails + text before the first call of each session); a reminder that cloud providers must not get
  patient data the user isn't allowed to share; a local model recommended for PACS recordings.
- **Cost, before each call:** an estimate on the button's confirmation ("≈ $0.002 with gemini-flash"), from the
  provider's published prices or OpenRouter's reported cost; local models show "free (local)".
- **Cost, in Settings → AI → Usage:** a table the user can always open:
  - spending this month and all time, per provider and per model;
  - the last 50 calls (date, task, model, images sent, tokens, cost), each marked "estimated" or "reported by the
    provider";
  - a **monthly cap** (off by default): past it, every call asks first; an optional hard stop;
  - Reset, and Export as CSV.
  Usage is kept in the add-on's `user_files/` folder on this computer (not synced, never in the collection).
  The dialog says that the provider's own dashboard is the bill of record.

**Implementation Notes:** one small HTTP client (standard library, no provider SDKs) speaking the
OpenAI-compatible chat format, which OpenRouter, OpenAI, Gemini, Ollama and LM Studio all accept, plus Anthropic's
own format; images sent downscaled (≤ 512 px) and only the slices a task needs (first / middle / last for order,
an overview sheet for key slice). Calls run off the UI thread with a timeout; a failure leaves the stack unchanged.

#### F14: Annotated twins and marks
**Target Version:** v1.2
**Description:** Pair a clean recording with an annotated one (coloured marks found by colour), linked scrolling,
arrows / boxes on single slices, ◀ ▶ between marked slices (the viewer already supports these).

#### F15: Shared-deck polish
**Target Version:** v1.3
**Description:** "Prepare for sharing" check (sizes, credits, privacy checklist), burn-in credit option.

#### F16: A no-install web page
**Target Version:** later
**Description:** The same pipeline in a static page (GitHub Pages) that outputs an `.apkg`, for people who don't
install add-ons. Possible only if the pipeline runs in the browser (Phase 0 decision).

### Out of Scope

- MPR, window / level on screen-recorded (8-bit) images, measurements, PACS connections.
- Generated or AI-altered images of any kind.
- Auto-playing cine loops (maybe later as a ▶ button).
- A server, accounts, payments, telemetry.
- Talking to AnkiWeb from code (sync stays Anki's job).
- Bulk downloading from Radiopaedia or any site.

---

## System Architecture

### High-Level Overview

```
┌──────────────────────── Anki desktop (the add-on) ─────────────────────────┐
│  Editor: [Add stack] / drop ──► Intake (clip · images · Radiopaedia · DICOM)│
│                                     │                                       │
│                     Processing core (F6–F9): runs, repeats, blur, outline,  │
│                     trim ends, order, margin, encode WebP                    │
│                                     │                                       │
│                     Review strip (Qt dialog + web view UI)                   │
│                                     │                                       │
│  Writers: col.media (slices, still) · field HTML (ra-board v1) ·            │
│           Template manager (marked viewer block in note types)              │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Anki sync (AnkiWeb or self-hosted)
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
   Anki desktop reviewer         AnkiMobile (iOS)           AnkiDroid
   └─ viewer (template JS)       └─ viewer (template JS)    └─ viewer (template JS)

Shared with the author's site: viewer (TS) · board schema + fixtures · pipeline rules
```

### Key decisions and Phase 0 spikes

1. **Viewer delivery.** Default: marked block in the templates (works on AnkiMobile today). Spike: a versioned
   media file loaded by `<script src>` on AnkiMobile and AnkiDroid; adopt only if it loads reliably.
2. **Decoding engine** (Anki ≥ 26.05 packages add-ons with Briefcase; compiled wheels must be bundled per
   platform and Python version). Candidates, judged on size, speed, H.264 support and maintenance:
   - (a) the pipeline in TypeScript inside a hidden Anki web view, decoding with WebCodecs or ffmpeg.wasm
     (single-thread core; no SharedArrayBuffer). Qt WebEngine plays H.264 only when built with proprietary
     codecs, so WebCodecs H.264 support in Anki's build must be tested; ffmpeg.wasm decodes in software.
   - (b) Python with per-platform numpy and an ffmpeg binary downloaded on first use (checksum-verified).
   - (c) A hybrid: ffmpeg for decoding, pixel work in TypeScript.
   - (d) **What Anki already ships** (checked 2026-10-25 in Anki 26.09.2 on macOS): Python 3.13; PyQt6 with
     QtMultimedia and its **FFmpeg media backend** (`libavcodec` 61 with H.264, HEVC, VP8 / VP9, AV1, MJPEG,
     ProRes, GIF, WebP and APNG decoders) and the **WebP image plugin**; the `anki_audio` package with **mpv
     0.41**. So a pure-Python add-on can decode any recording with `QMediaPlayer` + `QVideoSink` (frames as
     `QImage`, hardware-accelerated where the OS allows) or by running the bundled `mpv` (`--vo=image` with a scale
     filter for pass 1), do the pixel work on `QImage` bytes (downscale, grayscale and compositing in Qt's C++; the
     differencing in Python on ≈ 200 px frames), and encode WebP through `QImage.save`. No wheel, no download,
     no licence question beyond Qt's own. To verify in the spike: the same plugins ship in the Windows and Linux
     builds (`anki_audio` carries mpv for Windows and macOS; Linux may rely on the system mpv, so the Qt path is
     the primary one), decode speed of pass 1 on a 3-minute clip, exact seeking for pass 2, HEVC on Windows without
     the paid Microsoft codec, and rotation metadata.
   (a) also enables F16. **Test (d) first**; it is the only candidate that needs nothing bundled and nothing
   downloaded. Decide with the F4a recorder matrix (H.264, HEVC, VP9, AV1, GIF, constant and variable
   frame rate) on macOS, Windows and Linux: an engine that can't decode HEVC phone recordings or VP9 / AV1 web
   recordings on all three is out, or needs a fallback. Mind codec licensing when bundling decoders.
3. **Image I/O without compiled dependencies:** Qt's image plugins (`libqwebp` is in the macOS build; confirm
   Windows and Linux) via the bundled PyQt6, or the web view's canvas; Pillow only if bundled. TIFF and HEIC come
   from the same plugin set (`qtiff`, `qmacheif` on macOS only).
4. **Minimum Anki version.** The PRD's first draft set 26.05 because of the packaging change. Nothing in the add-on
   needs 26.05: hooks, the editor button, media and note-type APIs are older. Set `min_point_version` to the oldest
   release whose bundled Qt has the FFmpeg backend and WebP plugin (Qt ≥ 6.5, so Anki 24.x or later), then test the
   last three releases and state the floor in the manifest and the README.

### Technology Stack

| Layer | Technology | Version | Rationale |
|---|---|---|---|
| Host | Anki desktop (`aqt`, `anki`) | 26.9.2 current (the author's install); minimum set by spike 4, tested on the last three releases | Current stable; Briefcase packaging since 26.05 |
| Add-on language | Python | 3.13 (Anki 26.09.2 bundle, checked 2026-10-25) | Anki add-on API |
| UI toolkit | PyQt6 / Qt | Qt 6.11 (Anki 26.09 line) | Bundled with Anki |
| Viewer + web UI | TypeScript → one IIFE (esbuild) | TS 5.x | No runtime dependencies on cards |
| Video decoding | Candidate (d) first: QtMultimedia's FFmpeg backend / bundled `mpv`; else WebCodecs / ffmpeg.wasm (`@ffmpeg/ffmpeg` 0.12.15, `@ffmpeg/core` 0.12.10) or an ffmpeg binary | Phase 0 | See spike 2 |
| DICOM | pydicom | 3.0.2 | Pure Python |
| Tests | pytest (+ the `anki` package for collection tests), vitest, Playwright (WebKit ≈ iOS, Chromium ≈ Android / desktop) | current | Headless checks of the viewer and the template manager |
| CI / release | GitHub Actions → `.ankiaddon` artifact | — | Upload to AnkiWeb by hand; GitHub Releases |
| Docs site | GitHub Pages | — | Demo videos, install, privacy |

*Versions checked on 2026-10-25 (PyPI, npm, GitHub releases).*

### Data Model

#### Core Entities

- **Board** (HTML in a field): `ra-board v1`, a still, 1–6 stacks and ≤ 9 tiles, geometry in percentages.
- **Stack** (`ra-stack`): label, kind (`clean` / `annotated`), key slice, link group, slice map (annotated twin →
  clean slice), marked slices, parts (joined series).
- **Slice**: a media file `ra-s-<sha1>.webp`.
- **Source** (on the back): the credit line and link (Radiopaedia, a lecture, a book page).
- **Add-on config** (Anki's add-on config JSON): margin, max side, WebP quality, budgets, Radiopaedia on / off,
  AI provider (keys stored outside the synced collection).

#### Relationships

A field holds at most one board; a board holds stacks and pictures; stacks may link across fields of the same
card (front clean ↔ back annotated). Slices are shared by content hash across stacks and cards.

### External Integrations

| Service | Purpose | Documentation |
|---|---|---|
| Anki add-on API | Hooks, editor buttons, media, note types | https://addon-docs.ankiweb.net/ |
| AnkiWeb add-ons | Distribution | https://docs.ankiweb.net/addons/sharing |
| Radiopaedia (user-started) | Case import | https://radiopaedia.org/robots.txt, licence: CC BY-NC-SA |
| AI providers (optional, own key) | F13 | OpenRouter / Gemini / OpenAI / Ollama docs |

---

## Design Guidelines

### UX Principles

1. **One button, then review.** Every intake ends in the same review strip; nothing is written to a card before
   the user presses Insert.
2. **Say what was removed.** Every automatic removal is listed with Restore; no silent changes.
3. **Feel like PACS.** Scroll speed, inertia and full screen are tuned on real devices, not in a desktop browser.
4. **Never surprise the phone.** Card scrolling and slice scrolling must never fight; no gesture that AnkiMobile
   uses for answering.

### Visual Design

**Style:** Native to Anki: Qt dialogs that follow Anki's light / dark theme; the viewer is black-background,
minimal chrome (counter, label, a thin stack outline).
**Component library:** Qt widgets for dialogs; plain DOM + CSS variables for the viewer.

### Accessibility

- Every action in the review strip reachable by keyboard; visible focus.
- Viewer: counter text readable at 16 px base font, controls ≥ 40 px touch targets, labels with `aria-label`.
- Never rely on colour alone (marked slices have a symbol too).

---

## Security & Compliance

### Authentication & Authorization

None: no accounts, no server. AI keys (F13) are the user's own, stored outside the synced collection.

### Data Protection

- Everything is local. Network use: the user-started Radiopaedia import and, if enabled, the user's AI provider.
- Template JavaScript makes no network or file requests.
- No telemetry, no analytics.

### Compliance Requirements

| Area | Requirement | How Addressed |
|---|---|---|
| Patient privacy (HIPAA, GDPR and equivalents) | **RadScroll is not HIPAA compliant and makes no compliance claim**; it is not a de-identification tool | The disclaimer everywhere it matters (F11); mask / crop tools offered as help, not a guarantee; AI off by default with a "what will be sent" step; local models suggested; a sharing check (F15). Responsibility stays with the user |
| AnkiWeb terms | AGPL-3.0 or compatible licence | AGPL-3.0 |
| Anki trademark | No implied affiliation | Name without "Anki"; "for Anki" only in descriptions |
| Radiopaedia | CC BY-NC-SA: non-commercial, credit, share-alike; robots.txt crawl delay | One case at a time, user-started, cached; credit line on the back; first-use notice; read Radiopaedia's Terms of Use before release (open question) |
| Third-party code | Licences compatible with AGPL | Dependency licence check in CI |

---

## Development Phases

The detailed plan, with what each milestone delivers, how it is tested and the gate at its end, is
[`PLAN.md`](PLAN.md). The milestones are internal: one public release, v1.0, after the last gate. In short:

### Phase 0: Spikes (1–2 sessions)
**Goals:** settle viewer delivery, the decoding engine (candidate (d) first), image I/O and the minimum Anki
version; a first look at the viewer inside a stranger-style note type on AnkiMobile and AnkiDroid (new study screen).
**Deliverables:** a short decision record each, with measurements on macOS / Windows / Linux and AnkiMobile /
AnkiDroid; the recorder matrix started (synthetic or licensed images only).

### Phase 1: "Scroll" (viewer, template manager, image sets)
**Goals:** F1, F2, F3, F4 (images), F9, F11, F17. The author's 400+ cards run on it; the author tests it from scratch on Windows and Linux VMs.
**Deliverables:** the viewer moved here as the single source (with its tests) and built to one file; the board
schema and fixtures; the template manager with backup and byte-for-byte restore; Add stack for images; the
privacy notice; diagnostics; CI building `.ankiaddon` on three platforms; the device checklist run on real phones.

### Phase 2: "Record" (recordings)
**Goals:** F4a, F5, F6, F7, F8 (manual always; automatic viewport only if it passes its bar).
**Deliverables:** the ported pipeline on the chosen engine; the recorder-matrix test set and its measurements; the
review strip; the author's own fresh clips from recorders he doesn't normally use.

### Phase 3: "Import" (Radiopaedia)
**Goals:** F10 by the path chosen in Phase 0 (playlist download first; the link import behind a switch).
**Deliverables:** the import with its politeness tests, on fixtures and a fake server.

### Phase 4: v1.0, the whole product, then the launch
**Goals:** the complete product through a private beta (the first time anyone outside sees it); every gate re-run;
then the one public release.
**Deliverables:** the "Prepare for sharing" basics from F15 that the masking tools need; docs site; the beta's fix
rounds closed; AnkiWeb listing ("RadScroll: scrollable CT/MRI stacks from clips, images and Radiopaedia"), GitHub
Release, a post on the author's blog, then r/Anki, r/medicalschoolanki and radiology subreddits (each sub's
self-promotion rules first), and an Anki Forums support thread.

### Phase 5: Enhancement (v1.1–v1.3) and convergence
**Goals:** DICOM (F12), the AI tier (F13), twins and marks (F14), the rest of sharing polish (F15). The author's
site consumes RadScroll's viewer, schema and pipelines; the author switches his own cards to RadScroll's template
block.

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| AnkiMobile / AnkiDroid web-view quirks break gestures | High | Medium | Device checklist before every release; inline viewer block; no reliance on external scripts |
| Anki updates change hooks, packaging or what templates may do | High | Medium | Minimum / maximum Anki versions in the manifest; CI against the latest beta; DOM-only viewer |
| Compiled dependencies can't be bundled cleanly | High | Medium | Phase 0 spike; prefer TS / WASM or Qt-only paths |
| PHI ends up in shared decks or AI requests | High | Medium | Masking tools with the disclaimer beside them, AI off by default, sharing check, clear docs that name permitted material only |
| Recordings from other tools break the pipeline (codecs, constant frame rate, compression noise, full-screen UI) | High | High | F4a recorder matrix in the test set from Phase 0; adaptive thresholds; viewport detection (F8) |
| An API key leaks (synced config, logs, screenshots in issues) | High | Low | OS keychain or owner-only file outside the collection; masked field; keys never logged |
| An AI provider changes its API or prices | Low | Medium | OpenAI-compatible client; custom base URL; models editable |
| Radiopaedia blocks or objects | Medium | Low | Polite fetching, credit, non-commercial; ask Radiopaedia before launch; the feature can be switched off |
| Large media slows sync | Medium | Medium | WebP, ≤ 1024 px, budgets, content-addressed reuse |
| New AnkiWeb account can't upload yet | Low | Low | The author's existing account; GitHub Releases meanwhile |
| A closed fork re-sells it | Low | Low | AGPL-3.0 |
| Maintenance load from strangers | Medium | Medium | Issue templates, a support thread, clear scope |

---

## Research References

### Sources Consulted

- Anki Forums: scrollable CT/MRI template (2023) and its unanswered 2024 follow-up.
- RadNote site and its exported package for one case (analysed locally, 2026-10-25).
- AnkiWeb sharing docs (`.ankiaddon` packaging), AnkiWeb terms (AGPL-3.0), the add-on account waiting period.
- Forum threads on add-on dependencies under Anki 26.05 (Briefcase) and bundling numpy.
- Forum threads on external scripts in templates (`_file.js`, AnkiMobile reports).
- Qt WebEngine docs: MP4 / H.264 only with proprietary codecs.
- AnkiWeb FAQ: 100 MB per media file, no total media limit.
- Radiopaedia: `robots.txt` (crawl delay 10, `/api/` and search disallowed), licence and attribution guidance,
  the `/studies/<id>/stacks` JSON fields.
- Name checks: RadStax, CaseStacks, RadiologyStack, StackViewer, Cinebot, SliceStack, Stackscope; no RadScroll
  product found (Telerik's `RadScrollView` is an unrelated UI control).

### Version Information

*Checked 2026-10-25:* Anki / aqt 26.9.3 (released 2026-09-23); Qt 6.11 in the 26.09 line; pydicom 3.0.2;
`@ffmpeg/ffmpeg` 0.12.15, `@ffmpeg/core` 0.12.10; numpy 2.5.4 (for comparison only).

---

## Open Questions

- [ ] Viewer delivery: can a media-file script load reliably on AnkiMobile and AnkiDroid (spike 1)?
- [ ] Decoding engine (spike 2: candidate (d) first), image I/O (spike 3) and the minimum Anki version (spike 4).
- [ ] Do the Windows and Linux Anki builds ship the same Qt FFmpeg backend, WebP plugin and mpv as the macOS build?
  Does HEVC decode on Windows without the paid Microsoft codec? Any AnkiWeb add-on size limit?
- [ ] Radiopaedia's Terms of Use on automated downloading. The content licence (CC BY-NC-SA 3.0, checked
  2026-10-25) allows non-commercial study use with their credit format, so the cards are fine. The Terms separately
  forbid access "by any automated or systematic means" and say there is no API for downloading cases; one
  user-started case at a time is polite and not bulk, but it is still code fetching pages. **Decision (Pouria,
  2026-10-25): no outreach; remove the risk by design instead.** (1) Try first in Phase 0 their "download playlist"
  feature, which the Terms sanction "for teaching or personal study": if that download holds the slices in a readable
  form, "import a playlist you downloaded yourself" makes no request at all and becomes the primary path. (2) If the
  paste-a-link path stays, it behaves like one person browsing (one user-started case, ≥ 10 s between requests,
  cached, credit kept) and sits behind a config switch so a release can turn it off if Radiopaedia ever objects.
  (3) It is listed as one intake among others, never the headline.
- [x] Class names: keep `ra-board` / `ra-stack` / `data-ra-*` as they are. They are the contract with the author's
  cards and site; a second name would mean two code paths forever. (Decided 2026-10-25.)
- [ ] An Android test device: the author has none. Borrow one, or use an emulator for the gesture suite and a real
  device from an outside tester for the release checklist.
- [ ] Windows and Linux test machines: a VM each for Phase 0 and CI runners for every release.
- [ ] Domain: `radscroll.org` / `radscroll.app` (look unregistered), or a subdomain of the author's site.
- [ ] Relation to the author's possible startup idea (Mnemoscope): stays separate for now.
- [ ] Which AI providers to support first (F13), and whether `keyring` can be bundled on all three platforms.
- [ ] Whether a local OCR (no AI) is worth bundling for overlay text, or the static-region rule (F8) plus the
  optional AI task is enough.
- [ ] Collecting the F4a recorder matrix: clips of public or synthetic images only (e.g. Radiopaedia cases under
  their licence, phantom scans), recorded with each tool.

---

## Appendix

### Glossary

- **Stack / series:** the ordered slices of one CT / MR acquisition plane.
- **Board:** a field's layout of stacks and pictures.
- **Key slice:** the slice used as the still picture.
- **Twin:** an annotated copy of a stack, linked so both scroll in step.
- **Stray reference picture:** an image of another plane placed at the start or end of a series.
- **PHI:** protected health information (names, record numbers, dates, faces).

### Background

Brainstormed on 2026-10-25 in the author's study workspace, alongside the decision to add a Radiopaedia import to
his private study site first (its design record covers the stray-picture, margin and layout findings that this
PRD reuses).

### Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-10-25 | Pouria Rouzrokh (with Claude) | Initial draft from the brainstorm |
| 1.1 | 2026-10-25 | Pouria Rouzrokh (with Claude) | F4a any recorder / format; F8 automatic crop without AI (viewport by change, overlays by stillness); F13 AI settings, key storage, providers |
| 1.2 | 2026-10-25 | Pouria Rouzrokh (with Claude) | F11 "not HIPAA compliant" disclaimer everywhere it matters; F13 cost shown before each call and in Settings → AI → Usage |
| 1.3 | 2026-10-25 | Pouria Rouzrokh (with Claude) | Critical review: v1.0 in four steps; Radiopaedia and image sets as the paths that must work for everyone, PACS recordings as the power path; F8 manual crop guaranteed, automatic viewport only past a measured bar; F17 "runs on a stranger's machine" (compatibility matrix, diagnostics, fail-safe, coexistence); decoding candidate (d) from what Anki already ships (Qt FFmpeg backend, WebP plugin, mpv; found in 26.09.2); minimum Anki version as a spike; F1 host quirks (AnkiDroid new study screen, swipes); "works for strangers" metrics; Radiopaedia go / no-go (dropped in 1.4); `ra-` names kept; the plan moved to `PLAN.md` |
| 1.4 | 2026-10-25 | Pouria Rouzrokh (with Claude) | His review: one launch with everything in it, no public 0.x releases; the four steps become internal milestones tested by the author alone, with a private beta on the complete product (the first thing anyone outside sees) before the single v1.0 release; "privacy guard" wording replaced by "masking tools" where it described the feature; licensing and politeness kept as the add-on's own obligations; no outreach to Radiopaedia: the playlist download tried first, the link import behind a switch |
