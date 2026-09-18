"""make_terse.py -- regenerate haskell-terse.py from haskell.py.
Strips docstrings (AST ranges), comments (except section headers, which are
the level structure), blank lines, alignment padding outside strings, and
the __main__ block. Also collapses any top-level `def name(args): return
EXPR` whose body is EXACTLY one return (no loop, no yield -- the only
reason it was written as `def` at all was to carry a docstring, which is
already gone in terse mode) into `name = lambda args: EXPR`, a pure,
zero-risk syntactic transform (verified equivalent by construction: same
args, same expression, called the same way). Multi-statement/loop/yield
functions are structurally incapable of being one-liners and are left as
`def`.  Run after any haskell.py change."""
import ast, re

src = open('haskell.py').read()
tree = ast.parse(src)
doc = set()
collapse = {}  # lineno-range -> replacement one-liner text
for n in ast.walk(tree):
    if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body:
        f = n.body[0]
        if isinstance(f, ast.Expr) and isinstance(f.value, ast.Constant) and isinstance(f.value.value, str):
            doc.update(range(f.lineno, f.end_lineno + 1))

for node in tree.body:
    if not isinstance(node, ast.FunctionDef):
        continue
    has_doc = ast.get_docstring(node) is not None
    body = node.body[1:] if has_doc else node.body
    if len(body) == 1 and isinstance(body[0], ast.Return) and body[0].value is not None:
        args_src = ast.unparse(node.args)
        expr_src = ast.unparse(body[0].value)
        one_liner = f"{node.name} = lambda {args_src}: {expr_src}" if args_src else \
                    f"{node.name} = lambda: {expr_src}"
        collapse[(node.lineno, node.end_lineno)] = one_liner

def strip_line(ln):
    indent = ln[:len(ln) - len(ln.lstrip())]
    rest, out, q, i = ln.lstrip(), [], None, 0
    while i < len(rest):
        c = rest[i]
        if q:
            out.append(c)
            if c == '\\' and i + 1 < len(rest): out.append(rest[i+1]); i += 1
            elif c == q: q = None
        elif c in '\'"':
            q = c; out.append(c)
        elif c == '#':
            break
        elif c == ' ':
            if not (out and out[-1] == ' '): out.append(' ')
        else:
            out.append(c)
        i += 1
    return (indent + ''.join(out)).rstrip()

sec = re.compile(r'# ============ (\d+)\. (.+?) ============')
lines = src.splitlines()
collapsed_ranges = {}  # start_line -> (end_line, one_liner)
for (start, end), one_liner in collapse.items():
    collapsed_ranges[start] = (end, one_liner)

out = []
i = 1
n = len(lines)
while i <= n:
    ln = lines[i - 1]
    if ln.startswith('if __name__'):
        break
    if i in collapsed_ranges:
        end, one_liner = collapsed_ranges[i]
        out.append(one_liner)
        i = end + 1
        continue
    if i in doc or not ln.strip():
        i += 1
        continue
    if ln.lstrip().startswith('#'):
        m = sec.match(ln)
        if m: out.append(f"# {m.group(1)}. {m.group(2)}")
        i += 1
        continue
    s = strip_line(ln)
    if s: out.append(s)
    i += 1

collapsed_names = sorted(node.name for node in tree.body
                         if isinstance(node, ast.FunctionDef)
                         and (node.lineno, node.end_lineno) in collapse)

# Point-free pass: `name = lambda a, b, ...: f(a, b, ...)` with the SAME
# params in the SAME order is eta-reducible to `name = f` -- zero risk,
# since Python calls are positional-order-sensitive by construction, so
# identical order guarantees identical behaviour for every call site.
eta = re.compile(r'^(\w+) = lambda ([\w, ]+): (\w+)\(([\w, ]+)\)$')
etad = []
for j, line in enumerate(out):
    m = eta.match(line)
    if m:
        name, params, called, cargs = m.groups()
        if [p.strip() for p in params.split(',')] == [a.strip() for a in cargs.split(',')]:
            out[j] = f"{name} = {called}"
            etad.append(name)

