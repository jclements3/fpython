"""verify_hw.py -- referee for the course homework banks.

    python3 verify_hw.py             # verify every hw*.py in this directory
    python3 verify_hw.py hw05 hw06   # verify matching files only

Each hw file defines CHAPTER (int), TITLE (str) and ITEMS: a list of dicts
with keys id, level (drill|apply|challenge), title, statement, contract,
tests (doctest text), solution (code), note. Every solution is executed in a
namespace containing the whole prelude, then its doctests are run. Exit 0
only if every item passes schema + tests.
"""
import doctest
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent                     # .../prelude

spec = importlib.util.spec_from_file_location("prelude", ROOT / "prelude.py")
_P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_P)
BASE = {k: v for k, v in vars(_P).items() if not k.startswith("__")}

REQUIRED = ["id", "level", "title", "statement", "contract", "tests",
            "solution", "note"]
LEVELS = {"drill", "apply", "challenge"}


def check_file(path):
    mod = {}
    exec(compile(path.read_text(), str(path), "exec"), mod)
    items = mod["ITEMS"]
    ok = bad = 0
    for it in items:
        label = f"{path.name}:{it.get('id', '?')}"
        missing = [k for k in REQUIRED if k not in it or not str(it[k]).strip()]
        if missing or it.get("level") not in LEVELS:
            print(f"FAIL {label}: schema ({missing or it.get('level')})")
            bad += 1
            continue
        if it["tests"].count(">>>") < 3:
            print(f"FAIL {label}: fewer than 3 doctests")
            bad += 1
            continue
        long = [l for l in (it["solution"] + "\n" + it["statement"]).splitlines()
                if len(l) > 105]
        if long:
            print(f"FAIL {label}: line over 105 cols: {long[0][:60]!r}")
            bad += 1
            continue
        ns = dict(BASE)
        try:
            exec(compile(it["solution"], label, "exec"), ns)
        except Exception as e:
            print(f"FAIL {label}: solution raised {type(e).__name__}: {e}")
            bad += 1
            continue
        test = doctest.DocTestParser().get_doctest(it["tests"], ns, label,
                                                   str(path), 0)
        runner = doctest.DocTestRunner(verbose=False)
        runner.run(test)
        if runner.failures:
            print(f"FAIL {label}: {runner.failures} doctest failure(s)")
            bad += 1
        else:
            ok += 1
    counts = {}
    for it in items:
        counts[it.get("level")] = counts.get(it.get("level"), 0) + 1
    print(f"{path.name}: {ok} pass, {bad} fail  {counts}")
    return bad


def main(args):
    pats = args or [""]
    files = sorted(f for f in HERE.glob("hw*.py")
                   if any(f.name.startswith(p) for p in pats))
    if not files:
        print("no hw files matched")
        return 1
    total = sum(check_file(f) for f in files)
    print("ALL PASS" if total == 0 else f"{total} FAILURES")
    return 1 if total else 0


if __name__ == u'__main__':
    sys.exit(main(sys.argv[1:]))
