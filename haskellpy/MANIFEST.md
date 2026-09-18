# haskellpy -- production FP library + course + Emacs games
haskell.py              the library (23 doctests; python3 haskell.py)
gen_book.py             source of truth: 41 verified problems -> emits HaskellPythonFP.tex
                        (verifies every solution first; refuses to emit on any failure)
HaskellPythonFP.tex/pdf the book (compile: pdflatex x2, haskell.py beside it)
haskellpy-trainer.el    M-x haskellpy-trainer   -- type haskell.py from memory (17 levels, 146 cards)
haskellpy-problems.el   M-x haskellpy-problems  -- type the book's solutions (9 chapters, 41 cards)
hpy-course/hw01..09.py  card data for the problems game, generated from gen_book.py
Install: .el files + haskell.py + hpy-course/ in one load-path dir.
Regenerate everything: python3 gen_book.py && (re-export hw files from C) && pdflatex.
examples/                imperative-vs-functional app pairs (each asserts both agree)
examples/FP-vs-Imperative.md  the comparison doc, code extracted verbatim from the apps
haskell-terse.py         haskell.py stripped to bare keystrokes (make_terse.py regenerates)
haskellpy-memorize.el    M-x haskellpy-memorize -- fading-source memorization of haskell-terse.py
