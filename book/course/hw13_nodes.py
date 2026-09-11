CHAPTER = 13
TITLE = "Nodes: Linked Lists and Binary Trees"

ITEMS = [
{
 "id": "13.1", "level": "drill", "title": "Sum of the tree",
 "statement": "Return the sum of every value in a binary tree. The empty tree sums to 0.\n"
              "Use tfold: pick the combining arm and the empty-tree seed.",
 "contract": "tree_sum(t: TreeNode | None) -> int",
 "tests": ">>> tree_sum(TreeNode(2, TreeNode(1), TreeNode(3)))\n"
          "6\n"
          ">>> tree_sum(TreeNode(5, TreeNode(3, TreeNode(1)), TreeNode(2)))\n"
          "11\n"
          ">>> tree_sum(None)\n"
          "0",
 "solution": "tree_sum = lambda t: tfold(lambda v, l, r: v + l + r, 0, t)",
 "note": "The catamorphism with f = plus and z = 0. O(n). Common slip: forgetting z covers BOTH "
         "missing children and the empty tree.",
},
{
 "id": "13.2", "level": "drill", "title": "Largest value in the tree",
 "statement": "Return the largest value in a NON-EMPTY binary tree of integers, again as one tfold.\n"
              "Think about what seed is safe when every real value must be able to beat it.",
 "contract": "tree_max(t: TreeNode) -> int   # t is non-empty",
 "tests": ">>> tree_max(TreeNode(2, TreeNode(9), TreeNode(3)))\n"
          "9\n"
          ">>> tree_max(TreeNode(-5, TreeNode(-2, TreeNode(-8)), None))\n"
          "-2\n"
          ">>> tree_max(TreeNode(7))\n"
          "7",
 "solution": "tree_max = lambda t: tfold(lambda v, l, r: max(v, l, r), float('-inf'), t)",
 "note": "f = three-way max, z = -infinity so absent children never win. O(n). The non-empty "
         "contract is what keeps -inf from leaking out.",
},
{
 "id": "13.3", "level": "drill", "title": "Count the leaves",
 "statement": "Count the LEAVES (nodes with no children) of a binary tree. One tfold suffices --\n"
              "notice that a node is a leaf exactly when both child results are zero.",
 "contract": "count_leaves(t: TreeNode | None) -> int",
 "tests": ">>> count_leaves(TreeNode(2, TreeNode(1), TreeNode(3)))\n"
          "2\n"
          ">>> count_leaves(TreeNode(1, TreeNode(2, TreeNode(3))))\n"
          "1\n"
          ">>> count_leaves(TreeNode(7))\n"
          "1\n"
          ">>> count_leaves(None)\n"
          "0",
 "solution": "count_leaves = lambda t: tfold(lambda v, l, r: (l + r) or 1, 0, t)",
 "note": "(l + r) or 1: internal nodes pass the children's total through; a leaf's 0 total falls "
         "back to 1. O(n). The `or` trick replaces an explicit is-leaf test tfold cannot make.",
},
{
 "id": "13.4", "level": "drill", "title": "Linked length",
 "statement": "Return how many nodes a linked list holds. Convert once and measure -- to_list is the\n"
              "bridge between pointer-land and list-land.",
 "contract": "llen(node: ListNode | None) -> int",
 "tests": ">>> llen(from_list([1, 2, 3]))\n"
          "3\n"
          ">>> llen(from_list([]))\n"
          "0\n"
          ">>> llen(ListNode(9))\n"
          "1",
 "solution": "llen = lambda node: len(to_list(node))",
 "note": "to_list then len: O(n) either way, and the list form is printable and testable. "
         "from_list([]) is None -- the empty list IS the null pointer.",
},
{
 "id": "13.5", "level": "drill", "title": "The traversal triple",
 "statement": "Return a tree's (inorder, preorder, postorder) value lists as one tuple. All three are\n"
              "tfold one-liners already in the prelude; this drill is about KNOWING their orders cold.",
 "contract": "traversals(t: TreeNode | None) -> tuple[list, list, list]",
 "tests": ">>> traversals(TreeNode(2, TreeNode(1), TreeNode(3)))\n"
          "([1, 2, 3], [2, 1, 3], [1, 3, 2])\n"
          ">>> traversals(TreeNode(3, TreeNode(2, TreeNode(1))))\n"
          "([1, 2, 3], [3, 2, 1], [1, 2, 3])\n"
          ">>> traversals(None)\n"
          "([], [], [])",
 "solution": "traversals = lambda t: (inorder(t), preorder(t), postorder(t))",
 "note": "inorder = left,node,right; preorder = node first (serialise/copy order); postorder = "
         "node last (delete/evaluate order). A left chain makes pre and post read as reverses.",
},
{
 "id": "13.6", "level": "apply", "title": "Kth newest audit entry",
 "statement": "A server keeps an append-only audit trail as a linked list, oldest entry first. Ops "
              "asks\n"
              "for the k-th NEWEST entry (k = 1 is the last one). 1 <= k <= length is guaranteed.",
 "contract": "kth_from_end(node: ListNode, k: int) -> value",
 "tests": ">>> kth_from_end(from_list([10, 20, 30, 40]), 1)\n"
          "40\n"
          ">>> kth_from_end(from_list([10, 20, 30, 40]), 4)\n"
          "10\n"
          ">>> kth_from_end(from_list([7]), 1)\n"
          "7",
 "solution": "kth_from_end = lambda node, k: to_list(node)[-k]",
 "note": "Materialise once, index from the end: O(n) time either way. The two-pointer gap trick "
         "saves memory, not time -- say that trade aloud if asked.",
},
{
 "id": "13.7", "level": "apply", "title": "Palindrome ticket tape",
 "statement": "A ticket printer spools IDs onto a tape held as a linked list. QA wants to know whether\n"
              "the tape reads the same in both directions. The empty tape counts as a palindrome.",
 "contract": "is_palindrome_list(node: ListNode | None) -> bool",
 "tests": ">>> is_palindrome_list(from_list([1, 2, 1]))\n"
          "True\n"
          ">>> is_palindrome_list(from_list([1, 2]))\n"
          "False\n"
          ">>> is_palindrome_list(from_list([]))\n"
          "True\n"
          ">>> is_palindrome_list(from_list([7]))\n"
          "True",
 "solution": "def is_palindrome_list(node):\n"
             "    xs = to_list(node)\n"
             "    return xs == xs[::-1]",
 "note": "Convert, compare with the reversed slice: O(n) time, O(n) space. The O(1)-space version "
         "(reverse_list on the back half from middle) is the follow-up interviewers like.",
},
{
 "id": "13.8", "level": "apply", "title": "Deduplicate a sorted list",
 "statement": "Subscription events arrive as a SORTED linked list of customer ids, possibly with\n"
              "repeats. Return a linked list with each id once, order preserved.",
 "contract": "dedup(node: ListNode | None) -> ListNode | None",
 "tests": ">>> to_list(dedup(from_list([1, 1, 2, 3, 3])))\n"
          "[1, 2, 3]\n"
          ">>> to_list(dedup(from_list([4, 4, 4])))\n"
          "[4]\n"
          ">>> to_list(dedup(from_list([])))\n"
          "[]\n"
          ">>> to_list(dedup(from_list([1, 2])))\n"
          "[1, 2]",
 "solution": "dedup = lambda node: from_list(nub(to_list(node)))",
 "note": "Round-trip through list-land: to_list, nub (first occurrence wins -- on sorted input "
         "that equals adjacent-dedup), from_list. O(n). Pointer surgery is the O(1)-extra-space "
         "alternative.",
},
{
 "id": "13.9", "level": "apply", "title": "Is it a search tree?",
 "statement": "A binary tree claims to be a binary SEARCH tree with strictly increasing values.\n"
              "Verify the claim. Key insight: a BST is exactly a tree whose inorder walk is strictly\n"
              "increasing -- so check the walk, not the tree.",
 "contract": "is_bst(t: TreeNode | None) -> bool",
 "tests": ">>> is_bst(TreeNode(2, TreeNode(1), TreeNode(3)))\n"
          "True\n"
          ">>> is_bst(TreeNode(2, TreeNode(3), TreeNode(1)))\n"
          "False\n"
          ">>> is_bst(TreeNode(2, TreeNode(2)))\n"
          "False\n"
          ">>> is_bst(None)\n"
          "True",
 "solution": "def is_bst(t):\n"
             "    xs = inorder(t)\n"
             "    return all(a < b for a, b in pairwise(xs))",
 "note": "inorder + pairwise + all: three prelude names replace the classic min/max-bounds "
         "recursion. Strict < also rejects duplicates. O(n). The bounds recursion is the O(1)-"
         "extra-space follow-up.",
},
{
 "id": "13.10", "level": "apply", "title": "Symmetric tree",
 "statement": "An org chart is 'symmetric' if the whole tree equals its own mirror image -- values AND\n"
              "structure. Check it by folding the tree into a nested-tuple shape twice: once as-is,\n"
              "once with the child results swapped, and comparing.",
 "contract": "is_symmetric(t: TreeNode | None) -> bool",
 "tests": ">>> is_symmetric(TreeNode(1, TreeNode(2), TreeNode(2)))\n"
          "True\n"
          ">>> is_symmetric(TreeNode(1, TreeNode(2), TreeNode(3)))\n"
          "False\n"
          ">>> is_symmetric(TreeNode(1, TreeNode(2, TreeNode(3)), TreeNode(2, TreeNode(3))))\n"
          "False\n"
          ">>> is_symmetric(TreeNode(1, TreeNode(2, None, TreeNode(3)), TreeNode(2, TreeNode(3))))\n"
          "True\n"
          ">>> is_symmetric(None)\n"
          "True",
 "solution": "def is_symmetric(t):\n"
             "    shape  = tfold(lambda v, l, r: (v, l, r), None, t)\n"
             "    mirror = tfold(lambda v, l, r: (v, r, l), None, t)\n"
             "    return shape == mirror",
 "note": "tfold with (v, l, r) serialises the exact structure as nested tuples; swapping to "
         "(v, r, l) builds the mirror's serialisation. Equal tuples == symmetric tree. O(n). "
         "Plain inorder comparison is NOT enough -- it loses structure.",
},
{
 "id": "13.11", "level": "challenge", "title": "Merge k sorted feeds",
 "statement": "k sensor feeds each deliver readings as a sorted linked list. Produce one sorted linked\n"
              "list containing everything. An empty collection of feeds yields the empty list.\n"
              "Hint: you already own a two-list merge; what fold turns two-way into k-way?",
 "contract": "merge_k(feeds: list[ListNode | None]) -> ListNode | None",
 "tests": ">>> to_list(merge_k([from_list([1, 4]), from_list([2, 3]), from_list([5])]))\n"
          "[1, 2, 3, 4, 5]\n"
          ">>> to_list(merge_k([from_list([]), from_list([2]), from_list([1, 3])]))\n"
          "[1, 2, 3]\n"
          ">>> to_list(merge_k([]))\n"
          "[]\n"
          ">>> to_list(merge_k([from_list([9])]))\n"
          "[9]",
 "solution": "merge_k = lambda feeds: foldl(merge_lists, feeds, None)",
 "note": "foldl of the two-way merge, seeded with the empty list. O(k*N) total; the heap-of-heads "
         "version is O(N log k) -- name it, then justify the simpler fold at interview scale.",
},
{
 "id": "13.12", "level": "challenge", "title": "Height-balanced?",
 "statement": "A tree is height-balanced when EVERY node's two subtrees differ in height by at most 1.\n"
              "Decide it in one pass. Hint: tfold can carry a PAIR upward -- (height, balanced_so_far)\n"
              "-- so each node judges itself from its children's pairs.",
 "contract": "is_balanced(t: TreeNode | None) -> bool",
 "tests": ">>> is_balanced(TreeNode(1, TreeNode(2), TreeNode(3)))\n"
          "True\n"
          ">>> is_balanced(TreeNode(1, TreeNode(2, TreeNode(3))))\n"
          "False\n"
          ">>> is_balanced(None)\n"
          "True\n"
          ">>> deep = TreeNode(2, TreeNode(3, TreeNode(4)))\n"
          ">>> is_balanced(TreeNode(1, deep, TreeNode(9)))\n"
          "False",
 "solution": "def is_balanced(t):\n"
             "    def f(v, l, r):\n"
             "        return (1 + max(l[0], r[0]),\n"
             "                l[1] and r[1] and abs(l[0] - r[0]) <= 1)\n"
             "    return tfold(f, (0, True), t)[1]",
 "note": "The compound-accumulator trick: fold up (height, ok) pairs so balance is checked at "
         "every node in one O(n) pass. The classic mistake is checking only the root's height "
         "difference -- the fourth test catches exactly that.",
},
]
