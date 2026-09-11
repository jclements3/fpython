"""make_prints.py -- rebuild prelude.pdf and prelude-doctests.pdf.

The two top-level PDFs are color printouts of prelude.py and
prelude-doctests.py: Emacs ps-print (via ps-print-sources.el, under a
headless X server so faces keep their colors) piped through ps2pdf.

    python3 make_prints.py            # both
    python3 make_prints.py prelude.py # just one

Needs: emacs, xvfb-run (package xvfb), ps2pdf (ghostscript), pdfinfo.
"""

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                            # .../fpython
SOURCES = ["prelude.py", "prelude-doctests.py"]

files = sys.argv[1:] or SOURCES
env = dict(os.environ, PSPRINT_FILES=" ".join(str(ROOT / f) for f in files))
r = subprocess.run(["xvfb-run", "-a", "emacs", "-Q", "-l", str(HERE / "ps-print-sources.el")],
                   env=env, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[-2000:])
    raise SystemExit("emacs ps-print failed")

for f in files:
    ps = (ROOT / f).with_suffix(".ps")
    pdf = ps.with_suffix(".pdf")
    subprocess.run(["ps2pdf", "-sPAPERSIZE=a4", str(ps), str(pdf)], check=True)
    ps.unlink()
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    print(pdf.name, [l for l in info.splitlines() if l.startswith("Pages")])
