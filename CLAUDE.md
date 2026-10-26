# CLAUDE.md — RadScroll

RadScroll is an open-source (AGPL-3.0) Anki add-on: scrollable CT / MR stacks made from screen recordings, image
sets, DICOM series and Radiopaedia cases, with a viewer that runs on Anki desktop, AnkiMobile and AnkiDroid.

**Start here:** [`docs/PRD.md`](docs/PRD.md) is the product plan (features F1–F17, the architecture, the Phase 0
spikes, risks and open questions) and [`docs/PLAN.md`](docs/PLAN.md) is the build and evaluation plan (four internal
milestones with gates, one public release at v1.0, the recorder matrix, the device checklist, the private beta). `.claude/checkpoints/checkpoint-0/prd.md` points to the same file for the
`/pr:mvp-dev` workflow.

**Private context:** if `CLAUDE.local.md` exists (git-ignored, on the owner's machine only), read it first. It says
where the original implementation and the design conversation live. Never copy its contents into tracked files:
this repository is public.

## Status

Phase 0 spikes (PRD v1.4, plan v1.1). One launch, everything in it; no public 0.x releases. Each spike ends in a
short decision record under `docs/decisions/`:
- Spike 2, decoding: decided (record 0002). mpv where Anki ships it (macOS, Windows) or the user installed it
  (Linux), else Qt, with frames handled on Qt's decoding thread. Real recordings and an in-Anki check stay open
  for milestone 1.
- Spike 1, viewer delivery: open (record 0001). Desktop and AnkiDroid (both study screens, and a v1 → v2 update)
  ran every delivery with no failure; leaning to the inline block. AnkiMobile on the iPad is left.
- Spike 3 (image I/O), spike 4 (minimum Anki): not started.

No outreach to Radiopaedia: the playlist download is tried first, the link import stays behind a switch.

## Rules

- **Public repo.** No patient data, no private hostnames, paths, keys or personal infrastructure in tracked files,
  commits or issues. Test media must be synthetic, public-domain or licensed for reuse (record the licence).
- **Real images only.** Never generate or alter anatomy. Allowed: removing duplicate / blurred / stray frames,
  trimming plain black padding to a small margin (≈ 4 %, one box per stack, anatomy never cut), masks that hide
  patient details or answers.
- **Never claim compliance.** RadScroll is not HIPAA compliant and not a de-identification tool. Never write
  "HIPAA", "compliant", "anonymised" or "de-identified" in UI, docs or marketing except to say it is not; the
  disclaimer (PRD F11) shows wherever privacy matters.
- **No AI in the core.** Everything in the MVP is image processing. The AI tier (F13) is optional, the user's own
  key, off by default, and shows what will be sent.
- **Phones run no add-ons.** Anything a card needs at review time lives in the template block (viewer JS + CSS)
  and the field HTML. The viewer makes no network or file requests and leaves no global listeners behind.
- **The board format (`ra-board v1`) is a contract.** The owner's existing cards and his private site use it.
  Additions must be ignorable by older viewers; never rename or remove an attribute without a migration plan.
- **One implementation.** The viewer and pipelines here become the single source for the owner's site too; never
  fork them.
- **Never change a user's fields or card types** (that forces a full sync). Templates are edited only inside
  RadScroll's markers, with a backup first.
- **Radiopaedia:** one case at a time, started by the user, ≥ 10 s between requests to radiopaedia.org, cached,
  credit on the back, nothing on the front that names the case.
- **Names:** no "Anki" or "Radiopaedia" in product names; "for Anki" only in descriptions.
- **Writing:** plain, short sentences in docs and UI text; explain what changed and why in commit messages.

## Workflow

- Design work goes through decision records (`docs/decisions/NNNN-title.md`) before code.
- Commit and push to `main` often (solo project); open issues for anything deferred.
- Tests: pytest for Python, vitest for the viewer, Playwright (WebKit ≈ iOS, Chromium ≈ Android / desktop) for
  gestures. Real-device checks on AnkiMobile and AnkiDroid before every release.
