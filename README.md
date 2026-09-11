# Prelude applications — every problem so far, no imports

All the problems collected so far (the 19 NeetCode/challenge set, the
30 doctest exercises from `../tests/`, the ladder and lesson problems
worth reworking, and 4 harder LeetCode additions), regrouped into
clusters by the KIND of `prelude.py` snippet
their solution wants, with those snippets copied in. **No file imports
anything** — each is self-contained: the snippets it needs are pasted
above the solution slot, exactly as they appear in `prelude.py`.

Every file has the same shape:

    """<name> -- <problem statement>

    Contract:  the exact signature and semantics
    Hint:      which snippets, and the shape of the solution

    >>> doctests
    """

    # -- prelude --
    <the snippets this problem needs, verbatim>

    # solution goes here


    if __name__ == u'__main__':
        import doctest
        ...prints N/N doctests passing

Write your solution under `# solution goes here`, run the file, repeat
until N/N. `prelude.py` itself sits in this directory as the reference
— read it top to bottom once before starting; it is in strict
define-before-use order.

## How to pick the tool — the recognition drill

`prelude_flowchart.svg` (in this directory — print it) is this section
as a picture. The process, every time, before typing anything:

**Step 0 — name three things from the statement:**

1. the INPUT shape (a list? two lists? pairs? a grid? edges?),
2. the OUTPUT shape (one value? a list? a dict? yes/no? *all* solutions?),
3. the quantity word (the "most", "fewest", "longest", "every" that
   names what's being asked).

The OUTPUT shape is the strongest clue: one value smells like a fold,
a dict smells like `fromListWith`, "all of them" smells like
enumerate-or-tree, yes/no often hides a fold (`all`/`any`) or a
reachability question.

**Step 1 — walk the ladder.** Match the statement's words against the
triggers; first row that fits names your tools:

| Trigger words in the statement | Shape | Reach for |
|---|---|---|
| "sorted", "k-th", "closest pair", "can they be arranged", "intervals" | SORT FIRST — does order unlock it? | `sorted` `sortOn` `bisect_left` `merge` |
| "total", "count", "largest", "best single ..." | FOLD — collapses to one value in one pass | `foldl` `minOn`/`maxOn` |
| "running", "so far", "at each step", "prefix sums" | SCAN — a fold that keeps its history | `scanl` `scanl1` |
| "group by", "frequency", "most common", "anagrams together" | DICT FOLD — aggregating by key | `fromListWith` `Counter` `unionWith` |
| "substring", "contiguous", "longest run", "within the last k" | WINDOW — best contiguous run under a constraint | `longest_window` `pairwise` |
| "nested", "matching pairs", "most recent open", "next greater" | STACK — a fold whose accumulator is a stack | plain list + `foldl`; `None` as the failed state |
| "digits of", "split into pieces", "repeat until", "simulate" | UNFOLD — generating from a seed, not consuming | `unfoldr` `iterate`+`take` |
| "all subsets", "any combination", "every way to pick" | ENUMERATE — try every candidate (n small; say the bound) | `subsequences` `replicateM` `cross` |
| "nested", "prefix" (trie), "directories", "solutions as paths" | TREE / PATHS — input or answer is hierarchical | `ITree` `paths` `setpath` `tfold` |
| "prerequisites", "network", "shortest route", "reachable" | GRAPH — things pointing at other things | `Tree(1,list)` adjacency · `deque` BFS · heap · `until` |
| "fewest", "max value", "count the ways", "can it be done" | MEMOIZE — choices now change what's possible later | `memo` over indices |

Cross-cutting, any row: messy input → `mapMaybe` · absence → `None` +
`fromMaybe` · first hit → `find` · same-up-to-order → canonical form
(`sorted` or `Counter`) · connectivity → `dsu` · repeated best-next →
`heappush`/`heappop`.

**Step 2 — say it out loud** (this is scored on the real screen):
the shape, the tools, and the complexity — "group-by-key with
fromListWith, then best-by-key with minOn, O(n)." If two rows
both apply, the one that names the OUTPUT wins: "most common word"
*mentions* frequency (dict fold) but *asks for* one value (fold) —
so it's Counter feeding minOn.

**Step 3 — compose, don't invent.** Solutions here are pipelines of
two or three prelude names plus one lambda of your own. If you're
writing a raw loop, first ask which combinator you're rebuilding.

Worked micro-recognitions from this very set:

- "Merge overlapping *intervals*" → SORT FIRST, then a fold that
  extends-or-appends: `sortOn(fst)` + `foldl`.
- "Split a list into *pieces* of k" → UNFOLD, and `splitAt` already
  returns (value, next-seed): `unfoldr` of `splitAt`.
- "*Fewest* coins to reach the amount" → MEMOIZE: `memo` on the
  remaining amount.
- "All words with this *prefix*" → TREE: `getpath` down, `paths` out.

## The groups, in order

| Group | Snippet kind | Problems |
|---|---|---|
| `g1_arith_and_unfolds` | signum, unfoldr, foldl, pairwise | sign · rect_area · reverse_digits · to_base · to_roman · from_roman |
| `g2_lists_and_strings` | map_/filter_/concat/concatMap, nub, splitAt+unfoldr, words/unwords, transpose | greet · count_vowels · fizzbuzz · word_lengths · flatten · caesar · contains_duplicate · chunks · permutations · reverse_words · transpose_matrix · rotate_right |
| `g3_folds_scans_streams` | foldl, scanl/scanl1/scanr, pairwise, iterate, take, count | two_sum · best_time_stock · maximum_subarray · product_except_self · moving_average · pascal · climbing_stairs · primes_up_to · totals_and_deltas · paren_depth |
| `g4_sorting_and_searching` | sorted, sortOn, bisect_left/right, merge | is_anagram_sorted · second_largest · binary_search · merge_intervals · photo_lineup · merge_sort · lis · russian_doll · pairs_within_budget · sensor_pairing |
| `g5_bags_and_grouping` | Counter, fromListWith, Tree(1,·), group/groupBy, minOn, find/fromMaybe, mapMaybe, swap | valid_anagram · ransom_note · most_frequent · top_k_words · group_words · group_anagrams · merge_sum · rle_encode · lru_class · first_unique · log_report · invert_dict |
| `g6_tries_and_paths` | ITree, paths, setpath, getpath, maxOn | deepest_directory · autocomplete · subset_sum_paths · subset_sum_trie |
| `g7_graphs_grids_heaps` | deque, heappush/heappop, neighbors4, longest_window, until | longest_unique · grid_path · rate_limiter · running_median · dijkstra · dag_longest_path · bellman_ford · course_schedule |
| `g8_dp_and_control` | memo, takeWhile/span, bitmasks | coin_change · lcs · edit_distance · knapsack · calculator · max_height_cuboids · guillotine_cut · partition_k_subsets · min_path_sum |
| `g9_stack_folds` | a plain list IS a stack; foldl with a stack accumulator, None as poison | balanced_brackets · eval_rpn · next_greater |

74 problems. Work the groups in order — the snippets stack the same
way the prelude's sections do — but within a group any order works.
The g8 back three are the hard tier: russian_doll (g4) feeds
max_height_cuboids (weighted LIS), guillotine_cut is the rectangle
DP, partition_k_subsets is the bitmask family. (g8 numbering skips
06 — its hints reference a g8_06 mask problem not yet added.)

## Deliberate pairings to notice

- **is_anagram twice**: g4 solves it with a sorted canonical form, g5
  with Counter bags. Same problem, different algebra — know both and
  have a preference.
- **subset_sum twice**: g6's decision-tree version returns a multiset
  of solutions; the trie version collapses duplicates to a set. The
  data structure changed the semantics.
- **merge_sum vs bag_union**: your fold ADDS counts; the prelude's
  bag_union takes max. Same shape, different monoid.
- **lcs vs edit_distance**: one skeleton, max vs min — and
  dag_longest_path is the same move on graphs (Dijkstra's relax with
  max, ordered by topo sort instead of a heap).

## Run everything

    cd ~/projects/fpython
    for f in g*/*.py; do python3 "$f"; done

## Solutions

`solutions/` holds every problem solved in prelude style, flat, named
`<group>_<problem>.py` (e.g. `g2_08_chunks.py`), each identical to its
problem file with the answer inserted after `# solution goes here` —
all 74 doctest-verified. They are for AFTER you've fought a problem:
compare your shape against the intended composition, then move on.
Peeking first defeats the recognition drill.
