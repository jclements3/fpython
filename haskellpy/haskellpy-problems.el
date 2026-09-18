;;; haskellpy-problems.el --- Type HaskellPythonFP's homework solutions from memory -*- lexical-binding: t; -*-

;; A memory game over hpy-course/hw*.py, sibling to haskellpy-trainer.el.
;; Where haskellpy-trainer drills haskell.py's vocabulary, this one drills
;; HaskellPythonFP's homework: the same 9 chapters, same problems, same
;; solutions, as printed in the book.  Each chapter (hw01..hw09) is a level.
;; A card shows one problem exactly as the book prints it --
;;
;;     6.2  Account history                                        [drill]
;;     An account opens at balance `start` and applies signed transactions
;;     in order.  Using scanl, return the FULL balance history...
;;
;;     Contract: account_history(start: int, txns: list[int]) -> list[int]
;;
;;     Tests:
;;     >>> account_history(100, [-20, 50])
;;     [100, 80, 130]
;;     ...
;;
;; -- and you type the solution from memory.  Every card in a level must
;; be answered correctly, first try (blind, see below), to clear the level
;; and unlock the next one.  Anything less and you replay the level.
;; Cleared levels are remembered between sessions.
;;
;; Each card is a "vanishing cues" cycle of `haskellpy-problems-fade-steps'
;; reps: the first rep shows the full solution to copy, and each rep after
;; that shows it more faded, until the last rep shows nothing and you must
;; recall it from memory -- that final blind rep is the one that counts
;; toward the level's score.  Get a rep wrong and you repeat it at the same
;; fade level before it fades further.  The problem statement, contract and
;; tests never fade -- only the solution does.
;;
;;   M-x haskellpy-problems          play (starts at the highest unlocked level)
;;   M-x haskellpy-problems-reset    forget all progress
;;
;; Comments, blank lines and all whitespace are ignored when checking an
;; answer; the code has to match. Unlike haskellpy-trainer's one-liners, a
;; homework solution is read from hpy-course/hw*.py via Python (those
;; files are executable modules, not text worth hand-parsing), so a
;; `haskellpy-problems-python-executable' must be on hand.

;;; Code:

