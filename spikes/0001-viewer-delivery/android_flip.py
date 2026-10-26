"""Flip the spike 1 cards on AnkiDroid through adb and record what each side's badge says.

    python3.13 -I android_flip.py [--reset <apkg> old|new] <label> <deck> ...
    e.g. android_flip.py --reset rs-spike1-v1.apkg new new "A inline" "B src" "C loader"

With --reset it first wipes AnkiDroid, imports the package and picks the old or new study screen.

Starts from AnkiDroid's deck list with the "RS spike 1" decks imported. For every card it reads the screen through
the accessibility tree (uiautomator, which sees the card web view's text), drags once on the stack to check that a
slice scroll lands, shows the answer, reads again and answers Easy (so no card comes back). A badge still red after
the first read is read again 3 s later, so a late run is told apart from no run. One JSON line per side goes to stdout.
"""

import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ADB = os.environ.get("ADB", "/opt/homebrew/share/android-commandlinetools/platform-tools/adb")
BADGE = re.compile(r"^(RAN ·|NOT RUN ·|LOAD ERROR ·)")
SLICE = re.compile(r"^(\d+) / 12$")


def adb(*args: str) -> str:
    return subprocess.run([ADB, *args], capture_output=True, text=True, check=True).stdout


def screen() -> list[tuple[str, tuple[int, int]]]:
    """(text or content-desc, centre) for every node on screen."""
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    root = ET.fromstring(adb("shell", "cat", "/sdcard/ui.xml"))
    out = []
    for n in root.iter("node"):
        text = n.get("text") or n.get("content-desc") or ""
        x1, y1, x2, y2 = map(int, re.findall(r"\d+", n.get("bounds", "[0,0][0,0]")))
        if text:
            out.append((text, ((x1 + x2) // 2, (y1 + y2) // 2)))
    return out


def find(nodes, pattern: re.Pattern | str):
    for text, xy in nodes:
        if (pattern.search(text) if isinstance(pattern, re.Pattern) else text == pattern):
            return text, xy
    return None


def tap(xy) -> None:
    adb("shell", "input", "tap", str(xy[0]), str(xy[1]))


def read_side() -> dict:
    nodes = screen()
    badges = [t for t, _ in nodes if BADGE.search(t)]
    late = False
    if not badges or any(not b.startswith("RAN") for b in badges):
        time.sleep(3)
        nodes = screen()
        badges2 = [t for t, _ in nodes if BADGE.search(t)]
        late = badges2 != badges and all(b.startswith("RAN") for b in badges2)
        badges = badges2
    label = find(nodes, re.compile(r" · card \d\d / 20$"))
    return {"label": label[0] if label else None, "badges": badges, "late": late, "nodes": nodes}


def drag_scrolls(nodes) -> bool | None:
    """Drag down on the stack: True if the slice number moved, None if no stack was found."""
    at = find(nodes, SLICE)
    img = find(nodes, re.compile(r"^rs-spike1-s\d\d"))
    if not at or not img:
        return None
    x, y = img[1]
    adb("shell", "input", "swipe", str(x), str(y - 100), str(x), str(y + 150), "400")
    time.sleep(0.4)
    after = find(screen(), SLICE)
    return bool(after and after[0] != at[0])


def run_deck(label: str, deck: str) -> None:
    tap(find(screen(), deck)[1])
    time.sleep(3)
    for _ in range(25):  # 20 cards, with room to notice a loop
        time.sleep(1)
        q = read_side()
        if not q["label"] and not q["badges"]:
            break  # the deck is finished
        scrolled = drag_scrolls(q["nodes"])
        print(json.dumps({"screen": label, "deck": deck, "card": q["label"], "side": "q", "badges": q["badges"],
                          "late": q["late"], "scrolled": scrolled}), flush=True)
        tap(find(q["nodes"], "Show answer")[1])
        time.sleep(1)
        a = read_side()
        print(json.dumps({"screen": label, "deck": deck, "card": a["label"], "side": "a", "badges": a["badges"],
                          "late": a["late"]}), flush=True)
        easy = find(a["nodes"], re.compile(r"^Easy"))
        tap(easy[1])
    adb("shell", "input", "keyevent", "KEYCODE_BACK")
    time.sleep(2)


def wait_tap(pattern, timeout: float = 15, pick=lambda hits: hits[0]) -> None:
    """Wait for a node matching `pattern`, then tap the first one (or the one `pick` chooses; None taps nothing)."""
    end = time.time() + timeout
    while time.time() < end:
        nodes = screen()
        hits = [(t, xy) for t, xy in nodes
                if (pattern.search(t) if isinstance(pattern, re.Pattern) else t == pattern)]
        if hits:
            hit = pick(hits)
            if hit:
                tap(hit[1])
                time.sleep(1.5)
            return
        time.sleep(1)
    raise SystemExit(f"not on screen: {pattern}")


def reset(apkg: str, new_screen: bool) -> None:
    """Wipe AnkiDroid (app data and its collection folder), import `apkg` with its deck presets, pick the screen."""
    pkg = "com.ichi2.anki"
    adb("shell", "pm", "clear", pkg)
    adb("shell", "rm", "-rf", "/sdcard/AnkiDroid")
    adb("shell", "appops", "set", pkg, "MANAGE_EXTERNAL_STORAGE", "allow")
    adb("push", apkg, "/sdcard/Download/")
    adb("shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1")
    wait_tap("Get started")
    adb("shell", "am", "force-stop", pkg)  # the permission screen only notices the grant on a fresh start
    adb("shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1")
    wait_tap("More options")
    wait_tap("Import")
    wait_tap(re.compile(r"^Deck package"))
    wait_tap("Show roots")
    wait_tap("Downloads")
    wait_tap(os.path.basename(apkg))
    wait_tap("Add")
    wait_tap("Import any deck presets", pick=lambda hits: hits[-1])  # the switch, not its label
    wait_tap("Import", pick=lambda hits: hits[-1])  # the button, not the title
    wait_tap(re.compile(r"new notes imported"), timeout=30, pick=lambda hits: None)
    adb("shell", "input", "keyevent", "KEYCODE_BACK")
    time.sleep(2)
    if new_screen:
        wait_tap("Open drawer")
        wait_tap("Settings")
        wait_tap("New study screen")
        wait_tap("New study screen", pick=lambda hits: (hits[-1][0], (970, hits[-1][1][1])))  # its switch
        for _ in range(2):
            adb("shell", "input", "keyevent", "KEYCODE_BACK")
            time.sleep(1.5)
    wait_tap(re.compile(r"cards due"), pick=lambda hits: None)  # back on the deck list


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) >= 2 and args[0] == "--reset":
        reset(args[1], new_screen=args[2] == "new")
        args = args[2:]
    if len(args) < 2:
        raise SystemExit(__doc__)
    for d in args[1:]:
        run_deck(args[0], d)
