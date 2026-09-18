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
 (1, "hw01", [1, 2, 3], r"""
A function that names its argument commits to one shape of input; a function
built from other functions (\texttt{compose}, \texttt{on}, \texttt{partial})
stays a transformation, reusable wherever the types line up. This chapter's
five one-liners (\texttt{identity}, \texttt{const}, \texttt{flip},
\texttt{curry}, \texttt{uncurry}) are the adapters that make composition
possible at all -- they change nothing about the values, only the SHAPE of
the call. Two sentinels close the chapter: \texttt{NOTHING} means ``no
answer'', and \texttt{FAIL} means ``the parser gave up'' -- both real
objects, never \texttt{None}, so a function can return an ordinary
\texttt{None} as genuine data without it being mistaken for absence."""),
 (2, "hw02", [4, 5, 6], r"""
A fold collapses a list to one value; a scan is a fold that keeps its
history; an unfold grows a list from a seed instead of consuming one.
\texttt{scanl} here is \emph{exactly} \texttt{itertools.accumulate} --
naming it the Haskell way does not change what runs. \texttt{unfoldr} is
the fold's mirror image: given a step function that returns
\texttt{(value, next\_seed)} or \texttt{NOTHING} to stop, it produces the
whole list, which is why balances, digit sequences and Collatz chains all
turn out to be one \texttt{unfoldr} call apiece. \texttt{iterate} is
\texttt{unfoldr}'s lazy, infinite cousin: it never stops on its own, so
\texttt{take} is what makes it usable."""),
 (3, "hw03", [7, 8, 9, 10, 11, 12], r"""
The largest chapter because it is the least glamorous: the ordinary list
and dict work that every program needs, named consistently instead of
reached for ad hoc. \texttt{windows} and \texttt{groupBy} both slide a view
across a sequence, but for different reasons -- one for a fixed-width
lookback (moving averages), one for runs of equal elements (RLE,
compression). \texttt{transpose} is ragged-safe on purpose: short rows
simply drop out of later columns instead of raising, so uneven data never
needs a special case. \texttt{fromListWith} and \texttt{unionWith} are the
two dict-building folds worth memorising -- almost every ``group these'' or
``merge these two counters'' problem is one of them with the right
combining function."""),
 (4, "hw04", [13], r"""
\texttt{None} is Python's ``no value'', which is exactly the problem: a
function cannot then return \texttt{None} to mean a REAL answer without
creating an ambiguity. \texttt{NOTHING} fixes this by being a distinct
object that is never a legitimate value -- \texttt{maybe\_get} returns
\texttt{None} for a key whose stored value truly is \texttt{None}, and
\texttt{NOTHING} only when the key is missing outright. \texttt{bind}
chains failable steps by short-circuiting the moment one returns
\texttt{NOTHING}; \texttt{sequenceM} and \texttt{traverseM} extend that to
a whole list, all-or-nothing. Once a pipeline's failure mode is a value
instead of an exception, the pipeline composes like any other function."""),
 (5, "hw05", [14], r"""
Maybe answers ``did it work?''; Either answers that AND ``why not?''.
\texttt{Ok}/\texttt{Err} are tagged pairs -- \texttt{("ok", v)} or
\texttt{("err", why)} -- so \texttt{bindE} can short-circuit exactly like
\texttt{bind} while still carrying the failure's reason to wherever the
pipeline is finally inspected. \texttt{sequenceE} and \texttt{traverseE}
are Either's all-or-nothing gates, and \texttt{note} is the bridge from the
last chapter: it turns a \texttt{NOTHING} into an \texttt{Err} with a
message attached, for the moment a Maybe pipeline needs to explain itself
to a caller."""),
 (6, "hw06", [15], r"""
Chaining \texttt{bind} calls by hand nests one call inside the next, one
level per step -- the ``bind pyramid''. \texttt{do} rebuilds that same
chain out of an ordinary generator function: each \texttt{yield} is one
\texttt{bind}, and the value sent back in is what the step would have
returned. \texttt{doM} wires this to the Maybe monad, \texttt{doE} to
Either -- same decorator, same generator shape, different short-circuit
rule. The win is not cleverness for its own sake: a five-step Maybe
pipeline written with \texttt{doM} reads top to bottom, in the order the
steps actually happen, with the failure path made invisible instead of
handled at every line."""),
 (7, "hw07", [16], r"""
A parser is a function from a string to \texttt{(value, rest)} or
\texttt{FAIL} -- once that shape is fixed, parsers compose like any other
function. \texttt{doP} threads the remaining input through a generator the
same way \texttt{doM} threads a Maybe; \texttt{alt} tries alternatives in
order; \texttt{many} and \texttt{sepBy} handle repetition and
separator-delimited lists without recursion. \texttt{chainl1} deserves
special attention: it folds a sequence of \texttt{p (op p)*} LEFT, which is
exactly how left-associative arithmetic is supposed to parse, and it is the
one combinator in this chapter doing real algorithmic work rather than
just gluing others together."""),
 (8, "hw08", [17], r"""
A monoid is nothing but an identity element paired with an associative
combiner, reified as the pair \texttt{(empty, op)} -- naming it as DATA
means one engine, \texttt{mconcat}, folds every instance, and
\texttt{foldMap} fuses ``measure each element'' with ``combine the
measurements'' into one pass. \texttt{both} is the chapter's real payoff:
it pairs two monoids into one, so a max and a min, or a count and a total,
fall out of a SINGLE traversal instead of two separate loops. That matters
most exactly when it looks like it should not -- a one-shot iterator or a
huge file that can only be read once."""),
 (9, "hw09", [], r"""
No new vocabulary -- this chapter is the payoff for the previous eight.
Each problem reaches back for tools from more than one chapter at once:
parsing with \texttt{doP}, then judging the parsed value with
\texttt{bindE}; folding a monoid across a batch validated with
\texttt{doE}. If a chapter's tools felt like isolated tricks on first
reading, this is where they stop being isolated."""),
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
\usepackage[margin=0.22in,bindingoffset=0.25in,includeheadfoot]{geometry}
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
  upquote=true,aboveskip=6pt,belowskip=6pt,xleftmargin=0.5em,
  frame=leftline,framerule=0.8pt,rulecolor=\color{rulecol}}
\lstdefinestyle{ex}{basicstyle=\ttfamily\small,keepspaces=true,
  columns=fullflexible,breaklines=true,breakatwhitespace=true,
  postbreak=\mbox{\textcolor{numcol}{$\hookrightarrow$}\space},
  upquote=true,aboveskip=4pt,belowskip=7pt,xleftmargin=0.5em,
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

The whole library is one listing, up front, in Chapter 1 -- read it once,
top to bottom, the way you would read any short source file. The nine
chapters after it are not a second pass over the same material: each opens
with why its slice of the library exists and how its pieces fit together,
then goes straight to \textbf{Homework} -- drills cement each tool, applies
combine them, and challenges are interview-grade. Write each solution in a
scratch file with the given doctests pasted in; \texttt{python3 -m doctest}
is the referee.

\tableofcontents
\mainmatter
\part{The Nine Chapters}
\chapter{haskell.py, Complete}
Every name this book teaches, in one file, in the order it is defined --
docstrings and comments stripped to the section headers, which are the
only thing worth keeping as a wayfinding aid in a listing this short. Read
it once before the first chapter; the chapters that follow assume you have.
""")
    A(lst(ROOT.joinpath("haskell-terse.py").read_text(), "file"))
    for num, hwstem, secnums, intro in CHAPTERS:
        title, items = load_hw(hwstem)
        A("\\chapter{%s}\n" % esc(title))
        A(intro + "\n")
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
