"""make_book.py -- generate PythonFP.tex (and the PDF) from the prelude project.

The prose lives here; every code listing, problem statement, hint, doctest and
solution is extracted from ../prelude.py, ../g*/, ../solutions/ at build time,
so the book can never drift from the course files.

    python3 make_book.py          # writes PythonFP.tex, runs latexmk -> PythonFP.pdf
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "PythonFP.tex"
sys.path.insert(0, str(HERE))
import entrylib


# --------------------------------------------------------------- helpers

def code(s, style="code"):
    s = s.rstrip("\n").replace("\u2014", "--")
    return "\\begin{lstlisting}[style=%s]\n%s\n\\end{lstlisting}\n" % (style, s)


def esc(s):
    return (s.replace("\\", r"\textbackslash{}").replace("&", r"\&")
             .replace("%", r"\%").replace("#", r"\#").replace("_", r"\_")
             .replace("$", r"\$").replace("^", r"\^{}").replace("`", "'"))


def load_problem(path):
    doc = path.read_text().split('"""')[1]
    lines = doc.splitlines()
    title = lines[0]
    idx = next(i for i, l in enumerate(lines) if l.startswith(">>>"))
    body = "\n".join(lines[1:idx]).strip("\n")
    tests = "\n".join(lines[idx:]).strip("\n")
    name, _, tagline = title.partition(" -- ")
    name = re.sub(r"^\d+_", "", name)
    return name, tagline.rstrip("."), body, tests


def load_solution(group, stem):
    t = (ROOT / "solutions" / ("%s_%s.py" % (group[:2], stem))).read_text()
    after = t.split("# solution goes here\n", 1)[1]
    return after.split("\nif __name__", 1)[0].strip("\n")


def prelude_sections():
    text = ROOT.joinpath("prelude.py").read_text()
    marks = [(m.start(), m.group(1)) for m in
             re.finditer(r"^# ============ (.+?) ============.*$", text, re.M)]
    out = {}
    for i, (pos, name) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        num = int(name.split(".")[0])
        out[num] = text[pos:end].strip("\n")
    return out


SEC = prelude_sections()
GROUPS = ["g1_arith_and_unfolds", "g2_lists_and_strings",
          "g3_folds_scans_streams", "g4_sorting_and_searching",
          "g5_bags_and_grouping", "g6_tries_and_paths",
          "g7_graphs_grids_heaps", "g8_dp_and_control", "g9_stack_folds"]

