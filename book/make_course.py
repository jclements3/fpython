"""make_course.py -- build PreludeStudent.pdf and PreludeTeacher.pdf.

One builder, two modes from the same sources: concept entries (gists,
examples, deep dives, roll-your-own walkthroughs) come from
prelude-doctests.py via entrylib; implementations verbatim from prelude.py;
homework from book/course/hw*.py (verified by verify_hw.py); applied labs
from the 74 course problems. The Teacher edition is a superset: every
homework item and lab carries its solution and teaching note.

    python3 make_course.py            # builds both PDFs, compiling in parallel
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
COURSE = HERE / "course"
LABS = ROOT / "labs"
sys.path.insert(0, str(HERE))
import entrylib

# ------------------------------------------------------------- chapter plan

CHAPTERS = [
 (1, "Grammar, Pairs and Maybe", "hw01",
  ["fst", "snd", "swap", "NOTHING", "fromMaybe", "isJust", "isNothing"], r"""
Every course opens with its grammar. Here it is the conventions the whole
prelude leans on: functions come first and data second in every call;
\texttt{None} is Nothing -- the universal ``no answer'' -- and
\texttt{fromMaybe} is how a pipeline lands a default, and
\texttt{isJust}/\texttt{isNothing} make the None test itself a predicate you
can hand to other tools; \texttt{NOTHING} is the other absence, the ``no
argument supplied'' sentinel. The pair accessors look
trivial, and are: that is what makes them readable inside sort keys and maps
where an index would be noise."""),
 (2, "Arithmetic and Logic", "hw02",
  ["succ", "pred", "even", "odd", "not_", "otherwise", "signum", "div", "mod",
   "quot", "rem", "quotRem", "gcd", "lcm", "hypot", "isqrt", "add", "sub"], r"""
Small tools with sharp edges. The floor-versus-truncate split
(\texttt{div}/\texttt{mod} against \texttt{quot}/\texttt{rem}) decides real
interview questions the moment a negative number appears; \texttt{signum}
compresses three-way comparison into arithmetic; \texttt{isqrt} shows Newton's
method surviving entirely inside the integers. Master the edges here and
modular-arithmetic problems stop being scary."""),
 (3, "Lists I: The Basics", "hw03",
  ["head", "tail", "init", "last", "null", "elem", "notElem", "replicate",
   "drop", "splitAt", "nub", "lookup", "zip_", "zip3", "unzip", "transpose",
   "enum", "pairwise", "isPrefixOf", "isSuffixOf", "stripPrefix"], r"""
The list is the prelude's universal substrate, and this chapter is its
anatomy: take lists apart at the ends, cut them at positions, pair them
against each other -- and against their own tails, which is what
\texttt{pairwise} does and why every rule about ``adjacent elements'' starts
there. \texttt{nub}, \texttt{transpose} and the prefix family each hide one
idea worth owning outright."""),
 (4, "Lists II: Higher-Order", "hw04",
  ["map_", "filter_", "find", "partition", "mapMaybe", "catMaybes", "concat",
   "concatMap", "starmap", "zipWith", "zipWith3", "cross"], r"""
Where loops go to be named. \texttt{map\_} transforms, \texttt{filter\_}
selects, \texttt{concatMap} enumerates, \texttt{zipWith} combines --
and two tools do what loops do badly: \texttt{find} stops at the first hit
(even on an infinite stream), and \texttt{mapMaybe} runs a parser over messy
input and keeps only what parsed, one pass, no flags. This chapter is the
single highest-frequency vocabulary in the whole course."""),
 (5, "The Fold", "hw05",
  ["foldl", "foldl1", "foldr", "foldr1", "product", "subsequences",
   "replicateM"], r"""
The trunk of the tree. A fold is a for-loop whose state has been given a
contract: an accumulator, a combiner, one pass. Everything after this chapter
is a fold in costume -- scans keep the fold's history, unfolds run it
backwards, dict folds aim it at a mapping, \texttt{memo} folds a recursion
into a cache. Learn the two argument disciplines cold: \texttt{foldl}'s
combiner takes \texttt{(acc, x)}, \texttt{foldr}'s takes \texttt{(x, acc)}.
The enumeration folds close the chapter with the brute-force licenses:
$2^n$ subsets and $|xs|^n$ words, legal when you say the bound out loud."""),
 (6, "Scans", "hw06",
  ["accumulate", "scanl", "scanl1", "scanr", "scanr1"], r"""
