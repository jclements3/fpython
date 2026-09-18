"""make_hpy_course.py -- build HaskellTeacher.pdf, same look and feel as
../../book/PreludeTeacher.pdf (same LaTeX preamble/styles/layout), but
sourced from haskell.py + hpy-course/hw*.py instead of prelude.py.

    python3 make_hpy_course.py        # writes HaskellTeacher.tex, builds the PDF
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
COURSE = ROOT / "hpy-course"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(COURSE))
import hpylib
import verify_hw
import examplelib

EXAMPLES = ROOT / "examples"

# ------------------------------------------------------- chapter plan
# 9 book chapters over haskell.py's 17 code sections, one hw0N.py bank each.
CHAPTERS = [
 (1, "hw01", [1, 2, 3]),
 (2, "hw02", [4, 5, 6]),
 (3, "hw03", [7, 8, 9, 10, 11, 12]),
 (4, "hw04", [13]),
 (5, "hw05", [14]),
 (6, "hw06", [15]),
 (7, "hw07", [16]),
 (8, "hw08", [17]),
 (9, "hw09", []),          # Capstone Labs: homework only, no new concepts
]


def esc(s):
    return (s.replace("\\", r"\textbackslash{}").replace("&", r"\&")
             .replace("%", r"\%").replace("#", r"\#").replace("_", r"\_")
             .replace("$", r"\$").replace("^", r"\^{}").replace("~", r"\~{}")
             .replace("`", "'"))


def prose(txt):
    return esc(" ".join(txt.split()))


def lst(codetext, style="ex"):
    return ("\\begin{lstlisting}[style=%s]\n%s\n\\end{lstlisting}\n"
            % (style, codetext.replace("\u2014", "--")))


def load_hw(stem):
    path = COURSE / (stem + ".py")
    mod = {}
    exec(compile(path.read_text(), str(path), "exec"), mod)
    return mod["TITLE"], mod["ITEMS"]


SECTIONS = {num: (name, entries) for num, name, entries in hpylib.parse(ROOT)}


def render_concept(A, entry):
    names = entry["names"]
    label = "def:" + "-".join(names)
    A("\\subsection{\\texttt{%s}}\\label{%s}\n" % (esc(", ".join(names)), label))
    if entry["gist"]:
        A(prose(entry["gist"]) + "\n")
    if entry["tests"]:
        A(lst(entry["tests"]))
    A("\n\\begin{lstlisting}[style=ex]\n%s\n\\end{lstlisting}\n"
      % entry["code"].replace("\u2014", "--"))


def render_hw(A, items, chapter):
    A("\\section{Homework}\n")
    A(r"""Work in order: drills cement each tool, applies combine them,
challenges are interview-grade. Write each solution in a scratch file with
the given doctests pasted in, and let \texttt{python3 -m doctest} referee.
""")
    for it in items:
        A("\\subsection*{%s\\quad %s\\hfill\\textnormal{\\textit{%s}}}\n"
          % (esc(it["id"]), esc(it["title"]), it["level"]))
        A(prose(it["statement"]) + "\n\n")
        A("\\noindent\\texttt{%s}\n" % esc(it["contract"]))
        A(lst(it["tests"]))
        A("\\noindent\\textbf{Solution.}\n")
        A(lst(it["solution"], "code"))
        A("\\noindent\\textit{Note.} " + prose(it["note"]) + "\n\n")
    A("\\clearpage\n")


def build():
    tex = []
    A = tex.append
    A(r"""\documentclass[10pt,letterpaper]{book}
\usepackage[margin=0.3in,bindingoffset=0.25in,includeheadfoot]{geometry}
\setlength{\headheight}{14pt}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{booktabs}
\usepackage{emptypage}
\usepackage[colorlinks,linkcolor=refcol,urlcolor=refcol]{hyperref}
\definecolor{refcol}{RGB}{20,60,130}
\makeatletter                            % TOC: room for two-digit section numbers
\renewcommand*\l@section{\@dottedtocline{1}{1.5em}{3.2em}}
\makeatother

\definecolor{kw}{RGB}{20,60,130}
\definecolor{cm}{RGB}{80,120,80}
\definecolor{st}{RGB}{150,50,50}
\definecolor{rulecol}{RGB}{170,175,190}
\definecolor{numcol}{RGB}{150,150,150}

\lstdefinestyle{code}{language=Python,basicstyle=\ttfamily\small,
  keywordstyle=\color{kw}\bfseries,commentstyle=\color{cm}\itshape,
  stringstyle=\color{st},showstringspaces=false,keepspaces=true,
  columns=fullflexible,breaklines=true,breakatwhitespace=true,
  postbreak=\mbox{\textcolor{numcol}{$\hookrightarrow$}\space},
  upquote=true,aboveskip=6pt,belowskip=6pt,xleftmargin=1.1em,
  frame=leftline,framerule=0.8pt,rulecolor=\color{rulecol}}
\lstdefinestyle{ex}{basicstyle=\ttfamily\small,keepspaces=true,
  columns=fullflexible,breaklines=true,breakatwhitespace=true,
  postbreak=\mbox{\textcolor{numcol}{$\hookrightarrow$}\space},
  upquote=true,aboveskip=4pt,belowskip=7pt,xleftmargin=1.1em,
  frame=leftline,framerule=0.8pt,rulecolor=\color{rulecol},language={}}
