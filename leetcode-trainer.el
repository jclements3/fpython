;;; leetcode-trainer.el --- Type LeetCode-style solutions from memory, in 12 levels -*- lexical-binding: t; -*-

;; A memory game over leetcode.py, sibling to fpython-trainer.el.  Where
;; fpython-trainer drills the prelude's vocabulary, this one drills the
;; techniques interviewers actually probe for: hash maps, two pointers,
;; sliding window, binary search on the answer space, BFS/DFS, backtracking,
;; DP, intervals, heaps.  Each of the 12 sections of leetcode.py is a level.
;; A card shows the left-hand side of one solution --
;;
;;     def two_sum(                  class MinStack:
;;
;; -- and you type the rest.  Every card in a level must be answered
;; correctly, first try (blind, see below), to clear the level and unlock
;; the next one.  Anything less and you replay the level.  Cleared levels
;; are remembered between sessions.
;;
;; Each card is a "vanishing cues" cycle of `leetcode-trainer-fade-steps'
;; reps: the first rep shows the full solution to copy, and each rep after
;; that shows it more faded, until the last rep shows nothing and you must
;; recall it from memory -- that final blind rep is the one that counts
;; toward the level's score.  Get a rep wrong and you repeat it at the same
;; fade level before it fades further.
;;
;;   M-x leetcode-trainer          play (starts at the highest unlocked level)
;;   M-x leetcode-trainer-reset    forget all progress
;;
;; Comments, spacing and indentation are ignored when checking an answer;
;; the code has to match.

;;; Code:

(require 'cl-lib)
(require 'python)
(require 'color)

(defgroup leetcode-trainer nil
  "Type LeetCode-style interview solutions from memory."
  :group 'games
  :prefix "leetcode-trainer-")

(defcustom leetcode-trainer-file
  (expand-file-name "leetcode.py"
                    (file-name-directory
                     (file-truename (or load-file-name buffer-file-name
                                        default-directory))))
  "The leetcode.py to drill.  Defaults to the one beside this file
\(symlinks resolved, so the file may live in a load-path directory)."
  :type 'file)

(defcustom leetcode-trainer-progress-file
  (locate-user-emacs-file "leetcode-trainer-progress")
  "Where the highest unlocked level is saved."
  :type 'file)

(defcustom leetcode-trainer-fade-steps 5
  "Reps per card, fading the shown solution from full to invisible.

This is the \"vanishing cues\" technique: rep 1 shows the whole solution
for you to copy, the middle reps show it progressively dimmer as a
shrinking hint, and the final rep shows nothing -- pure recall -- which
is the only rep that counts toward clearing the level.  A wrong or given-up
answer on a non-final rep repeats that same fade level rather than
advancing it.

5 is a reasonable default: enough steps to fade gradually without making
each card tedious.  Set to 1 to disable fading entirely (every rep is
blind, the original behavior)."
  :type 'integer)

(defconst leetcode-trainer-buffer-name "*LeetCode*")

;; ---------------------------------------------------------------- state

(defvar leetcode-trainer--levels nil
  "Vector of levels; each is (NAME . ITEMS), ITEM is (NAME PROMPT CODE).")
(defvar leetcode-trainer--unlocked 1 "Highest level the player may start.")
(defvar leetcode-trainer--level 1 "Level being played.")
(defvar leetcode-trainer--queue nil "Cards still to be dealt this level.")
(defvar leetcode-trainer--item nil "The card on the table.")
(defvar leetcode-trainer--total 0 "Cards in this level.")
(defvar leetcode-trainer--hits 0 "Cards answered correctly this level.")
(defvar leetcode-trainer--misses nil "Names of cards missed this level.")
(defvar leetcode-trainer--state 'idle "One of idle, typing, shown, level-end, won.")
(defvar leetcode-trainer--answer-start nil "Marker: where the answer area begins.")
(defvar leetcode-trainer--round 1 "Fade rep (1..leetcode-trainer-fade-steps) for the card on the table.")
(defvar leetcode-trainer--last-gave-up nil "Whether the most recent rep ended in a give-up.")

;; ---------------------------------------------------------------- parsing

(defun leetcode-trainer--split-prompt (line)
  "The part of definition LINE the player is shown, or nil if not a definition."
  (when (string-match
         (concat "\\`\\(?:def [A-Za-z_][A-Za-z0-9_]*(" ; def name(
                 "\\|class [A-Za-z_][A-Za-z0-9_]*[(:]" ; class name( / class name:
                 "\\|[A-Za-z_][A-Za-z0-9_]* *= *lambda ?" ; name = lambda
                 "\\|[A-Za-z_][A-Za-z0-9_]* *= *\\)") ; name =
         line)
    (match-string 0 line)))