A scan is a fold that keeps its history -- every intermediate accumulator,
not just the last. That one change turns ``the state at every step'' from n
folds into one pass, makes prefix sums (and with them $O(1)$ range queries)
a single line, and reveals celebrated one-pass algorithms -- Kadane's most
famously -- as scans in a trench coat. When a statement says ``running'',
``so far'' or ``at each step'', it is dictating this chapter."""),
 (7, "Streams and Unfolds", "hw07",
  ["count", "repeat", "cycle", "iterate", "unfoldr", "chain"], r"""
Production instead of consumption. Generators let a sequence be infinite --
\texttt{count}, \texttt{cycle}, \texttt{iterate} -- because nothing is
computed until a consumer asks; \texttt{unfoldr} is the finite twin, growing
a list from a seed until the step function says stop. Anything that PEELS
(digits, chunks, trajectories, parent chains) is an unfold, and recognising
that retires a whole family of while-loops with threaded state."""),
 (8, "Spans and Views", "hw08",
  ["islice", "take", "takewhile", "takeuntil", "dropwhile", "takeWhile",
   "dropWhile", "span", "break_", "inits", "tails", "chunksOf"], r"""
The consumers and finite views that make streams usable: \texttt{take} and
friends stop lazily; \texttt{span}/\texttt{break\_} cut a sequence at a
condition -- a lexer in one call; \texttt{inits}/\texttt{tails} enumerate
every prefix and suffix, which is where substring problems begin; and
\texttt{chunksOf} pages anything. Small tools, constant use."""),
 (9, "Order and Text", "hw09",
  ["sortOn", "minOn", "maxOn", "cmp_to_key", "sortBy", "merge", "bisect_left",
   "bisect_right", "words", "unwords", "lines", "unlines"], r"""
``Does order unlock it?'' is the recognition ladder's first question because
sorting linearises problems: tuple keys buy multi-level orderings in one
call, \texttt{minOn}/\texttt{maxOn} answer best-by-key in $O(n)$, and the
bisect pair reads a sorted list's True/False boundary three different ways
-- membership, insertion point, counting. The string quartet turns text
pipelines into list pipelines and back."""),
 (10, "Dict Folds and Bags", "hw10",
  ["defaultdict", "Counter", "insertWith", "fromListWith", "unionWith",
   "groupBy", "group", "bag_union", "bag_inter", "bag_diff", "bag_sub"], r"""
Aggregation by key -- the fold aimed at a mapping. One family, one idea:
\texttt{insertWith} resolves a single collision, \texttt{fromListWith} a
list of them, \texttt{unionWith} two dicts' worth; and CHOOSING the combiner
is choosing a monoid -- addition counts, \texttt{old + new} groups,
\texttt{max} is bag union. Mind the Haskell order: the combiner hears the
NEW value first. \texttt{group}/\texttt{groupBy} handle the positional
cousin: runs, not piles."""),
 (11, "Trees and Tries", "hw11",
  ["Tree", "ITree", "paths", "leaves", "setpath", "getpath"], r"""
Hierarchy as nested dicts that build themselves. \texttt{ITree} autovivifies
a branch the moment you touch it -- a trie in one line -- and
\texttt{Tree(depth, leaf)} bottoms the same idea out at fixed depth.
Writing is indexing or \texttt{setpath}; asking is ALWAYS \texttt{getpath}
(reads plant ghost branches otherwise); and \texttt{paths} folds the whole
tree back into rows, which is where the value gets harvested."""),
 (12, "Machines: Deque, DSU, Heap", "hw12",
  ["deque", "dsu", "heappush", "heappop"], r"""
Three data structures rebuilt from nothing, each carrying one great argument:
the two-stack \texttt{deque}'s amortised $O(1)$ ends (each element migrates
once); union--find's path halving making connectivity effectively constant
-- with \texttt{union} returning False AS the cycle detector; and the heap's
single invariant (parent beats children) keeping the minimum readable at
\texttt{h[0]} forever. Owning these means never being helpless without
imports."""),
 (13, "Nodes: Linked Lists and Binary Trees", "hw13",
  ["TreeNode", "tfold", "inorder", "preorder", "postorder", "tdepth", "tsize",
   "levelorder", "ListNode", "from_list", "to_list", "reverse_list", "middle",
   "has_cycle", "merge_lists"], r"""
The LeetCode givens. For trees, one catamorphism -- \texttt{tfold} -- makes
every traversal and measure a one-liner, because \texttt{z} is the
empty-tree arm and \texttt{f} the node arm; \texttt{levelorder} adds the
deque for breadth-first. For linked lists, the pointer idioms worth knowing
cold: three-pointer reversal, fast/slow middles, Floyd's cycle detection,
dummy-head merging. Convert node results with \texttt{to\_list} so
everything stays testable."""),
 (14, "Grids and Windows", "hw14",
  ["neighbors4", "neighbors8", "longest_window"], r"""
