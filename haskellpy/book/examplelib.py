"""examplelib.py -- extract imperative/functional code blocks from
haskellpy/examples/*.py for the book's Compare and Contrast part.

Each example file has a module docstring (one-line description), a
"# --- imperative ---" section, a "# --- functional ---" section, and a
"# --- demo ---" __main__ block. Runs every example first (subprocess,
PYTHONPATH set) and refuses to return anything if one fails, so the book
can never print an example that doesn't actually agree.
"""
import subprocess
import sys
from pathlib import Path


def _section(lines, tag):
    starts = [i for i, l in enumerate(lines) if l.strip() == f"# --- {tag} ---"]
    if not starts:
        return None
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines))
               if lines[i].startswith("# --- ")), len(lines))
    return "\n".join(lines[start + 1:end]).strip("\n")


def load(examples_dir):
    """[(stem, title, imperative_code, functional_code, oop_code_or_None,
    demo_code, demo_output)], run-verified. oop_code is None for examples
    with no "# --- oop ---" section -- not every problem's domain is
    naturally class-shaped. demo_output is the example's OWN captured
    stdout from the run that just verified it, not a fabricated
    transcript -- what the book prints is what actually executed."""
    out = []
    for path in sorted(examples_dir.glob("*.py")):
        r = subprocess.run([sys.executable, path.name], cwd=examples_dir,
                           env={**__import__("os").environ,
                                "PYTHONPATH": str(examples_dir.parent)},
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f"example {path.name} failed:\n{r.stdout}\n{r.stderr}")
        text = path.read_text()
        title = " ".join(text.split('"""')[1].split()).split(" -- ", 1)
        title = title[1] if len(title) > 1 else title[0]
        lines = text.splitlines()
        imp = _section(lines, "imperative")
        fn = _section(lines, "functional")
        oop = _section(lines, "oop")
        demo = _section(lines, "demo")
        out.append((path.stem, title.rstrip("."), imp, fn, oop,
                    demo, r.stdout.rstrip("\n")))
    return out