REMARKS = {  # hand commentary for flagship problems, keyed by stem
"03_reverse_digits": r"""The state never needed to be a tuple threaded through
\texttt{until} -- \texttt{unfoldr} peels the digits into a list (already reversed,
because \texttt{m \% 10} yields the low digit first), and a fold reassembles them.
Unfold, then fold: when you see that pair, you are looking at a pipeline.""",
"06_from_roman": r"""Every subtractive rule in Roman numerals is a statement about
a symbol and its \emph{right neighbour}. \texttt{pairwise} materialises exactly
that relationship, and the padding zero gives the final symbol a neighbour too.
When a rule talks about adjacent elements, reach for \texttt{pairwise} before you
reach for indices.""",
"08_chunks": r"""\texttt{splitAt} already returns \texttt{(front, rest)} -- which
is precisely the \texttt{(value, next\_seed)} contract of \texttt{unfoldr}. The
whole solution is recognising that two signatures line up. You are deriving the
prelude's own \texttt{chunksOf}; deriving a tool once is why it sticks.""",
"09_permutations": r"""\texttt{concatMap} is the shape of ``for every choice,
recurse, and pool the results.'' Any backtracking enumeration can be written this
way; \texttt{nub} then absorbs duplicate letters without a special case.""",
"03_maximum_subarray": r"""Kadane's algorithm is famous as a clever trick; seen
functionally it is one \texttt{scanl1}. The scan \emph{is} the DP table
(best sum ending at each index), and \texttt{max} reads the answer off it. Many
celebrated one-pass algorithms are scans wearing a trench coat.""",
"04_product_except_self": r"""One scan from the left, one from the right, and a
\texttt{zipWith} to marry them. The offset slicing (\texttt{pre[:-1]},
\texttt{suf[1:]}) is where the ``except self'' lives -- each position sees the
product of everything strictly before and strictly after it.""",
"09_totals_and_deltas": r"""\texttt{scanl1 (+)} and pairwise differences are
inverses -- discrete integration and differentiation. Recognising an operation's
inverse is a testing superpower: the round-trip doctest here is a property test
in miniature.""",
"08_russian_doll": r"""Sorting by \texttt{(width asc, height desc)} is the whole
problem. The descending tie-break guarantees equal-width envelopes can never
chain, which collapses a 2-D dominance question into a 1-D LIS on heights.
Sorting linearised one dimension; the tails trick handles the other.""",
"07_lis": r"""Patience sorting: \texttt{tails[i]} is the smallest possible tail
of an increasing run of length $i{+}1$; \texttt{bisect\_left} says which pile
each element lands on. Landing past the end grows the answer. Know the
$O(n^2)$ DP too, and say both complexities out loud.""",
"10_sensor_pairing": r"""The interview capstone, distilled: build every
compatible candidate, sort by cost, greedily take what is still unused. The
wrap-around rule lives in \emph{one} helper, which is why phase mutations cost
one line here. Name the better algorithm (optimal assignment, Hungarian,
$O(n^3)$) and deliberately choose the simpler one -- that sentence is a senior
signal.""",
"11_log_report": r"""The messy-input shape: \texttt{parse} returns a value or
\texttt{None}, and everything downstream is bookkeeping over Maybes --
\texttt{catMaybes} for the survivors, a filter for the casualty count,
\texttt{Counter} and \texttt{sortOn} for the report. No raw loops, no flags.""",
"10_first_unique": r"""Three prelude names, one line: \texttt{Counter} builds the
evidence, \texttt{find} stops at the first witness, \texttt{fromMaybe} supplies
the default. This is what vocabulary buys: the solution is its own
specification.""",
"06_group_anagrams": r"""Two respectable routes: \texttt{Tree(1, list)} with a
bare append (autovivification suits write-heavy access) or one
\texttt{fromListWith} over \texttt{(key, [w])} pairs, combining old + new
(the combiner hears the new value first). Solve it both ways once; afterwards
you will see every grouping problem as a one-liner.""",
"01_deepest_directory": r"""Walking \emph{is} building: folding indexing over the
path parts autovivifies the whole branch. Note why \texttt{setpath} would be
wrong -- writing \texttt{a/b} after \texttt{a/b/c} would clobber the subtree.
Choosing the writing primitive is part of the design.""",
"04_subset_sum_trie": r"""The \texttt{\$} terminator earns its place: one
solution can be a prefix of another, and without an end marker the shorter one
vanishes into the longer one's interior. Also note the semantic shift from the
decision-tree version: a trie stores a \emph{set} of solutions, so duplicate
index-choices collapse.""",
"05_dijkstra": r"""Lazy deletion is the grown-up move: the heap may hold stale
distances, so skip a popped entry unless it matches the current best. Path
reconstruction is an unfold along the parent chain. Graphs are not trees --
cycles make tree unfolds diverge, so we fold over \emph{states} to a fixed
point.""",
"07_bellman_ford": r"""Shortest paths \emph{are} a fixed point: the least map
satisfying every edge's triangle inequality. \texttt{until} iterates the relax
step to stability; a change on pass $|V|$ proves a negative cycle. Dijkstra is
the same relax with a clever order; Bellman--Ford orders nothing and pays in
passes.""",
"01_longest_unique": r"""The window skeleton does the two-pointer bookkeeping;
you supply state as closures. Writing \texttt{valid}/\texttt{add}/\texttt{rem}
separately is exactly the decomposition that survives a mutating interview
prompt.""",
"08_guillotine_cut": r"""Guillotine cuts are what re-admit dynamic programming:
free-form 2-D packing has no small state, but edge-to-edge cuts keep every
subproblem a rectangle -- two integers. A smaller piece never needs a direct
case; the cut that isolates it is one of the splits.""",
"09_partition_k_subsets": r"""The mask family in pure form: the future needs only
(which numbers remain, room left in the open group), because a closed group's
room resets to the target. Fill one group at a time so orderings are not counted
twice. $2^n$ states -- say the bound before you code.""",
"01_balanced_brackets": r"""A fold whose accumulator is a stack -- and whose
failure state is \texttt{None}, propagating untouched through the rest of the
fold. That is Maybe as an accumulator, and it removes every flag and early
return from the classic solution.""",
"03_next_greater": r"""The monotonic stack: the newcomer pops every index it
beats (it is their answer) and then waits for its own. Each index pushes and
pops at most once, so the nested \texttt{while} is still $O(n)$ -- amortised
analysis in one picture.""",
}