(require 'cl-lib)
(require 'python)
(require 'color)
(require 'json)

(defgroup haskellpy-problems nil
  "Type HaskellPythonFP's homework solutions from memory."
  :group 'games
  :prefix "haskellpy-problems-")

(defcustom haskellpy-problems-course-dir
  (expand-file-name "hpy-course"
                    (file-name-directory
                     (file-truename (or load-file-name buffer-file-name
                                        default-directory))))
  "Directory holding hpy-course's hw01.py..hw09.py.  Defaults to the
hpy-course beside this file (symlinks resolved, so the file may live in
a load-path directory)."
  :type 'directory)

(defcustom haskellpy-problems-python-executable "python3"
  "Python 3 interpreter used to read the hw*.py files (they are Python
modules -- a list-of-dicts literal spread across string concatenations --
not text worth regexp-parsing)."
  :type 'string)

(defcustom haskellpy-problems-progress-file
  (locate-user-emacs-file "haskellpy-problems-progress")
  "Where the highest unlocked level is saved."
  :type 'file)

(defcustom haskellpy-problems-fade-steps 5
  "Reps per card, fading the shown solution from full to invisible.

This is the \"vanishing cues\" technique: rep 1 shows the whole solution
for you to copy, the middle reps show it progressively dimmer as a
shrinking hint, and the final rep shows nothing -- pure recall -- which
is the only rep that counts toward clearing the level.  A wrong or given-up
answer on a non-final rep repeats that same fade level rather than
advancing it.  The problem statement, contract and tests are never faded,
only the solution.

5 is a reasonable default: enough steps to fade gradually without making
each card tedious.  Set to 1 to disable fading entirely (every rep is
blind, the original behavior)."
  :type 'integer)

(defconst haskellpy-problems-buffer-name "*HaskellPyProblems*")

;; ---------------------------------------------------------------- state

(defvar haskellpy-problems--levels nil
  "Vector of levels; each is (NAME . ITEMS), ITEM is (NAME PROMPT CODE NOTE).
NAME is \"ID  TITLE\"; PROMPT is the problem statement/contract/tests,
shown in full and never faded; CODE is the reference solution, the thing
to be recalled; NOTE is the book's teaching note, shown alongside CODE
after a miss or give-up.")
(defvar haskellpy-problems--unlocked 1 "Highest level the player may start.")
(defvar haskellpy-problems--level 1 "Level being played.")
(defvar haskellpy-problems--queue nil "Cards still to be dealt this level.")
(defvar haskellpy-problems--item nil "The card on the table.")
(defvar haskellpy-problems--total 0 "Cards in this level.")
(defvar haskellpy-problems--hits 0 "Cards answered correctly this level.")
(defvar haskellpy-problems--misses nil "Names of cards missed this level.")
(defvar haskellpy-problems--state 'idle "One of idle, typing, shown, level-end, won.")
(defvar haskellpy-problems--answer-start nil "Marker: where the answer area begins.")
(defvar haskellpy-problems--round 1 "Fade rep (1..haskellpy-problems-fade-steps) for the card on the table.")
(defvar haskellpy-problems--last-gave-up nil "Whether the most recent rep ended in a give-up.")

;; ---------------------------------------------------------------- parsing

(defconst haskellpy-problems--dump-script "\
import sys, json
from pathlib import Path

course_dir = Path(sys.argv[1])
chapters = []
for fp in sorted(course_dir.glob('hw*.py')):
    ns = {}
    exec(compile(fp.read_text(), str(fp), 'exec'), ns)
    chapters.append({
        'title': ns.get('TITLE', fp.stem),
        'items': [
            {'id': it['id'], 'level': it['level'], 'title': it['title'],
             'statement': it['statement'], 'contract': it['contract'],
             'tests': it['tests'], 'solution': it['solution'],
             'note': it['note']}
            for it in ns['ITEMS']
        ],
    })
json.dump(chapters, sys.stdout)
"
  "Python: read every hw*.py in argv[1] into a JSON list of chapters.
The hw files are exec'd, same as `verify_hw.py' does -- they are Python
modules, not a text format worth reimplementing a parser for.")

(defun haskellpy-problems--run-dump ()
  "Shell out to Python; return the parsed JSON (alists, lists) it prints."
  (unless (file-directory-p haskellpy-problems-course-dir)
    (error "No such directory: %s" haskellpy-problems-course-dir))
  (with-temp-buffer
    (let ((status (call-process haskellpy-problems-python-executable nil t nil
                                 "-c" haskellpy-problems--dump-script
                                 (expand-file-name haskellpy-problems-course-dir))))
      (unless (zerop status)
        (error "haskellpy-problems: %s failed (exit %s):\n%s"
               haskellpy-problems-python-executable status (buffer-string)))
      (goto-char (point-min))
      (let ((json-object-type 'alist) (json-array-type 'list) (json-key-type 'symbol))
        (json-read)))))

(defun haskellpy-problems--wrap (text width)
  "TEXT, greedily word-wrapped to WIDTH.  Blank lines are paragraph
breaks; any other newline is just where the source happened to wrap,
so it is collapsed to a space before refilling."
  (mapconcat
   (lambda (para)
     (if (string-empty-p para)
         ""
       (with-temp-buffer
         (insert (replace-regexp-in-string "[ \t\n]+" " " (string-trim para)))
         (let ((fill-column width)) (fill-region (point-min) (point-max)))
         (buffer-string))))
   (split-string text "\n[ \t]*\n") "\n\n"))

(defun haskellpy-problems--format-prompt (item)
  "The always-visible, never-faded half of a card: everything but the solution."
  (format "%s  %s%s\n\n%s\n\nContract:\n    %s\n\nTests:\n%s\n"
          (alist-get 'id item) (alist-get 'title item)
          (format "   [%s]" (alist-get 'level item))
          (haskellpy-problems--wrap (alist-get 'statement item) 78)
          (alist-get 'contract item)
          (alist-get 'tests item)))

(defun haskellpy-problems--parse ()
  "Build the vector of levels straight from the Python-side JSON dump."
  (let* ((chapters (haskellpy-problems--run-dump)))
    (unless chapters
      (error "No chapters found in %s" haskellpy-problems-course-dir))
    (vconcat
     (mapcar
      (lambda (chapter)
        (cons (alist-get 'title chapter)
              (mapcar (lambda (item)
                        (list (format "%s %s" (alist-get 'id item) (alist-get 'title item))
                              (haskellpy-problems--format-prompt item)
                              (alist-get 'solution item)
                              (alist-get 'note item)))
                      (alist-get 'items chapter))))
      chapters))))

(defun haskellpy-problems--normalize (code)
  "CODE with comments, blank lines and all whitespace removed."
  (mapconcat #'identity
             (delq nil (mapcar (lambda (line)
                                 (let ((s (replace-regexp-in-string
                                           "[ \t]" "" (car (split-string line "#")))))
                                   (and (not (string-empty-p s)) s)))
                               (split-string code "\n")))
             "\n"))

(defun haskellpy-problems--shuffle (list)
  (let ((v (vconcat list)))
    (cl-loop for i from (1- (length v)) downto 1
             do (cl-rotatef (aref v i) (aref v (random (1+ i)))))
    (append v nil)))

;; ---------------------------------------------------------------- fading

(defun haskellpy-problems--blind-p ()
  "Whether the current rep is the final, unhinted, graded one."
  (or (<= haskellpy-problems-fade-steps 1)
      (= haskellpy-problems--round haskellpy-problems-fade-steps)))

(defun haskellpy-problems--opacity ()
  "How solid the hint is on the current rep: 1.0 full, 0.0 invisible."
  (if (<= haskellpy-problems-fade-steps 1)
      0.0
    (- 1.0 (/ (float (1- haskellpy-problems--round)) (1- haskellpy-problems-fade-steps)))))

(defun haskellpy-problems--face-rgb (attribute fallback)
  "The current frame's ATTRIBUTE of the default face as an (R G B) list,
or FALLBACK's if the frame has no color set (e.g. batch mode)."
  (or (color-name-to-rgb (face-attribute 'default attribute nil t))
      (color-name-to-rgb fallback)))

(defun haskellpy-problems--fade-color (opacity)
  "A foreground color OPACITY of the way from the background to the
default foreground, as a hex string."
  (cl-destructuring-bind (fr fg fb) (haskellpy-problems--face-rgb :foreground "white")
    (cl-destructuring-bind (br bg bb) (haskellpy-problems--face-rgb :background "black")
      (color-rgb-to-hex (+ (* opacity fr) (* (- 1 opacity) br))
                         (+ (* opacity fg) (* (- 1 opacity) bg))
                         (+ (* opacity fb) (* (- 1 opacity) bb))
                         2))))

(defun haskellpy-problems--insert-hint ()
  "Show the fading solution above the answer area, at the current rep's opacity."
  (haskellpy-problems--insert
   (list :foreground (haskellpy-problems--fade-color (haskellpy-problems--opacity)))
   (nth 2 haskellpy-problems--item))
  (insert "\n\n"))

;; ---------------------------------------------------------------- progress

(defun haskellpy-problems--load-progress ()
  (setq haskellpy-problems--unlocked
        (or (ignore-errors
              (with-temp-buffer
                (insert-file-contents haskellpy-problems-progress-file)
                (plist-get (read (current-buffer)) :unlocked)))
            1)))

(defun haskellpy-problems--save-progress ()
  (with-temp-file haskellpy-problems-progress-file
    (prin1 (list :unlocked haskellpy-problems--unlocked) (current-buffer))))

;; ---------------------------------------------------------------- mode

(defvar haskellpy-problems-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "C-c C-c") #'haskellpy-problems-check)
    (define-key map (kbd "C-c C-r") #'haskellpy-problems-give-up)
    (define-key map (kbd "C-c C-q") #'haskellpy-problems-quit)
    map)
  "Keys while typing an answer.")

(defvar haskellpy-problems-menu-map
  (let ((map (make-sparse-keymap)))
    (set-keymap-parent map special-mode-map)
    (define-key map (kbd "SPC") #'haskellpy-problems-next)
    (define-key map (kbd "RET") #'haskellpy-problems-next)
    (define-key map "n" #'haskellpy-problems-new-game)
    (define-key map "r" #'haskellpy-problems-replay)
    (define-key map "l" #'haskellpy-problems-choose-level)
    (define-key map "q" #'haskellpy-problems-quit)
    map)
  "Keys between cards and between levels.")

(define-derived-mode haskellpy-problems-mode python-mode "HaskellPyHW"
  "Major mode for the homework-solution typing game.

While typing an answer:
\\{haskellpy-problems-mode-map}
Between cards and levels:
\\{haskellpy-problems-menu-map}"
  (setq-local header-line-format '(:eval (haskellpy-problems--header-line)))
  (setq-local truncate-lines nil))

(defcustom haskellpy-problems-progress-bar-width 20
  "Width, in characters, of the whole-course progress bar in the header line."
  :type 'integer)

(defun haskellpy-problems--progress-bar (fraction)
  "A block-character progress bar FRACTION (0.0-1.0) full,
`haskellpy-problems-progress-bar-width' characters wide."
  (let* ((width haskellpy-problems-progress-bar-width)
         (filled (round (* fraction width))))
    (concat "[" (make-string filled ?\N{U+2588}) (make-string (- width filled) ?\N{U+2591}) "]")))

(defun haskellpy-problems--overall-progress ()
  "Fraction of the whole course cleared: levels unlocked beyond the
current one, plus this level's progress through its cards."
  (let* ((nlevels (length haskellpy-problems--levels))
         (cleared (1- haskellpy-problems--unlocked))
         (in-level (if (zerop haskellpy-problems--total)
                       0.0
                     (/ (float (- haskellpy-problems--total (length haskellpy-problems--queue)))
                        haskellpy-problems--total))))
    (min 1.0 (/ (+ cleared in-level) (float nlevels)))))

(defun haskellpy-problems--header-line ()
  (let* ((nlevels (length haskellpy-problems--levels))
         (fraction (if (eq haskellpy-problems--state 'won) 1.0 (haskellpy-problems--overall-progress)))
         (bar (format " %s %d%%  (%d/%d levels unlocked)"
                      (haskellpy-problems--progress-bar fraction)
                      (round (* 100 fraction))
                      (min haskellpy-problems--unlocked nlevels) nlevels)))
    (if (eq haskellpy-problems--state 'won)
        (format " HaskellPy Problems  %s   all %d levels cleared" bar nlevels)
      (format " HaskellPy Problems  %s   Ch %d/%d  %s   card %d/%d   rep %d/%d   correct %d   missed %d"
              bar
              haskellpy-problems--level nlevels
              (haskellpy-problems--level-name haskellpy-problems--level)
              (- haskellpy-problems--total (length haskellpy-problems--queue))
              haskellpy-problems--total
              haskellpy-problems--round haskellpy-problems-fade-steps
              haskellpy-problems--hits (length haskellpy-problems--misses)))))

(defun haskellpy-problems--level-name (n)
  (car (aref haskellpy-problems--levels (1- n))))

(defun haskellpy-problems--level-items (n)
  (cdr (aref haskellpy-problems--levels (1- n))))

(defun haskellpy-problems--insert (face &rest strings)
  "Insert STRINGS, shown in FACE (an overlay, so font-lock leaves it alone)."
  (let ((beg (point)))
    (apply #'insert strings)
    (when face
      (overlay-put (make-overlay beg (point)) 'face face))))

(defun haskellpy-problems--clear ()
  (let ((inhibit-read-only t))
    (remove-overlays)
    (erase-buffer))
  (setq buffer-read-only nil))

(defun haskellpy-problems--menu-phase ()
  (setq buffer-read-only t)
  (use-local-map haskellpy-problems-menu-map)
  (goto-char (point-min)))

;; ---------------------------------------------------------------- play

;;;###autoload
(defun haskellpy-problems ()
  "Play the homework typing game: 9 chapters, perfect score to advance."
  (interactive)
  (setq haskellpy-problems--levels (haskellpy-problems--parse))
  (when (zerop (length haskellpy-problems--levels))
    (error "No chapters found in %s" haskellpy-problems-course-dir))
  (haskellpy-problems--load-progress)
  (switch-to-buffer haskellpy-problems-buffer-name)
  (unless (derived-mode-p 'haskellpy-problems-mode)
    ;; A game buffer, not a source file: keep linters, LSP and line
    ;; numbers from the user's Python hooks out of it.
    (let ((python-mode-hook nil)
          (prog-mode-hook nil)
          (python-indent-guess-indent-offset nil))
      (haskellpy-problems-mode)))
  (haskellpy-problems--start-level (min haskellpy-problems--unlocked
                                      (length haskellpy-problems--levels))))

(defun haskellpy-problems-new-game ()
  "Start over at the highest unlocked level."
  (interactive)
  (haskellpy-problems))

(defun haskellpy-problems--start-level (n)
  (setq haskellpy-problems--level n
        haskellpy-problems--queue (haskellpy-problems--shuffle (haskellpy-problems--level-items n))
        haskellpy-problems--total (length haskellpy-problems--queue)
        haskellpy-problems--hits 0
        haskellpy-problems--misses nil)
  (haskellpy-problems--deal-card))

(defun haskellpy-problems--deal-card ()
  "Pop the next card from the queue and start its fade cycle at rep 1."
  (setq haskellpy-problems--item (pop haskellpy-problems--queue)
        haskellpy-problems--round 1)
  (haskellpy-problems--deal-round))

(defun haskellpy-problems--deal-round ()
  "(Re)present the card on the table at the current fade rep."
  (let ((prompt (nth 1 haskellpy-problems--item)))
    (setq haskellpy-problems--state 'typing)
    (haskellpy-problems--clear)
    (use-local-map haskellpy-problems-mode-map)
    (haskellpy-problems--insert 'bold (format "Chapter %d: %s" haskellpy-problems--level
                                            (haskellpy-problems--level-name haskellpy-problems--level)))
    (haskellpy-problems--insert 'font-lock-comment-face
                              (format "   card %d of %d   rep %d/%d\n\n"
                                      (- haskellpy-problems--total (length haskellpy-problems--queue))
                                      haskellpy-problems--total
                                      haskellpy-problems--round haskellpy-problems-fade-steps))
    (insert prompt)
    (haskellpy-problems--insert
     'font-lock-comment-face
     (if (haskellpy-problems--blind-p)
         "Write the solution from memory.   C-c C-c check   C-c C-r give up   C-c C-q quit\n"
       "Retype the solution shown below.   C-c C-c check   C-c C-q quit\n"))
    (unless (haskellpy-problems--blind-p)
      (insert "\n")
      (haskellpy-problems--insert-hint))
    (insert "\n")
    (let ((end (point))
          (inhibit-read-only t))
      (put-text-property (point-min) end 'read-only t)
      (put-text-property (point-min) (1+ (point-min)) 'front-sticky t)
      (put-text-property (1- end) end 'rear-nonsticky t)
      (setq haskellpy-problems--answer-start (copy-marker end)))))

(defun haskellpy-problems--attempt ()
  (buffer-substring-no-properties haskellpy-problems--answer-start (point-max)))

(defun haskellpy-problems--expected ()
  (nth 2 haskellpy-problems--item))

(defun haskellpy-problems-check ()
  "Check the answer typed under the prompt.  A correct answer needs no
review: it just updates the score and moves straight on.  A wrong answer
shows the reference solution (and its note), and waits for SPC."
  (interactive)
  (unless (eq haskellpy-problems--state 'typing)
    (user-error "No card on the table"))
  (let ((attempt (haskellpy-problems--attempt)))
    (if (string= (haskellpy-problems--normalize attempt)
                 (haskellpy-problems--normalize (haskellpy-problems--expected)))
        (haskellpy-problems--advance)
      (haskellpy-problems--show-result nil))))

(defun haskellpy-problems-give-up ()
  "Give up on this rep: the answer is shown, and (only on the blind rep)
it counts as a miss."
  (interactive)
  (unless (eq haskellpy-problems--state 'typing)
    (user-error "No card on the table"))
  (haskellpy-problems--show-result t))

(defun haskellpy-problems--advance ()
  "A correct check: record the hit (if this was the blind rep) and move
straight to the next rep, card, or level, with no review screen."
  (when (haskellpy-problems--blind-p)
    (cl-incf haskellpy-problems--hits))
  (if (haskellpy-problems--blind-p)
      (if haskellpy-problems--queue (haskellpy-problems--deal-card) (haskellpy-problems--level-end))
    (cl-incf haskellpy-problems--round)
    (haskellpy-problems--deal-round)))

(defun haskellpy-problems--show-result (gave-up)
  "Show the miss/give-up screen for a wrong or given-up rep."
  (setq haskellpy-problems--state 'shown
        haskellpy-problems--last-gave-up gave-up)
  (when (haskellpy-problems--blind-p)
    (push (car haskellpy-problems--item) haskellpy-problems--misses))
  (let ((inhibit-read-only t))
    (goto-char (point-max))
    (unless (bolp) (insert "\n"))
    (insert "\n")
    (haskellpy-problems--insert 'error
                              (if gave-up "Gave up.  The solution is:\n\n" "Miss.  The solution is:\n\n"))
    (insert (nth 2 haskellpy-problems--item) "\n")
    (haskellpy-problems--insert 'font-lock-comment-face
                              (format "\nNote: %s\n" (nth 3 haskellpy-problems--item)))
    (haskellpy-problems--insert
     'font-lock-comment-face
     (cond
      ((and (not gave-up) (not (haskellpy-problems--blind-p)))
       "\nSPC  try this rep again     q  quit\n")
      ((haskellpy-problems--blind-p)
       (if haskellpy-problems--queue "\nSPC  next card     q  quit\n" "\nSPC  level result  q  quit\n"))
      (t "\nSPC  next rep, less shown     q  quit\n"))))
  (haskellpy-problems--menu-phase)
  (goto-char (point-max)))

(defun haskellpy-problems-next ()
  "Continue after a miss/give-up screen: retry this rep, fade to the next
rep, next card, level result, or the next level."
  (interactive)
  (pcase haskellpy-problems--state
    ('shown
     (cond
      ;; Wrong (not given up) on a hinted rep: repeat it at the same fade level.
      ((and (not haskellpy-problems--last-gave-up) (not (haskellpy-problems--blind-p)))
       (haskellpy-problems--deal-round))
      ;; The blind rep just finished (wrong or given up): next card, or end the level.
      ((haskellpy-problems--blind-p)
       (if haskellpy-problems--queue (haskellpy-problems--deal-card) (haskellpy-problems--level-end)))
      ;; Given up on a hinted rep: fade it further.
      (t (cl-incf haskellpy-problems--round) (haskellpy-problems--deal-round))))
    ('level-end (haskellpy-problems--start-level
                 (min haskellpy-problems--unlocked (length haskellpy-problems--levels))))
    ('won (haskellpy-problems-choose-level))
    (_ (user-error "Type your answer, then C-c C-c"))))

(defun haskellpy-problems--level-end ()
  (let* ((n haskellpy-problems--total)
         (nlevels (length haskellpy-problems--levels))
         (perfect (= haskellpy-problems--hits n))
         (last (= haskellpy-problems--level nlevels))
         (next (1+ haskellpy-problems--level)))
    (when (and perfect (> next haskellpy-problems--unlocked) (not last))
      (setq haskellpy-problems--unlocked next)
      (haskellpy-problems--save-progress))
    (haskellpy-problems--clear)
    (cond
     ((and perfect last)
      (setq haskellpy-problems--state 'won)
      (haskellpy-problems--insert 'success
                                (format "\n   *** CHAPTER %d CLEARED -- %d/%d ***\n\n" haskellpy-problems--level n n))
      (haskellpy-problems--insert 'bold
                                (format "   You have typed the whole homework course from memory.  All %d chapters cleared.\n\n" nlevels))
      (haskellpy-problems--insert 'font-lock-comment-face
                                "   l  replay any level     n  new game     q  quit\n"))
     (perfect
      (setq haskellpy-problems--state 'level-end)
      (haskellpy-problems--insert 'success
                                (format "\n   *** CHAPTER %d CLEARED -- %d/%d perfect! ***\n\n" haskellpy-problems--level n n))
      (haskellpy-problems--insert 'bold
                                (format "   Chapter %d unlocked: %s (%d cards)\n\n"
                                        next (haskellpy-problems--level-name next)
                                        (length (haskellpy-problems--level-items next))))
      (haskellpy-problems--insert 'font-lock-comment-face
                                (format "   SPC  play chapter %d     r  replay chapter %d     l  choose level     q  quit\n"
                                        next haskellpy-problems--level)))
     (t
      (setq haskellpy-problems--state 'level-end)
      (haskellpy-problems--insert 'error
                                (format "\n   Chapter %d: %d/%d.  " haskellpy-problems--level haskellpy-problems--hits n))
      (haskellpy-problems--insert 'bold
                                "Missed: " (mapconcat #'identity (reverse haskellpy-problems--misses) ", ") "\n\n")
      (insert "   A perfect score is needed to clear the chapter.\n\n")
      (haskellpy-problems--insert 'font-lock-comment-face
                                (format "   SPC  try chapter %d again     l  choose level     q  quit\n"
                                        haskellpy-problems--level))))
    (haskellpy-problems--menu-phase)))

(defun haskellpy-problems-replay ()
  "Play the current level again from the start."
  (interactive)
  (haskellpy-problems--start-level haskellpy-problems--level))

(defun haskellpy-problems-choose-level ()
  "Play any level up to the highest unlocked one."
  (interactive)
  (let* ((top (min haskellpy-problems--unlocked (length haskellpy-problems--levels)))
         (n (read-number (format "Chapter (1-%d): " top) top)))
    (unless (<= 1 n top)
      (user-error "Chapter %d is not unlocked yet" n))
    (haskellpy-problems--start-level n)))

(defun haskellpy-problems-quit ()
  "Leave the game.  Cleared levels are already saved."
  (interactive)
  (quit-window))

(defun haskellpy-problems-reset ()
  "Forget all progress: lock every chapter but the first."
  (interactive)
  (when (yes-or-no-p "Forget all haskellpy-problems progress? ")
    (setq haskellpy-problems--unlocked 1)
    (haskellpy-problems--save-progress)
    (message "Progress reset")))

(provide 'haskellpy-problems)
;;; haskellpy-problems.el ends here
