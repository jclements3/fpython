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


def terse_sections():
    """[(num, name, code_chunk)] by splitting haskell-terse.py at its own
    "# N. name" markers; the few import lines before the first marker are
    folded into section 1's chunk, since they logically belong there."""
    import re
    text = (ROOT / "haskell-terse.py").read_text()
    marker = re.compile(r"^# (\d+)\. (.+)$")
    chunks, cur, preamble = [], None, []
    for l in text.splitlines():
        m = marker.match(l)
        if m:
            if cur:
                chunks.append(cur)
            cur = [int(m.group(1)), m.group(2), []]
        elif cur is None:
            preamble.append(l)
        else:
            cur[2].append(l)
    if cur:
        chunks.append(cur)
    chunks[0][2] = preamble + chunks[0][2]
    return [(n, name, "\n".join(lines)) for n, name, lines in chunks]


# Commentary for chapter 1's per-section walkthrough: prose explaining the
# section's role, a few doctest-style examples (every one run against
# haskell.py and verified before being written here -- see the session
# that authored this), and for the sections whose mechanism most needs it,
# a step-by-step evaluation trace.
SECTION_COMMENTARY = {
1: (r"""
This section is the adapter kit: none of these change what a value IS, only how it gets PASSED
around. \texttt{compose} and \texttt{pipe} chain functions together (right-to-left and left-to-right
respectively); \texttt{on} routes a comparison through a shared key first; \texttt{curry}/
\texttt{uncurry} convert between a two-argument function and a function of one pair; \texttt{flip}
swaps an argument order to fit a slot it wasn't written for. The five one-liners at the top
(\texttt{identity}, \texttt{const}, \texttt{flip}, \texttt{curry}, \texttt{uncurry}) are the smallest
possible versions of these ideas -- worth reading once, not worth a paragraph each.""",
[">>> compose(str, abs)(-3)", "'3'",
 ">>> pipe(-3, abs, str)", "'3'",
 ">>> on(sub, len)('haskell', 'py')", "5",
 ">>> curry(add)(3)(4)", "7"],
r"""Trace of \texttt{compose(str, abs)(-3)} -- right to left, so \texttt{abs} runs FIRST:
  compose(str, abs)  builds g(x) = str(abs(x))
  g(-3)
    abs(-3)  -> 3
    str(3)   -> '3'
  result: '3'"""),
2: (r"""
Pair accessors. \texttt{fst}/\texttt{snd} read a 2-tuple's first or second element by name instead
of by index, which reads better inside a \texttt{sortOn} key or a dict comprehension than a bare
\texttt{[0]}/\texttt{[1]} does. \texttt{swap} exchanges the two -- built from \texttt{o(tuple,
reversed)}, composition rather than indexing.""",
[">>> fst(('a', 1))", "'a'",
 ">>> snd(('a', 1))", "1",
 ">>> swap((1, 2))", "(2, 1)"],
None),
3: (r"""
Three sentinel OBJECTS, not values -- each is a distinct \texttt{\_Sentinel} instance that is never
equal to anything except itself, so none of them can be confused with a legitimate piece of data.
\texttt{NOTHING} means ``no answer'' (Maybe's absence, distinct from a stored \texttt{None});
\texttt{FAIL} means ``the parser gave up''; \texttt{\_MISS} is a private default meaning ``no argument
was supplied'', used internally by \texttt{foldl}/\texttt{scanl} so a real \texttt{None} can still be
passed as a seed. \texttt{isJust}/\texttt{isNothing} name the \texttt{NOTHING} test itself as a
predicate, so it can be handed to \texttt{find}, \texttt{filter\_}, or \texttt{all} directly.""",
[">>> isJust(5)", "True",
 ">>> isNothing(NOTHING)", "True",
 ">>> NOTHING == None", "False"],
None),
4: (r"""
Small tools with a sharp edge: Python's own \texttt{//} and \texttt{\%} FLOOR toward negative
infinity, but Haskell's \texttt{quot}/\texttt{rem} TRUNCATE toward zero -- the two families disagree
the moment a negative number is involved, and this section keeps both available under their own
names rather than picking one and hiding the difference. \texttt{signum} compresses a three-way
comparison into arithmetic; \texttt{succ}/\texttt{pred} work on both numbers and single characters.""",
[">>> quot(-7, 2)", "-3",
 ">>> rem(-7, 2)", "-1",
 ">>> -7 // 2, -7 % 2", "(-4, 1)",
 ">>> signum(-5)", "-1",
 ">>> succ('a')", "'b'"],
None),
5: (r"""
The trunk of the file. A FOLD collapses a list to one value; a SCAN is a fold that keeps every
intermediate accumulator instead of just the last; an UNFOLD runs the whole idea backwards, growing
a list from a seed instead of consuming one. \texttt{scanl} here is exactly \texttt{itertools.
accumulate} under its Haskell name -- naming it differently doesn't change what runs.
\texttt{unfoldr}'s step function returns \texttt{(value, next\_seed)} to keep going, or
\texttt{NOTHING} to stop; that single convention is why countdown timers, digit sequences, and
Collatz chains all turn out to be one \texttt{unfoldr} call apiece.""",
[">>> foldl(lambda a, b: a - b, [1, 2, 3], 10)", "4",
 ">>> scanl(add, [1, 2, 3], 0)", "[0, 1, 3, 6]",
 ">>> unfoldr(lambda n: NOTHING if n == 0 else (n, n - 1), 3)", "[3, 2, 1]"],
r"""Trace of \texttt{unfoldr(step, 3)} where \texttt{step(n) = NOTHING if n==0 else (n, n-1)}:
  step(3) -> (3, 2)   emit 3, seed becomes 2
  step(2) -> (2, 1)   emit 2, seed becomes 1
  step(1) -> (1, 0)   emit 1, seed becomes 0
  step(0) -> NOTHING  stop
  result: [3, 2, 1]"""),
6: (r"""
Two names, one idea: a stream can be INFINITE because nothing is computed until something asks for
it. \texttt{iterate(f, x)} yields \texttt{x, f(x), f(f(x)), ...} forever; \texttt{take(n, ...)} is
what makes an infinite generator usable by cutting it off after \texttt{n} elements -- \texttt{chain},
\texttt{count}, \texttt{cycle}, and \texttt{repeat} (imported straight from \texttt{itertools} in
section 1's import block) round out the family.""",
[">>> take(5, iterate(lambda n: n * 2, 1))", "[1, 2, 4, 8, 16]"],
None),
7: (r"""
The list's own anatomy: taking it apart at the ends (\texttt{head}/\texttt{tail}/\texttt{init}/
\texttt{last}), cutting it at a position (\texttt{drop}/\texttt{splitAt}), and pairing it against
itself (\texttt{pairwise} zips a list against its own tail, which is why every rule about ADJACENT
elements starts there). \texttt{lookup} and \texttt{stripPrefix} both return \texttt{NOTHING} rather
than raising or returning an ambiguous \texttt{None} on failure.""",
[">>> pairwise([1, 2, 3])", "[(1, 2), (2, 3)]",
 ">>> stripPrefix('foo', 'foobar')", "'bar'",
 ">>> stripPrefix('x', 'foobar') is NOTHING", "True"],
None),
8: (r"""
Where loops go to be named. \texttt{map\_} transforms, \texttt{filter\_} selects, \texttt{concatMap}
enumerates (map, then flatten, in one pass), \texttt{zipWith} combines two lists element-wise. Two
tools do what a raw loop does badly: \texttt{find} stops at the first match even on an infinite
stream, and \texttt{partition} splits a list into (keepers, rest) in a single pass with the predicate
called exactly once per element.""",
[">>> concatMap(lambda x: [x, x], [1, 2])", "[1, 1, 2, 2]",
 ">>> find(even, [1, 3, 4, 5])", "4",
 ">>> partition(even, [1, 2, 3, 4])", "([2, 4], [1, 3])"],
None),
9: (r"""
Finite VIEWS of a sequence. \texttt{span}/\texttt{break\_} cut a sequence at the first place a
condition changes -- a lexer in one call. \texttt{windows(n, xs)} produces every contiguous
length-\texttt{n} slice (a genuine sliding view, not index arithmetic), while \texttt{groupBy}
segments a sequence into runs of CONSECUTIVE equal elements, each new element compared against its
run's first member. \texttt{chunksOf} pages anything into fixed-size (possibly ragged-last) pieces.""",
[">>> windows(3, [1, 2, 3, 4])", "[[1, 2, 3], [2, 3, 4]]",
 ">>> groupBy(lambda a, b: a == b, 'aabba')", "[['a', 'a'], ['b', 'b'], ['a']]",
 ">>> chunksOf(2, [1, 2, 3, 4, 5])", "[[1, 2], [3, 4], [5]]"],
None),
10: (r"""
``Does order unlock it?'' is the first question worth asking of almost any problem: sorting
linearises it, and this section is the toolkit for once it has. \texttt{sortOn} sorts by a computed
key (the key function runs once per element, not once per comparison); \texttt{minOn}/\texttt{maxOn}
answer ``best by key'' in one linear pass instead of sorting the whole list just to look at one end.""",
[">>> sortOn(len, ['abc', 'a', 'ab'])", "['a', 'ab', 'abc']",
 ">>> maxOn(len, ['a', 'abc', 'ab'])", "'abc'"],
None),
11: (r"""
Four names turning text into lists and back: \texttt{words}/\texttt{unwords} split and rejoin on
whitespace, \texttt{lines}/\texttt{unlines} split and rejoin on newlines. Once text becomes a list,
every list tool in this file applies to it -- that conversion is usually the first step, not an
afterthought.""",
[">>> words('a b c')", "['a', 'b', 'c']",
 ">>> unwords(['a', 'b', 'c'])", "'a b c'"],
None),
12: (r"""
Aggregation by key -- a fold aimed at a dictionary instead of a list. \texttt{fromListWith} is THE
dict-building fold: given \texttt{(key, value)} pairs and a combiner, it builds one dict, calling the
combiner as \texttt{f(new, old)} on a collision. \texttt{unionWith} does the same job for two EXISTING
dicts. Choosing the combiner is choosing what the merge MEANS: addition counts, list-append groups,
\texttt{max} takes a bag union.

\textit{Analogy.} Think of \texttt{fromListWith} as a tally sheet at a polling station: each ballot
is a \texttt{(candidate, 1)} pair, and every ballot either opens a new tally or adds to an existing
one using whatever rule you hand it (here, addition). \texttt{unionWith} is the same idea for
MERGING two already-tallied sheets from two polling stations -- the combiner says how to reconcile a
candidate who appears on both.

\texttt{getpath} deserves its own picture: a nested dict IS a tree, and \texttt{getpath(t, ['a',
'b', 'c'])} walks it exactly the way you'd \texttt{cd a/b/c} on a filesystem -- one directory at a
time, and the moment a directory doesn't exist, you stop and report ``not found'' (\texttt{NOTHING})
instead of creating it. That last part matters: \texttt{getpath} only ever READS the tree, it never
grows one by accident the way indexing a \texttt{defaultdict} silently would.""",
[">>> fromListWith(add, [('a', 1), ('a', 2), ('b', 3)])", "{'a': 3, 'b': 3}",
 ">>> unionWith(add, {'a': 1}, {'a': 2, 'b': 3})", "{'a': 3, 'b': 3}",
 ">>> getpath({'a': {'b': {'c': 42}}}, ['a', 'b', 'c'])", "42",
 ">>> getpath({'a': {}}, ['a', 'b', 'c']) is NOTHING", "True"],
r"""Trace of \texttt{getpath} walking the tree \texttt{\{'a': \{'b': \{'c': 42\}\}\}} along
\texttt{['a', 'b', 'c']} -- like changing directories one level at a time:
  start at the whole dict            t = {'a': {'b': {'c': 42}}}
  step 'a': t has key 'a'  -> descend: t = {'b': {'c': 42}}
  step 'b': t has key 'b'  -> descend: t = {'c': 42}
  step 'c': t has key 'c'  -> descend: t = 42
  no keys left -- return t: 42
  (had any step's key been missing, getpath would have stopped right there and returned NOTHING,
   the same way `cd` refuses to enter a directory that isn't there)"""),
13: (r"""
The Maybe monad. \texttt{bind} is Haskell's \texttt{>>=} for this file's Maybe: it passes a value on
to the next step unless that value is already \texttt{NOTHING}, in which case it short-circuits
without calling anything. \texttt{sequenceM}/\texttt{traverseM} extend that idea to a whole list --
ALL of it succeeds, or the combined result is \texttt{NOTHING} -- and \texttt{mapMaybe}/
\texttt{catMaybes} are the ``map into Maybe, then keep only the successes'' pair.

\textit{Analogy.} \texttt{bind} is a factory conveyor belt with a quality inspector stationed at
every workstation. Each inspector checks the part that just arrived; if it's already broken
(\texttt{NOTHING}), they wave the whole belt to a stop right there -- no downstream station ever
even LOOKS at a broken part, let alone tries to work on it. A Maybe VALUE is a part on the belt
(or the ``broken'' signal itself); \texttt{bind} is one inspector's station. Chaining several binds
is the whole assembly line: one break anywhere, and the finished product at the end is
automatically \texttt{NOTHING}, with no station having to explicitly ask ``did the last guy fail?''
\texttt{sequenceM} is the same idea applied to a whole PALLET of parts at once: the pallet only ships
if every single part on it passed inspection.""",
[">>> bind(4, succ)", "5",
 ">>> bind(NOTHING, succ) is NOTHING", "True",
 ">>> sequenceM([1, 2, 3])", "[1, 2, 3]",
 ">>> sequenceM([1, NOTHING, 3]) is NOTHING", "True"],
r"""Trace of a two-step chain, \texttt{bind(bind(4, succ), str)}:
  bind(4, succ)        4 is not NOTHING -> succ(4) -> 5
  bind(5, str)          5 is not NOTHING -> str(5)  -> '5'
  result: '5'
  (had the first step produced NOTHING, the second bind would never call str at all --
   the inspector at station 2 would find nothing to inspect and wave the belt to a stop)"""),
14: (r"""
Where Maybe only says ``it failed'', Either says WHY. \texttt{Ok}/\texttt{Err} are tagged pairs --
\texttt{("ok", value)} or \texttt{("err", reason)} -- and \texttt{bindE} short-circuits on the first
\texttt{Err} exactly like \texttt{bind} does on \texttt{NOTHING}, but keeps the message riding along.
\texttt{note} is the bridge FROM Maybe: it turns a \texttt{NOTHING} into an \texttt{Err} carrying a
reason you supply.

\textit{Analogy.} If Maybe is a doctor's yes/no answer to ``are you okay?'', Either is the doctor's
note that also names the symptom: not just ``no'', but ``no, your temperature is 102''. The factory
line from section 13 gets the same upgrade -- each inspector, instead of just halting the belt on a
broken part, ATTACHES A TAG explaining what was wrong with it, and that tag rides along, unread by
any later station, until it reaches whoever is waiting at the end of the line to read the final
report. \texttt{bindE} is that tag-preserving inspector; \texttt{sequenceE} is the whole-pallet
version, reporting the FIRST tag it finds rather than just ``something on this pallet was bad''.""",
[">>> Ok(5)", "('ok', 5)",
 ">>> Err('bad input')", "('err', 'bad input')",
 ">>> bindE(Ok(4), lambda v: Ok(v + 1))", "('ok', 5)",
 ">>> bindE(Err('boom'), lambda v: Ok(v + 1))", "('err', 'boom')"],
r"""Trace of a three-step Either chain, each step either passing a value on or attaching a tag:
  start:            Ok(4)
  step 1  bindE(Ok(4), lambda v: Ok(v + 1))        -> Ok(5)      (4 was fine, +1 applied)
  step 2  bindE(Ok(5), lambda v: Err('too big') if v > 3 else Ok(v))
                                                    -> Err('too big')   (5 > 3, tag attached HERE)
  step 3  bindE(Err('too big'), lambda v: Ok(v * 2))
                                                    -> Err('too big')   (step 3 never even runs --
                                                                          the tag just rides through)
  final result: ('err', 'too big') -- the reason survives all the way to the end"""),
15: (r"""
Chaining \texttt{bind} calls by hand nests one call inside the next, one level of indentation per
step -- the ``bind pyramid''. \texttt{do} rebuilds that same chain from an ordinary generator
function instead: each \texttt{yield} sends a Maybe (or Either) value to \texttt{do}'s machinery,
which unwraps it and sends the unwrapped value back as the yield expression's result, or aborts the
whole function the moment any step fails. \texttt{doM} wires this to Maybe, \texttt{doE} to Either --
same generator shape, different short-circuit rule.

\textit{Analogy.} A generator written with \texttt{@doM} reads like a recipe written in plain
imperative steps -- ``get the flour, get the sugar, mix them'' -- even though every single step could
secretly fail. \texttt{do} is the kitchen assistant standing behind you: you write the recipe as if
nothing ever goes wrong, and the assistant is the one who actually checks the pantry before handing
you each ingredient, silently walking away with the whole recipe abandoned the moment one ingredient
is missing. You never write the ``is it there?'' check yourself -- \texttt{yield} IS that check,
happening invisibly at every line.""",
[""">>> @doM
... def h(d):
...     a = yield maybe_get(d, 'x')
...     b = yield maybe_get(d, 'y')
...     return a + b
>>> h({'x': 1, 'y': 2})""", "3",
 ">>> h({'x': 1}) is NOTHING", "True"],
r"""What \texttt{do} does to the generator above, roughly desugared to nested binds:
  bind(maybe_get(d, 'x'), lambda a:
      bind(maybe_get(d, 'y'), lambda b:
          a + b))
  -- one yield per bind, read top to bottom instead of nested inward. Calling h({'x': 1}) is like
  the kitchen assistant reaching for sugar that was never bought: the assistant stops right there,
  and you never even see whether the mixing step would have worked."""),
16: (r"""
A parser here is just a function from a string to \texttt{(value, rest)} or \texttt{FAIL} -- once
that shape is fixed, parsers compose like any other function. \texttt{doP} threads the remaining
input through a generator the same way \texttt{doM} threads a Maybe; \texttt{alt} tries alternatives
in order; \texttt{many}/\texttt{sepBy} handle repetition and separator-delimited lists without
recursion (so they cost no stack, no matter how long the input). \texttt{chainl1} folds a sequence of
\texttt{p (op p)*} strictly LEFT, which is how ordinary arithmetic is supposed to associate.

\textit{Analogy.} Parsing a string is like eating a plate of food one bite at a time, always
reporting how much plate is left after each bite: a parser is one BITE (it consumes some prefix of
the input) plus a report of the leftovers. \texttt{alt} is ``try dish A; if you can't stomach it, try
dish B instead, from the same starting plate''. \texttt{many} is ``keep taking bites of the same dish
until there's nothing left you can eat''. \texttt{doP} lets you describe a whole MEAL as a sequence
of bites, one \texttt{yield} per course, with the plate (the remaining input) silently passed from
bite to bite behind the scenes -- you never carry the plate yourself.""",
[">>> n = rx(r'-?\\d+', int)",
 ">>> runParser(sepBy(n, lit(',')), '1,2,3')", "('ok', [1, 2, 3])",
 ">>> runParser(chainl1(n, {'+': add, '-': sub}), '1+2-3')", "('ok', 0)"],
r"""Trace of \texttt{chainl1} folding \texttt{'1+2-3'} strictly LEFT:
  read 1
  see '+', read 2  -> fold:  1 + 2  = 3
  see '-', read 3  -> fold:  3 - 3  = 0
  result: ('ok', 0)   -- left-associative, exactly like hand-written arithmetic, or like a running
  restaurant tab where each new item is added to (or subtracted as a discount from) the running
  total so far, left to right, never revisited once tallied"""),
17: (r"""
A monoid is nothing but an identity element paired with an associative combiner, reified as the pair
\texttt{(empty, op)} -- naming it as DATA means one engine, \texttt{mconcat}, folds every instance,
and \texttt{foldMap} fuses ``measure each element'' with ``combine the measurements'' into one call.
\texttt{both} is the payoff: it pairs two monoids into one, so two statistics (a max AND a min, a
count AND a total) fall out of a SINGLE traversal instead of two separate loops.

\textit{Analogy.} A monoid is a ``combine two of these into one'' rule that comes bundled with its
own honest ``empty'' starting point -- the way a shopping cart's running total combines with a
starting balance of \$0 (not \$1, not ``undefined''), and adding zero items never breaks the rule.
\texttt{Sum} is that shopping-cart total; \texttt{MaxM} is a scoreboard that starts at negative
infinity so the very first score posted is guaranteed to beat it; \texttt{ListM} is string
concatenation's starting point, the empty string, generalised to any list. \texttt{both} is running
TWO REGISTERS over the same single pass of items through a checkout line -- one register tallying
cost, the other counting items -- instead of scanning the cart twice, once per register.""",
[">>> mconcat(Sum, [1, 2, 3])", "6",
 ">>> foldMap(len, Sum, ['ab', 'c'])", "3",
 ">>> both(MaxM, MinM)[1]((3, 1), (5, -2))", "(5, -2)"],
r"""Trace of \texttt{both(MaxM, MinM)} folding the pairs \texttt{(3,1)} then \texttt{(5,-2)} --
two registers, ticking together, over one pass of items through the till:
  start:            (-inf, inf)          -- (MaxM identity, MinM identity): both registers at zero
  op with (3, 1):   (max(-inf,3), min(inf,1))   = (3, 1)     -- both registers update on the SAME item
  op with (5, -2):  (max(3,5), min(1,-2))       = (5, -2)    -- still one pass, two running answers
  result: (5, -2)   -- a running max AND min from one pass over the pairs, not two separate scans"""),
}