Two small tools with outsized reach. The neighbour generators put the
bounds check in ONE place so every flood-fill and BFS body stays clean.
\texttt{longest\_window} inverts control for sliding windows: the skeleton
owns the two pointers, you own the state as three closures --
\texttt{valid}, \texttt{push}, \texttt{shed} -- and designing them is just
answering ``what makes a window illegal?''."""),
 (15, "Control and Dynamic Programming", "hw15",
  ["memo", "until"], r"""
The capstone machinery. \texttt{memo} turns an honest recurrence into
dynamic programming -- state the truth, decorate it, and the cache is your
DP table, inspectable at \texttt{.cache}; the craft is naming the state so
``the future only needs $X$'' comes out in one sentence. \texttt{until}
handles the loops with no list to fold: iterate a step to a goal or a fixed
point, Bellman--Ford being the textbook case."""),
 (16, "Combinators Capstone", "hw16",
  ["id", "const", "flip", "curry", "uncurry", "partial", "on", "compose"], r"""
The functions about functions come FIRST in the file and LAST in a person:
you have been using them all course, and now they get named as a
discipline. \texttt{curry} and \texttt{partial} stage arguments;
\texttt{flip} and \texttt{on} adapt argument order and route comparisons
through keys; \texttt{compose} makes a pipeline a value. The capstone skill
is judgement -- writing point-free when it clarifies, and refusing to when
it does not."""),
 (17, "Monoids and Monads", "hw17",
  ["Monoid", "mconcat", "foldMap", "All", "Any", "First", "Last", "ListM",
   "MaxM", "MinM", "Product", "Sum", "both", "bind", "chainM", "sequenceM",
   "traverseM", "Ok", "Err", "bindE", "chainE"], r"""
The file closes with two ideas about combining more safely than by hand. A
monoid is nothing but an identity element paired with an associative
combiner, reified as data -- \texttt{Monoid(empty, op)} -- so \texttt{mconcat}
and \texttt{foldMap} can fold with ANY instance, and \texttt{both} runs two
folds over the same data in a single pass. The Maybe monad
(\texttt{bind}, \texttt{chainM}, \texttt{sequenceM}, \texttt{traverseM})
threads None-propagation through a pipeline so a failing step needs no
if-ladder to guard the rest; \texttt{Ok}/\texttt{Err} with
\texttt{bindE}/\texttt{chainE} upgrade that same shape so failure carries a
reason, not just an absence. If a fold or a chain of fallible steps looks
like it needs a loop with early exits, it almost always wants one of
these instead."""),
]

GROUPS = ["g1_arith_and_unfolds", "g2_lists_and_strings",
          "g3_folds_scans_streams", "g4_sorting_and_searching",
          "g5_bags_and_grouping", "g6_tries_and_paths",
          "g7_graphs_grids_heaps", "g8_dp_and_control", "g9_stack_folds"]

LADDER = [
 ("SORT FIRST", "``sorted'', ``k-th'', ``closest pair'', ``intervals''",
  r"sorted, sortOn, bisect\_left, merge"),
 ("FOLD", "``total'', ``count'', ``largest'', ``best single \\ldots''",
  r"foldl, minOn / maxOn"),
 ("SCAN", "``running'', ``so far'', ``at each step'', ``prefix sums''",
  "scanl, scanl1"),
 ("DICT FOLD", "``group by'', ``frequency'', ``most common''",
  "fromListWith, Counter, unionWith"),
 ("WINDOW", "``substring'', ``contiguous'', ``longest run''",
  r"longest\_window, pairwise"),
 ("STACK", "``nested'', ``matching pairs'', ``next greater''",
  "list as stack; foldl with stack acc"),
 ("UNFOLD", "``digits of'', ``split into pieces'', ``repeat until''",
  "unfoldr, iterate + take"),
 ("ENUMERATE", "``all subsets'', ``every way to pick''",
  "subsequences, replicateM, cross"),
 ("TREE / PATHS", "``nested'', ``prefix'' (trie), ``directories''",
  "ITree, paths, setpath, tfold"),
 ("GRAPH", "``prerequisites'', ``network'', ``shortest route''",
  "Tree(1,list) adjacency, deque BFS, heap, until"),
 ("MEMOIZE", "``fewest'', ``max value'', ``count the ways''",
  "memo over indices"),
]


# ------------------------------------------------------------- helpers

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


def load_problem(path):
    doc = path.read_text().split('"""')[1]
    lines = doc.splitlines()
    title = lines[0]
    idx = next(i for i, l in enumerate(lines) if l.startswith(">>>"))
    body = "\n".join(lines[1:idx]).strip("\n")
    tests = "\n".join(lines[idx:]).strip("\n")
    name, _, tagline = title.partition(" -- ")
    return re.sub(r"^\d+_", "", name), tagline.rstrip("."), body, tests


