CHAPTER = 11
TITLE = "Trees and Tries"

ITEMS = [
{
 "id": "11.1", "level": "drill", "title": "Plant a settings tree",
 "statement": (
  "Write set_all(pairs), where each pair is (key_path, value) with key_path a list of keys.\n"
  "Plant every value in a fresh ITree with setpath and return the tree. Later pairs overwrite\n"
  "earlier ones at the same path."),
 "contract": "set_all(pairs: list[tuple[list, object]]) -> dict",
 "tests": """>>> set_all([(['a', 'b'], 1), (['c'], 2)])
{'a': {'b': 1}, 'c': 2}
>>> set_all([(['x'], 1), (['x'], 9)])
{'x': 9}
>>> set_all([])
{}""",
 "solution": """def set_all(pairs):
    t = ITree()
    for ks, v in pairs:
        setpath(t, ks, v)
    return t""",
 "note": ("One setpath per pair; autovivification builds every interior node. O(total path\n"
          "length). Common mistake: forgetting that setpath at an interior key clobbers the\n"
          "subtree below it -- here that is the specified overwrite behaviour."),
},
{
 "id": "11.2", "level": "drill", "title": "Dotted config lookup",
 "statement": (
  "Write get_setting(cfg, dotted, default): read a nested dict with a dotted key string like\n"
  "'server.tls.on'. Missing keys -- or a path that runs THROUGH a non-dict leaf -- answer the\n"
  "default, and the read must never plant ghost keys."),
 "contract": "get_setting(cfg: dict, dotted: str, default) -> object",
 "tests": """>>> cfg = {'server': {'port': 8080, 'tls': {'on': True}}}
>>> get_setting(cfg, 'server.port', 0)
8080
>>> get_setting(cfg, 'server.tls.on', False)
True
>>> get_setting(cfg, 'server.host', 'localhost')
'localhost'
>>> get_setting(cfg, 'server.port.max', -1)
-1""",
 "solution": "get_setting = lambda cfg, dotted, default: getpath(cfg, dotted.split('.'), default)",
 "note": ("split('.') turns the dotted string into a key path; getpath does the safe descent.\n"
          "Common mistake: chained cfg[a][b] indexing, which raises on misses and autovivifies\n"
          "on defaultdicts."),
},
{
 "id": "11.3", "level": "drill", "title": "Every leaf value",
 "statement": (
  "Write leaf_values(t): all leaf values of a nested dict, in insertion order. Recognise the\n"
  "prelude tool before writing any recursion."),
 "contract": "leaf_values(t: dict) -> list",
 "tests": """>>> leaf_values({'a': {'b': 1, 'c': 2}, 'd': 3})
[1, 2, 3]
>>> leaf_values({'x': 7})
[7]
>>> leaf_values({'a': {'b': {'c': 'deep'}}})
['deep']""",
 "solution": "leaf_values = leaves",
 "note": ("This IS the prelude's leaves -- the second column of paths. Like flatten == concat,\n"
          "recognising an existing tool is the whole exercise."),
},
{
 "id": "11.4", "level": "drill", "title": "Two-level tally",
 "statement": (
  "Write sales_table(pairs): count (city, product) sale events into a two-level table --\n"
  "table[city][product] is the number of sales. Use Tree(2, int) so no key ever needs\n"
  "checking."),
 "contract": "sales_table(pairs: list[tuple[str, str]]) -> dict",
 "tests": """>>> sales_table([('nyc', 'ai'), ('nyc', 'ai'), ('la', 'uav')])
{'nyc': {'ai': 2}, 'la': {'uav': 1}}
>>> sales_table([])
{}
>>> sales_table([('x', 'y')])['x']['y']
1""",
 "solution": """def sales_table(pairs):
    t = Tree(2, int)
    for city, product in pairs:
        t[city][product] += 1
    return t""",
 "note": ("Tree(2, int) autovivifies the city level and hands the product level an int leaf\n"
          "factory, so the whole body is one +=. O(n)."),
},
{
 "id": "11.5", "level": "drill", "title": "Slash-joined key paths",
 "statement": (
  "Write key_paths(t): the key path of every leaf in a nested dict (string keys), joined with\n"
  "'/', in insertion order."),
 "contract": "key_paths(t: dict) -> list[str]",
 "tests": """>>> key_paths({'a': {'b': 1}, 'c': 2})
['a/b', 'c']
>>> key_paths({'solo': 9})
['solo']
>>> key_paths({'a': {'b': {'c': 0}}})
['a/b/c']""",
 "solution": "key_paths = lambda t: ['/'.join(p) for p, _ in paths(t)]",
 "note": "paths hands back (keypath, leaf) rows; keep the first column and join. O(total keys).",
},
{
 "id": "11.6", "level": "apply", "title": "Phone prefix counter",
 "statement": (
  "A call-routing box holds a set of DISTINCT phone numbers (digit strings). Write\n"
  "count_with_prefix(numbers, prefix): how many numbers start with the given prefix. Build a\n"
  "digit trie once ('$'-terminated so a full number survives being a prefix of another),\n"
  "descend to the prefix subtree with getpath, and count the '$' leaves below it."),
 "contract": "count_with_prefix(numbers: list[str], prefix: str) -> int",
 "tests": """>>> nums = ['5551234', '5555678', '5551299']
>>> count_with_prefix(nums, '555')
3
>>> count_with_prefix(nums, '5551')
2
>>> count_with_prefix(nums, '9')
0
>>> count_with_prefix(['12', '123'], '12')
2""",
 "solution": """def count_with_prefix(numbers, prefix):
    t = ITree()
    for n in numbers:
        setpath(t, list(n) + ['$'], True)
    sub = getpath(t, list(prefix), {})
    return len([1 for p, _ in paths(sub) if p and p[-1] == '$'])""",
 "note": ("The '$' terminator is what lets '12' be counted under prefix '12' even though '123'\n"
          "continues past it. getpath (never indexing) keeps the miss case from planting a ghost\n"
          "branch. O(total digits) to build, O(subtree) to count."),
},
{
 "id": "11.7", "level": "apply", "title": "Deep config merge",
 "statement": (
  "Deployment configs are nested dicts. Write deep_merge(a, b): b's settings override a's,\n"
  "except where BOTH sides hold dicts -- then merge recursively. Return a new dict; neither\n"
  "argument may be mutated at any level you touch. Key order: a's keys first, then b's new\n"
  "ones."),
 "contract": "deep_merge(a: dict, b: dict) -> dict",
 "tests": """>>> deep_merge({'a': {'x': 1}, 'b': 2}, {'a': {'y': 9}, 'c': 3})
{'a': {'x': 1, 'y': 9}, 'b': 2, 'c': 3}
>>> deep_merge({'a': {'x': 1}}, {'a': 5})
{'a': 5}
>>> deep_merge({}, {'k': 1})
{'k': 1}
>>> orig = {'a': {'x': 1}}
>>> _ = deep_merge(orig, {'a': {'y': 2}})
>>> orig
{'a': {'x': 1}}""",
 "solution": """def deep_merge(a, b):
    out = dict(a)
    for k, v in b.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out""",
 "note": ("unionWith's shape, recursing when both sides are dicts -- dict(a) at every level is\n"
          "the persistence (compare insertWith). Common mistake: out[k].update(v), which mutates\n"
          "a's subtree in place."),
},
{
 "id": "11.8", "level": "apply", "title": "Folder rollup",
 "statement": (
  "Given (path, size) pairs like ('a/b/f.txt', 10), write folder_size(files, folder): the\n"
  "total size under a folder such as 'a/b' (or the size of a single file if the path names\n"
  "one). Unknown paths answer 0. Build the tree with setpath, descend with getpath, sum the\n"
  "leaves."),
 "contract": "folder_size(files: list[tuple[str, int]], folder: str) -> int",
 "tests": """>>> fs = [('a/b/f.txt', 10), ('a/b/g.txt', 5), ('a/c/h.txt', 7), ('d.txt', 1)]
>>> folder_size(fs, 'a/b')
15
>>> folder_size(fs, 'a')
22
>>> folder_size(fs, 'zzz')
0
>>> folder_size(fs, 'a/b/f.txt')
10""",
 "solution": """def folder_size(files, folder):
    t = ITree()
    for path, size in files:
        setpath(t, path.split('/'), size)
    sub = getpath(t, folder.split('/'), {})
    return 0 if sub == {} else sum(leaves(sub))""",
 "note": ("A file path resolves to an int, and paths() on a non-dict yields one ([], leaf) row,\n"
          "so sum(leaves(...)) covers files and folders alike. The == {} guard matters: paths\n"
          "treats an empty dict as a LEAF, so summing the miss default would try 0 + {}."),
},
{
 "id": "11.9", "level": "apply", "title": "Word index, two keys deep",
 "statement": (
  "Write word_index(words): index words first by initial letter, then by length --\n"
  "index[letter][length] is the list of matching words in arrival order. Words are non-empty\n"
  "and lowercase."),
 "contract": "word_index(words: list[str]) -> dict",
 "tests": """>>> word_index(['ant', 'ape', 'bee', 'at'])
{'a': {3: ['ant', 'ape'], 2: ['at']}, 'b': {3: ['bee']}}
>>> word_index([])
{}
>>> word_index(['x'])['x'][1]
['x']""",
 "solution": """def word_index(words):
    t = Tree(2, list)
    for w in words:
        t[w[0]][len(w)].append(w)
    return t""",
 "note": ("Tree(2, list): two autovivified levels ending in list leaves, so grouping is a bare\n"
          "append. The fromListWith alternative needs nested dict surgery -- fixed-depth Tree is\n"
          "the cleaner fit here."),
},
{
 "id": "11.10", "level": "apply", "title": "Flatten to dotted lines",
 "statement": (
  "The inverse of a config tree: write dotted(t) producing sorted 'path.to.key=value' strings\n"
  "for every leaf (str() the value). An empty tree yields []. Keys are strings without dots."),
 "contract": "dotted(t: dict) -> list[str]",
 "tests": """>>> dotted({'srv': {'port': 8080, 'tls': {'on': True}}, 'debug': False})
['debug=False', 'srv.port=8080', 'srv.tls.on=True']
>>> dotted({})
[]
>>> dotted({'a': 1})
['a=1']""",
 "solution": """def dotted(t):
    if not t:
        return []
    return sorted('.'.join(p) + '=' + str(leaf) for p, leaf in paths(t))""",
 "note": ("paths flattens, join+str renders, sorted makes the output deterministic. The empty\n"
          "guard exists because paths({}) reports the empty dict itself as a leaf row -- a\n"
          "corner of the paths contract worth remembering."),
},
{
 "id": "11.11", "level": "challenge", "title": "Longest common prefix via trie",
 "statement": (
  "Write common_prefix(words): the longest string that every word starts with. Build a\n"
  "'$'-terminated trie, then walk from the root while the current node has EXACTLY one child\n"
  "and that child is not the terminator. [] answers ''. Classic interview question -- the trie\n"
  "walk is the O(total chars) answer that scales to millions of words."),
 "contract": "common_prefix(words: list[str]) -> str",
 "tests": """>>> common_prefix(['flower', 'flow', 'flight'])
'fl'
>>> common_prefix(['car', 'card'])
'car'
>>> common_prefix(['abc'])
'abc'
>>> common_prefix(['dog', 'race'])
''
>>> common_prefix([])
''""",
 "solution": """def common_prefix(words):
    t = ITree()
    for w in words:
        setpath(t, list(w) + ['$'], True)
    out, node = '', t
    while len(node) == 1 and '$' not in node:
        k = next(iter(node))
        out, node = out + k, node[k]
    return out""",
 "note": ("The walk stops at the first branch point OR the first '$' -- the terminator is what\n"
          "stops 'car'/'card' at 'car'. Membership ('$' in node) is safe on an ITree: `in` never\n"
          "autovivifies, only indexing does."),
},
{
 "id": "11.12", "level": "challenge", "title": "Render the directory listing",
 "statement": (
  "Given directory paths like 'a/b' (parents may or may not be listed separately), write\n"
  "tree_lines(dirs): the indented listing -- each name on its own line, two spaces per depth,\n"
  "children in first-mention order. Build by folding indexing over each path's parts (walking\n"
  "IS building on an ITree), then emit with your own recursion over items()."),
 "contract": "tree_lines(dirs: list[str]) -> list[str]",
 "tests": """>>> tree_lines(['a/b', 'a/c', 'd'])
['a', '  b', '  c', 'd']
>>> tree_lines(['x/y/z'])
['x', '  y', '    z']
>>> tree_lines([])
[]
>>> tree_lines(['m', 'm/n'])
['m', '  n']""",
 "solution": """def tree_lines(dirs):
    t = ITree()
    for d in dirs:
        foldl(lambda node, k: node[k], d.split('/'), t)
    def emit(node, depth):
        out = []
        for k, sub in node.items():
            out.append('  ' * depth + k)
            out.extend(emit(sub, depth + 1))
        return out
    return emit(t, 0)""",
 "note": ("The build needs no setpath because there is no leaf value -- indexing autovivifies\n"
          "the whole branch (the deepest_directory move). paths() cannot render interior nodes,\n"
          "so the emitter is a hand recursion over items(); that is the intended lesson."),
},
]