GROUP_INTROS = {
"g1_arith_and_unfolds": (r"Class I --- Arithmetic and Unfolds", r"""
The warm-up class, and the home of the \emph{unfold}: producing a sequence from
a seed instead of consuming one. Digits, base renderings and numeral systems all
peel a value apart step by step -- \texttt{unfoldr} when you want the pieces as
a list, \texttt{until} when you only want the final state, \texttt{foldl} when
a value table drives the steps. Watch how often a produced list is immediately
folded back into a value: unfold-then-fold is a pipeline, not a coincidence."""),
"g2_lists_and_strings": (r"Class II --- Lists and Strings", r"""
Bread and butter: \texttt{map\_}, \texttt{filter\_}, \texttt{concat},
\texttt{concatMap}, and the string pair \texttt{words}/\texttt{unwords}. Two
problems here are deliberate one-liners (\texttt{flatten} \emph{is}
\texttt{concat}, \texttt{transpose\_matrix} \emph{is} \texttt{transpose}):
recognising an existing tool is a skill worth isolating and drilling. The
harder members (\texttt{chunks}, \texttt{permutations}) preview unfolds and
backtracking enumeration."""),
"g3_folds_scans_streams": (r"Class III --- Folds, Scans and Streams", r"""
The heart of functional problem solving. A fold collapses a list to one value;
a scan is a fold that keeps its history; a stream generates lazily until
\texttt{take} says stop. The famous surprises live here: Kadane's algorithm is
a \texttt{scanl1}, Fibonacci is \texttt{iterate} on a pair, prefix sums turn
every window-sum question into two slices and a \texttt{zipWith}. When a
statement says ``running'', ``so far'' or ``at each step'', you are being told
the answer is a scan."""),
"g4_sorting_and_searching": (r"Class IV --- Sorting and Searching", r"""
``Does order unlock it?'' is the first question of the recognition ladder for a
reason: sorting linearises a problem so that greedy passes, binary searches and
pairwise arguments become available. The exchange argument (\texttt{photo\_%
lineup}), the tie-break trick (\texttt{russian\_doll}) and patience sorting
(\texttt{lis}) are all consequences of choosing the \emph{right} sort key --
which is where the thinking happens. \texttt{sensor\_pairing} closes the class
with the interview's own domain problem."""),
"g5_bags_and_grouping": (r"Class V --- Bags, Dicts and Grouping", r"""
Aggregating by key. \texttt{Counter} counts, \texttt{fromListWith} is the
general dict-building fold, \texttt{unionWith} merges two dicts under any
combining function -- and choosing that function is choosing a monoid
(\texttt{max} gives bag union, \texttt{+} gives a summing merge). The class
also carries the Maybe pipeline (\texttt{first\_unique}, \texttt{log\_report}):
parse to value-or-\texttt{None}, then let the Maybe tools do the bookkeeping."""),
"g6_tries_and_paths": (r"Class VI --- Tries and Paths", r"""
Hierarchy as nested dicts. \texttt{ITree} autovivifies branches on touch;
\texttt{setpath}/\texttt{getpath} write and read key paths; \texttt{paths}
folds a whole tree back into a flat list of (keypath, leaf). The subset-sum
pair is the deep exhibit: the same search recorded first as a decision tree
(a multiset of solutions) and then as a trie (a set) -- the data structure
changed the semantics."""),
"g7_graphs_grids_heaps": (r"Class VII --- Graphs, Grids, Windows and Heaps", r"""
Things pointing at other things. Adjacency is a \texttt{Tree(1, list)} fold
over the edges; BFS is the \texttt{deque} earning its keep; Dijkstra adds a
heap and lazy deletion; Kahn's topological sort turns cycle detection into a
counting argument; Bellman--Ford is \texttt{until} iterating to a fixed point.
The window problems ride along because their state discipline (add, remove,
valid) is the same closure-shaped thinking on a 1-D track."""),
"g8_dp_and_control": (r"Class VIII --- Dynamic Programming and Control", r"""
Choices now change what is possible later -- so memoise the future's needs.
The craft is naming the \emph{state}: index pairs for alignments
(\texttt{lcs}, \texttt{edit\_distance}), remaining capacity for knapsacks, a
rectangle for guillotine cuts, a bitmask plus room for the partition problem.
If you can say ``the future only needs $X$'' in one sentence, \texttt{memo}
over $X$ writes the rest. The parser closes the class: recursive descent
is control flow as grammar."""),
"g9_stack_folds": (r"Class IX --- Stack Folds", r"""
The prelude has no stack section because a plain Python list already is one:
\texttt{append} pushes, \texttt{pop} pops, both $O(1)$. What this class adds is
the \emph{fold} discipline: the stack is the accumulator, and in
\texttt{balanced\_brackets} the failed state is \texttt{None} -- a poison value
that propagates untouched, Maybe as an accumulator. \texttt{next\_greater}
graduates to the monotonic stack, the pro tier, with its lovely amortised
$O(n)$ argument."""),
}

