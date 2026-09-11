"""prelude_trainer.py -- Mavis-Beacon-style memory trainer for prelude.py.

Each drill: a prompt ("Write a function that does: ..."), the solution shown at your
current fade level, and you type it. Level 0 shows the whole definition (overtype);
each success fades it further. In Emacs the fade is GRADUAL COLOR: the body blends
toward the background (faint -> fainter -> ghost -> gone) while the signature stays
crisp; the terminal fallback blanks characters instead. A
spaced scheduler decides when each item comes back (misses drop a level and return
sooner). Prompts come from prelude-doctests.py; code comes from prelude.py; your
progress lives in .trainer.json next to this file.

The intended cockpit is Emacs (real editing keys while you type):

    (load "~/projects/fpython/fpython-trainer.el")
    M-x prelude-trainer          ; C-c C-c submit · C-c C-r reveal · C-c C-q quit

Terminal fallback and tools:

    python3 prelude_trainer.py              # terminal session: due items + 4 new
    python3 prelude_trainer.py --new 10     # introduce up to 10 new items instead
    python3 prelude_trainer.py --stats      # progress table

Machine interface (what the Emacs side calls):

    python3 prelude_trainer.py --next-json [--new N]   # one card as JSON
    python3 prelude_trainer.py --grade NAME            # attempt on stdin -> JSON

Scoring ignores comments and column alignment -- you type the code, not the layout.
"""
import difflib
import json
import random
import re
import sys
import textwrap
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE_FILE = HERE / ".trainer.json"

NEW_PER_SESSION = 10
INTERVALS = [60, 600, 3600, 6 * 3600, 86400, 3 * 86400, 7 * 86400, 14 * 86400]
LEVEL_NAMES = ["copy", "faint", "fainter", "ghost", "from scratch"]
PASS, PARTIAL = 0.97, 0.85


# ------------------------------------------------------------------ parsing

def parse_prelude():
    """[(name, section, code)] for every top-level definition, in file order."""
    items, section, in_doc, block = [], "?", False, None
    for line in (HERE / "prelude.py").read_text().splitlines():
        if line.count('"""') % 2 == 1:
            in_doc = not in_doc
            continue
        if in_doc:
            continue
        m = re.match(r"^# ============ \d+\. (.+?) ============", line)
        if m:
            section, block = m.group(1), None
            continue
        if block is not None and line.startswith((" ", "\t")) and line.strip():
            block[2].append(line)
            continue
        block = None
        if re.match(r"^(def |class |[A-Za-z_]\w*\s*=)", line):
            name = (line.split()[1].split("(")[0].rstrip(":")
                    if line.startswith(("def ", "class ")) else line.split()[0])
            block = (name, section, [line])
            items.append(block)
    return [(n, s, "\n".join(ls)) for n, s, ls in items]


def parse_descriptions():
    """name -> prose description, from prelude-doctests.py entries."""
    doc = (HERE / "prelude-doctests.py").read_text().split('r"""')[1].split('"""')[0]
    descs = {}
    for entry in re.split(r"\n\n+", doc):
        lines = entry.strip("\n").splitlines()
        if not lines or " -- " not in lines[0]:
            continue
        name, _, first = lines[0].partition(" -- ")
        prose = [first]
        for ln in lines[1:]:
            if ln.startswith(">>>"):
                break
            prose.append(ln.strip())
        descs[name.strip()] = " ".join(prose)
    return descs


ITEMS = parse_prelude()
DESCS = parse_descriptions()
BY_NAME = {n: (n, s, c) for n, s, c in ITEMS}


# ------------------------------------------------------------------ mechanics

def norm(code):
    """Comparison form: comments gone, indent kept, spacing style erased.
    Spaces around punctuation are dropped entirely, so `f(y,x)` == `f(y, x)`
    and `init=NOTHING` == `init = NOTHING` -- you are graded on the code,
    not on comma style."""
    out = []
    for ln in code.splitlines():
        ln = ln.split("#", 1)[0].rstrip()
        m = re.match(r"(\s*)(.*)$", ln)
        body = re.sub(r"\s{2,}", " ", m.group(2))
        body = re.sub(r"\s*([,()\[\]{}:=+\-*/%<>|&])\s*", r"\1", body)
        out.append(m.group(1) + body)
    while out and not out[-1]:
        out.pop()
    return "\n".join(out)


def anchor_len(first_line):
    if first_line.startswith(("def ", "class ")):
        return first_line.index(":") + 1 if ":" in first_line else len(first_line)
    return first_line.index("=") + 1 if "=" in first_line else len(first_line)


def masked_view(code, level):
    if level == 0:
        return code
    if level >= 4:
        return "  (no scaffold -- from scratch)"
    lines = code.splitlines()
    keep = anchor_len(lines[0])
    frac = {1: 0.35, 2: 0.7, 3: 1.0}[level]
    out = []
    for i, line in enumerate(lines):
        chars = list(line)
        for j, c in enumerate(chars):
            if (i == 0 and j < keep) or c == " ":
                continue
            if level >= 3 or random.random() < frac:
                chars[j] = " "
        out.append("".join(chars).rstrip())
    return "\n".join(out)


def load_state():
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=1))


