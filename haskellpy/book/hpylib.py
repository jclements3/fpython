"""hpylib.py -- concept extractor for haskell.py (docstrings live inline,
unlike prelude.py's separate prelude-doctests.py convention).

Walks haskell.py's AST in source order. For each top-level def/assignment:
  name(s), section number, one-line gist (docstring's first paragraph),
  doctest block (>>> lines), and the verbatim source text.
Definitions with no docstring (most one-line lambdas) get source text only.
"""
import ast
import re
from pathlib import Path

MARKER = re.compile(r"^# ============ (\d+)\. (.+?) ============")


def _names_of(node):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return [node.name]
    if isinstance(node, ast.Assign):
        out = []
        for t in node.targets:
            if isinstance(t, ast.Name):
                out.append(t.id)
            elif isinstance(t, ast.Tuple):
                out.extend(e.id for e in t.elts if isinstance(e, ast.Name))
        return out
    return []


def _gist_and_tests(doc):
    if not doc:
        return None, None
    lines = doc.splitlines()
    idx = next((i for i, l in enumerate(lines) if l.strip().startswith(">>>")),
               len(lines))
    gist = " ".join(" ".join(lines[:idx]).split())
    tests = "\n".join(l.strip() for l in lines[idx:]).strip("\n")
    return gist or None, tests or None


def parse(root):
    """[(section_num, section_name, [entry, ...])], entry = dict(names, gist, tests, code)."""
    src = (root / "haskell.py").read_text()
    lines = src.splitlines()
    tree = ast.parse(src)

    marks = []
    for i, l in enumerate(lines, 1):
        m = MARKER.match(l)
        if m:
            marks.append((i, int(m.group(1)), m.group(2)))

    def section_at(lineno):
        sec = marks[0][1:] if marks else (0, "?")
        for ln, num, name in marks:
            if ln <= lineno:
                sec = (num, name)
            else:
                break
        return sec

    sections = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.Assign)):
            names = _names_of(node)
            if not names:
                continue
            num, name = section_at(node.lineno)
            doc = ast.get_docstring(node) if isinstance(node, ast.FunctionDef) else None
            gist, tests = _gist_and_tests(doc)
            code = ast.get_source_segment(src, node)
            if isinstance(node, ast.FunctionDef) and doc:
                # Strip the docstring itself out of the printed code (gist/tests render separately)
                doc_node = node.body[0]
                code = "\n".join(lines[node.lineno - 1:doc_node.lineno - 1] +
                                 lines[doc_node.end_lineno:node.end_lineno])
            sections.setdefault((num, name), []).append(
                dict(names=names, gist=gist, tests=tests, code=code))
    return [(num, name, entries) for (num, name), entries in
            sorted(sections.items())]
