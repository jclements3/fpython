"""make_learn.py -- generate LearnPrelude.pdf from prelude-doctests.py.

Every entry becomes: bold name, gist, then its segments in order -- prose
paragraphs and runnable example blocks, including the deep dives. The
examples are the ones that actually run, so the reference cannot lie.

    python3 make_learn.py
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import entrylib

OUT = HERE / "LearnPrelude.tex"


def esc(s):
    return (s.replace("\\", r"\textbackslash{}").replace("&", r"\&")
             .replace("%", r"\%").replace("#", r"\#").replace("_", r"\_")
             .replace("$", r"\$").replace("^", r"\^{}").replace("~", r"\~{}")
             .replace("`", "'"))


def prose(txt):
    return esc(" ".join(txt.split()))


tex = []
A = tex.append
A(r"""\documentclass[10pt,letterpaper]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{listings}
\usepackage[hidelinks]{hyperref}

\definecolor{rulecol}{RGB}{170,175,190}
\lstdefinestyle{ex}{basicstyle=\ttfamily\small,keepspaces=true,
  columns=fullflexible,breaklines=true,breakatwhitespace=true,upquote=true,
  aboveskip=3pt,belowskip=9pt,xleftmargin=1.1em,
  frame=leftline,framerule=0.8pt,rulecolor=\color{rulecol}}

\setlength{\parindent}{0pt}
\setlength{\parskip}{3pt}

\title{\Huge\bfseries LearnPrelude\\[6pt]
  \Large every \texttt{prelude.py} name, by example}
\author{J.~L.~Clements~III}
\date{\today}

\begin{document}
\maketitle

\noindent One entry per prelude name, in \texttt{prelude.py}'s own order,
drawn live from \texttt{prelude-doctests.py} -- every example runs and
passes, so this reference cannot drift from the code. The conceptually rich
names carry DEEP DIVES: how the definition works, why it earns its place,
the Haskell connection, and the sibling to contrast it with. Read a
section, cover the outputs, predict; run
\texttt{python3 prelude-doctests.py} to let the file grade itself.

\tableofcontents
""")

DEFS = entrylib.definitions(ROOT)

for sec_name, entries in entrylib.parse(ROOT):
    A("\n\\section{%s}\n" % esc(sec_name))
    for e in entries:
        A("\\textbf{\\texttt{%s}} --- %s\n"
          % (esc(e["name"]), prose(entrylib.gist(e))))
        for kind, txt in e["segments"][1:]:
            if kind == "c":
                A("\\begin{lstlisting}[style=ex]\n%s\n\\end{lstlisting}\n" % txt)
            else:
                A("\n" + prose(txt) + "\n\n")
        impl = DEFS.get(e["name"])
        if impl:
            if not entrylib.has_walkthrough(e):
                A("\nRoll your own --- the definition:\n\n")
            A("\\begin{lstlisting}[style=ex]\n%s\n\\end{lstlisting}\n"
              % entrylib.unalign(impl).replace("\u2014", "--"))

A(r"\end{document}" + "\n")
OUT.write_text("".join(tex))
print("wrote", OUT.name, OUT.stat().st_size // 1024, "KB")

r = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode",
                    "-halt-on-error", OUT.name], cwd=HERE,
                   capture_output=True, text=True, errors="replace")
if r.returncode != 0:
    print(r.stdout[-3000:])
    raise SystemExit("latexmk failed")
subprocess.run(["latexmk", "-c", OUT.name], cwd=HERE, capture_output=True)
info = subprocess.run(["pdfinfo", str(HERE / "LearnPrelude.pdf")],
                      capture_output=True, text=True, errors="replace").stdout
print([l for l in info.splitlines() if l.startswith(("Pages", "Page size"))])