def compact_param_commas(line):
    """Drop the space after a comma inside a function CALL's arguments or a
    def/lambda's PARAMETER list -- the comma is delimiter enough there.
    Tuple/assignment/list/dict commas (e.g. `x, y = 1, 2`, `[1, 2]`) are
    left with their space; a bracket-depth stack tells the two apart, so
    nesting (a lambda's own params inside a call's arguments, a tuple
    literal passed as one call argument) is handled correctly at every
    depth, not just the outermost one."""
    result, stack, q, i, n = [], [], None, 0, len(line)
    while i < n:
        c = line[i]
        if q:
            result.append(c)
            if c == '\\' and i + 1 < n:
                result.append(line[i + 1]); i += 1
            elif c == q:
                q = None
            i += 1
            continue
        if c in '\'"':
            q = c; result.append(c); i += 1; continue
        if c == '(':
            prev = result[-1] if result else ''
            stack.append('call' if (prev.isalnum() or prev in '_)]') else 'group')
            result.append(c); i += 1; continue
        if c in '[{':
            stack.append('group')
            result.append(c); i += 1; continue
        if c in ')]}':
            if stack: stack.pop()
            result.append(c); i += 1; continue
        if (line[i:i+6] == 'lambda'
                and (i == 0 or not (line[i-1].isalnum() or line[i-1] == '_'))
                and (i + 6 >= n or not (line[i+6].isalnum() or line[i+6] == '_'))):
            stack.append('lambda')
            result.append('lambda'); i += 6; continue
        if c == ':' and stack and stack[-1] == 'lambda':
            stack.pop()
            result.append(c); i += 1; continue
        if c == ',':
            result.append(',')
            i += 1
            if stack and stack[-1] in ('call', 'lambda'):
                while i < n and line[i] == ' ':
                    i += 1
            continue
        result.append(c); i += 1
    return ''.join(result)

def collapse_simple_ifs(lines):
    """`if cond:` / `elif cond:` / `else:` followed by exactly ONE simple
    statement (not itself a compound `if`/`for`/`while`/`def`/etc, and not
    followed by more lines at the deeper indent) becomes one line -- Python
    allows a one-line suite, and this is semantically identical, just fewer
    lines to scroll past for the same three-word body."""
    out, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i]
        stripped = ln.strip()
        indent = len(ln) - len(ln.lstrip())
        is_header = (stripped.endswith(':') and
                     (stripped.startswith(('if ', 'elif ')) or stripped == 'else:'))
        if is_header and i + 1 < n:
            nxt = lines[i + 1]
            nxt_stripped = nxt.strip()
            nxt_indent = len(nxt) - len(nxt.lstrip())
            simple_body = (nxt_indent > indent and nxt_stripped and not
                          nxt_stripped.startswith(('if ', 'elif ', 'else', 'for ',
                                                   'while ', 'def ', 'class ', 'try', 'with ')))
            suite_ends = (i + 2 >= n) or (len(lines[i+2]) - len(lines[i+2].lstrip())) <= indent
            if simple_body and suite_ends:
                out.append(f"{ln} {nxt_stripped}")
                i += 2
                continue
        out.append(ln)
        i += 1
    return out

def wrap_long_line(line, limit=104):
    """A line over `limit` cols that ends inside brackets gets one break, at
    the LAST top-level (not nested deeper, not inside a string) ` for `
    clause before the limit -- the natural seam in a comprehension -- with
    the continuation aligned just past the bracket it's inside. Lines that
    don't fit this shape (no comprehension to break at) are left long
    rather than mangled."""
    if len(line) <= limit:
        return [line]
    depth, q, stack_cols, candidates = 0, None, [], []
    i, n = 0, len(line)
    while i < n:
        c = line[i]
        if q:
            if c == '\\' and i + 1 < n:
                i += 2; continue
            if c == q: q = None
            i += 1; continue
        if c in '\'"':
            q = c; i += 1; continue
        if c in '([{':
            stack_cols.append(i); i += 1; continue
        if c in ')]}':
            if stack_cols: stack_cols.pop()
            i += 1; continue
        if stack_cols and line[i:i+5] == ' for ' and i < limit:
            candidates.append((i, stack_cols[-1]))
        i += 1
    if not candidates:
        return [line]
    brk, open_col = candidates[-1]
    indent = open_col + 1
    return [line[:brk], ' ' * indent + line[brk+1:]]

out = collapse_simple_ifs(out)
out = [compact_param_commas(l) for l in out]
wrapped = []
for l in out:
    wrapped.extend(wrap_long_line(l))
out = wrapped

open('haskell-terse.py', 'w').write('\n'.join(out) + '\n')
print(len(out), "lines written to haskell-terse.py")
print(len(collapse), "def functions collapsed to one-line lambdas:", collapsed_names)
print(len(etad), "point-free eta-reductions:", etad)
