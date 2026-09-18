;;; haskellpy-trainer.el --- Type haskell.py from memory, in 17 levels -*- lexical-binding: t; -*-

;; A memory game over haskell.py (prelude.py's production sibling), in the spirit of the games in lisp/play
;; (tetris, 5x5, mpuz).  Each of the 17 sections of haskell.py is a level.
;; A card shows the left-hand side of one definition --
;;
;;     head      = lambda            def isqrt(
;;
;; -- and you type the rest.  Every card in a level must be answered
;; correctly, first try (blind, see below), to clear the level and unlock
;; the next one.  Anything less and you replay the level.  Cleared levels
;; are remembered between sessions.
;;
;; Each card is a "vanishing cues" cycle of `haskellpy-trainer-fade-steps'
;; reps: the first rep shows the full solution to copy, and each rep after
;; that shows it more faded, until the last rep shows nothing and you must
;; recall it from memory -- that final blind rep is the one that counts
;; toward the level's score.  Get a rep wrong and you repeat it at the same
;; fade level before it fades further.
;;
;;   M-x haskellpy-trainer          play (starts at the highest unlocked level)
;;   M-x haskellpy-trainer-reset    forget all progress
;;
;; Comments, spacing and indentation are ignored when checking an answer;
;; the code has to match.

;;; Code:

(require 'cl-lib)
(require 'python)
(require 'color)

(defgroup haskellpy-trainer nil
  "Type haskell.py from memory."
  :group 'games
  :prefix "haskellpy-trainer-")

(defcustom haskellpy-trainer-file
  (expand-file-name "haskell.py"
                    (file-name-directory
                     (file-truename (or load-file-name buffer-file-name
                                        default-directory))))
  "The haskell.py to drill.  Defaults to the one beside this file
\(symlinks resolved, so the file may live in a load-path directory)."
  :type 'file)

(defcustom haskellpy-trainer-progress-file
  (locate-user-emacs-file "haskellpy-trainer-progress")
  "Where the highest unlocked level is saved."
  :type 'file)

(defcustom haskellpy-trainer-fade-steps 5
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

(defconst haskellpy-trainer-buffer-name "*HaskellPy*")

;; ---------------------------------------------------------------- state

(defvar haskellpy-trainer--levels nil
  "Vector of levels; each is (NAME . ITEMS), ITEM is (NAME PROMPT CODE).")
(defvar haskellpy-trainer--unlocked 1 "Highest level the player may start.")
(defvar haskellpy-trainer--level 1 "Level being played.")
(defvar haskellpy-trainer--queue nil "Cards still to be dealt this level.")
(defvar haskellpy-trainer--item nil "The card on the table.")
(defvar haskellpy-trainer--total 0 "Cards in this level.")
(defvar haskellpy-trainer--hits 0 "Cards answered correctly this level.")
(defvar haskellpy-trainer--misses nil "Names of cards missed this level.")
(defvar haskellpy-trainer--state 'idle "One of idle, typing, shown, level-end, won.")
(defvar haskellpy-trainer--answer-start nil "Marker: where the answer area begins.")
(defvar haskellpy-trainer--round 1 "Fade rep (1..haskellpy-trainer-fade-steps) for the card on the table.")
(defvar haskellpy-trainer--last-gave-up nil "Whether the most recent rep ended in a give-up.")

;; ---------------------------------------------------------------- parsing

(defun haskellpy-trainer--split-prompt (line)
  "The part of definition LINE the player is shown, or nil if not a definition."
  (when (string-match
         (concat "\\`\\(?:def [A-Za-z_][A-Za-z0-9_]*(" ; def name(
                 "\\|class [A-Za-z_][A-Za-z0-9_]*[(:]" ; class name( / class name:
                 "\\|[A-Za-z_][A-Za-z0-9_]* *= *lambda ?" ; name = lambda
                 "\\|[A-Za-z_][A-Za-z0-9_]* *= *\\)") ; name =
         line)
    (match-string 0 line)))

(defun haskellpy-trainer--parse ()
  "Read `haskellpy-trainer-file' into a vector of levels."
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
        (insert-file-contents haskellpy-trainer-file)
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
             ((string-match "\\`# [0-9]+\\. \\(.+\\)\\'" line)
              ;; capture BEFORE close-block/close-section: their regexp
              ;; calls clobber the match data (bites when a header
              ;; directly follows a definition with no blank line)
              (let ((name (match-string 1 line)))
                (close-block)
                (close-section)
                (setq section name)))
             ((and block (string-match "\\`[ \t]+[^ \t]" line))
              (push line (cdr block)))
             (t
              (close-block)
              (let ((prompt (and section (haskellpy-trainer--split-prompt line))))
                (when prompt
                  (setq block (list prompt line)))))))
          (forward-line 1))
        (close-block)
        (close-section)))
    (vconcat (nreverse levels))))