PRELUDE_CHAPTERS = [
 (r"Functions About Functions", [1, 2], r"""
Functional programming begins with one liberty: a function is a value. It can
be passed, returned, stored in a dict, and -- most usefully -- \emph{shaped} by
other functions. Section~1 is a kit of shapers. \texttt{flip} swaps an argument
order so a function fits a slot it was not written for; \texttt{curry} and
\texttt{uncurry} convert between two-argument functions and functions of pairs;
\texttt{partial} freezes the first arguments; \texttt{on} routes both arguments
of a comparison through a key first.

Two definitions here are load-bearing conventions rather than tools.
\texttt{NOTHING} is a private sentinel meaning ``no argument was supplied'' --
it lets \texttt{foldl} and \texttt{accumulate} distinguish an omitted initial
value from a legitimate \texttt{None}. And the file-wide contract \emph{None is
Nothing}: every partial function in the prelude signals absence with
\texttt{None}, \texttt{fromMaybe} is the standard way to land a default, and
\texttt{isJust}/\texttt{isNothing} name the None test itself -- a predicate
you can hand to \texttt{find}, \texttt{filter\_} or \texttt{all}, and one that
asks identity against \texttt{None} rather than truthiness, so \texttt{0} and
\texttt{""} count as present.
Section~2 adds the pair accessors -- \texttt{fst}, \texttt{snd}, \texttt{swap}
-- which read better than \texttt{[0]} and \texttt{[1]} in code built from
tuples.""", r""">>> add = lambda a, b: a + b
>>> flip(add)("world", "hello ")
'hello world'
>>> on(add, len)("ab", "c")            # combine THROUGH a key
3
>>> fromMaybe(0, None), fromMaybe(0, 5)
(0, 5)
>>> isJust(0), isNothing(None)         # identity, never truthiness
(True, True)
>>> swap((1, 2))
(2, 1)"""),
 (r"Arithmetic and Logic", [3], r"""
Small tools, chosen for their sharp edges. \texttt{signum} compresses a
three-way comparison into arithmetic. \texttt{div}/\texttt{mod} floor like
Haskell's \texttt{div}; \texttt{quot}/\texttt{rem} truncate toward zero --
knowing which one your language does to negative numbers has decided real
interviews. \texttt{gcd} recurses safely because Euclid's depth is tiny even
for 64-bit inputs (the worst case is consecutive Fibonaccis), and
\texttt{isqrt} is Newton's method on integers: floor square roots with no
floating point in sight.""", r""">>> signum(-7), signum(0), signum(3)
(-1, 0, 1)
>>> div(-7, 2), quot(-7, 2)            # floor vs truncate
(-4, -3)
>>> isqrt(10**18)
1000000000"""),
 (r"Lists I: The Basics", [4], r"""
The list vocabulary. \texttt{head}/\texttt{tail}/\texttt{init}/\texttt{last}
name the four ways to take a list apart at its ends; \texttt{null} asks if
there is anything left -- together they are the grammar of structural
recursion. Three definitions deserve special study. \texttt{nub} deduplicates
\emph{keeping first occurrences}, exploiting the guarantee that dicts remember
insertion order. \texttt{transpose} flips rows and columns, ragged-safe like
Haskell's -- short rows simply drop out of later columns. \texttt{pairwise}
zips a list against its own tail, giving every element
its right neighbour -- the tool for any rule about adjacency. The prefix family
(\texttt{isPrefixOf}, \texttt{isSuffixOf}, \texttt{stripPrefix}) works on
strings and lists alike, and \texttt{isSuffixOf}'s comment preserves a scar:
\texttt{xs[-0:]} is the \emph{whole} list, so never slice a suffix by
\texttt{-len(p)}.""", r""">>> nub([3, 1, 3, 2, 1])
[3, 1, 2]
>>> transpose([[1, 2, 3], [4, 5, 6]])
[[1, 4], [2, 5], [3, 6]]
>>> pairwise([1, 4, 9])
[(1, 4), (4, 9)]
>>> stripPrefix("re", "rebuild")
'build'"""),
 (r"Lists II: Higher-Order", [5], r"""
Where loops go to be named. \texttt{map\_} transforms, \texttt{filter\_}
selects, \texttt{concat} flattens one level, and \texttt{concatMap} does both
at once -- it is the backbone of enumeration (``for every choice, produce all
results, pooled''). \texttt{find} is the early exit folds cannot perform: it is
lazy, works on infinite streams, and returns \texttt{None} on failure, feeding
\texttt{fromMaybe}. \texttt{mapMaybe} is the messy-input workhorse -- map a
parser that returns value-or-\texttt{None}, drop the Nothings, one pass. When
input is dirty, reach for it before you reach for a loop with an \texttt{if}
and a flag.""", r""">>> concatMap(lambda w: [w, w.upper()], ["a", "b"])
['a', 'A', 'b', 'B']
>>> find(lambda x: x % 7 == 0, count(1))     # lazy: an infinite stream
7
>>> mapMaybe(lambda s: int(s) if s.isdigit() else None, ["3", "x", "7"])
[3, 7]"""),
 (r"Folds", [6], r"""
The fold is the master pattern: an accumulator, a combining function, one pass.
\texttt{foldl} is the definition -- modern Python has no builtin fold (its
\texttt{reduce} was banished to \texttt{functools}), so the prelude keeps only
the Haskell name -- functools can wait for days when imports return. Study
\texttt{foldl}'s handling of the missing initial value via
\texttt{NOTHING}. \texttt{foldr} is derived from
\texttt{foldl} by flipping and reversing -- an identity that is only valid
because Python is strict, and stated in the file header so you never forget the
caveat. \texttt{all}/\texttt{any} are the Boolean folds, used bare as builtins
over Booleans; \texttt{compose} folds a tuple of functions into one.

The section ends with the \emph{enumeration folds} -- brute-force licenses.
\texttt{subsequences} builds the powerset by doubling the accumulator per
element ($2^n$: fine to $n \approx 20$, and you should say that bound out
loud); \texttt{replicateM} builds every length-$n$ word over an alphabet
($|xs|^n$). When $n$ is small, honest enumeration beats clever and fragile.""",
 r""">>> foldl(lambda a, x: a * 10 + x, [1, 2, 3], 0)
123
>>> compose(str.strip, str.upper)("  hi  ")
'HI'
>>> subsequences([1, 2])
[[], [1], [2], [1, 2]]
>>> replicateM(2, "ab")
[['a', 'a'], ['a', 'b'], ['b', 'a'], ['b', 'b']]"""),
 (r"Scans, Streams, and Finite Views", [7, 8, 9], r"""
A scan is a fold that keeps its history: \texttt{scanl} hands back every
intermediate accumulator. Prefix sums are \texttt{scanl (+) 0}; running
minima are \texttt{scanl1 min}; the depth of nested parentheses is a scan over
$\pm1$. When you need ``the state at every step'', do not run $n$ folds -- run
one scan.

Section~8 turns to streams: generators that may never end.
\texttt{count}, \texttt{repeat}, \texttt{cycle}, \texttt{iterate} produce;
nothing is computed until something consumes. \texttt{unfoldr} is
\texttt{iterate}'s finite twin -- \texttt{f(seed)} returns \texttt{(value,
seed')} or \texttt{None} to stop -- and it ends the habit of threading
\texttt{(state, acc)} tuples through loops. Section~9 supplies the consumers
and finite views: \texttt{take}, \texttt{takeWhile}/\texttt{dropWhile},
\texttt{span}/\texttt{break\_} for splitting at a condition (one pass, safe
on generators), and the view
factories \texttt{inits}, \texttt{tails} (every prefix and suffix -- substring
problems start there) and \texttt{chunksOf}. Note the deliberate naming: these
carry Python's own \texttt{itertools} names with Haskell semantics, so both
vocabularies stay warm.""", r""">>> scanl(lambda a, b: a + b, 0, [3, 1, 4])
[0, 3, 4, 8]
>>> take(5, iterate(lambda x: 2 * x, 1))
[1, 2, 4, 8, 16]
>>> unfoldr(lambda m: None if m == 0 else (m % 10, m // 10), 407)
[7, 0, 4]
>>> tails("abc")
['abc', 'bc', 'c', '']"""),
 (r"Order and Text", [10, 11], r"""
Sorting with keys is the single most-used line in any timed test.
\texttt{sortOn} evaluates the key once per element; tuple keys give multi-level
orderings, and the \texttt{(-count, name)} idiom gets ``count descending, ties
alphabetical'' in one shot -- something \texttt{reverse=True} cannot do.
\texttt{minOn}/\texttt{maxOn} answer ``best element by key'' in $O(n)$;
sorting first to take the head is paying $O(n \log n)$ for the same
information. \texttt{merge} joins two sorted lists stably -- the heart of merge
sort -- and the \texttt{bisect} pair performs binary search over sorted data:
\texttt{bisect\_left} finds the first slot $\ge x$, \texttt{bisect\_right} the
first $> x$; their difference counts occurrences. Section~11 is four honest
aliases (\texttt{words}, \texttt{unwords}, \texttt{lines}, \texttt{unlines})
that make string pipelines read like Haskell.""",
 r""">>> sortOn(lambda w: (len(w), w), ["bb", "a", "ccc", "aa"])
['a', 'aa', 'bb', 'ccc']
>>> minOn(abs, [-3, 2, 5])
2
>>> bisect_right([1, 3, 3, 5], 3) - bisect_left([1, 3, 3, 5], 3)
2
>>> unwords(words("  such   spacing  "))
'such spacing'"""),
 (r"Containers: Dicts, Bags, Trees, Heaps", [12], r"""
The longest section, and the richest. \texttt{defaultdict} rebuilds
autovivification from one dunder: touch a missing key and the factory fills it.
\texttt{Counter} is its \texttt{int} instance. Then the dict-building folds:
\texttt{insertWith} combines on collision, \texttt{fromListWith} folds a pair
list into a dict, combining collisions with f(new, old) -- Haskell's order, so
groups keep arrival order when you combine old + new -- and \texttt{unionWith}
merges two dicts under any combining function. \texttt{insertWith} is
persistent, returning a fresh dict like the immutable original. The bag
operations show the same shape specialised to
multisets -- and comparing \texttt{bag\_union} (\texttt{max}) with a summing
merge (\texttt{+}) is a first lesson in monoids.

\texttt{Tree} and \texttt{ITree} nest defaultdicts into tries;
\texttt{paths} folds a whole tree to \texttt{(keypath, leaf)} pairs;
\texttt{setpath} writes (autovivifying), \texttt{getpath} reads
\emph{without} autovivifying -- reading with \texttt{[]} would plant ghost
branches. The section closes with three machines built from scratch: a
two-stack \texttt{deque} with all four ends amortised $O(1)$, union--find with
path halving, and a binary heap as two functions on a plain list. Owning these
means never being helpless when a ``batteries included'' import is off the
table.""", r""">>> fromListWith(lambda a, b: a + b, [("a", [1]), ("b", [2]), ("a", [3])])
{'a': [1, 3], 'b': [2]}
>>> unionWith(max, Counter("aab"), Counter("abb")) == {'a': 2, 'b': 2}
True
>>> t = ITree(); setpath(t, list("hi") + ["$"], "hi"); paths(t)
[(['h', 'i', '$'], 'hi')]
>>> h = []; heappush(h, 3); heappush(h, 1); heappop(h)
1"""),
 (r"Nodes, Grids, Windows, Control", [13, 14, 15], r"""
Section~13 covers the LeetCode givens. \texttt{TreeNode} with \texttt{tfold} --
a catamorphism -- makes every traversal a one-liner: in-, pre-, post-order,
depth and size are just different combining functions. \texttt{levelorder} is
BFS, the deque earning its keep. The linked-list block collects the pointer
idioms worth knowing cold: build by \texttt{foldr}, reverse with three
pointers, fast/slow for the middle, Floyd for cycles, dummy-head for merges.

Section~14 gives grids their neighbour generators (bounds-checked, so BFS
bodies stay clean) and \texttt{longest\_window}, the sliding-window skeleton:
you supply \texttt{add}, \texttt{rem} and \texttt{valid} as closures and it
does the two-pointer bookkeeping. Section~15 is control: \texttt{memo},
an unbounded memo in eight lines (with the cache exposed, so you can watch a DP
table fill), and \texttt{until}, the fixed-point loop -- iteration without
recursion depth limits.""", r""">>> t = TreeNode(2, TreeNode(1), TreeNode(3))
>>> inorder(t), tdepth(t), tsize(t)
([1, 2, 3], 2, 3)
>>> to_list(reverse_list(from_list([1, 2, 3])))
[3, 2, 1]
>>> sorted(neighbors4(0, 0, 2, 2))
[(0, 1), (1, 0)]
>>> until(lambda x: x > 100, lambda x: x * 2, 1)
128"""),
]

