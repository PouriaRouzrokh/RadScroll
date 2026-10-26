"""Summarise spike 1 result logs (JSON lines from android_flip.py or the desktop driver) as a Markdown table.

    python3.13 -I summarize.py results/*.jsonl
"""

import collections
import json
import sys


def main(paths: list[str]) -> None:
    rows = collections.defaultdict(lambda: collections.Counter())
    for path in paths:
        seen = set()
        for line in open(path):
            r = json.loads(line)
            if "deck" not in r:
                continue
            screen = r.get("screen", "desktop")
            key = (screen, r["deck"].split("::")[-1], r.get("card"), r["side"])
            if key in seen:  # the desktop driver can read one side twice
                continue
            seen.add(key)
            c = rows[(screen, r["deck"].split("::")[-1])]
            badges = [b[1] if isinstance(b, list) else b for b in r["badges"]]
            ran = bool(badges) and all(b.startswith("RAN") for b in badges)
            c["sides"] += 1
            c["ran"] += ran
            c["late"] += bool(r.get("late"))
            c["not run"] += not ran
            if r.get("scrolled") is not None:
                c["drags"] += 1
                c["scrolled"] += r["scrolled"]
            for b in badges:
                if b.startswith("RAN"):
                    c[b.split("· ")[-2].strip()] += 1  # the probe version
    print("| Host | Delivery | Sides shown | Viewer ran | Not run | Late (> 1 s) | Drags that scrolled | Probe |")
    print("|---|---|---|---|---|---|---|---|")
    for (screen, deck), c in sorted(rows.items()):
        probes = ", ".join(k for k in c if k.startswith("probe"))
        drags = f"{c['scrolled']} / {c['drags']}" if c["drags"] else "–"
        print(f"| {screen} | {deck} | {c['sides']} | {c['ran']} | {c['not run']} | {c['late']} | {drags} | {probes} |")


if __name__ == "__main__":
    main(sys.argv[1:])