(defun leetcode-trainer--parse ()
  "Read `leetcode-trainer-file' into a vector of levels."
  (let ((levels nil) (items nil) (section nil) (block nil) (in-doc nil))
    (cl-flet ((close-section ()
                (when section
                  (push (cons section (nreverse items)) levels))
                (setq items nil))
              (close-block ()
                (when block
                  (let* ((code (mapconcat #'identity (nreverse (cdr block)) "\n"))
                         (prompt (car block)))
                    (push (list (replace-regexp-in-string
                                 "\\`\\(?:def\\|class\\) " ""
                                 (string-trim (car (split-string prompt "[(:=]"))))
                                prompt code)
                          items)))
                (setq block nil)))
      (with-temp-buffer
        (insert-file-contents leetcode-trainer-file)
        (goto-char (point-min))
        (while (not (eobp))
          (let ((line (buffer-substring-no-properties
                       (line-beginning-position) (line-end-position))))
            (cond
             ((cl-oddp (cl-loop with start = 0
                                while (string-match "\"\"\"" line start)
                                do (setq start (match-end 0))
                                count t))
              (setq in-doc (not in-doc)))
             (in-doc)
             ((string-match "\\`# ============ [0-9]+\\. \\(.+?\\) ============" line)
              (close-block)
              (close-section)
              (setq section (match-string 1 line)))
             ((and block (string-match "\\`[ \t]+[^ \t]" line))
              (push line (cdr block)))
             (t
              (close-block)
              (let ((prompt (and section (leetcode-trainer--split-prompt line))))
                (when prompt
                  (setq block (list prompt line)))))))
          (forward-line 1))
        (close-block)
        (close-section)))
    (vconcat (nreverse levels))))

(defun leetcode-trainer--normalize (code)
  "CODE with comments, blank lines and all whitespace removed."
  (mapconcat #'identity
             (delq nil (mapcar (lambda (line)
                                 (let ((s (replace-regexp-in-string
                                           "[ \t]" "" (car (split-string line "#")))))
                                   (and (not (string-empty-p s)) s)))
                               (split-string code "\n")))
             "\n"))

(defun leetcode-trainer--shuffle (list)
  (let ((v (vconcat list)))
    (cl-loop for i from (1- (length v)) downto 1
             do (cl-rotatef (aref v i) (aref v (random (1+ i)))))
    (append v nil)))

;; ---------------------------------------------------------------- fading

(defun leetcode-trainer--blind-p ()
  "Whether the current rep is the final, unhinted, graded one."
  (or (<= leetcode-trainer-fade-steps 1)
      (= leetcode-trainer--round leetcode-trainer-fade-steps)))

(defun leetcode-trainer--opacity ()
  "How solid the hint is on the current rep: 1.0 full, 0.0 invisible."
  (if (<= leetcode-trainer-fade-steps 1)
      0.0
    (- 1.0 (/ (float (1- leetcode-trainer--round)) (1- leetcode-trainer-fade-steps)))))

(defun leetcode-trainer--face-rgb (attribute fallback)
  "The current frame's ATTRIBUTE of the default face as an (R G B) list,
or FALLBACK's if the frame has no color set (e.g. batch mode)."
  (or (color-name-to-rgb (face-attribute 'default attribute nil t))
      (color-name-to-rgb fallback)))

(defun leetcode-trainer--fade-color (opacity)
  "A foreground color OPACITY of the way from the background to the
default foreground, as a hex string."
  (cl-destructuring-bind (fr fg fb) (leetcode-trainer--face-rgb :foreground "white")
    (cl-destructuring-bind (br bg bb) (leetcode-trainer--face-rgb :background "black")
      (color-rgb-to-hex (+ (* opacity fr) (* (- 1 opacity) br))
                         (+ (* opacity fg) (* (- 1 opacity) bg))
                         (+ (* opacity fb) (* (- 1 opacity) bb))
                         2))))

(defun leetcode-trainer--insert-hint ()
  "Show the fading solution above the prompt, at the current rep's opacity."
  (leetcode-trainer--insert
   (list :foreground (leetcode-trainer--fade-color (leetcode-trainer--opacity)))
   (nth 2 leetcode-trainer--item))
  (insert "\n\n"))

;; ---------------------------------------------------------------- progress

(defun leetcode-trainer--load-progress ()
  (setq leetcode-trainer--unlocked
        (or (ignore-errors
              (with-temp-buffer
                (insert-file-contents leetcode-trainer-progress-file)
                (plist-get (read (current-buffer)) :unlocked)))
            1)))

(defun leetcode-trainer--save-progress ()
  (with-temp-file leetcode-trainer-progress-file
    (prin1 (list :unlocked leetcode-trainer--unlocked) (current-buffer))))

;; ---------------------------------------------------------------- mode

(defvar leetcode-trainer-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "C-c C-c") #'leetcode-trainer-check)
    (define-key map (kbd "C-c C-r") #'leetcode-trainer-give-up)
    (define-key map (kbd "C-c C-q") #'leetcode-trainer-quit)
    map)
  "Keys while typing an answer.")

(defvar leetcode-trainer-menu-map
  (let ((map (make-sparse-keymap)))
    (set-keymap-parent map special-mode-map)
    (define-key map (kbd "SPC") #'leetcode-trainer-next)
    (define-key map (kbd "RET") #'leetcode-trainer-next)
    (define-key map "n" #'leetcode-trainer-new-game)
    (define-key map "r" #'leetcode-trainer-replay)
    (define-key map "l" #'leetcode-trainer-choose-level)
    (define-key map "q" #'leetcode-trainer-quit)
    map)
  "Keys between cards and between levels.")

(define-derived-mode leetcode-trainer-mode python-mode "FPython"
  "Major mode for the LeetCode typing game.

While typing an answer:
\\{leetcode-trainer-mode-map}
Between cards and levels:
\\{leetcode-trainer-menu-map}"
  (setq-local header-line-format '(:eval (leetcode-trainer--header-line)))
  (setq-local truncate-lines nil))

(defcustom leetcode-trainer-progress-bar-width 20
  "Width, in characters, of the whole-file progress bar in the header line."
  :type 'integer)

(defun leetcode-trainer--progress-bar (fraction)
  "A block-character progress bar FRACTION (0.0-1.0) full,
`leetcode-trainer-progress-bar-width' characters wide."
  (let* ((width leetcode-trainer-progress-bar-width)
         (filled (round (* fraction width))))
    (concat "[" (make-string filled ?\N{U+2588}) (make-string (- width filled) ?\N{U+2591}) "]")))

(defun leetcode-trainer--overall-progress ()
  "Fraction of the whole file cleared: levels unlocked beyond the
current one, plus this level's progress through its cards."
  (let* ((nlevels (length leetcode-trainer--levels))
         (cleared (1- leetcode-trainer--unlocked))
         (in-level (if (zerop leetcode-trainer--total)
                       0.0
                     (/ (float (- leetcode-trainer--total (length leetcode-trainer--queue)))
                        leetcode-trainer--total))))
    (min 1.0 (/ (+ cleared in-level) (float nlevels)))))

(defun leetcode-trainer--header-line ()
  (let* ((nlevels (length leetcode-trainer--levels))
         (fraction (if (eq leetcode-trainer--state 'won) 1.0 (leetcode-trainer--overall-progress)))
         (bar (format " %s %d%%  (%d/%d levels unlocked)"
                      (leetcode-trainer--progress-bar fraction)
                      (round (* 100 fraction))
                      (min leetcode-trainer--unlocked nlevels) nlevels)))
    (if (eq leetcode-trainer--state 'won)
        (format " LeetCode Trainer  %s   all %d levels cleared" bar nlevels)
      (format " LeetCode Trainer  %s   Level %d/%d  %s   card %d/%d   rep %d/%d   correct %d   missed %d"
              bar
              leetcode-trainer--level nlevels
              (leetcode-trainer--level-name leetcode-trainer--level)
              (- leetcode-trainer--total (length leetcode-trainer--queue))
              leetcode-trainer--total
              leetcode-trainer--round leetcode-trainer-fade-steps
              leetcode-trainer--hits (length leetcode-trainer--misses)))))

(defun leetcode-trainer--level-name (n)
  (car (aref leetcode-trainer--levels (1- n))))

(defun leetcode-trainer--level-items (n)
  (cdr (aref leetcode-trainer--levels (1- n))))

(defun leetcode-trainer--insert (face &rest strings)
  "Insert STRINGS, shown in FACE (an overlay, so font-lock leaves it alone)."
  (let ((beg (point)))
    (apply #'insert strings)
    (when face
      (overlay-put (make-overlay beg (point)) 'face face))))

(defun leetcode-trainer--clear ()
  (let ((inhibit-read-only t))
    (remove-overlays)
    (erase-buffer))
  (setq buffer-read-only nil))

(defun leetcode-trainer--menu-phase ()
  (setq buffer-read-only t)
  (use-local-map leetcode-trainer-menu-map)
  (goto-char (point-min)))

;; ---------------------------------------------------------------- play

;;;###autoload
(defun leetcode-trainer ()
  "Play the LeetCode typing game: 12 levels, perfect score to advance."
  (interactive)
  (setq leetcode-trainer--levels (leetcode-trainer--parse))
  (when (zerop (length leetcode-trainer--levels))
    (error "No sections found in %s" leetcode-trainer-file))
  (leetcode-trainer--load-progress)
  (switch-to-buffer leetcode-trainer-buffer-name)
  (unless (derived-mode-p 'leetcode-trainer-mode)
    ;; A game buffer, not a source file: keep linters, LSP and line
    ;; numbers from the user's Python hooks out of it.
    (let ((python-mode-hook nil)
          (prog-mode-hook nil)
          (python-indent-guess-indent-offset nil))
      (leetcode-trainer-mode)))
  (leetcode-trainer--start-level (min leetcode-trainer--unlocked
                                     (length leetcode-trainer--levels))))

(defun leetcode-trainer-new-game ()
  "Start over at the highest unlocked level."
  (interactive)
  (leetcode-trainer))

(defun leetcode-trainer--start-level (n)
  (setq leetcode-trainer--level n
        leetcode-trainer--queue (leetcode-trainer--shuffle (leetcode-trainer--level-items n))
        leetcode-trainer--total (length leetcode-trainer--queue)
        leetcode-trainer--hits 0
        leetcode-trainer--misses nil)
  (leetcode-trainer--deal-card))

(defun leetcode-trainer--deal-card ()
  "Pop the next card from the queue and start its fade cycle at rep 1."
  (setq leetcode-trainer--item (pop leetcode-trainer--queue)
        leetcode-trainer--round 1)
  (leetcode-trainer--deal-round))

(defun leetcode-trainer--deal-round ()
  "(Re)present the card on the table at the current fade rep."
  (let ((prompt (nth 1 leetcode-trainer--item)))
    (setq leetcode-trainer--state 'typing)
    (leetcode-trainer--clear)
    (use-local-map leetcode-trainer-mode-map)
    (leetcode-trainer--insert 'bold (format "Level %d: %s" leetcode-trainer--level
                                          (leetcode-trainer--level-name leetcode-trainer--level)))
    (leetcode-trainer--insert 'font-lock-comment-face
                             (format "   card %d of %d   rep %d/%d\n"
                                     (- leetcode-trainer--total (length leetcode-trainer--queue))
                                     leetcode-trainer--total
                                     leetcode-trainer--round leetcode-trainer-fade-steps))
    (leetcode-trainer--insert
     'font-lock-comment-face
     (if (leetcode-trainer--blind-p)
         "Finish the definition from memory.   C-c C-c check   C-c C-r give up   C-c C-q quit\n\n"
       "Retype the definition shown below.   C-c C-c check   C-c C-q quit\n\n"))
    (unless (leetcode-trainer--blind-p)
      (leetcode-trainer--insert-hint))
    (insert prompt)
    (let ((end (point))
          (inhibit-read-only t))
      (put-text-property (point-min) end 'read-only t)
      (put-text-property (point-min) (1+ (point-min)) 'front-sticky t)
      (put-text-property (1- end) end 'rear-nonsticky t)
      (setq leetcode-trainer--answer-start (copy-marker end)))))

(defun leetcode-trainer--attempt ()
  (buffer-substring-no-properties leetcode-trainer--answer-start (point-max)))

(defun leetcode-trainer--expected ()
  (substring (nth 2 leetcode-trainer--item) (length (nth 1 leetcode-trainer--item))))

(defun leetcode-trainer-check ()
  "Check the answer typed under the prompt.  A correct answer needs no
review: it just updates the score and moves straight on.  A wrong answer
shows what the solution actually has, and waits for SPC."
  (interactive)
  (unless (eq leetcode-trainer--state 'typing)
    (user-error "No card on the table"))
  (let ((attempt (leetcode-trainer--attempt)))
    (if (string= (leetcode-trainer--normalize attempt)
                 (leetcode-trainer--normalize (leetcode-trainer--expected)))
        (leetcode-trainer--advance)
      (leetcode-trainer--show-result nil))))

(defun leetcode-trainer-give-up ()
  "Give up on this rep: the answer is shown, and (only on the blind rep)
it counts as a miss."
  (interactive)
  (unless (eq leetcode-trainer--state 'typing)
    (user-error "No card on the table"))
  (leetcode-trainer--show-result t))

(defun leetcode-trainer--advance ()
  "A correct check: record the hit (if this was the blind rep) and move
straight to the next rep, card, or level, with no review screen."
  (when (leetcode-trainer--blind-p)
    (cl-incf leetcode-trainer--hits))
  (if (leetcode-trainer--blind-p)
      (if leetcode-trainer--queue (leetcode-trainer--deal-card) (leetcode-trainer--level-end))
    (cl-incf leetcode-trainer--round)
    (leetcode-trainer--deal-round)))

(defun leetcode-trainer--show-result (gave-up)
  "Show the miss/give-up screen for a wrong or given-up rep."
  (setq leetcode-trainer--state 'shown
        leetcode-trainer--last-gave-up gave-up)
  (when (leetcode-trainer--blind-p)
    (push (car leetcode-trainer--item) leetcode-trainer--misses))
  (let ((inhibit-read-only t))
    (goto-char (point-max))
    (unless (bolp) (insert "\n"))
    (insert "\n")
    (leetcode-trainer--insert 'error
                             (if gave-up "Gave up.  The solution is:\n\n" "Miss.  The solution is:\n\n"))
    (insert (nth 2 leetcode-trainer--item) "\n")
    (leetcode-trainer--insert
     'font-lock-comment-face
     (cond
      ((and (not gave-up) (not (leetcode-trainer--blind-p)))
       "\nSPC  try this rep again     q  quit\n")
      ((leetcode-trainer--blind-p)
       (if leetcode-trainer--queue "\nSPC  next card     q  quit\n" "\nSPC  level result  q  quit\n"))
      (t "\nSPC  next rep, less shown     q  quit\n"))))
  (leetcode-trainer--menu-phase)
  (goto-char (point-max)))

(defun leetcode-trainer-next ()
  "Continue after a miss/give-up screen: retry this rep, fade to the next
rep, next card, level result, or the next level."
  (interactive)
  (pcase leetcode-trainer--state
    ('shown
     (cond
      ;; Wrong (not given up) on a hinted rep: repeat it at the same fade level.
      ((and (not leetcode-trainer--last-gave-up) (not (leetcode-trainer--blind-p)))
       (leetcode-trainer--deal-round))
      ;; The blind rep just finished (wrong or given up): next card, or end the level.
      ((leetcode-trainer--blind-p)
       (if leetcode-trainer--queue (leetcode-trainer--deal-card) (leetcode-trainer--level-end)))
      ;; Given up on a hinted rep: fade it further.
      (t (cl-incf leetcode-trainer--round) (leetcode-trainer--deal-round))))
    ('level-end (leetcode-trainer--start-level
                 (min leetcode-trainer--unlocked (length leetcode-trainer--levels))))
    ('won (leetcode-trainer-choose-level))
    (_ (user-error "Type your answer, then C-c C-c"))))

(defun leetcode-trainer--level-end ()
  (let* ((n leetcode-trainer--total)
         (nlevels (length leetcode-trainer--levels))
         (perfect (= leetcode-trainer--hits n))
         (last (= leetcode-trainer--level nlevels))
         (next (1+ leetcode-trainer--level)))
    (when (and perfect (> next leetcode-trainer--unlocked) (not last))
      (setq leetcode-trainer--unlocked next)
      (leetcode-trainer--save-progress))
    (leetcode-trainer--clear)
    (cond
     ((and perfect last)
      (setq leetcode-trainer--state 'won)
      (leetcode-trainer--insert 'success
                               (format "\n   *** LEVEL %d CLEARED -- %d/%d ***\n\n" leetcode-trainer--level n n))
      (leetcode-trainer--insert 'bold
                               (format "   You have typed every solution from memory.  All %d levels cleared.\n\n" nlevels))
      (leetcode-trainer--insert 'font-lock-comment-face
                               "   l  replay any level     n  new game     q  quit\n"))
     (perfect
      (setq leetcode-trainer--state 'level-end)
      (leetcode-trainer--insert 'success
                               (format "\n   *** LEVEL %d CLEARED -- %d/%d perfect! ***\n\n" leetcode-trainer--level n n))
      (leetcode-trainer--insert 'bold
                               (format "   Level %d unlocked: %s (%d cards)\n\n"
                                       next (leetcode-trainer--level-name next)
                                       (length (leetcode-trainer--level-items next))))
      (leetcode-trainer--insert 'font-lock-comment-face
                               (format "   SPC  play level %d     r  replay level %d     l  choose level     q  quit\n"
                                       next leetcode-trainer--level)))
     (t
      (setq leetcode-trainer--state 'level-end)
      (leetcode-trainer--insert 'error
                               (format "\n   Level %d: %d/%d.  " leetcode-trainer--level leetcode-trainer--hits n))
      (leetcode-trainer--insert 'bold
                               "Missed: " (mapconcat #'identity (reverse leetcode-trainer--misses) ", ") "\n\n")
      (insert "   A perfect score is needed to clear the level.\n\n")
      (leetcode-trainer--insert 'font-lock-comment-face
                               (format "   SPC  try level %d again     l  choose level     q  quit\n"
                                       leetcode-trainer--level))))
    (leetcode-trainer--menu-phase)))

(defun leetcode-trainer-replay ()
  "Play the current level again from the start."
  (interactive)
  (leetcode-trainer--start-level leetcode-trainer--level))

(defun leetcode-trainer-choose-level ()
  "Play any level up to the highest unlocked one."
  (interactive)
  (let* ((top (min leetcode-trainer--unlocked (length leetcode-trainer--levels)))
         (n (read-number (format "Level (1-%d): " top) top)))
    (unless (<= 1 n top)
      (user-error "Level %d is not unlocked yet" n))
    (leetcode-trainer--start-level n)))

(defun leetcode-trainer-quit ()
  "Leave the game.  Cleared levels are already saved."
  (interactive)
  (quit-window))

(defun leetcode-trainer-reset ()
  "Forget all progress: lock every level but the first."
  (interactive)
  (when (yes-or-no-p "Forget all leetcode-trainer progress? ")
    (setq leetcode-trainer--unlocked 1)
    (leetcode-trainer--save-progress)
    (message "Progress reset")))

(provide 'leetcode-trainer)
;;; leetcode-trainer.el ends here