LADDER = [
 ("SORT FIRST",
  r"``sorted'', ``k-th'', ``closest pair'', ``can they be arranged'', ``intervals''",
  r"sort, sortOn, bisect\_left, merge"),
 ("FOLD",
  r"``total'', ``count'', ``largest'', ``best single \ldots''",
  r"foldl, minOn / maxOn"),
 ("SCAN",
  r"``running'', ``so far'', ``at each step'', ``prefix sums''",
  r"scanl, scanl1"),
 ("DICT FOLD",
  r"``group by'', ``frequency'', ``most common'', ``anagrams together''",
  r"fromListWith, Counter, unionWith"),
 ("WINDOW",
  r"``substring'', ``contiguous'', ``longest run'', ``within the last k''",
  r"longest\_window, pairwise"),
 ("STACK",
  r"``nested'', ``matching pairs'', ``most recent open'', ``next greater''",
  r"list as stack; foldl with stack acc"),
 ("UNFOLD",
  r"``digits of'', ``split into pieces'', ``repeat until'', ``simulate''",
  r"unfoldr, iterate + take"),
 ("ENUMERATE",
  r"``all subsets'', ``any combination'', ``every way to pick''",
  r"subsequences, replicateM, cross"),
 ("TREE / PATHS",
  r"``nested'', ``prefix'' (trie), ``directories'', ``solutions as paths''",
  r"ITree, paths, setpath, tfold"),
 ("GRAPH",
  r"``prerequisites'', ``network'', ``shortest route'', ``reachable''",
  r"Tree(1,list) adjacency, deque BFS, heap, until"),
 ("MEMOIZE",
  r"``fewest'', ``max value'', ``count the ways'', ``can it be done''",
  r"memo over indices"),
]


