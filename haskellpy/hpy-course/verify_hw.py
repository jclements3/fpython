"""verify_hw.py -- referee for hpy-course's homework banks.

Unlike book/course/verify_hw.py (each fpython hw item is self-contained),
hpy-course is a RUNNING TUTORIAL: one namespace accumulates every solution
across ALL chapters in order (hw01.1, hw01.2, ..., hw09.4), so a later item
may depend on an earlier one's definition (e.g. hw05's all_ports uses
hw05's own to_port; hw06's sum_of_ratios uses hw05's div_e). This mirrors
gen_book.py's own verification loop exactly.

    python3 verify_hw.py             # verify every hw*.py in order
"""
import doctest
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

spec = importlib.util.spec_from_file_location("haskell", ROOT / "haskell.py")
_H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_H)

PRE_EXTRA = "from operator import eq, itemgetter\n"

REQUIRED = ["id", "level", "title", "statement", "contract", "tests",
            "solution", "note"]
LEVELS = {"drill", "applied", "challenge", "lab"}


def main():
    files = sorted(HERE.glob("hw*.py"))
    ns = {k: v for k, v in vars(_H).items() if not k.startswith("__")}
    exec(compile(PRE_EXTRA, "<extra>", "exec"), ns)
    parser = doctest.DocTestParser()
    ok = bad = 0
    for path in files:
        mod = {}
        exec(compile(path.read_text(), str(path), "exec"), mod)
        for it in mod["ITEMS"]:
            label = f"{path.name}:{it.get('id', '?')}"
            missing = [k for k in REQUIRED if k not in it or not str(it[k]).strip()]
            if missing or it.get("level") not in LEVELS:
                print(f"FAIL {label}: schema ({missing or it.get('level')})")
                bad += 1
                continue
            try:
                exec(compile(it["solution"], label, "exec"), ns)
            except Exception as e:
                print(f"FAIL {label}: solution raised {type(e).__name__}: {e}")
                bad += 1
                continue
            test = parser.get_doctest(it["tests"], ns, label, str(path), 0)
            runner = doctest.DocTestRunner(verbose=False)
            runner.run(test)
            if runner.failures:
                print(f"FAIL {label}: {runner.failures} doctest failure(s)")
                bad += 1
            else:
                ok += 1
    print(f"{ok} pass, {bad} fail")
    print("ALL PASS" if bad == 0 else f"{bad} FAILURES")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