\lstdefinestyle{file}{language=Python,basicstyle=\ttfamily\footnotesize,
  keywordstyle=\color{kw}\bfseries,commentstyle=\color{cm}\itshape,
  stringstyle=\color{st},showstringspaces=false,keepspaces=true,
  columns=fullflexible,breaklines=true,upquote=true,numbers=left,
  numberstyle=\tiny\color{numcol},numbersep=7pt,aboveskip=5pt,belowskip=5pt}

\setcounter{tocdepth}{1}
\setlength{\parskip}{2pt}
""")
    total_hw = sum(len(load_hw(c[1])[1]) for c in CHAPTERS)
    total_ex = len(list(EXAMPLES.glob("*.py")))
    A("\\title{\\Huge\\bfseries Haskell.py Teacher's Edition\\\\[6pt]"
      "\\Large A Complete Course in Idiomatic Functional Python\\\\[14pt]"
      "\\normalsize nine chapters, %d homework problems, "
      "%d compare-and-contrast apps}\n" % (total_hw, total_ex))
    A("\\author{J.~L.~Clements~III}\n\\date{\\today}\n")
    A(r"""\begin{document}
\frontmatter
\maketitle

\chapter{How to Take This Course}
This book teaches \texttt{haskell.py} -- prelude.py's production sibling.
Where prelude.py reimplements every tool from scratch for pedagogy,
haskell.py WRAPS the standard library wherever it already has the tool
(\texttt{scanl} is \texttt{itertools.accumulate}, \texttt{memo} is
\texttt{functools.cache}) -- one vocabulary, zero reimplementation. Failure
is a value throughout: a true \texttt{NOTHING} sentinel keeps \texttt{None}
legal as everyday data, parsers fail with \texttt{FAIL}, and \texttt{Either}
carries WHY.

Each chapter has two movements. \textbf{Concepts}: every function
introduced with its purpose, its worked doctest, and its definition.
\textbf{Homework}: drills cement each tool, applies combine them, and
challenges are interview-grade. Write each solution in a scratch file with
the given doctests pasted in; \texttt{python3 -m doctest} is the referee.

\tableofcontents
\mainmatter
\part{The Nine Chapters}
""")
    for num, hwstem, secnums in CHAPTERS:
        title, items = load_hw(hwstem)
        A("\\chapter{%s}\n" % esc(title))
        if secnums:
            A("\\section{Concepts}\n")
            for sn in secnums:
                _, entries = SECTIONS[sn]
                for e in entries:
                    render_concept(A, e)
        render_hw(A, items, num)
    A(r"""\part{Compare and Contrast: Imperative vs Functional}
\chapter*{About this part}
\addcontentsline{toc}{chapter}{About this part}
Ten small apps, each written twice over the same inputs: once imperative,
once with \texttt{haskell.py}, with a \texttt{\_\_main\_\_} block that
ASSERTS the two agree. Every listing below is verified to actually run and
agree before this book is built -- what you read is what was executed.

\begin{center}\small
\begin{tabular}{@{}p{0.13\textwidth}p{0.40\textwidth}p{0.38\textwidth}@{}}
\toprule
& \textbf{imperative} & \textbf{functional} \\
\midrule
state & mutable slots you maintain & threaded by the combinator \\
errors & exceptions / early return & values (NOTHING, Err) that compose \\
no value yet & hand-rolled sentinel per site & NOTHING, once, in the library \\
passes over data & one loop per concern & monoids fuse concerns into one pass \\
extension & edit inside the loop & add a stage / another \texttt{both} \\
\bottomrule
\end{tabular}
\end{center}
""")
    for stem, title, imp, fn in examplelib.load(EXAMPLES):
        A("\\chapter{%s}\n" % esc(stem))
        A(prose(title) + "\n\n")
        A("\\section*{Imperative}\n")
        A(lst(imp, "code"))
        A("\\section*{Functional}\n")
        A(lst(fn, "code"))
    A(r"""\appendix
\part{Appendices}
\chapter{haskell.py, Complete}
""")
    A(lst(ROOT.joinpath("haskell.py").read_text(), "file"))
    A(r"\backmatter" + "\n" + r"\end{document}" + "\n")

    out = HERE / "HaskellTeacher.tex"
    out.write_text("".join(tex))
    print("wrote", out.name, out.stat().st_size // 1024, "KB")
    return out


def main():
    if verify_hw.main() != 0:
        raise SystemExit("hpy-course verification failed -- book NOT built")
    out = build()
    p = subprocess.run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
         out.name], cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        print(p.stdout.decode(errors="replace")[-3000:])
        raise SystemExit("latexmk failed")
    subprocess.run(["latexmk", "-c", out.name], cwd=HERE, capture_output=True)
    info = subprocess.run(["pdfinfo", str(out.with_suffix(".pdf"))],
                          capture_output=True, text=True).stdout
    pages = [l for l in info.splitlines() if l.startswith("Pages")]
    print(out.stem, pages)


if __name__ == "__main__":
    main()