# --------------------------------------------------------------- assembly

tex = []
A = tex.append

A(r"""\documentclass[11pt,letterpaper]{book}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{booktabs}
\usepackage{array}
\usepackage{emptypage}
\usepackage[hidelinks]{hyperref}
\makeatletter                            % TOC: room for two-digit section numbers (12.10)
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
  upquote=true,aboveskip=8pt,belowskip=8pt,xleftmargin=1.1em,
  frame=leftline,framerule=0.8pt,rulecolor=\color{rulecol}}
\lstdefinestyle{spec}{basicstyle=\ttfamily\small,keepspaces=true,
  columns=fullflexible,breaklines=true,breakatwhitespace=true,
  postbreak=\mbox{\textcolor{numcol}{$\hookrightarrow$}\space},
  upquote=true,aboveskip=6pt,belowskip=6pt,xleftmargin=1.1em,
  frame=leftline,framerule=0.8pt,rulecolor=\color{rulecol},language={}}
\lstdefinestyle{file}{language=Python,basicstyle=\ttfamily\footnotesize,
  keywordstyle=\color{kw}\bfseries,commentstyle=\color{cm}\itshape,
  stringstyle=\color{st},showstringspaces=false,keepspaces=true,
  columns=fullflexible,breaklines=true,breakatwhitespace=true,
  postbreak=\mbox{\textcolor{numcol}{$\hookrightarrow$}\space},
  upquote=true,numbers=left,numberstyle=\tiny\color{numcol},numbersep=8pt,
  aboveskip=6pt,belowskip=6pt}

\setcounter{tocdepth}{1}
\setlength{\parskip}{2pt}

\title{\Huge\bfseries PythonFP\\[6pt]
  \Large Functional Programming in Python, the Prelude Way\\[16pt]
  \normalsize A course in one file and seventy-four problems}
\author{J.~L.~Clements~III}
\date{\today}

\begin{document}
\frontmatter
\maketitle

\chapter{Preface}
This book teaches functional programming in Python through a single artifact:
\texttt{prelude.py}, a Haskell-style prelude rebuilt in pure Python with no
imports, read top to bottom in strict define-before-use order. Around it sit
seventy-four problems, each solved by \emph{composing} prelude tools rather
than narrating loops.

The course has three movements. Part~I teaches how to \emph{think} in this
style: what functional Python buys you, and the recognition drill that maps the
words of a problem statement to the right tool. Part~II walks the prelude
section by section -- every definition, why it exists, and what it displaces.
Part~III applies the toolkit to nine classes of problems; every problem appears
with its statement, contract, hint, doctests and a worked solution.

The book is generated from the course files themselves, so every listing is the
real code. The intended use is active: keep \texttt{prelude.py} open beside the
book, attempt each problem in its practice file before reading the solution,
and let the doctests judge you. Appendix~D describes that workflow.

\tableofcontents
\mainmatter
""")

# ---------------- Part I
A(r"\part{Thinking in PythonFP}" + "\n")

