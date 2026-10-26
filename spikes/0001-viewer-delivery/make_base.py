"""Turn a folder holding "User 1/collection.anki2" into an Anki base folder that opens without first-run dialogs.

    PYTHONPATH=/Applications/Anki.app/Contents/Resources/app_packages python3.13 -I make_base.py <base> [addon-dir]

With `addon-dir`, that add-on is copied into the base's addons21 (used for the desktop driver). Then:
    /Applications/Anki.app/Contents/MacOS/Anki -b <base>
"""

import os
import shutil
import sys
from pathlib import Path

PACKAGES = os.environ.get("RADSCROLL_ANKI_PACKAGES", "/Applications/Anki.app/Contents/Resources/app_packages")
if PACKAGES:
    sys.path.insert(0, PACKAGES)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from aqt.profiles import ProfileManager  # noqa: E402


def make_base(base: Path, addon: Path | None) -> None:
    pm = ProfileManager(base)
    pm.setupMeta()
    pm.setLang("en_US")
    if "User 1" not in pm.profiles():
        pm.create("User 1")
    pm.set_last_loaded_profile_name("User 1")
    pm.load("User 1")
    pm.save()
    if addon:
        dest = base / "addons21" / addon.name
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(addon, dest, ignore=shutil.ignore_patterns("__pycache__"))


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        raise SystemExit(__doc__)
    make_base(Path(sys.argv[1]).expanduser(), Path(sys.argv[2]).resolve() if len(sys.argv) == 3 else None)