def load_solution(group, stem):
    t = (LABS / "solutions" / ("%s_%s.py" % (group[:2], stem))).read_text()
    after = t.split("# solution goes here\n", 1)[1]
    return after.split("\nif __name__", 1)[0].strip("\n")


def load_hw(stem):
    matches = sorted(COURSE.glob(stem + "*.py"))
    if not matches:
        return None
    mod = {}
    try:
        exec(compile(matches[0].read_text(), str(matches[0]), "exec"), mod)
    except Exception as e:
        print(f"  ! skipping {matches[0].name}: {type(e).__name__}: {e}",
              file=sys.stderr)
        return None
    return mod["ITEMS"]


ENTRIES = {}
for _sec, _es in entrylib.parse(ROOT):
    for _e in _es:
        ENTRIES[_e["name"]] = _e
DEFS = entrylib.definitions(ROOT)

# global teaching order: name -> (chapter number, index within chapter)
ORDER = {n: (num, k) for num, _t, _h, names, _i in CHAPTERS
         for k, n in enumerate(names)}
NAME_RX = re.compile(r"\b(%s)\b" % "|".join(
    sorted(ORDER, key=len, reverse=True)))


def _label(name):
    return "def:" + name.replace("_", "-")


def forward_refs(code, here):
    """Prelude names in `code` whose Roll-your-own comes after position
    `here` in the teaching order, earliest first."""
    used = {m.group(1) for m in NAME_RX.finditer(code)}
    return sorted((n for n in used if ORDER[n] > here), key=ORDER.get)


def ref_note(A, names, lead):
    if not names:
        return
    A("\\noindent{\\small\\itshape %s %s.}\n\n" % (lead, ", ".join(
        "\\texttt{%s} in \\S\\ref{%s} (p.~\\pageref{%s})"
        % (esc(n), _label(n), _label(n)) for n in names)))


def render_entry(A, name):
    here = ORDER[name]
    e = ENTRIES.get(name)
    if e is None:
        A("\\textbf{\\texttt{%s}}\\label{%s} --- (see prelude.py)\n\n"
          % (esc(name), _label(name)))
        if name in DEFS:
            A(lst(entrylib.unalign(DEFS[name])))
        return
    A("\\subsection{\\texttt{%s}}\\label{%s}\n" % (esc(name), _label(name)))
    A(prose(entrylib.gist(e)) + "\n")
    code_seen = []
    for kind, txt in e["segments"][1:]:
        if kind == "c":
            A(lst(txt))
            code_seen.append(txt)
        else:
            A("\n" + prose(txt) + "\n\n")
    impl = DEFS.get(name)
    if impl:
        if not entrylib.has_walkthrough(e):
            A("\nRoll your own --- the definition:\n\n")
        A(lst(entrylib.unalign(impl)))
        code_seen.append(impl)
    ref_note(A, forward_refs("\n".join(code_seen), here),
             "Used before it is rolled:")


def render_hw(A, items, teacher, chapter):
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
        if teacher:
            A("\\noindent\\textbf{Solution.}\n")
            A(lst(it["solution"], "code"))
            A("\\noindent\\textit{Note.} " + prose(it["note"]) + "\n\n")
        ref_note(A, forward_refs(it["tests"] + "\n" + it["solution"],
                                 (chapter, len(ORDER))),
                 "Rolled later:")
    A("\\clearpage\n")