A(r"""\chapter{Why Functional Python}
\section{One file, no imports}
Everything in this course runs on bare \texttt{python3}. That constraint is not
asceticism; it is the point. When \texttt{collections.Counter} is an import,
it is a black box; when it is six lines you have retyped from memory, it is
knowledge. The prelude rebuilds the working parts of Haskell's standard
vocabulary -- and the useful corners of \texttt{Data.List}, \texttt{Data.Map},
\texttt{Data.Maybe} and friends -- as Python one-liners and small definitions
you can carry into any interview editor, any locked-down environment, any
whiteboard.

\section{What ``functional'' buys you}
Three habits, none of which require giving up Python:

\begin{itemize}
\item \textbf{Functions are values.} Sort keys, predicates, combining
functions, closures over window state: passing behaviour as data is what lets
one skeleton (\texttt{longest\_window}, \texttt{foldl},
\texttt{fromListWith}) serve a hundred problems.
\item \textbf{Data in, data out.} Prefer expressions that build new values to
statements that mutate old ones. Not because mutation is sinful -- the prelude
mutates inside its machines -- but because data-in/data-out functions compose,
test in one line, and survive a mutating interview prompt.
\item \textbf{Name the transformation.} A loop narrates \emph{how}; a
composition of named tools states \emph{what}. \texttt{unwords(reversed(%
words(s)))} is its own documentation. Vocabulary is leverage: every name you
own is a loop you never write again.
\end{itemize}

\section{Conventions you must internalise}
\textbf{None is Nothing.} Every partial prelude function signals absence with
\texttt{None}; \texttt{fromMaybe} lands defaults, \texttt{mapMaybe} and
\texttt{catMaybes} sweep Nothings out of lists, \texttt{isJust} and
\texttt{isNothing} test a single value. Never overload \texttt{0} or
\texttt{""} to mean ``missing''.

\textbf{Haskell names shadow builtins by design.} \texttt{id}, \texttt{map\_},
\texttt{filter\_}, \texttt{sort}: inside prelude code the Haskell vocabulary
wins. The trailing underscore marks the few collisions with keywords
(\texttt{not\_} being the survivor; \texttt{all}/\texttt{any} serve bare).

\textbf{Define before use.} \texttt{prelude.py} reads top to bottom; every name
is already defined when you meet it. This is also how you should
\emph{study} it: read a section, close the file, retype its one-liners from
memory, and check yourself. The definitions are short on purpose.
""")

A(r"""\chapter{The Recognition Drill}
Most timed failures are not coding failures; they are \emph{recognition}
failures -- ten minutes spent hand-rolling a loop that was a \texttt{scanl1}.
The drill below runs before any typing.

\section{Step 0: name three things}
From the statement, extract: the \textbf{input shape} (a list? two lists?
pairs? a grid? edges?); the \textbf{output shape} (one value? a list? a dict?
yes/no? \emph{all} solutions?); and the \textbf{quantity word} (the ``most'',
``fewest'', ``longest'', ``every'' that names what is asked). The output shape
is the strongest clue: one value smells like a fold, a dict smells like
\texttt{fromListWith}, ``all of them'' smells like enumeration or a tree.

\section{Step 1: walk the ladder}
Match the statement's words against the trigger column; the first row that
fits names your tools.

\begin{center}\small
\begin{tabular}{@{}p{0.14\textwidth}p{0.44\textwidth}p{0.32\textwidth}@{}}
\toprule
\textbf{Shape} & \textbf{Trigger words} & \textbf{Reach for} \\
\midrule
""")
for shape, trig, tools in LADDER:
    A("%s & %s & \\texttt{%s} \\\\\n" % (shape, trig, tools))
A(r"""\bottomrule
\end{tabular}
\end{center}

Cross-cutting, any row: messy input $\rightarrow$ \texttt{mapMaybe}; absence
$\rightarrow$ \texttt{None} + \texttt{fromMaybe}; first hit $\rightarrow$
\texttt{find}; same-up-to-order $\rightarrow$ a canonical form (\texttt{sort}
or \texttt{Counter}); connectivity $\rightarrow$ \texttt{dsu}; repeated
best-next $\rightarrow$ the heap.

\section{Step 2: say it out loud}
State the shape, the tools, and the complexity before typing: ``group-by-key
with \texttt{fromListWith}, then best-by-key with \texttt{minOn},
$O(n)$.'' If two rows both apply, \textbf{the row that names the output wins}:
``most common word'' \emph{mentions} frequency (dict fold) but \emph{asks for}
one value (fold) -- so \texttt{Counter} feeds \texttt{minOn}.

Complexity vocabulary to keep loaded: $\sim$$10^7$ simple Python operations
per second is a safe planning number; $n \le 20$ licenses $2^n$ enumeration;
$n \le 10^4$ licenses $O(n^2)$; $n \le 10^6$ demands $O(n \log n)$ or better.

\section{Step 3: compose, don't invent}
Solutions in this course are pipelines of two or three prelude names plus one
lambda of your own. If you find yourself writing a raw loop, first ask which
combinator you are rebuilding. Sometimes the answer is ``none -- this loop is
the algorithm'' (BFS, a parser, a heap sift); then write the loop proudly.
""")

# ---------------- Part II
A(r"\part{The Prelude, Section by Section}" + "\n")
for title, secs, prose, repl in PRELUDE_CHAPTERS:
    A("\\chapter{%s}\n" % title)
    A(prose + "\n")
    for n in secs:
        A(code(SEC[n]))
    A("\n\\noindent\\textit{At the REPL:}\n")
    A(code(repl, "spec"))

# ---------------- Deep Dives (closes Part II)
A(r"""\chapter{Deep Dives}
The chapters above teach the prelude a section at a time; this one slows down
for the twenty-five names where the concept is the hard part. Each dive keeps
one shape: how the definition actually works (often with the evaluation
traced), why it earns its place, the Haskell connection where there is one,
and the sibling to contrast it with -- ending in one sentence built to be
remembered. Every example is a doctest from \texttt{prelude-doctests.py}, so
everything here runs.
""")
_DEFS = entrylib.definitions(ROOT)
for _sec_name, _entries in entrylib.parse(ROOT):
    for _e in _entries:
        if not entrylib.is_deep(_e):
            continue
        A("\n\\section{%s}\n" % esc(_e["name"]))
        A("\\noindent\\textit{[%s]} --- %s\n"
          % (esc(_sec_name), esc(" ".join(entrylib.gist(_e).split()))))
        for _kind, _txt in _e["segments"][1:]:
            if _kind == "c":
                A(code(_txt, "spec"))
            else:
                A("\n" + esc(" ".join(_txt.split())) + "\n\n")
        _impl = _DEFS.get(_e["name"])
        if _impl:
            if not entrylib.has_walkthrough(_e):
                A("\nRoll your own --- the definition:\n\n")
            A(code(entrylib.unalign(_impl)))