(defun haskellpy-trainer--normalize (code)
  "CODE with comments, blank lines and all whitespace removed."
  (mapconcat #'identity
             (delq nil (mapcar (lambda (line)
                                 (let ((s (replace-regexp-in-string
                                           "[ \t]" "" (car (split-string line "#")))))
                                   (and (not (string-empty-p s)) s)))
                               (split-string code "\n")))
             "\n"))

(defun haskellpy-trainer--shuffle (list)
  (let ((v (vconcat list)))
    (cl-loop for i from (1- (length v)) downto 1
             do (cl-rotatef (aref v i) (aref v (random (1+ i)))))
    (append v nil)))

;; ---------------------------------------------------------------- fading

(defun haskellpy-trainer--blind-p ()
  "Whether the current rep is the final, unhinted, graded one."
  (or (<= haskellpy-trainer-fade-steps 1)
      (= haskellpy-trainer--round haskellpy-trainer-fade-steps)))

(defun haskellpy-trainer--opacity ()
  "How solid the hint is on the current rep: 1.0 full, 0.0 invisible."
  (if (<= haskellpy-trainer-fade-steps 1)
      0.0
    (- 1.0 (/ (float (1- haskellpy-trainer--round)) (1- haskellpy-trainer-fade-steps)))))

(defun haskellpy-trainer--face-rgb (attribute fallback)
  "The current frame's ATTRIBUTE of the default face as an (R G B) list,
or FALLBACK's if the frame has no color set (e.g. batch mode)."
  (or (color-name-to-rgb (face-attribute 'default attribute nil t))
      (color-name-to-rgb fallback)))

(defun haskellpy-trainer--fade-color (opacity)
  "A foreground color OPACITY of the way from the background to the
default foreground, as a hex string."
  (cl-destructuring-bind (fr fg fb) (haskellpy-trainer--face-rgb :foreground "white")
    (cl-destructuring-bind (br bg bb) (haskellpy-trainer--face-rgb :background "black")
      (color-rgb-to-hex (+ (* opacity fr) (* (- 1 opacity) br))
                         (+ (* opacity fg) (* (- 1 opacity) bg))
                         (+ (* opacity fb) (* (- 1 opacity) bb))
                         2))))

(defun haskellpy-trainer--insert-hint ()
  "Show the fading solution above the prompt, at the current rep's opacity."
  (haskellpy-trainer--insert
   (list :foreground (haskellpy-trainer--fade-color (haskellpy-trainer--opacity)))
   (nth 2 haskellpy-trainer--item))
  (insert "\n\n"))

;; ---------------------------------------------------------------- progress

(defun haskellpy-trainer--load-progress ()
  (setq haskellpy-trainer--unlocked
        (or (ignore-errors
              (with-temp-buffer
                (insert-file-contents haskellpy-trainer-progress-file)
                (plist-get (read (current-buffer)) :unlocked)))
            1)))

(defun haskellpy-trainer--save-progress ()
  (with-temp-file haskellpy-trainer-progress-file
    (prin1 (list :unlocked haskellpy-trainer--unlocked) (current-buffer))))

;; ---------------------------------------------------------------- mode

(defvar haskellpy-trainer-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "C-c C-c") #'haskellpy-trainer-check)
    (define-key map (kbd "C-c C-r") #'haskellpy-trainer-give-up)
    (define-key map (kbd "C-c C-q") #'haskellpy-trainer-quit)
    map)
  "Keys while typing an answer.")

(defvar haskellpy-trainer-menu-map
  (let ((map (make-sparse-keymap)))
    (set-keymap-parent map special-mode-map)
    (define-key map (kbd "SPC") #'haskellpy-trainer-next)
    (define-key map (kbd "RET") #'haskellpy-trainer-next)
    (define-key map "n" #'haskellpy-trainer-new-game)
    (define-key map "r" #'haskellpy-trainer-replay)
    (define-key map "l" #'haskellpy-trainer-choose-level)
    (define-key map "q" #'haskellpy-trainer-quit)
    map)
  "Keys between cards and between levels.")

(define-derived-mode haskellpy-trainer-mode python-mode "HaskellPy"
  "Major mode for the haskell.py typing game.

While typing an answer:
\\{haskellpy-trainer-mode-map}
Between cards and levels:
\\{haskellpy-trainer-menu-map}"
  (setq-local header-line-format '(:eval (haskellpy-trainer--header-line)))
  (setq-local truncate-lines nil))

(defcustom haskellpy-trainer-progress-bar-width 20
  "Width, in characters, of the whole-library progress bar in the header line."
  :type 'integer)

(defun haskellpy-trainer--progress-bar (fraction)
  "A block-character progress bar FRACTION (0.0-1.0) full,
`haskellpy-trainer-progress-bar-width' characters wide."
  (let* ((width haskellpy-trainer-progress-bar-width)
         (filled (round (* fraction width))))
    (concat "[" (make-string filled ?\N{U+2588}) (make-string (- width filled) ?\N{U+2591}) "]")))

(defun haskellpy-trainer--overall-progress ()
  "Fraction of the whole library cleared: levels unlocked beyond the
current one, plus this level's progress through its cards."
  (let* ((nlevels (length haskellpy-trainer--levels))
         (cleared (1- haskellpy-trainer--unlocked))
         (in-level (if (zerop haskellpy-trainer--total)
                       0.0
                     (/ (float (- haskellpy-trainer--total (length haskellpy-trainer--queue)))
                        haskellpy-trainer--total))))
    (min 1.0 (/ (+ cleared in-level) (float nlevels)))))

(defun haskellpy-trainer--header-line ()
  (let* ((nlevels (length haskellpy-trainer--levels))
         (fraction (if (eq haskellpy-trainer--state 'won) 1.0 (haskellpy-trainer--overall-progress)))
         (bar (format " %s %d%%  (%d/%d levels unlocked)"
                      (haskellpy-trainer--progress-bar fraction)
                      (round (* 100 fraction))
                      (min haskellpy-trainer--unlocked nlevels) nlevels)))
    (if (eq haskellpy-trainer--state 'won)
        (format " HaskellPy Trainer  %s   all %d levels cleared" bar nlevels)
      (format " HaskellPy Trainer  %s   Level %d/%d  %s   card %d/%d   rep %d/%d   correct %d   missed %d"
              bar
              haskellpy-trainer--level nlevels
              (haskellpy-trainer--level-name haskellpy-trainer--level)
              (- haskellpy-trainer--total (length haskellpy-trainer--queue))
              haskellpy-trainer--total
              haskellpy-trainer--round haskellpy-trainer-fade-steps
              haskellpy-trainer--hits (length haskellpy-trainer--misses)))))

(defun haskellpy-trainer--level-name (n)
  (car (aref haskellpy-trainer--levels (1- n))))

(defun haskellpy-trainer--level-items (n)
  (cdr (aref haskellpy-trainer--levels (1- n))))

(defun haskellpy-trainer--insert (face &rest strings)
  "Insert STRINGS, shown in FACE (an overlay, so font-lock leaves it alone)."
  (let ((beg (point)))
    (apply #'insert strings)
    (when face
      (overlay-put (make-overlay beg (point)) 'face face))))

(defun haskellpy-trainer--clear ()
  (let ((inhibit-read-only t))
    (remove-overlays)
    (erase-buffer))
  (setq buffer-read-only nil))

(defun haskellpy-trainer--menu-phase ()
  (setq buffer-read-only t)
  (use-local-map haskellpy-trainer-menu-map)
  (goto-char (point-min)))

;; ---------------------------------------------------------------- play

;;;###autoload
(defun haskellpy-trainer ()
  "Play the haskell.py typing game: 17 levels, perfect score to advance."
  (interactive)
  (setq haskellpy-trainer--levels (haskellpy-trainer--parse))
  (when (zerop (length haskellpy-trainer--levels))
    (error "No sections found in %s" haskellpy-trainer-file))
  (haskellpy-trainer--load-progress)
  (switch-to-buffer haskellpy-trainer-buffer-name)
  (unless (derived-mode-p 'haskellpy-trainer-mode)
    ;; A game buffer, not a source file: keep linters, LSP and line
    ;; numbers from the user's Python hooks out of it.
    (let ((python-mode-hook nil)
          (prog-mode-hook nil)
          (python-indent-guess-indent-offset nil))
      (haskellpy-trainer-mode)))
  (haskellpy-trainer--start-level (min haskellpy-trainer--unlocked
                                     (length haskellpy-trainer--levels))))

(defun haskellpy-trainer-new-game ()
  "Start over at the highest unlocked level."
  (interactive)
  (haskellpy-trainer))

(defun haskellpy-trainer--start-level (n)
  (setq haskellpy-trainer--level n
        haskellpy-trainer--queue (haskellpy-trainer--shuffle (haskellpy-trainer--level-items n))
        haskellpy-trainer--total (length haskellpy-trainer--queue)
        haskellpy-trainer--hits 0
        haskellpy-trainer--misses nil)
  (haskellpy-trainer--deal-card))

(defun haskellpy-trainer--deal-card ()
  "Pop the next card from the queue and start its fade cycle at rep 1."
  (setq haskellpy-trainer--item (pop haskellpy-trainer--queue)
        haskellpy-trainer--round 1)
  (haskellpy-trainer--deal-round))

(defun haskellpy-trainer--deal-round ()
  "(Re)present the card on the table at the current fade rep."
  (let ((prompt (nth 1 haskellpy-trainer--item)))
    (setq haskellpy-trainer--state 'typing)
    (haskellpy-trainer--clear)
    (use-local-map haskellpy-trainer-mode-map)
    (haskellpy-trainer--insert 'bold (format "Level %d: %s" haskellpy-trainer--level
                                          (haskellpy-trainer--level-name haskellpy-trainer--level)))
    (haskellpy-trainer--insert 'font-lock-comment-face
                             (format "   card %d of %d   rep %d/%d\n"
                                     (- haskellpy-trainer--total (length haskellpy-trainer--queue))
                                     haskellpy-trainer--total
                                     haskellpy-trainer--round haskellpy-trainer-fade-steps))
    (haskellpy-trainer--insert
     'font-lock-comment-face
     (if (haskellpy-trainer--blind-p)
         "Finish the definition from memory.   C-c C-c check   C-c C-r give up   C-c C-q quit\n\n"
       "Retype the definition shown below.   C-c C-c check   C-c C-q quit\n\n"))
    (unless (haskellpy-trainer--blind-p)
      (haskellpy-trainer--insert-hint))
    (insert prompt)
    (let ((end (point))
          (inhibit-read-only t))
      (put-text-property (point-min) end 'read-only t)
      (put-text-property (point-min) (1+ (point-min)) 'front-sticky t)
      (put-text-property (1- end) end 'rear-nonsticky t)
      (setq haskellpy-trainer--answer-start (copy-marker end)))))

(defun haskellpy-trainer--attempt ()
  (buffer-substring-no-properties haskellpy-trainer--answer-start (point-max)))

(defun haskellpy-trainer--expected ()
  (substring (nth 2 haskellpy-trainer--item) (length (nth 1 haskellpy-trainer--item))))

(defun haskellpy-trainer-check ()
  "Check the answer typed under the prompt.  A correct answer needs no
review: it just updates the score and moves straight on.  A wrong answer
shows what haskell.py actually has, and waits for SPC."
  (interactive)
  (unless (eq haskellpy-trainer--state 'typing)
    (user-error "No card on the table"))
  (let ((attempt (haskellpy-trainer--attempt)))
    (if (string= (haskellpy-trainer--normalize attempt)
                 (haskellpy-trainer--normalize (haskellpy-trainer--expected)))
        (haskellpy-trainer--advance)
      (haskellpy-trainer--show-result nil))))

(defun haskellpy-trainer-give-up ()
  "Give up on this rep: the answer is shown, and (only on the blind rep)
it counts as a miss."
  (interactive)
  (unless (eq haskellpy-trainer--state 'typing)
    (user-error "No card on the table"))
  (haskellpy-trainer--show-result t))

(defun haskellpy-trainer--advance ()
  "A correct check: record the hit (if this was the blind rep) and move
straight to the next rep, card, or level, with no review screen."
  (when (haskellpy-trainer--blind-p)
    (cl-incf haskellpy-trainer--hits))
  (if (haskellpy-trainer--blind-p)
      (if haskellpy-trainer--queue (haskellpy-trainer--deal-card) (haskellpy-trainer--level-end))
    (cl-incf haskellpy-trainer--round)
    (haskellpy-trainer--deal-round)))

(defun haskellpy-trainer--show-result (gave-up)
  "Show the miss/give-up screen for a wrong or given-up rep."
  (setq haskellpy-trainer--state 'shown
        haskellpy-trainer--last-gave-up gave-up)
  (when (haskellpy-trainer--blind-p)
    (push (car haskellpy-trainer--item) haskellpy-trainer--misses))
  (let ((inhibit-read-only t))
    (goto-char (point-max))
    (unless (bolp) (insert "\n"))
    (insert "\n")
    (haskellpy-trainer--insert 'error
                             (if gave-up "Gave up.  haskell.py has:\n\n" "Miss.  haskell.py has:\n\n"))
    (insert (nth 2 haskellpy-trainer--item) "\n")
    (haskellpy-trainer--insert
     'font-lock-comment-face
     (cond
      ((and (not gave-up) (not (haskellpy-trainer--blind-p)))
       "\nSPC  try this rep again     q  quit\n")
      ((haskellpy-trainer--blind-p)
       (if haskellpy-trainer--queue "\nSPC  next card     q  quit\n" "\nSPC  level result  q  quit\n"))
      (t "\nSPC  next rep, less shown     q  quit\n"))))
  (haskellpy-trainer--menu-phase)
  (goto-char (point-max)))

(defun haskellpy-trainer-next ()
  "Continue after a miss/give-up screen: retry this rep, fade to the next
rep, next card, level result, or the next level."
  (interactive)
  (pcase haskellpy-trainer--state
    ('shown
     (cond
      ;; Wrong (not given up) on a hinted rep: repeat it at the same fade level.
      ((and (not haskellpy-trainer--last-gave-up) (not (haskellpy-trainer--blind-p)))
       (haskellpy-trainer--deal-round))
      ;; The blind rep just finished (wrong or given up): next card, or end the level.
      ((haskellpy-trainer--blind-p)
       (if haskellpy-trainer--queue (haskellpy-trainer--deal-card) (haskellpy-trainer--level-end)))
      ;; Given up on a hinted rep: fade it further.
      (t (cl-incf haskellpy-trainer--round) (haskellpy-trainer--deal-round))))
    ('level-end (haskellpy-trainer--start-level
                 (min haskellpy-trainer--unlocked (length haskellpy-trainer--levels))))
    ('won (haskellpy-trainer-choose-level))
    (_ (user-error "Type your answer, then C-c C-c"))))

(defun haskellpy-trainer--level-end ()
  (let* ((n haskellpy-trainer--total)
         (nlevels (length haskellpy-trainer--levels))
         (perfect (= haskellpy-trainer--hits n))
         (last (= haskellpy-trainer--level nlevels))
         (next (1+ haskellpy-trainer--level)))
    (when (and perfect (> next haskellpy-trainer--unlocked) (not last))
      (setq haskellpy-trainer--unlocked next)
      (haskellpy-trainer--save-progress))
    (haskellpy-trainer--clear)
    (cond
     ((and perfect last)
      (setq haskellpy-trainer--state 'won)
      (haskellpy-trainer--insert 'success
                               (format "\n   *** LEVEL %d CLEARED -- %d/%d ***\n\n" haskellpy-trainer--level n n))
      (haskellpy-trainer--insert 'bold
                               (format "   You have typed the whole of haskell.py from memory.  All %d levels cleared.\n\n" nlevels))
      (haskellpy-trainer--insert 'font-lock-comment-face
                               "   l  replay any level     n  new game     q  quit\n"))
     (perfect
      (setq haskellpy-trainer--state 'level-end)
      (haskellpy-trainer--insert 'success
                               (format "\n   *** LEVEL %d CLEARED -- %d/%d perfect! ***\n\n" haskellpy-trainer--level n n))
      (haskellpy-trainer--insert 'bold
                               (format "   Level %d unlocked: %s (%d cards)\n\n"
                                       next (haskellpy-trainer--level-name next)
                                       (length (haskellpy-trainer--level-items next))))
      (haskellpy-trainer--insert 'font-lock-comment-face
                               (format "   SPC  play level %d     r  replay level %d     l  choose level     q  quit\n"
                                       next haskellpy-trainer--level)))
     (t
      (setq haskellpy-trainer--state 'level-end)
      (haskellpy-trainer--insert 'error
                               (format "\n   Level %d: %d/%d.  " haskellpy-trainer--level haskellpy-trainer--hits n))
      (haskellpy-trainer--insert 'bold
                               "Missed: " (mapconcat #'identity (reverse haskellpy-trainer--misses) ", ") "\n\n")
      (insert "   A perfect score is needed to clear the level.\n\n")
      (haskellpy-trainer--insert 'font-lock-comment-face
                               (format "   SPC  try level %d again     l  choose level     q  quit\n"
                                       haskellpy-trainer--level))))
    (haskellpy-trainer--menu-phase)))

(defun haskellpy-trainer-replay ()
  "Play the current level again from the start."
  (interactive)
  (haskellpy-trainer--start-level haskellpy-trainer--level))

(defun haskellpy-trainer-choose-level ()
  "Play any level up to the highest unlocked one."
  (interactive)
  (let* ((top (min haskellpy-trainer--unlocked (length haskellpy-trainer--levels)))
         (n (read-number (format "Level (1-%d): " top) top)))
    (unless (<= 1 n top)
      (user-error "Level %d is not unlocked yet" n))
    (haskellpy-trainer--start-level n)))

(defun haskellpy-trainer-quit ()
  "Leave the game.  Cleared levels are already saved."
  (interactive)
  (quit-window))

(defun haskellpy-trainer-reset ()
  "Forget all progress: lock every level but the first."
  (interactive)
  (when (yes-or-no-p "Forget all haskellpy-trainer progress? ")
    (setq haskellpy-trainer--unlocked 1)
    (haskellpy-trainer--save-progress)
    (message "Progress reset")))

(provide 'haskellpy-trainer)
;;; haskellpy-trainer.el ends here
