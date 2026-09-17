;;; fpython-trainer.el --- Type the prelude from memory, in 16 levels -*- lexical-binding: t; -*-

;; A memory game over prelude.py, in the spirit of the games in lisp/play
;; (tetris, 5x5, mpuz).  Each of the 16 sections of the prelude is a level.
;; A card shows the left-hand side of one definition --
;;
;;     head      = lambda            def isqrt(
;;
;; -- and you type the rest.  Every card in a level must be answered
;; correctly, first try (blind, see below), to clear the level and unlock
;; the next one.  Anything less and you replay the level.  Cleared levels
;; are remembered between sessions.
;;
;; Each card is a "vanishing cues" cycle of `fpython-trainer-fade-steps'
;; reps: the first rep shows the full solution to copy, and each rep after
;; that shows it more faded, until the last rep shows nothing and you must
;; recall it from memory -- that final blind rep is the one that counts
;; toward the level's score.  Get a rep wrong and you repeat it at the same
;; fade level before it fades further.
;;
;;   M-x fpython-trainer          play (starts at the highest unlocked level)
;;   M-x fpython-trainer-reset    forget all progress
;;
;; Comments, spacing and indentation are ignored when checking an answer;
;; the code has to match.

;;; Code:

(require 'cl-lib)
(require 'python)
(require 'color)

(defgroup fpython-trainer nil
  "Type the prelude from memory."
  :group 'games
  :prefix "fpython-trainer-")

(defcustom fpython-trainer-file
  (expand-file-name "prelude.py"
                    (file-name-directory
                     (file-truename (or load-file-name buffer-file-name
                                        default-directory))))
  "The prelude.py to drill.  Defaults to the one beside this file
\(symlinks resolved, so the file may live in a load-path directory)."
  :type 'file)

(defcustom fpython-trainer-progress-file
  (locate-user-emacs-file "fpython-trainer-progress")
  "Where the highest unlocked level is saved."
  :type 'file)

(defcustom fpython-trainer-fade-steps 5
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

(defconst fpython-trainer-buffer-name "*FPython*")

;; ---------------------------------------------------------------- state

(defvar fpython-trainer--levels nil
  "Vector of levels; each is (NAME . ITEMS), ITEM is (NAME PROMPT CODE).")
(defvar fpython-trainer--unlocked 1 "Highest level the player may start.")
(defvar fpython-trainer--level 1 "Level being played.")
(defvar fpython-trainer--queue nil "Cards still to be dealt this level.")
(defvar fpython-trainer--item nil "The card on the table.")
(defvar fpython-trainer--total 0 "Cards in this level.")
(defvar fpython-trainer--hits 0 "Cards answered correctly this level.")
(defvar fpython-trainer--misses nil "Names of cards missed this level.")
(defvar fpython-trainer--state 'idle "One of idle, typing, shown, level-end, won.")
(defvar fpython-trainer--answer-start nil "Marker: where the answer area begins.")
(defvar fpython-trainer--round 1 "Fade rep (1..fpython-trainer-fade-steps) for the card on the table.")
(defvar fpython-trainer--last-gave-up nil "Whether the most recent rep ended in a give-up.")

;; ---------------------------------------------------------------- parsing

(defun fpython-trainer--split-prompt (line)
  "The part of definition LINE the player is shown, or nil if not a definition."
  (when (string-match
         (concat "\\`\\(?:def [A-Za-z_][A-Za-z0-9_]*(" ; def name(
                 "\\|class [A-Za-z_][A-Za-z0-9_]*[(:]" ; class name( / class name:
                 "\\|[A-Za-z_][A-Za-z0-9_]* *= *lambda ?" ; name = lambda
                 "\\|[A-Za-z_][A-Za-z0-9_]* *= *\\)") ; name =
         line)
    (match-string 0 line)))

(defun fpython-trainer--parse ()
  "Read `fpython-trainer-file' into a vector of levels."
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
        (insert-file-contents fpython-trainer-file)
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
              (let ((prompt (and section (fpython-trainer--split-prompt line))))
                (when prompt
                  (setq block (list prompt line)))))))
          (forward-line 1))
        (close-block)
        (close-section)))
    (vconcat (nreverse levels))))