# ---------------- Part III
A(r"\part{The Nine Problem Classes}" + "\n")
for g in GROUPS:
    heading, intro = GROUP_INTROS[g]
    A("\\chapter{%s}\n" % heading)
    A(intro + "\n")
    A(r"""\medskip\noindent\textit{Practice files live in }\texttt{%s/}\textit{;
each carries the prelude snippets it needs inline. Attempt every problem there
before reading on -- the doctests are the referee.}""" % esc(g) + "\n")
    for path in sorted((ROOT / g).glob("[0-9]*.py")):
        name, tagline, body, tests = load_problem(path)
        sol = load_solution(g, path.stem)
        A("\n\\section{%s: %s}\n" % (esc(name), esc(tagline)))
        A(code(body, "spec"))
        A("\\noindent\\textit{Doctests:}\n")
        A(code(tests, "spec"))
        A("\\noindent\\textbf{Solution.}\n")
        A(code(sol))
        if path.stem in REMARKS:
            A("\n\\noindent\\textit{Remark.} " + REMARKS[path.stem] + "\n")

# ---------------- Appendices
A(r"""\appendix
\part{Appendices}
\chapter{prelude.py, Complete}
The whole file, exactly as it ships -- 15 sections, define-before-use,
no line over 105 columns.
""")
A(code(ROOT.joinpath("prelude.py").read_text(), "file"))

A(r"""\chapter{Haskell Provenance}
Where each borrowed name comes from, for the day you meet the originals.

\begin{center}\small
\begin{tabular}{@{}p{0.25\textwidth}p{0.68\textwidth}@{}}
\toprule
\textbf{Module} & \textbf{Names} \\
\midrule
Prelude &
id, const, flip, curry, uncurry, fst, snd, succ, pred, even, odd, signum,
div, mod, quot, rem, gcd, lcm, head, tail, init, last, null, elem,
replicate, drop, splitAt, lookup, zip, unzip, map, filter,
concat, concatMap, zipWith, foldl, foldr, product, iterate, repeat,
cycle, take, takeWhile, dropWhile, span, break, words, unwords, lines,
unlines, until \\
Data.List &
find, partition, nub, sortOn, sortBy, transpose, unfoldr, subsequences,
inits, tails, isPrefixOf, isSuffixOf, stripPrefix, minimumBy/maximumBy
(as minOn/maxOn), groupBy, group \\
Data.Map &
insertWith, fromListWith, unionWith \\
Data.Maybe &
fromMaybe, isJust, isNothing, mapMaybe, catMaybes (None is Nothing) \\
Data.Function & on \\
Data.Tuple & swap \\
Control.Monad & replicateM \\
Data.List.Split & chunksOf \\
Python itertools (names) &
count, islice, takewhile, dropwhile, chain, accumulate, starmap, pairwise --
kept under Python's own names so both vocabularies stay warm \\
\bottomrule
\end{tabular}
\end{center}

Deliberately not ported: laziness-dependent knot-tying (\texttt{fix}),
typeclass machinery, and monadic control flow -- Python is strict and
untyped, and the prelude stays honest about it.
""")

A(r"""\chapter{How to Practice}
The course directory is the textbook's other half:

\begin{itemize}
\item \texttt{fpython/prelude.py} -- the toolkit. Study loop: read a section,
close the file, retype its definitions from memory, diff.
\item \texttt{fpython/g1\_\ldots{} g9\_\ldots} -- 74 practice files. Each is
self-contained: statement, contract, hint, the needed snippets copied inline,
a \texttt{\# solution goes here} slot, and a doctest runner. Run with
\texttt{python3 file.py} until it reports $N/N$.
\item \texttt{fpython/solutions/} -- the same files solved, flat, named
\texttt{g2\_08\_chunks.py}. For \emph{after} the fight: compare shapes, not
before.
\item \texttt{fpython/prelude\_flowchart.svg} -- the recognition ladder of
Chapter~2 as a printable picture.
\end{itemize}

Work the classes in order; within a class, any order. Narrate out loud as you
solve -- shape, tools, complexity -- because the interview grades the
narration as much as the code. When a solution of yours beats the book's,
trust the doctests and keep yours.
""")

A(r"\backmatter" + "\n" + r"\end{document}" + "\n")

OUT.write_text("".join(tex))
print("wrote %s (%d KB)" % (OUT, OUT.stat().st_size // 1024))

r = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode",
                    "-halt-on-error", OUT.name], cwd=HERE,
                   capture_output=True, text=True)
if r.returncode != 0:
    print(r.stdout[-3000:])
    raise SystemExit("latexmk failed")
subprocess.run(["latexmk", "-c", OUT.name], cwd=HERE, capture_output=True)
info = subprocess.run(["pdfinfo", str(HERE / "PythonFP.pdf")],
                      capture_output=True, text=True).stdout
print([l for l in info.splitlines() if l.startswith(("Pages", "Page size"))])
