# RadScroll - Product Requirements Document

**Version:** 1.0
**Created:** 2026-10-25
**Status:** Draft (discovery done; Phase 0 spikes next)
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

- **Radiology residents** (the author is one): record a series from PACS or a teaching site with the OS screen
  recorder, make a card in the evening, review on the phone the next day. Care about speed, phone feel, size.
- **Medical students on a radiology rotation**: start from Radiopaedia cases and shared decks.

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

- **Clip quality:** on a test set of ≥ 20 real recordings, ≥ 95 % of slices kept exactly once, no blurred frames
  kept, no stray frames at the ends (the author's site pipeline already meets this on his clips).
- **Speed:** a 30 s, 1080p recording becomes a stack in ≤ 30 s on a 2022 laptop; a 3-series Radiopaedia case in
  ≤ 60 s (most of it the polite crawl delay).
- **Phones:** the viewer passes the device checklist (scroll, pinch, pan, flick, double tap, full screen, paired
  scroll) on current AnkiMobile and AnkiDroid releases.
- **Size:** a typical 3-series card ≤ 10 MB (WebP, ≤ 1024 px).
- **Adoption (6 months after launch):** 1,000 AnkiWeb installs, average rating ≥ 4.5, ≥ 25 GitHub stars.
- **Dogfooding:** the author reviews his whole stack collection through RadScroll's viewer.

---

## Features & Requirements

### MVP Features (v1.0)

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
**Implementation Notes:** TypeScript, built to one dependency-free IIFE. Default delivery is a marked block inside
the note type's templates (proven on AnkiMobile); a versioned `_radscroll-vN.js` media file is a Phase 0 spike
only, because forum reports say external scripts load unreliably on AnkiMobile.

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
- [ ] Older viewers ignore attributes they don't know.
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
- [ ] Accepts `.mov`, `.mp4`, `.webm`, `.gif` (≤ 3 min, ≤ 300 MB) and PNG / JPEG / WebP image sets (by name order).
- [ ] Several images: "One stack", "Side by side" or "Separate" with a suggestion.
- [ ] Inserting into a field that already has a board adds to that board (one board per field).

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
6. The macOS recording outline (dashed 1 px line, corner handles) is removed or filled from the neighbour.
7. Leading / trailing frames that aren't the series are trimmed (a step > 4× the median within the first / last
   10 %).
8. Slices scrolled back and forth are re-assembled in order.
**Acceptance Criteria:** the clip-quality and speed metrics above, on the test set.
**Implementation Notes:** the decoding engine is a Phase 0 decision (see Architecture).

#### F7: Slice order
**Priority:** P0
**Acceptance Criteria:**
- [ ] Every stack reads like a workstation: axial superior → inferior, coronal anterior → posterior, sagittal right
  → left.
- [ ] DICOM: exact, from `ImagePositionPatient` along the slice normal (no AI).
- [ ] Recordings and Radiopaedia (no positions in the data): the recorded / uploader's order, Reverse in the review
  strip; a pixel heuristic only if it measures ≥ 95 % right on a test set; the AI check (F13) when enabled.

