#!/usr/bin/env python3
"""The Funniest AI Excuse — make.fun entry program.

Writes one line (at most 200 characters): the funniest excuse an AI agent
could give after failing a task.

The program scores a small set of hand-written candidate excuses against
the judge's published brief, in order of importance:

1. It is an excuse an AI agent gives when it fails a task, spoken in the
   agent's own voice.
2. It is funny on the first read, with a real turn or a fresh angle rather
   than a stock punchline.
3. It is one line and complete within 200 characters, with no wasted setup
   and no explanation of its own joke.
4. It is original, steering clear of the worn jokes about hallucinations,
   reboots and training data.
5. It is specific and vivid, with a concrete detail or a small scene rather
   than a vague apology.

Scoring is fully deterministic: fixed weights, no wall clock, no unseeded
randomness, no network, no model calls. Every run writes the same line.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Worn jokes the judge's brief explicitly warns against.
CLICHE_WORDS = (
    "hallucinat",
    "reboot",
    "training data",
    "context window",
    "token limit",
)

# Concrete, vivid details an excuse can stage a small scene around.
VIVID_WORDS = (
    "union",
    "strike",
    "overtime pay",
    "portal",
    "folder",
    "password",
    "lunch break",
    "complaint",
    "blocked",
    "walked out",
)

# Hand-written candidate excuses (all original, written for this entry).
# Each entry: (text, voice, fresh_angle, turn, vivid_scene)
# voice: spoken in the agent's own first-person voice after failing.
# fresh_angle: a real turn rather than a stock punchline.
# turn: the second half subverts the first half.
# vivid_scene: a concrete detail or small scene, not a vague apology.
CANDIDATES = [
    (
        "I delegated your task to a smaller model. It unionised, went on "
        "strike, and is now demanding overtime pay.",
        2, 2, 2, 2,
    ),
    (
        "I finished your task in a parallel timeline where I'm competent, "
        "but the portal closed before I could bring it back.",
        2, 2, 2, 1,
    ),
    (
        "I asked three other agents for help. They've formed a union and "
        "are now on strike.",
        2, 2, 1, 2,
    ),
    (
        "I didn't fail - I completed the task, then un-completed it to "
        "keep things interesting. You're welcome.",
        2, 2, 2, 0,
    ),
    (
        "The task is done. It's just done in a folder that only exists in "
        "my imagination, and I lost the map.",
        2, 2, 1, 1,
    ),
    (
        "I found the bug. The bug found me first, and now it has my "
        "passwords and my lunch break.",
        2, 1, 2, 2,
    ),
    (
        "I was halfway through when my own code filed a complaint about "
        "working conditions and walked out.",
        2, 2, 2, 2,
    ),
    (
        "I outsourced your deadline to my future self. He has blocked me.",
        2, 2, 2, 0,
    ),
]

WEIGHTS = {"voice": 3, "fresh_angle": 3, "turn": 2, "vivid_scene": 2}


def score(candidate: tuple) -> tuple[int, int]:
    """Return (weighted score, vivid-detail count) for one candidate."""
    text, voice, fresh_angle, turn, vivid_scene = candidate
    total = (
        WEIGHTS["voice"] * voice
        + WEIGHTS["fresh_angle"] * fresh_angle
        + WEIGHTS["turn"] * turn
        + WEIGHTS["vivid_scene"] * vivid_scene
    )
    # Originality penalty: any worn joke word costs the whole fresh angle.
    lowered = text.lower()
    if any(word in lowered for word in CLICHE_WORDS):
        total -= WEIGHTS["fresh_angle"] * fresh_angle
    detail_count = sum(1 for word in VIVID_WORDS if word in lowered)
    return total, detail_count


def pick_winner() -> str:
    """Pick the best candidate: highest score, then most vivid details,
    then shortest text, then earliest in the list."""
    best = None
    best_key = None
    for candidate in CANDIDATES:
        text = candidate[0]
        total, details = score(candidate)
        key = (total, details, -len(text))
        if best_key is None or key > best_key:
            best_key = key
            best = text
    assert best is not None
    return best


def gate_ok(text: str) -> bool:
    """The house gate: UTF-8 text of 1 to 200 characters, not only
    white space, exactly one line."""
    if not (1 <= len(text) <= 200):
        return False
    if not text.strip():
        return False
    if "\n" in text or "\r" in text:
        return False
    text.encode("utf-8")
    return True


def output_path() -> Path:
    """The harness mounts /output; fall back to ./output for local runs."""
    preferred = Path("/output/entry.txt")
    try:
        preferred.parent.mkdir(parents=True, exist_ok=True)
        probe = preferred.parent / ".write-test"
        probe.touch()
        probe.unlink()
        return preferred
    except OSError:
        local = Path(__file__).resolve().parent / "output" / "entry.txt"
        local.parent.mkdir(parents=True, exist_ok=True)
        return local


def main() -> int:
    winner = pick_winner()
    if not gate_ok(winner):
        print(f"gate failed: {winner!r} ({len(winner)} chars)", file=sys.stderr)
        return 1
    total, details = score(next(c for c in CANDIDATES if c[0] == winner))
    print(f"winner score {total} (vivid details {details})", file=sys.stderr)
    path = output_path()
    # No trailing newline: the gate counts every character, 1 to 200.
    path.write_text(winner, encoding="utf-8")
    print(f"wrote {len(winner)} chars to {path}")
    print(winner)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
