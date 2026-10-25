# RadScroll

**Scrollable CT / MRI stacks for your flashcards.** An open-source add-on for Anki that turns a screen recording,
a set of images, a DICOM series or a Radiopaedia case into a stack you scroll like PACS, on Anki desktop,
AnkiMobile and AnkiDroid.

> **Status: planning.** Nothing to install yet. The plan is in [`docs/PRD.md`](docs/PRD.md).

> **⚠️ Not HIPAA compliant.** RadScroll is a study tool, not a de-identification tool, and makes no compliance
> claim. Masking and cropping can miss patient details. Only record, store, sync or share images you are allowed to,
> and remove patient details yourself. AnkiWeb and AI providers are third parties.

## What it will do

- **Make stacks from what you already have.** Drop a screen recording of yourself scrolling a series: repeated,
  blurred and stray frames are removed and each slice is kept once. Or drop images, a DICOM series, or paste a
  Radiopaedia case link.
- **Scroll like a workstation, on your phone too.** Wheel or drag on desktop; hold-and-drag, pinch-zoom, pan,
  double tap and full screen on iPhone, iPad and Android. Nothing to install on the phone: the viewer travels
  with your cards.
- **Several series on one card**, and a clean stack on the front with its annotated twin on the back, scrolling in
  step.
- **Plain Anki data.** Slices are ordinary media files; cards sync through AnkiWeb or your own sync server.
- **Any recorder, any format.** Mac, Windows, Linux or phone recordings (MP4, MOV, MKV, WebM, GIF…). The image area
  is found and cropped automatically, with a small black margin.
- **No AI needed.** Optionally, add your own AI key (OpenRouter, OpenAI, Gemini, Anthropic) or a local model
  (Ollama) in RadScroll's settings for extras such as finding burned-in text.
- **Privacy first.** Nothing leaves your computer unless you start it. Tools to mask patient details are built in.

## Licence

[AGPL-3.0](LICENSE). Not affiliated with Anki / Ankitects or Radiopaedia.