DISCUSSION = {
"calculator": r"""
The imperative version's mutable cursor (\texttt{class P: pos = 0}) is a
common workaround for parsing in Python: state lives on an object because
a closure can't reassign an outer \texttt{int} without \texttt{nonlocal}
threaded through every helper. The functional version needs no cursor at
all -- \texttt{doP} threads the remaining input as an ordinary return
value, and \texttt{chainl1} handles left-associativity as a fold instead
of a hand-written \texttt{while} loop. Errors ride two different rails,
too: exceptions in the imperative version, an \texttt{Either} in the
functional one -- and only the \texttt{Either} can be inspected, logged,
or handed to another function without a \texttt{try}/\texttt{except} at
every call site.""",
"gradebook": r"""
Compare all three. The imperative version accumulates into a list and
returns early on a bad row, then needs a SECOND loop afterward just to
compute stats. The object-oriented version is the natural instinct for
validation-heavy code -- a class that grows by \texttt{.add()} and raises
on trouble -- but it still needs a \texttt{try}/\texttt{except} at the
call site, and its \texttt{.stats()} re-walks the same rows the loop
already built. The functional version fuses validation
(\texttt{traverseE}) and the one-pass fold (\texttt{foldMap} with
\texttt{both} nested twice) into two lines: one pass builds the valid
rows AND the stats at once, because \texttt{both} fuses monoids instead
of running loops back to back.""",
"layers": r"""
This is the one example where ``just use a config object'' would
recreate the exact bug the Maybe chapter exists to prevent: a plain class
doing \texttt{self.proxy = self.proxy or default} silently treats an
explicit \texttt{None} as ``no override'' -- backwards from what this
problem needs, since \texttt{FILECFG}'s \texttt{proxy: None} must WIN
over the default, not defer to it. The imperative fix (a private
\texttt{\_UNSET} sentinel) and the functional fix (\texttt{NOTHING}) are
the same idea; object-oriented encapsulation doesn't make the ambiguity
go away, it just relocates where you'd have to solve it.""",
"leaderboard": r"""
All three agree, so look at WHERE each one clamps. The imperative version
clamps inside the loop with an \texttt{if}/\texttt{elif}. The
object-oriented version clamps once, in \texttt{Player.\_\_init\_\_} --
so a \texttt{Player} object is a standing proof that its own score is
always valid, which is real encapsulation value, not just different
syntax for the same check. The functional version clamps by composing two
curried \texttt{max}/\texttt{min} calls into one reusable function
(\texttt{clamp}) -- no class needed to get the same ``validate once,
trust everywhere'' property, because \texttt{clamp100} IS the validated
boundary, not an object that happens to carry one.""",
"logtriage": r"""
Two mutable slots plus a hand-rolled \texttt{seen\_first} flag in the
imperative version, because plain \texttt{None} can't distinguish ``no
error yet'' from ``the first error had an empty message''. The functional
version needs no flag at all: \texttt{First}'s identity is
\texttt{NOTHING}, not \texttt{None}, so the fold itself carries the
distinction. This is the same bug shape as \texttt{layers.py} --
\texttt{first}/\texttt{seen\_first} is a private sentinel invented from
scratch, precisely because Python's \texttt{None} is overloaded.""",
"orderbatch": r"""
Deliberately no object-oriented version here: an \texttt{Order} class
with a \texttt{.total()} method would just move \texttt{total\_imp}'s
body into a method, changing nothing about how a validation failure
PROPAGATES through a whole batch. That propagation -- stop at the first
bad order, carry which one and why -- is what \texttt{doE} and
\texttt{sequenceE} actually buy; encapsulating the per-order check
doesn't touch the batch-level control flow, which is the actual hard
part of this problem.""",
"orgchart": r"""
Also deliberately no object-oriented version: wrapping
\texttt{MANAGER\_OF}/\texttt{EMAIL\_OF} in a class would just rename
\texttt{maybe\_get}/\texttt{doM} as methods, and the real challenge --
keeping ``employee not found'' distinguishable from ``employee found, no
email on file'' -- lives in the DATA MODEL, not the calling convention. A
hypothetical \texttt{.skip\_manager\_email()} written with plain
\texttt{dict.get(x)} returning \texttt{None} would silently reintroduce
the exact ambiguity \texttt{NOTHING} exists to prevent; you would just end
up reimplementing a sentinel inside the class anyway.""",
"payoff": r"""
The imperative \texttt{while} loop and the functional \texttt{unfoldr}
compute the same recurrence, but \texttt{unfoldr}'s stopping condition is
DATA (\texttt{NOTHING}) returned from the step function, not a loop
condition checked from outside. That distinction matters most for
testing: \texttt{step(payment, rate)} is a pure function you can call
directly with one balance and inspect the answer, with no loop, no
mutable balance variable, and no need to run the whole schedule just to
check one step's arithmetic.""",
"sensoralert": r"""
\texttt{windows} and \texttt{groupBy} each replace a hand-rolled
index-walking loop with a name. The imperative version's inner
\texttt{while} (walking \texttt{flags} to find where each run ends) is
exactly what \texttt{groupBy} does generically -- once ``runs of the same
flag value'' is recognised as a \texttt{groupBy} problem, the run-finding
code disappears entirely, replaced by grouping and then filtering for the
runs that are \texttt{True}.""",
"wordfreq": r"""
\texttt{pipe} reads top to bottom in the order the data actually flows --
lowercase, split, count, sort, take -- while the imperative version's
five separate steps (build counts, get items, sort in place, slice) are
the same five stages with no name tying them together. Neither version is
shorter by much; the functional one is easier to extend, because
inserting a new stage means inserting one more line in the \texttt{pipe}
call, not renumbering a sequence of loop variables.""",
}

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
Every name this book teaches, in the order it is defined, broken into the same seventeen sections
\texttt{haskell.py} itself uses -- each section's code first, then commentary, a few verified
examples, and for the sections whose mechanism most needs it, a step-by-step trace. Comments and
docstrings are stripped from the listings themselves (that is what makes them worth calling
``terse''); everything explanatory here is written fresh, not copied out of the source.
""")
    for num, name, code in terse_sections():
        A("\\section*{%s. %s}\n" % (num, esc(name)))
        A(lst(code, "code"))
        prose_text, examples, trace = SECTION_COMMENTARY[num]
        A(prose_text + "\n")
        if examples:
            A(lst("\n".join(examples), "ex"))
        if trace:
            A("\\noindent\\textit{Illustration.}\n")
            A(lst(trace, "ex"))
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
    for stem, title, imp, fn, oop, demo, output in examplelib.load(EXAMPLES):
        A("\\chapter{%s}\n" % esc(stem))
        A(prose(title) + "\n\n")
        A("\\section*{Imperative}\n")
        A(lst(imp, "code"))
        if oop:
            A("\\section*{Object-Oriented}\n")
            A(lst(oop, "code"))
        A("\\section*{Functional}\n")
        A(lst(fn, "code"))
        A("\\section*{Discussion}\n")
        A(DISCUSSION[stem] + "\n\n")
        A("\\section*{Example}\n")
        A("The demo below is the file's own \\texttt{\\_\\_main\\_\\_} block; "
          "the output beneath it is that exact run's actual captured "
          "\\texttt{stdout} -- not retyped, not fabricated.\n")
        A(lst(demo, "code"))
        A("\\noindent\\textbf{Output.}\n")
        A(lst(output, "ex"))
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
