"""make_terse.py -- regenerate haskell-terse.py from haskell.py.
Strips docstrings (AST ranges), comments (except section headers, which are
the level structure), blank lines, alignment padding outside strings, and
the __main__ block.  Run after any haskell.py change."""
import ast, re

src = open('haskell.py').read()
doc = set()
for n in ast.walk(ast.parse(src)):
    if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body:
        f = n.body[0]
        if isinstance(f, ast.Expr) and isinstance(f.value, ast.Constant) and isinstance(f.value.value, str):
            doc.update(range(f.lineno, f.end_lineno + 1))

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

sec = re.compile(r'# ============ \d+\. .+? ============')
out = []
for i, ln in enumerate(src.splitlines(), 1):
    if i in doc or not ln.strip(): continue
    if ln.startswith('if __name__'): break
    if ln.lstrip().startswith('#'):
        m = sec.match(ln)
        if m: out.append(m.group(0))
        continue
    s = strip_line(ln)
    if s: out.append(s)
open('haskell-terse.py', 'w').write('\n'.join(out) + '\n')
print(len(out), "lines written to haskell-terse.py")