(defun fpython-trainer--normalize (code)
  "CODE with comments, blank lines and all whitespace removed."
  (mapconcat #'identity
             (delq nil (mapcar (lambda (line)
                                 (let ((s (replace-regexp-in-string
                                           "[ \t]" "" (car (split-string line "#")))))
                                   (and (not (string-empty-p s)) s)))
                               (split-string code "\n")))
             "\n"))

(defun fpython-trainer--shuffle (list)
  (let ((v (vconcat list)))
    (cl-loop for i from (1- (length v)) downto 1
             do (cl-rotatef (aref v i) (aref v (random (1+ i)))))
    (append v nil)))

;; ---------------------------------------------------------------- fading

(defun fpython-trainer--blind-p ()
  "Whether the current rep is the final, unhinted, graded one."
  (or (<= fpython-trainer-fade-steps 1)
      (= fpython-trainer--round fpython-trainer-fade-steps)))

(defun fpython-trainer--opacity ()
  "How solid the hint is on the current rep: 1.0 full, 0.0 invisible."
  (if (<= fpython-trainer-fade-steps 1)
      0.0
    (- 1.0 (/ (float (1- fpython-trainer--round)) (1- fpython-trainer-fade-steps)))))

(defun fpython-trainer--face-rgb (attribute fallback)
  "The current frame's ATTRIBUTE of the default face as an (R G B) list,
or FALLBACK's if the frame has no color set (e.g. batch mode)."
  (or (color-name-to-rgb (face-attribute 'default attribute nil t))
      (color-name-to-rgb fallback)))

(defun fpython-trainer--fade-color (opacity)
  "A foreground color OPACITY of the way from the background to the
default foreground, as a hex string."
  (cl-destructuring-bind (fr fg fb) (fpython-trainer--face-rgb :foreground "white")
    (cl-destructuring-bind (br bg bb) (fpython-trainer--face-rgb :background "black")
      (color-rgb-to-hex (+ (* opacity fr) (* (- 1 opacity) br))
                         (+ (* opacity fg) (* (- 1 opacity) bg))
                         (+ (* opacity fb) (* (- 1 opacity) bb))
                         2))))

(defun fpython-trainer--insert-hint ()
  "Show the fading solution above the prompt, at the current rep's opacity."
  (fpython-trainer--insert
   (list :foreground (fpython-trainer--fade-color (fpython-trainer--opacity)))
   (nth 2 fpython-trainer--item))
  (insert "\n\n"))

;; ---------------------------------------------------------------- progress

(defun fpython-trainer--load-progress ()
  (setq fpython-trainer--unlocked
        (or (ignore-errors
              (with-temp-buffer
                (insert-file-contents fpython-trainer-progress-file)
                (plist-get (read (current-buffer)) :unlocked)))
            1)))

(defun fpython-trainer--save-progress ()
  (with-temp-file fpython-trainer-progress-file
    (prin1 (list :unlocked fpython-trainer--unlocked) (current-buffer))))

;; ---------------------------------------------------------------- mode

(defvar fpython-trainer-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "C-c C-c") #'fpython-trainer-check)
    (define-key map (kbd "C-c C-r") #'fpython-trainer-give-up)
    (define-key map (kbd "C-c C-q") #'fpython-trainer-quit)
    map)
  "Keys while typing an answer.")

(defvar fpython-trainer-menu-map
  (let ((map (make-sparse-keymap)))
    (set-keymap-parent map special-mode-map)
    (define-key map (kbd "SPC") #'fpython-trainer-next)
    (define-key map (kbd "RET") #'fpython-trainer-next)
    (define-key map "n" #'fpython-trainer-new-game)
    (define-key map "r" #'fpython-trainer-replay)
    (define-key map "l" #'fpython-trainer-choose-level)
    (define-key map "q" #'fpython-trainer-quit)
    map)
  "Keys between cards and between levels.")

(define-derived-mode fpython-trainer-mode python-mode "FPython"
  "Major mode for the prelude typing game.

While typing an answer:
\\{fpython-trainer-mode-map}
Between cards and levels:
\\{fpython-trainer-menu-map}"
  (setq-local header-line-format '(:eval (fpython-trainer--header-line)))
  (setq-local truncate-lines nil))

(defcustom fpython-trainer-progress-bar-width 20
  "Width, in characters, of the whole-prelude progress bar in the header line."
  :type 'integer)

(defun fpython-trainer--progress-bar (fraction)
  "A block-character progress bar FRACTION (0.0-1.0) full,
`fpython-trainer-progress-bar-width' characters wide."
  (let* ((width fpython-trainer-progress-bar-width)
         (filled (round (* fraction width))))
    (concat "[" (make-string filled ?\N{U+2588}) (make-string (- width filled) ?\N{U+2591}) "]")))

(defun fpython-trainer--overall-progress ()
  "Fraction of the whole prelude cleared: levels unlocked beyond the
current one, plus this level's progress through its cards."
  (let* ((nlevels (length fpython-trainer--levels))
         (cleared (1- fpython-trainer--unlocked))
         (in-level (if (zerop fpython-trainer--total)
                       0.0
                     (/ (float (- fpython-trainer--total (length fpython-trainer--queue)))
                        fpython-trainer--total))))
    (min 1.0 (/ (+ cleared in-level) (float nlevels)))))

(defun fpython-trainer--header-line ()
  (let* ((nlevels (length fpython-trainer--levels))
         (fraction (if (eq fpython-trainer--state 'won) 1.0 (fpython-trainer--overall-progress)))
         (bar (format " %s %d%%  (%d/%d levels unlocked)"
                      (fpython-trainer--progress-bar fraction)
                      (round (* 100 fraction))
                      (min fpython-trainer--unlocked nlevels) nlevels)))
    (if (eq fpython-trainer--state 'won)
        (format " FPython Trainer  %s   all %d levels cleared" bar nlevels)
      (format " FPython Trainer  %s   Level %d/%d  %s   card %d/%d   rep %d/%d   correct %d   missed %d"
              bar
              fpython-trainer--level nlevels
              (fpython-trainer--level-name fpython-trainer--level)
              (- fpython-trainer--total (length fpython-trainer--queue))
              fpython-trainer--total
              fpython-trainer--round fpython-trainer-fade-steps
              fpython-trainer--hits (length fpython-trainer--misses)))))

(defun fpython-trainer--level-name (n)
  (car (aref fpython-trainer--levels (1- n))))

(defun fpython-trainer--level-items (n)
  (cdr (aref fpython-trainer--levels (1- n))))

(defun fpython-trainer--insert (face &rest strings)
  "Insert STRINGS, shown in FACE (an overlay, so font-lock leaves it alone)."
  (let ((beg (point)))
    (apply #'insert strings)
    (when face
      (overlay-put (make-overlay beg (point)) 'face face))))

(defun fpython-trainer--clear ()
  (let ((inhibit-read-only t))
    (remove-overlays)
    (erase-buffer))
  (setq buffer-read-only nil))

(defun fpython-trainer--menu-phase ()
  (setq buffer-read-only t)
  (use-local-map fpython-trainer-menu-map)
  (goto-char (point-min)))

;; ---------------------------------------------------------------- play

;;;###autoload
(defun fpython-trainer ()
  "Play the prelude typing game: 16 levels, perfect score to advance."
  (interactive)
  (setq fpython-trainer--levels (fpython-trainer--parse))
  (when (zerop (length fpython-trainer--levels))
    (error "No sections found in %s" fpython-trainer-file))
  (fpython-trainer--load-progress)
  (switch-to-buffer fpython-trainer-buffer-name)
  (unless (derived-mode-p 'fpython-trainer-mode)
    ;; A game buffer, not a source file: keep linters, LSP and line
    ;; numbers from the user's Python hooks out of it.
    (let ((python-mode-hook nil)
          (prog-mode-hook nil)
          (python-indent-guess-indent-offset nil))
      (fpython-trainer-mode)))
  (fpython-trainer--start-level (min fpython-trainer--unlocked
                                     (length fpython-trainer--levels))))

(defun fpython-trainer-new-game ()
  "Start over at the highest unlocked level."
  (interactive)
  (fpython-trainer))

(defun fpython-trainer--start-level (n)
  (setq fpython-trainer--level n
        fpython-trainer--queue (fpython-trainer--shuffle (fpython-trainer--level-items n))
        fpython-trainer--total (length fpython-trainer--queue)
        fpython-trainer--hits 0
        fpython-trainer--misses nil)
  (fpython-trainer--deal-card))

(defun fpython-trainer--deal-card ()
  "Pop the next card from the queue and start its fade cycle at rep 1."
  (setq fpython-trainer--item (pop fpython-trainer--queue)
        fpython-trainer--round 1)
  (fpython-trainer--deal-round))

(defun fpython-trainer--deal-round ()
  "(Re)present the card on the table at the current fade rep."
  (let ((prompt (nth 1 fpython-trainer--item)))
    (setq fpython-trainer--state 'typing)
    (fpython-trainer--clear)
    (use-local-map fpython-trainer-mode-map)
    (fpython-trainer--insert 'bold (format "Level %d: %s" fpython-trainer--level
                                          (fpython-trainer--level-name fpython-trainer--level)))
    (fpython-trainer--insert 'font-lock-comment-face
                             (format "   card %d of %d   rep %d/%d\n"
                                     (- fpython-trainer--total (length fpython-trainer--queue))
                                     fpython-trainer--total
                                     fpython-trainer--round fpython-trainer-fade-steps))
    (fpython-trainer--insert
     'font-lock-comment-face
     (if (fpython-trainer--blind-p)
         "Finish the definition from memory.   C-c C-c check   C-c C-r give up   C-c C-q quit\n\n"
       "Retype the definition shown below.   C-c C-c check   C-c C-q quit\n\n"))
    (unless (fpython-trainer--blind-p)
      (fpython-trainer--insert-hint))
    (insert prompt)
    (let ((end (point))
          (inhibit-read-only t))
      (put-text-property (point-min) end 'read-only t)
      (put-text-property (point-min) (1+ (point-min)) 'front-sticky t)
      (put-text-property (1- end) end 'rear-nonsticky t)
      (setq fpython-trainer--answer-start (copy-marker end)))))

(defun fpython-trainer--attempt ()
  (buffer-substring-no-properties fpython-trainer--answer-start (point-max)))

(defun fpython-trainer--expected ()
  (substring (nth 2 fpython-trainer--item) (length (nth 1 fpython-trainer--item))))

(defun fpython-trainer-check ()
  "Check the answer typed under the prompt.  A correct answer needs no
review: it just updates the score and moves straight on.  A wrong answer
shows what the prelude actually has, and waits for SPC."
  (interactive)
  (unless (eq fpython-trainer--state 'typing)
    (user-error "No card on the table"))
  (let ((attempt (fpython-trainer--attempt)))
    (if (string= (fpython-trainer--normalize attempt)
                 (fpython-trainer--normalize (fpython-trainer--expected)))
        (fpython-trainer--advance)
      (fpython-trainer--show-result nil))))

(defun fpython-trainer-give-up ()
  "Give up on this rep: the answer is shown, and (only on the blind rep)
it counts as a miss."
  (interactive)
  (unless (eq fpython-trainer--state 'typing)
    (user-error "No card on the table"))
  (fpython-trainer--show-result t))

(defun fpython-trainer--advance ()
  "A correct check: record the hit (if this was the blind rep) and move
straight to the next rep, card, or level, with no review screen."
  (when (fpython-trainer--blind-p)
    (cl-incf fpython-trainer--hits))
  (if (fpython-trainer--blind-p)
      (if fpython-trainer--queue (fpython-trainer--deal-card) (fpython-trainer--level-end))
    (cl-incf fpython-trainer--round)
    (fpython-trainer--deal-round)))

(defun fpython-trainer--show-result (gave-up)
  "Show the miss/give-up screen for a wrong or given-up rep."
  (setq fpython-trainer--state 'shown
        fpython-trainer--last-gave-up gave-up)
  (when (fpython-trainer--blind-p)
    (push (car fpython-trainer--item) fpython-trainer--misses))
  (let ((inhibit-read-only t))
    (goto-char (point-max))
    (unless (bolp) (insert "\n"))
    (insert "\n")
    (fpython-trainer--insert 'error
                             (if gave-up "Gave up.  The prelude has:\n\n" "Miss.  The prelude has:\n\n"))
    (insert (nth 2 fpython-trainer--item) "\n")
    (fpython-trainer--insert
     'font-lock-comment-face
     (cond
      ((and (not gave-up) (not (fpython-trainer--blind-p)))
       "\nSPC  try this rep again     q  quit\n")
      ((fpython-trainer--blind-p)
       (if fpython-trainer--queue "\nSPC  next card     q  quit\n" "\nSPC  level result  q  quit\n"))
      (t "\nSPC  next rep, less shown     q  quit\n"))))
  (fpython-trainer--menu-phase)
  (goto-char (point-max)))

(defun fpython-trainer-next ()
  "Continue after a miss/give-up screen: retry this rep, fade to the next
rep, next card, level result, or the next level."
  (interactive)
  (pcase fpython-trainer--state
    ('shown
     (cond
      ;; Wrong (not given up) on a hinted rep: repeat it at the same fade level.
      ((and (not fpython-trainer--last-gave-up) (not (fpython-trainer--blind-p)))
       (fpython-trainer--deal-round))
      ;; The blind rep just finished (wrong or given up): next card, or end the level.
      ((fpython-trainer--blind-p)
       (if fpython-trainer--queue (fpython-trainer--deal-card) (fpython-trainer--level-end)))
      ;; Given up on a hinted rep: fade it further.
      (t (cl-incf fpython-trainer--round) (fpython-trainer--deal-round))))
    ('level-end (fpython-trainer--start-level
                 (min fpython-trainer--unlocked (length fpython-trainer--levels))))
    ('won (fpython-trainer-choose-level))
    (_ (user-error "Type your answer, then C-c C-c"))))

(defun fpython-trainer--level-end ()
  (let* ((n fpython-trainer--total)
         (nlevels (length fpython-trainer--levels))
         (perfect (= fpython-trainer--hits n))
         (last (= fpython-trainer--level nlevels))
         (next (1+ fpython-trainer--level)))
    (when (and perfect (> next fpython-trainer--unlocked) (not last))
      (setq fpython-trainer--unlocked next)
      (fpython-trainer--save-progress))
    (fpython-trainer--clear)
    (cond
     ((and perfect last)
      (setq fpython-trainer--state 'won)
      (fpython-trainer--insert 'success
                               (format "\n   *** LEVEL %d CLEARED -- %d/%d ***\n\n" fpython-trainer--level n n))
      (fpython-trainer--insert 'bold
                               (format "   You have typed the whole prelude from memory.  All %d levels cleared.\n\n" nlevels))
      (fpython-trainer--insert 'font-lock-comment-face
                               "   l  replay any level     n  new game     q  quit\n"))
     (perfect
      (setq fpython-trainer--state 'level-end)
      (fpython-trainer--insert 'success
                               (format "\n   *** LEVEL %d CLEARED -- %d/%d perfect! ***\n\n" fpython-trainer--level n n))
      (fpython-trainer--insert 'bold
                               (format "   Level %d unlocked: %s (%d cards)\n\n"
                                       next (fpython-trainer--level-name next)
                                       (length (fpython-trainer--level-items next))))
      (fpython-trainer--insert 'font-lock-comment-face
                               (format "   SPC  play level %d     r  replay level %d     l  choose level     q  quit\n"
                                       next fpython-trainer--level)))
     (t
      (setq fpython-trainer--state 'level-end)
      (fpython-trainer--insert 'error
                               (format "\n   Level %d: %d/%d.  " fpython-trainer--level fpython-trainer--hits n))
      (fpython-trainer--insert 'bold
                               "Missed: " (mapconcat #'identity (reverse fpython-trainer--misses) ", ") "\n\n")
      (insert "   A perfect score is needed to clear the level.\n\n")
      (fpython-trainer--insert 'font-lock-comment-face
                               (format "   SPC  try level %d again     l  choose level     q  quit\n"
                                       fpython-trainer--level))))
    (fpython-trainer--menu-phase)))

(defun fpython-trainer-replay ()
  "Play the current level again from the start."
  (interactive)
  (fpython-trainer--start-level fpython-trainer--level))

(defun fpython-trainer-choose-level ()
  "Play any level up to the highest unlocked one."
  (interactive)
  (let* ((top (min fpython-trainer--unlocked (length fpython-trainer--levels)))
         (n (read-number (format "Level (1-%d): " top) top)))
    (unless (<= 1 n top)
      (user-error "Level %d is not unlocked yet" n))
    (fpython-trainer--start-level n)))

(defun fpython-trainer-quit ()
  "Leave the game.  Cleared levels are already saved."
  (interactive)
  (quit-window))

(defun fpython-trainer-reset ()
  "Forget all progress: lock every level but the first."
  (interactive)
  (when (yes-or-no-p "Forget all fpython-trainer progress? ")
    (setq fpython-trainer--unlocked 1)
    (fpython-trainer--save-progress)
    (message "Progress reset")))

(provide 'fpython-trainer)
;;; fpython-trainer.el ends here
