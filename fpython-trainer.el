;;; fpython-trainer.el --- Type the prelude from memory, in 15 levels -*- lexical-binding: t; -*-

;; A memory game over prelude.py, in the spirit of the games in lisp/play
;; (tetris, 5x5, mpuz).  Each of the 15 sections of the prelude is a level.
;; A card shows the left-hand side of one definition --
;;
;;     head      = lambda            def isqrt(
;;
;; -- and you type the rest.  Every card in a level must be answered
;; correctly, first try, to clear the level and unlock the next one.
;; Anything less and you replay the level.  Cleared levels are remembered
;; between sessions.
;;
;;   M-x fpython-trainer          play (starts at the highest unlocked level)
;;   M-x fpython-trainer-reset    forget all progress
;;
;; Comments, spacing and indentation are ignored when checking an answer;
;; the code has to match.

;;; Code:

(require 'cl-lib)
(require 'python)

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

(defun fpython-trainer--header-line ()
  (if (eq fpython-trainer--state 'won)
      (format " FPython Trainer   all %d levels cleared" (length fpython-trainer--levels))
    (format " FPython Trainer   Level %d/%d  %s   card %d/%d   correct %d   missed %d"
            fpython-trainer--level (length fpython-trainer--levels)
            (fpython-trainer--level-name fpython-trainer--level)
            (- fpython-trainer--total (length fpython-trainer--queue))
            fpython-trainer--total
            fpython-trainer--hits (length fpython-trainer--misses))))

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
  "Play the prelude typing game: 15 levels, perfect score to advance."
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
  (fpython-trainer--deal))

(defun fpython-trainer--deal ()
  "Put the next card on the table."
  (let* ((item (pop fpython-trainer--queue))
         (prompt (nth 1 item)))
    (setq fpython-trainer--item item
          fpython-trainer--state 'typing)
    (fpython-trainer--clear)
    (use-local-map fpython-trainer-mode-map)
    (fpython-trainer--insert 'bold (format "Level %d: %s" fpython-trainer--level
                                          (fpython-trainer--level-name fpython-trainer--level)))
    (fpython-trainer--insert 'font-lock-comment-face
                             (format "   card %d of %d\n"
                                     (- fpython-trainer--total (length fpython-trainer--queue))
                                     fpython-trainer--total))
    (fpython-trainer--insert 'font-lock-comment-face
                             "Finish the definition.   C-c C-c check   C-c C-r give up   C-c C-q quit\n\n")
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
  "Check the answer typed under the prompt."
  (interactive)
  (unless (eq fpython-trainer--state 'typing)
    (user-error "No card on the table"))
  (let ((attempt (fpython-trainer--attempt)))
    (fpython-trainer--show-result
     (string= (fpython-trainer--normalize attempt)
              (fpython-trainer--normalize (fpython-trainer--expected))))))

(defun fpython-trainer-give-up ()
  "Give up on this card: it counts as a miss and the answer is shown."
  (interactive)
  (unless (eq fpython-trainer--state 'typing)
    (user-error "No card on the table"))
  (fpython-trainer--show-result nil))

(defun fpython-trainer--show-result (ok)
  (setq fpython-trainer--state 'shown)
  (if ok
      (cl-incf fpython-trainer--hits)
    (push (car fpython-trainer--item) fpython-trainer--misses))
  (let ((inhibit-read-only t))
    (goto-char (point-max))
    (unless (bolp) (insert "\n"))
    (insert "\n")
    (if ok
        (fpython-trainer--insert 'success "Correct!\n")
      (fpython-trainer--insert 'error "Miss.  The prelude has:\n\n")
      (insert (nth 2 fpython-trainer--item) "\n"))
    (fpython-trainer--insert 'font-lock-comment-face
                             (if fpython-trainer--queue
                                 "\nSPC  next card     q  quit\n"
                               "\nSPC  level result  q  quit\n")))
  (fpython-trainer--menu-phase)
  (goto-char (point-max)))

(defun fpython-trainer-next ()
  "Continue: next card, level result, or the next level."
  (interactive)
  (pcase fpython-trainer--state
    ('shown (if fpython-trainer--queue
                (fpython-trainer--deal)
              (fpython-trainer--level-end)))
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
