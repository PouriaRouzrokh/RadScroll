"""Throw-away driver for the desktop baseline of spike 1. Install it only in a sandbox base folder.

When the profile opens it reviews every "RS spike 1" deck: on each question and answer it waits, reads every
.rs-status badge from the page, then shows the answer or answers Good. One JSON line per side goes to
spike1-desktop.jsonl in the base folder; Anki closes when the last deck is done.
"""

import json
import time
from pathlib import Path

from aqt import gui_hooks, mw
from aqt.qt import QTimer

WAIT_MS = 800
READ = "JSON.stringify(Array.from(document.querySelectorAll('.rs-status')).map(b => [b.className, b.textContent]))"

state = {"decks": [], "log": None, "deck": None}


def log(row: dict) -> None:
    with state["log"].open("a") as f:
        f.write(json.dumps(row) + "\n")


def next_deck() -> None:
    if not state["decks"]:
        log({"done": True, "t": time.time()})
        mw.close()
        return
    name, did = state["decks"].pop(0)
    state["deck"] = name
    mw.col.decks.select(did)
    mw.moveToState("review")
    QTimer.singleShot(2000, check_finished)


def check_finished() -> None:
    if mw.state != "review":  # the deck ran out of cards: the overview came back
        next_deck()


def read_then(side: str, after) -> None:
    card = mw.reviewer.card

    def got(result: str) -> None:
        log({"deck": state["deck"], "card": card.id, "side": side, "badges": json.loads(result or "[]")})
        after()

    QTimer.singleShot(WAIT_MS, lambda: mw.reviewer.web.evalWithCallback(READ, got))


def on_question(card) -> None:
    read_then("q", lambda: mw.reviewer._showAnswer())


def on_answer(card) -> None:
    def answer() -> None:
        mw.reviewer._answerCard(3)
        QTimer.singleShot(1500, check_finished)

    read_then("a", answer)


def on_open() -> None:
    state["log"] = Path(mw.pm.base) / "spike1-desktop.jsonl"
    state["decks"] = sorted((d.name, d.id) for d in mw.col.decks.all_names_and_ids()
                            if d.name.startswith("RS spike 1::"))
    gui_hooks.reviewer_did_show_question.append(on_question)
    gui_hooks.reviewer_did_show_answer.append(on_answer)
    QTimer.singleShot(1500, next_deck)


gui_hooks.profile_did_open.append(on_open)
