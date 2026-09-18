"""entrylib.py -- shared parser for prelude-doctests.py entries.

An entry starts at a chunk whose first line is `name -- gist`; following
chunks (labelled prose paragraphs and further doctest blocks) belong to it
until the next entry or section marker. Segments come back in order as
("p", prose) / ("c", doctest-block) pairs; an entry with more than the
basic gist+examples pair is a DEEP DIVE.
"""
import re

HEADER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]* -- ")
MARKER = re.compile(r"^============ \d+\. (.+?) ============")


def _split_chunk(chunk):
    lines = chunk.splitlines()
    di = next((i for i, l in enumerate(lines) if l.startswith(">>>")), len(lines))
    segs = []
    if di:
        segs.append(("p", "\n".join(lines[:di])))
    if di < len(lines):
        segs.append(("c", "\n".join(lines[di:])))
    return segs


def parse(root):
    """[(section_name, [entry, ...])]; entry = {name, segments}."""
    doc = (root / "prelude-doctests.py").read_text().split('r"""')[1].split('"""')[0]
    sections, secname, entries, entry = [], None, [], None
    for chunk in re.split(r"\n\n+", doc.strip("\n")):
        first = chunk.splitlines()[0]
        m = MARKER.match(first)
        if m:
            if secname is not None:
                sections.append((secname, entries))
            secname, entries, entry = m.group(1), [], None
            continue
        if secname is None:
            continue                                  # file intro
        if HEADER.match(first):
            entry = {"name": first.split(" -- ")[0], "segments": _split_chunk(chunk)}
            entries.append(entry)
        elif entry is not None:
            entry["segments"].extend(_split_chunk(chunk))
    if secname is not None:
        sections.append((secname, entries))
    return sections


def is_deep(entry):
    return len(entry["segments"]) > 2


def gist(entry):
    """The reference one-liner: first prose chunk, minus the `name -- ` header."""
    first = entry["segments"][0][1]
    return " ".join(first.split(" -- ", 1)[1].split())


def definitions(root):
    """name -> verbatim definition text, parsed from prelude.py."""
    defs, block, in_doc = {}, None, False
    for line in (root / "prelude.py").read_text().splitlines():
        if line.count(chr(34) * 3) % 2 == 1:
            in_doc = not in_doc
            continue
        if in_doc or line.startswith("# ============"):
            block = None
            continue
        if block is not None and line.startswith((" ", "\t")) and line.strip():
            for name in block:
                defs[name].append(line)
            continue
        block = None
        if re.match(r"^(def |class |[A-Za-z_]\w*(\s*,\s*[A-Za-z_]\w*)*\s*=)", line):
            if line.startswith(("def ", "class ")):
                names = [line.split()[1].split("(")[0].rstrip(":")]
            else:
                names = [n.strip() for n in line.split("=", 1)[0].split(",")]
            for name in names:
                defs[name] = [line]
            block = names
    return {k: "\n".join(v) for k, v in defs.items()}


def unalign(code):
    """Collapse the column-alignment padding around '=' for book display.

    prelude.py aligns its equals signs and trailing comments to columns shared
    across neighbouring definitions; quoted alone in a listing that padding
    reads as noise. Runs of 2+ spaces before '= ' collapse to one (so '==',
    '<=' and single-space assignments are untouched) and runs of 3+ spaces
    before a trailing '#' collapse to two; no prelude definition holds '#'
    inside a string, so the comment rule is safe.
    """
    return "\n".join(re.sub(r" {3,}#", "  #", re.sub(r" {2,}= ", " = ", l))
                     for l in code.splitlines())


def has_walkthrough(entry):
    return any(k == "p" and txt.lstrip().startswith("Roll your own")
               for k, txt in entry["segments"])