def grade(code, attempt, st):
    """Score an attempt, update the item's state in place, return a result dict."""
    acc = difflib.SequenceMatcher(None, norm(code), norm(attempt)).ratio() if attempt else 0.0
    level, streak, now = st.get("level", 0), st.get("streak", 0), time.time()
    if acc >= PASS:
        streak += 1
        level = min(4, level + 1)
        due, verdict = now + INTERVALS[min(streak, len(INTERVALS) - 1)], "ok"
    elif acc >= PARTIAL:
        due, verdict = now + 600, "close"
    else:
        streak, level, due, verdict = 0, max(0, st.get("level", 0) - 1), now + 60, "miss"
    st.update(level=level, streak=streak, due=due, seen=st.get("seen", 0) + 1)
    return {"acc": round(acc * 100), "verdict": verdict,
            "next_level": LEVEL_NAMES[level], "streak": streak}


def pick_next(state, n_new):
    """A due item if any; else a fresh one (at most n_new new per 8-hour window);
    else LEARN AHEAD: the soonest item due within the next hour, served early,
    so a sitting never dies while short-interval reps are pending."""
    now = time.time()
    due = [it for it in ITEMS if it[0] in state and state[it[0]]["due"] <= now]
    if due:
        return random.choice(due)
    recent = len([1 for st in state.values() if now - st.get("intro", 0) < 8 * 3600])
    if recent < n_new:
        fresh = [it for it in ITEMS if it[0] not in state]
        if fresh:
            return fresh[0]
    ahead = [it for it in ITEMS if it[0] in state and state[it[0]]["due"] <= now + 3600]
    if ahead:
        return min(ahead, key=lambda it: state[it[0]]["due"])
    return None


def card(item, state):
    name, section, code = item
    st = state.get(name, {})
    level = st.get("level", 0)
    kind = "function" if "lambda" in code or code.startswith(("def", "class")) else "definition"
    return {"name": name, "section": section, "level": level,
            "level_name": LEVEL_NAMES[level], "streak": st.get("streak", 0),
            "prompt": f"Write a {kind} that does: {DESCS.get(name, name)}",
            "view": masked_view(code, level), "answer": code}


# ------------------------------------------------------------------ interfaces

def cmd_next_json(argv):
    state = load_state()
    n_new = int(argv[argv.index("--new") + 1]) if "--new" in argv else NEW_PER_SESSION
    item = pick_next(state, n_new)
    if item is None:
        print(json.dumps({"done": True}))
        return
    if item[0] not in state:                    # mark introduced so --new is a cap
        state[item[0]] = {"level": 0, "streak": 0, "due": time.time(),
                          "intro": time.time()}
        save_state(state)
    print(json.dumps(card(item, state)))


def cmd_grade(argv):
    name = argv[argv.index("--grade") + 1]
    attempt = sys.stdin.read()
    state = load_state()
    _, _, code = BY_NAME[name]
    st = state.setdefault(name, {})
    result = grade(code, attempt, st)
    save_state(state)
    result["answer"] = code
    print(json.dumps(result))


def cmd_stats():
    state, now = load_state(), time.time()
    print(f"{'name':<14} {'section':<22} {'level':<15} streak  due")
    for name, section, _ in ITEMS:
        st = state.get(name)
        if not st:
            continue
        wait = st["due"] - now
        due = "now" if wait <= 0 else f"{wait / 3600:.1f}h"
        print(f"{name:<14} {section:<22} {LEVEL_NAMES[st['level']]:<15} "
              f"{st['streak']:<7}{due}")
    print(f"\n{len([1 for n, _, _ in ITEMS if n in state])}/{len(ITEMS)} items started")


def read_attempt():
    lines = []
    while True:
        try:
            ln = input()
        except EOFError:
            return "\n".join(lines) if lines else "quit"
        if ln.strip() == "q" and not lines:
            return "quit"
        if ln.strip() == "?" and not lines:
            return ""
        if ln == "":
            if lines:
                return "\n".join(lines)
            continue
        lines.append(ln)


def cmd_terminal(argv):
    state = load_state()
    n_new = int(argv[argv.index("--new") + 1]) if "--new" in argv else NEW_PER_SESSION
    now = time.time()
    due = [it for it in ITEMS if it[0] in state and state[it[0]]["due"] <= now]
    fresh = [it for it in ITEMS if it[0] not in state][:n_new]
    queue = due + fresh
    random.shuffle(queue)
    if not queue:
        print("Nothing due and no new items. Try --new N or come back later.")
        return
    print(f"Session: {len(due)} due, {len(fresh)} new. "
          "(empty line = done, ? = give up, q = quit)")
    results = []
    for item in queue:
        c = card(item, state)
        print("\n" + "=" * 78)
        print(f"{c['name']}   [{c['section']}]   {c['level_name']}, streak {c['streak']}")
        print(textwrap.fill(c["prompt"], width=78))
        print("-" * 78)
        print(c["view"])
        print("-" * 78)
        attempt = read_attempt()
        if attempt == "quit":
            break
        st = state.setdefault(item[0], {})
        r = grade(item[2], attempt, st)
        save_state(state)
        results.append(r["acc"])
        print(f"  {r['verdict']} {r['acc']}% -> {r['next_level']}")
        if r["verdict"] != "ok":
            print(item[2])
    if results:
        clean = len([a for a in results if a >= PASS * 100])
        print(f"\nSession done: {len(results)} drills, {clean} clean, "
              f"mean {sum(results) / len(results):.0f}%.")


def main(argv):
    if "--stats" in argv:
        cmd_stats()
    elif "--next-json" in argv:
        cmd_next_json(argv)
    elif "--grade" in argv:
        cmd_grade(argv)
    else:
        cmd_terminal(argv)


if __name__ == u'__main__':
    main(sys.argv[1:])