def build(mode):
    teacher = (mode == "teacher")
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
\makeatletter                            % TOC: room for two-digit section numbers (18.10)
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
    A("\\title{\\Huge\\bfseries Prelude %s\\\\[6pt]"
      "\\Large A Complete Course in Functional Python\\\\[14pt]"
      "\\normalsize seventeen chapters, %d homework problems, %d applied labs}\n"
      % ("Teacher's Edition" if teacher else "Student",
         sum(len(load_hw(c[2]) or []) for c in CHAPTERS),
         len(list(LABS.glob("g*/[0-9]*.py")))))
    A("\\author{J.~L.~Clements~III}\n\\date{\\today}\n")
    A(r"""\begin{document}
\frontmatter
\maketitle

\chapter{How to Take This Course}
This book teaches \texttt{prelude.py} -- a Haskell-style prelude in pure
Python, no imports anywhere -- until it is not reference material but
reflex. The order is the mastery order, not the file order: the spine is
\textbf{fold $\rightarrow$ scan $\rightarrow$ unfold $\rightarrow$ dict fold
$\rightarrow$ memo} -- one concept in five costumes -- and every chapter
hangs off it.

Each chapter has three movements. \textbf{Concepts}: every function
introduced with its purpose, worked examples (all of them runnable
doctests), deep dives where the idea is subtle, and a ``roll your own''
walkthrough of the implementation itself. \textbf{Homework}: twelve
problems -- five drills, five applied scenarios, two interview-grade
challenges. \textbf{Discipline}: solve in a scratch file with the printed
doctests pasted in; \texttt{python3 -m doctest} is the referee, and an
answer is not done until it is N/N.

Part III then applies the whole toolkit to seventy-four classic problems
organised by class -- the HackerRank/LeetCode canon reworked in prelude
style. """ + ("This Teacher's Edition prints every solution and a teaching "
              "note inline; grade against the doctests, then against the "
              "style: two or three prelude names and one lambda beat a page "
              "of loops."
              if teacher else
              "Solutions live in the Teacher's Edition and in the repository "
              "-- fight each problem first; the doctests will tell you when "
              "you have won.") + r"""

\section*{The recognition ladder}
Before any problem, name the INPUT shape, the OUTPUT shape, and the quantity
word -- then walk this ladder; the first row whose trigger words match names
your tools.

\begin{center}\small
\begin{tabular}{@{}p{0.13\textwidth}p{0.37\textwidth}p{0.41\textwidth}@{}}
\toprule
\textbf{Shape} & \textbf{Trigger words} & \textbf{Reach for} \\
\midrule
""")
    for shape, trig, tools in LADDER:
        A("%s & %s & \\texttt{%s} \\\\\n" % (shape, trig, tools))
    A(r"""\bottomrule
\end{tabular}
\end{center}

\tableofcontents
\mainmatter
\part{The Seventeen Chapters}
""")
    for num, title, hwstem, names, intro in CHAPTERS:
        A("\\chapter{%s}\n" % title)
        A(intro + "\n")
        A("\\section{Concepts}\n")
        for n in names:
            render_entry(A, n)
        items = load_hw(hwstem)
        if items:
            render_hw(A, items, teacher, num)
        else:
            A("\\section{Homework}\n(homework bank %s not yet present)\n"
              % hwstem)
    A("\\part{Applied Labs: The Nine Problem Classes}\n")
    A(r"""\chapter*{About the labs}
\addcontentsline{toc}{chapter}{About the labs}
Seventy-four problems, each a self-contained practice file in the repository
(\texttt{fpython/labs/g*/}) carrying its needed snippets inline. Statements,
contracts, hints and doctests are printed here""" +
      ("; solutions follow each problem in this edition." if teacher
       else "; solve them in the repository files, where the doctest runner "
            "referees.") + "\n")
    for g in GROUPS:
        A("\\chapter{%s}\n" % esc(g[3:].replace("_", " ").title()))
        for path in sorted((LABS / g).glob("[0-9]*.py")):
            name, tagline, body, tests = load_problem(path)
            A("\n\\section{%s: %s}\n" % (esc(name), esc(tagline)))
            A(lst(body))
            A(lst(tests))
            if teacher:
                A("\\noindent\\textbf{Solution.}\n")
                A(lst(load_solution(g, path.stem), "code"))
    A(r"""\appendix
\part{Appendices}
\chapter{prelude.py, Complete}
""")
    A(lst(ROOT.joinpath("prelude.py").read_text(), "file"))
    A(r"\backmatter" + "\n" + r"\end{document}" + "\n")

    name = "PreludeTeacher" if teacher else "PreludeStudent"
    out = HERE / (name + ".tex")
    out.write_text("".join(tex))
    print("wrote", out.name, out.stat().st_size // 1024, "KB")
    return out


def main():
    texs = [build("student"), build("teacher")]
    procs = [subprocess.Popen(
        ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
         t.name], cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for t in texs]
    for t, p in zip(texs, procs):
        out, _ = p.communicate()
        if p.returncode != 0:
            print(out.decode(errors="replace")[-2500:])
            raise SystemExit(f"latexmk failed for {t.name}")
        subprocess.run(["latexmk", "-c", t.name], cwd=HERE,
                       capture_output=True)
        info = subprocess.run(["pdfinfo", str(t.with_suffix(".pdf"))],
                              capture_output=True, text=True).stdout
        pages = [l for l in info.splitlines() if l.startswith("Pages")]
        print(t.stem, pages)


if __name__ == u'__main__':
    main()