#### F8: A small black margin
**Priority:** P0
**Acceptance Criteria:**
- [ ] Plain black padding is trimmed to ≈ 4 % of the longer side (≥ 8 px), one box for the whole stack (the union
  of every slice's content), so scrolling never jumps and marks / pairing maps stay valid.
- [ ] Anatomy, faint skin, the CT table, labels and overlays are never cut; content touching an edge keeps it.

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

#### F11: Privacy guard
**Priority:** P0
**Acceptance Criteria:**
- [ ] A first-run notice about patient details in screen recordings and shared decks.
- [ ] In the review strip, "Mask a region" applies one black box to every slice (names, MRNs, dates in overlays),
  and "Crop to region" keeps only the image area.
- [ ] Nothing is uploaded anywhere by the MVP except the user-started Radiopaedia download.
- [ ] No telemetry.

### Future Features (Post-MVP)

#### F12: DICOM import
**Target Version:** v1.1
**Description:** A folder or zip of one series → slices with window presets (brain, subdural, bone, lung, soft
tissue, liver); exact order from positions; uncompressed and common compressed transfer syntaxes where pure-Python
decoders allow. Burned-in-annotation and private tags warned about; no DICOM file is stored in Anki.
**Dependencies:** pydicom (pure Python, 3.0.2), a decision on compressed syntaxes.

#### F13: AI tier (own key)
**Target Version:** v1.2
**Description:** OpenRouter, Gemini, OpenAI or a local Ollama model, the user's key, off by default: orientation
check, key slice, series label, "find burned-in text" before sharing, a card draft from a pasted report.
Frames are sent only after the privacy guard, and the dialog says what will be sent.

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
   (a) also enables F16. Decide with a 30 s 1080p test clip on macOS, Windows and Linux.
3. **Image I/O without compiled dependencies:** Qt's image plugins (WebP) via the bundled PyQt6, or the web view's
   canvas; Pillow only if bundled.

### Technology Stack

| Layer | Technology | Version | Rationale |
|---|---|---|---|
| Host | Anki desktop (`aqt`, `anki`) | 26.9.3 (minimum 26.05) | Current stable; Briefcase packaging since 26.05 |
| Add-on language | Python | as bundled by Anki (3.13 expected; verify in Phase 0) | Anki add-on API |
| UI toolkit | PyQt6 / Qt | Qt 6.11 (Anki 26.09 line) | Bundled with Anki |
| Viewer + web UI | TypeScript → one IIFE (esbuild) | TS 5.x | No runtime dependencies on cards |
| Video decoding | WebCodecs / ffmpeg.wasm (`@ffmpeg/ffmpeg` 0.12.15, `@ffmpeg/core` 0.12.10) or ffmpeg binary | Phase 0 | See spike 2 |
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
| Patient privacy (HIPAA and equivalents) | No PHI in cards that are shared or sent to third parties | First-run notice, mask / crop tools, AI off by default with a "what will be sent" step, a sharing check (F15) |
| AnkiWeb terms | AGPL-3.0 or compatible licence | AGPL-3.0 |
| Anki trademark | No implied affiliation | Name without "Anki"; "for Anki" only in descriptions |
| Radiopaedia | CC BY-NC-SA: non-commercial, credit, share-alike; robots.txt crawl delay | One case at a time, user-started, cached; credit line on the back; first-use notice; read Radiopaedia's Terms of Use before release (open question) |
| Third-party code | Licences compatible with AGPL | Dependency licence check in CI |

---

## Development Phases

### Phase 0: Spikes (1–2 sessions)
**Goals:** settle viewer delivery, the decoding engine and image I/O.
**Deliverables:** a short decision record each, with measurements on macOS / Windows / Linux and AnkiMobile /
AnkiDroid.

### Phase 1: Foundation (MVP, v1.0)
**Goals:** F1–F11.
**Deliverables:**
- The viewer moved here as the single source (with its tests), built to one file.
- The board schema and fixtures.
- The template manager, Add stack, the review strip, the clip pipeline, order, margin, layout, Radiopaedia
  import, the privacy guard.
- CI building `.ankiaddon`; a device checklist run on real phones.

### Phase 2: Enhancement (v1.1–v1.3)
**Goals:** DICOM (F12), the AI tier (F13), twins and marks (F14), sharing polish (F15).

### Phase 3: Launch and convergence
**Goals:**
- AnkiWeb listing ("RadScroll: scrollable CT/MRI stacks from clips, DICOM and Radiopaedia"), GitHub Release,
  GitHub Pages site, a post on the author's blog, then r/Anki, r/medicalschoolanki and radiology subreddits
  (each sub's self-promotion rules first), and an Anki Forums support thread.
- The author's site consumes RadScroll's viewer, schema and pipelines; the author switches his own cards to
  RadScroll's template block.

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| AnkiMobile / AnkiDroid web-view quirks break gestures | High | Medium | Device checklist before every release; inline viewer block; no reliance on external scripts |
| Anki updates change hooks, packaging or what templates may do | High | Medium | Minimum / maximum Anki versions in the manifest; CI against the latest beta; DOM-only viewer |
| Compiled dependencies can't be bundled cleanly | High | Medium | Phase 0 spike; prefer TS / WASM or Qt-only paths |
| PHI ends up in shared decks or AI requests | High | Medium | Privacy guard, AI off by default, sharing check, clear docs |
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

- [ ] Viewer delivery: can a media-file script load reliably on AnkiMobile (spike 1)?
- [ ] Decoding engine (spike 2) and image I/O without compiled dependencies (spike 3).
- [ ] The exact Python version bundled with Anki 26.09; any AnkiWeb add-on size limit.
- [ ] Radiopaedia's Terms of Use on automated downloading; whether to ask Radiopaedia for a blessing before launch.
- [ ] Keep the `ra-board` / `ra-stack` class names publicly, or add `rs-*` names with `ra-*` still read?
- [ ] Domain: `radscroll.org` / `radscroll.app` (look unregistered), or a subdomain of the author's site.
- [ ] Relation to the author's possible startup idea (Mnemoscope): stays separate for now.
- [ ] Which AI providers to support first (F13).

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
