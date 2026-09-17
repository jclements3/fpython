;;; fpython-problems.el --- Type PreludeTeacher's homework solutions from memory -*- lexical-binding: t; -*-

;; A memory game over book/course/hw*.py, sibling to fpython-trainer.el.
;; Where fpython-trainer drills the prelude's vocabulary, this one drills
;; PreludeTeacher's homework: the same 16 chapters, same problems, same
;; solutions, as printed in the book.  Each chapter (hw01..hw16) is a level.
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
;; Each card is a "vanishing cues" cycle of `fpython-problems-fade-steps'
;; reps: the first rep shows the full solution to copy, and each rep after
;; that shows it more faded, until the last rep shows nothing and you must
;; recall it from memory -- that final blind rep is the one that counts
;; toward the level's score.  Get a rep wrong and you repeat it at the same
;; fade level before it fades further.  The problem statement, contract and
;; tests never fade -- only the solution does.
;;
;;   M-x fpython-problems          play (starts at the highest unlocked level)
;;   M-x fpython-problems-reset    forget all progress
;;
;; Comments, blank lines and all whitespace are ignored when checking an
;; answer; the code has to match. Unlike fpython-trainer's one-liners, a
;; homework solution is read from book/course/hw*.py via Python (those
;; files are executable modules, not text worth hand-parsing), so a
;; `fpython-problems-python-executable' must be on hand.

;;; Code:

(require 'cl-lib)
(require 'python)
(require 'color)
(require 'json)

(defgroup fpython-problems nil
  "Type PreludeTeacher's homework solutions from memory."
  :group 'games
  :prefix "fpython-problems-")

(defcustom fpython-problems-course-dir
  (expand-file-name "book/course"
                    (file-name-directory
                     (file-truename (or load-file-name buffer-file-name
                                        default-directory))))
  "Directory holding book/course's hw01.py..hw16.py.  Defaults to the
book/course beside this file (symlinks resolved, so the file may live in
a load-path directory)."
  :type 'directory)

(defcustom fpython-problems-python-executable "python3"
  "Python 3 interpreter used to read the hw*.py files (they are Python
modules -- a list-of-dicts literal spread across string concatenations --
not text worth regexp-parsing)."
  :type 'string)

(defcustom fpython-problems-progress-file
  (locate-user-emacs-file "fpython-problems-progress")
  "Where the highest unlocked level is saved."
  :type 'file)

(defcustom fpython-problems-fade-steps 5
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

(defconst fpython-problems-buffer-name "*FPythonProblems*")

;; ---------------------------------------------------------------- state

(defvar fpython-problems--levels nil
  "Vector of levels; each is (NAME . ITEMS), ITEM is (NAME PROMPT CODE NOTE).
NAME is \"ID  TITLE\"; PROMPT is the problem statement/contract/tests,
shown in full and never faded; CODE is the reference solution, the thing
to be recalled; NOTE is the book's teaching note, shown alongside CODE
after a miss or give-up.")
(defvar fpython-problems--unlocked 1 "Highest level the player may start.")
(defvar fpython-problems--level 1 "Level being played.")
(defvar fpython-problems--queue nil "Cards still to be dealt this level.")
(defvar fpython-problems--item nil "The card on the table.")
(defvar fpython-problems--total 0 "Cards in this level.")
(defvar fpython-problems--hits 0 "Cards answered correctly this level.")
(defvar fpython-problems--misses nil "Names of cards missed this level.")
(defvar fpython-problems--state 'idle "One of idle, typing, shown, level-end, won.")
(defvar fpython-problems--answer-start nil "Marker: where the answer area begins.")
(defvar fpython-problems--round 1 "Fade rep (1..fpython-problems-fade-steps) for the card on the table.")
(defvar fpython-problems--last-gave-up nil "Whether the most recent rep ended in a give-up.")

;; ---------------------------------------------------------------- parsing

(defconst fpython-problems--dump-script "\
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

(defun fpython-problems--run-dump ()
  "Shell out to Python; return the parsed JSON (alists, lists) it prints."
  (unless (file-directory-p fpython-problems-course-dir)
    (error "No such directory: %s" fpython-problems-course-dir))
  (with-temp-buffer
    (let ((status (call-process fpython-problems-python-executable nil t nil
                                 "-c" fpython-problems--dump-script
                                 (expand-file-name fpython-problems-course-dir))))
      (unless (zerop status)
        (error "fpython-problems: %s failed (exit %s):\n%s"
               fpython-problems-python-executable status (buffer-string)))
      (goto-char (point-min))
      (let ((json-object-type 'alist) (json-array-type 'list) (json-key-type 'symbol))
        (json-read)))))

(defun fpython-problems--wrap (text width)
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

(defun fpython-problems--format-prompt (item)
  "The always-visible, never-faded half of a card: everything but the solution."
  (format "%s  %s%s\n\n%s\n\nContract:\n    %s\n\nTests:\n%s\n"
          (alist-get 'id item) (alist-get 'title item)
          (format "   [%s]" (alist-get 'level item))
          (fpython-problems--wrap (alist-get 'statement item) 78)
          (alist-get 'contract item)
          (alist-get 'tests item)))

(defun fpython-problems--parse ()
  "Build the vector of levels straight from the Python-side JSON dump."
  (let* ((chapters (fpython-problems--run-dump)))
    (unless chapters
      (error "No chapters found in %s" fpython-problems-course-dir))
    (vconcat
     (mapcar
      (lambda (chapter)
        (cons (alist-get 'title chapter)
              (mapcar (lambda (item)
                        (list (format "%s %s" (alist-get 'id item) (alist-get 'title item))
                              (fpython-problems--format-prompt item)
                              (alist-get 'solution item)
                              (alist-get 'note item)))
                      (alist-get 'items chapter))))
      chapters))))

(defun fpython-problems--normalize (code)
  "CODE with comments, blank lines and all whitespace removed."
  (mapconcat #'identity
             (delq nil (mapcar (lambda (line)
                                 (let ((s (replace-regexp-in-string
                                           "[ \t]" "" (car (split-string line "#")))))
                                   (and (not (string-empty-p s)) s)))
                               (split-string code "\n")))
             "\n"))

(defun fpython-problems--shuffle (list)
  (let ((v (vconcat list)))
    (cl-loop for i from (1- (length v)) downto 1
             do (cl-rotatef (aref v i) (aref v (random (1+ i)))))
    (append v nil)))

;; ---------------------------------------------------------------- fading

(defun fpython-problems--blind-p ()
  "Whether the current rep is the final, unhinted, graded one."
  (or (<= fpython-problems-fade-steps 1)
      (= fpython-problems--round fpython-problems-fade-steps)))

(defun fpython-problems--opacity ()
  "How solid the hint is on the current rep: 1.0 full, 0.0 invisible."
  (if (<= fpython-problems-fade-steps 1)
      0.0
    (- 1.0 (/ (float (1- fpython-problems--round)) (1- fpython-problems-fade-steps)))))

(defun fpython-problems--face-rgb (attribute fallback)
  "The current frame's ATTRIBUTE of the default face as an (R G B) list,
or FALLBACK's if the frame has no color set (e.g. batch mode)."
  (or (color-name-to-rgb (face-attribute 'default attribute nil t))
      (color-name-to-rgb fallback)))

(defun fpython-problems--fade-color (opacity)
  "A foreground color OPACITY of the way from the background to the
default foreground, as a hex string."
  (cl-destructuring-bind (fr fg fb) (fpython-problems--face-rgb :foreground "white")
    (cl-destructuring-bind (br bg bb) (fpython-problems--face-rgb :background "black")
      (color-rgb-to-hex (+ (* opacity fr) (* (- 1 opacity) br))
                         (+ (* opacity fg) (* (- 1 opacity) bg))
                         (+ (* opacity fb) (* (- 1 opacity) bb))
                         2))))

(defun fpython-problems--insert-hint ()
  "Show the fading solution above the answer area, at the current rep's opacity."
  (fpython-problems--insert
   (list :foreground (fpython-problems--fade-color (fpython-problems--opacity)))
   (nth 2 fpython-problems--item))
  (insert "\n\n"))

;; ---------------------------------------------------------------- progress

(defun fpython-problems--load-progress ()
  (setq fpython-problems--unlocked
        (or (ignore-errors
              (with-temp-buffer
                (insert-file-contents fpython-problems-progress-file)
                (plist-get (read (current-buffer)) :unlocked)))
            1)))

(defun fpython-problems--save-progress ()
  (with-temp-file fpython-problems-progress-file
    (prin1 (list :unlocked fpython-problems--unlocked) (current-buffer))))

;; ---------------------------------------------------------------- mode

(defvar fpython-problems-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "C-c C-c") #'fpython-problems-check)
    (define-key map (kbd "C-c C-r") #'fpython-problems-give-up)
    (define-key map (kbd "C-c C-q") #'fpython-problems-quit)
    map)
  "Keys while typing an answer.")

(defvar fpython-problems-menu-map
  (let ((map (make-sparse-keymap)))
    (set-keymap-parent map special-mode-map)
    (define-key map (kbd "SPC") #'fpython-problems-next)
    (define-key map (kbd "RET") #'fpython-problems-next)
    (define-key map "n" #'fpython-problems-new-game)
    (define-key map "r" #'fpython-problems-replay)
    (define-key map "l" #'fpython-problems-choose-level)
    (define-key map "q" #'fpython-problems-quit)
    map)
  "Keys between cards and between levels.")

(define-derived-mode fpython-problems-mode python-mode "FPythonHW"
  "Major mode for the homework-solution typing game.

While typing an answer:
\\{fpython-problems-mode-map}
Between cards and levels:
\\{fpython-problems-menu-map}"
  (setq-local header-line-format '(:eval (fpython-problems--header-line)))
  (setq-local truncate-lines nil))

(defcustom fpython-problems-progress-bar-width 20
  "Width, in characters, of the whole-course progress bar in the header line."
  :type 'integer)

(defun fpython-problems--progress-bar (fraction)
  "A block-character progress bar FRACTION (0.0-1.0) full,
`fpython-problems-progress-bar-width' characters wide."
  (let* ((width fpython-problems-progress-bar-width)
         (filled (round (* fraction width))))
    (concat "[" (make-string filled ?\N{U+2588}) (make-string (- width filled) ?\N{U+2591}) "]")))

(defun fpython-problems--overall-progress ()
  "Fraction of the whole course cleared: levels unlocked beyond the
current one, plus this level's progress through its cards."
  (let* ((nlevels (length fpython-problems--levels))
         (cleared (1- fpython-problems--unlocked))
         (in-level (if (zerop fpython-problems--total)
                       0.0
                     (/ (float (- fpython-problems--total (length fpython-problems--queue)))
                        fpython-problems--total))))
    (min 1.0 (/ (+ cleared in-level) (float nlevels)))))

(defun fpython-problems--header-line ()
  (let* ((nlevels (length fpython-problems--levels))
         (fraction (if (eq fpython-problems--state 'won) 1.0 (fpython-problems--overall-progress)))
         (bar (format " %s %d%%  (%d/%d levels unlocked)"
                      (fpython-problems--progress-bar fraction)
                      (round (* 100 fraction))
                      (min fpython-problems--unlocked nlevels) nlevels)))
    (if (eq fpython-problems--state 'won)
        (format " FPython Problems  %s   all %d levels cleared" bar nlevels)
      (format " FPython Problems  %s   Ch %d/%d  %s   card %d/%d   rep %d/%d   correct %d   missed %d"
              bar
              fpython-problems--level nlevels
              (fpython-problems--level-name fpython-problems--level)
              (- fpython-problems--total (length fpython-problems--queue))
              fpython-problems--total
              fpython-problems--round fpython-problems-fade-steps
              fpython-problems--hits (length fpython-problems--misses)))))

(defun fpython-problems--level-name (n)
  (car (aref fpython-problems--levels (1- n))))

(defun fpython-problems--level-items (n)
  (cdr (aref fpython-problems--levels (1- n))))

(defun fpython-problems--insert (face &rest strings)
  "Insert STRINGS, shown in FACE (an overlay, so font-lock leaves it alone)."
  (let ((beg (point)))
    (apply #'insert strings)
    (when face
      (overlay-put (make-overlay beg (point)) 'face face))))

(defun fpython-problems--clear ()
  (let ((inhibit-read-only t))
    (remove-overlays)
    (erase-buffer))
  (setq buffer-read-only nil))

(defun fpython-problems--menu-phase ()
  (setq buffer-read-only t)
  (use-local-map fpython-problems-menu-map)
  (goto-char (point-min)))

;; ---------------------------------------------------------------- play

;;;###autoload
(defun fpython-problems ()
  "Play the homework typing game: 16 chapters, perfect score to advance."
  (interactive)
  (setq fpython-problems--levels (fpython-problems--parse))
  (when (zerop (length fpython-problems--levels))
    (error "No chapters found in %s" fpython-problems-course-dir))
  (fpython-problems--load-progress)
  (switch-to-buffer fpython-problems-buffer-name)
  (unless (derived-mode-p 'fpython-problems-mode)
    ;; A game buffer, not a source file: keep linters, LSP and line
    ;; numbers from the user's Python hooks out of it.
    (let ((python-mode-hook nil)
          (prog-mode-hook nil)
          (python-indent-guess-indent-offset nil))
      (fpython-problems-mode)))
  (fpython-problems--start-level (min fpython-problems--unlocked
                                      (length fpython-problems--levels))))

(defun fpython-problems-new-game ()
  "Start over at the highest unlocked level."
  (interactive)
  (fpython-problems))

(defun fpython-problems--start-level (n)
  (setq fpython-problems--level n
        fpython-problems--queue (fpython-problems--shuffle (fpython-problems--level-items n))
        fpython-problems--total (length fpython-problems--queue)
        fpython-problems--hits 0
        fpython-problems--misses nil)
  (fpython-problems--deal-card))

(defun fpython-problems--deal-card ()
  "Pop the next card from the queue and start its fade cycle at rep 1."
  (setq fpython-problems--item (pop fpython-problems--queue)
        fpython-problems--round 1)
  (fpython-problems--deal-round))

(defun fpython-problems--deal-round ()
  "(Re)present the card on the table at the current fade rep."
  (let ((prompt (nth 1 fpython-problems--item)))
    (setq fpython-problems--state 'typing)
    (fpython-problems--clear)
    (use-local-map fpython-problems-mode-map)
    (fpython-problems--insert 'bold (format "Chapter %d: %s" fpython-problems--level
                                            (fpython-problems--level-name fpython-problems--level)))
    (fpython-problems--insert 'font-lock-comment-face
                              (format "   card %d of %d   rep %d/%d\n\n"
                                      (- fpython-problems--total (length fpython-problems--queue))
                                      fpython-problems--total
                                      fpython-problems--round fpython-problems-fade-steps))
    (insert prompt)
    (fpython-problems--insert
     'font-lock-comment-face
     (if (fpython-problems--blind-p)
         "Write the solution from memory.   C-c C-c check   C-c C-r give up   C-c C-q quit\n"
       "Retype the solution shown below.   C-c C-c check   C-c C-q quit\n"))
    (unless (fpython-problems--blind-p)
      (insert "\n")
      (fpython-problems--insert-hint))
    (insert "\n")
    (let ((end (point))
          (inhibit-read-only t))
      (put-text-property (point-min) end 'read-only t)
      (put-text-property (point-min) (1+ (point-min)) 'front-sticky t)
      (put-text-property (1- end) end 'rear-nonsticky t)
      (setq fpython-problems--answer-start (copy-marker end)))))

(defun fpython-problems--attempt ()
  (buffer-substring-no-properties fpython-problems--answer-start (point-max)))

(defun fpython-problems--expected ()
  (nth 2 fpython-problems--item))

(defun fpython-problems-check ()
  "Check the answer typed under the prompt.  A correct answer needs no
review: it just updates the score and moves straight on.  A wrong answer
shows the reference solution (and its note), and waits for SPC."
  (interactive)
  (unless (eq fpython-problems--state 'typing)
    (user-error "No card on the table"))
  (let ((attempt (fpython-problems--attempt)))
    (if (string= (fpython-problems--normalize attempt)
                 (fpython-problems--normalize (fpython-problems--expected)))
        (fpython-problems--advance)
      (fpython-problems--show-result nil))))

(defun fpython-problems-give-up ()
  "Give up on this rep: the answer is shown, and (only on the blind rep)
it counts as a miss."
  (interactive)
  (unless (eq fpython-problems--state 'typing)
    (user-error "No card on the table"))
  (fpython-problems--show-result t))

(defun fpython-problems--advance ()
  "A correct check: record the hit (if this was the blind rep) and move
straight to the next rep, card, or level, with no review screen."
  (when (fpython-problems--blind-p)
    (cl-incf fpython-problems--hits))
  (if (fpython-problems--blind-p)
      (if fpython-problems--queue (fpython-problems--deal-card) (fpython-problems--level-end))
    (cl-incf fpython-problems--round)
    (fpython-problems--deal-round)))

(defun fpython-problems--show-result (gave-up)
  "Show the miss/give-up screen for a wrong or given-up rep."
  (setq fpython-problems--state 'shown
        fpython-problems--last-gave-up gave-up)
  (when (fpython-problems--blind-p)
    (push (car fpython-problems--item) fpython-problems--misses))
  (let ((inhibit-read-only t))
    (goto-char (point-max))
    (unless (bolp) (insert "\n"))
    (insert "\n")
    (fpython-problems--insert 'error
                              (if gave-up "Gave up.  The solution is:\n\n" "Miss.  The solution is:\n\n"))
    (insert (nth 2 fpython-problems--item) "\n")
    (fpython-problems--insert 'font-lock-comment-face
                              (format "\nNote: %s\n" (nth 3 fpython-problems--item)))
    (fpython-problems--insert
     'font-lock-comment-face
     (cond
      ((and (not gave-up) (not (fpython-problems--blind-p)))
       "\nSPC  try this rep again     q  quit\n")
      ((fpython-problems--blind-p)
       (if fpython-problems--queue "\nSPC  next card     q  quit\n" "\nSPC  level result  q  quit\n"))
      (t "\nSPC  next rep, less shown     q  quit\n"))))
  (fpython-problems--menu-phase)
  (goto-char (point-max)))

(defun fpython-problems-next ()
  "Continue after a miss/give-up screen: retry this rep, fade to the next
rep, next card, level result, or the next level."
  (interactive)
  (pcase fpython-problems--state
    ('shown
     (cond
      ;; Wrong (not given up) on a hinted rep: repeat it at the same fade level.
      ((and (not fpython-problems--last-gave-up) (not (fpython-problems--blind-p)))
       (fpython-problems--deal-round))
      ;; The blind rep just finished (wrong or given up): next card, or end the level.
      ((fpython-problems--blind-p)
       (if fpython-problems--queue (fpython-problems--deal-card) (fpython-problems--level-end)))
      ;; Given up on a hinted rep: fade it further.
      (t (cl-incf fpython-problems--round) (fpython-problems--deal-round))))
    ('level-end (fpython-problems--start-level
                 (min fpython-problems--unlocked (length fpython-problems--levels))))
    ('won (fpython-problems-choose-level))
    (_ (user-error "Type your answer, then C-c C-c"))))

(defun fpython-problems--level-end ()
  (let* ((n fpython-problems--total)
         (nlevels (length fpython-problems--levels))
         (perfect (= fpython-problems--hits n))
         (last (= fpython-problems--level nlevels))
         (next (1+ fpython-problems--level)))
    (when (and perfect (> next fpython-problems--unlocked) (not last))
      (setq fpython-problems--unlocked next)
      (fpython-problems--save-progress))
    (fpython-problems--clear)
    (cond
     ((and perfect last)
      (setq fpython-problems--state 'won)
      (fpython-problems--insert 'success
                                (format "\n   *** CHAPTER %d CLEARED -- %d/%d ***\n\n" fpython-problems--level n n))
      (fpython-problems--insert 'bold
                                (format "   You have typed the whole homework course from memory.  All %d chapters cleared.\n\n" nlevels))
      (fpython-problems--insert 'font-lock-comment-face
                                "   l  replay any level     n  new game     q  quit\n"))
     (perfect
      (setq fpython-problems--state 'level-end)
      (fpython-problems--insert 'success
                                (format "\n   *** CHAPTER %d CLEARED -- %d/%d perfect! ***\n\n" fpython-problems--level n n))
      (fpython-problems--insert 'bold
                                (format "   Chapter %d unlocked: %s (%d cards)\n\n"
                                        next (fpython-problems--level-name next)
                                        (length (fpython-problems--level-items next))))
      (fpython-problems--insert 'font-lock-comment-face
                                (format "   SPC  play chapter %d     r  replay chapter %d     l  choose level     q  quit\n"
                                        next fpython-problems--level)))
     (t
      (setq fpython-problems--state 'level-end)
      (fpython-problems--insert 'error
                                (format "\n   Chapter %d: %d/%d.  " fpython-problems--level fpython-problems--hits n))
      (fpython-problems--insert 'bold
                                "Missed: " (mapconcat #'identity (reverse fpython-problems--misses) ", ") "\n\n")
      (insert "   A perfect score is needed to clear the chapter.\n\n")
      (fpython-problems--insert 'font-lock-comment-face
                                (format "   SPC  try chapter %d again     l  choose level     q  quit\n"
                                        fpython-problems--level))))
    (fpython-problems--menu-phase)))

(defun fpython-problems-replay ()
  "Play the current level again from the start."
  (interactive)
  (fpython-problems--start-level fpython-problems--level))

(defun fpython-problems-choose-level ()
  "Play any level up to the highest unlocked one."
  (interactive)
  (let* ((top (min fpython-problems--unlocked (length fpython-problems--levels)))
         (n (read-number (format "Chapter (1-%d): " top) top)))
    (unless (<= 1 n top)
      (user-error "Chapter %d is not unlocked yet" n))
    (fpython-problems--start-level n)))

(defun fpython-problems-quit ()
  "Leave the game.  Cleared levels are already saved."
  (interactive)
  (quit-window))

(defun fpython-problems-reset ()
  "Forget all progress: lock every chapter but the first."
  (interactive)
  (when (yes-or-no-p "Forget all fpython-problems progress? ")
    (setq fpython-problems--unlocked 1)
    (fpython-problems--save-progress)
    (message "Progress reset")))

(provide 'fpython-problems)
;;; fpython-problems.el ends here
