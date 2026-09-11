;;; prelude-trainer.el --- Type the prelude from memory, in 15 levels -*- lexical-binding: t; -*-

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
;;   M-x prelude-trainer          play (starts at the highest unlocked level)
;;   M-x prelude-trainer-reset    forget all progress
;;
;; Comments, spacing and indentation are ignored when checking an answer;
;; the code has to match.

;;; Code:

(require 'cl-lib)
(require 'python)

(defgroup prelude-trainer nil
  "Type the prelude from memory."
  :group 'games
  :prefix "prelude-trainer-")

(defcustom prelude-trainer-file
  (expand-file-name "prelude.py"
                    (file-name-directory
                     (file-truename (or load-file-name buffer-file-name
                                        default-directory))))
  "The prelude.py to drill.  Defaults to the one beside this file
\(symlinks resolved, so the file may live in a load-path directory)."
  :type 'file)

(defcustom prelude-trainer-progress-file
  (locate-user-emacs-file "prelude-trainer-progress")
  "Where the highest unlocked level is saved."
  :type 'file)

(defconst prelude-trainer-buffer-name "*Prelude*")

;; ---------------------------------------------------------------- state

(defvar prelude-trainer--levels nil
  "Vector of levels; each is (NAME . ITEMS), ITEM is (NAME PROMPT CODE).")
(defvar prelude-trainer--unlocked 1 "Highest level the player may start.")
(defvar prelude-trainer--level 1 "Level being played.")
(defvar prelude-trainer--queue nil "Cards still to be dealt this level.")
(defvar prelude-trainer--item nil "The card on the table.")
(defvar prelude-trainer--total 0 "Cards in this level.")
(defvar prelude-trainer--hits 0 "Cards answered correctly this level.")
(defvar prelude-trainer--misses nil "Names of cards missed this level.")
(defvar prelude-trainer--state 'idle "One of idle, typing, shown, level-end, won.")
(defvar prelude-trainer--answer-start nil "Marker: where the answer area begins.")

;; ---------------------------------------------------------------- parsing

(defun prelude-trainer--split-prompt (line)
  "The part of definition LINE the player is shown, or nil if not a definition."
  (when (string-match
         (concat "\\`\\(?:def [A-Za-z_][A-Za-z0-9_]*(" ; def name(
                 "\\|class [A-Za-z_][A-Za-z0-9_]*[(:]" ; class name( / class name:
                 "\\|[A-Za-z_][A-Za-z0-9_]* *= *lambda ?" ; name = lambda
                 "\\|[A-Za-z_][A-Za-z0-9_]* *= *\\)") ; name =
         line)
    (match-string 0 line)))

(defun prelude-trainer--parse ()
  "Read `prelude-trainer-file' into a vector of levels."
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
        (insert-file-contents prelude-trainer-file)
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
              (let ((prompt (and section (prelude-trainer--split-prompt line))))
                (when prompt
                  (setq block (list prompt line)))))))
          (forward-line 1))
        (close-block)
        (close-section)))
    (vconcat (nreverse levels))))

(defun prelude-trainer--normalize (code)
  "CODE with comments, blank lines and all whitespace removed."
  (mapconcat #'identity
             (delq nil (mapcar (lambda (line)
                                 (let ((s (replace-regexp-in-string
                                           "[ \t]" "" (car (split-string line "#")))))
                                   (and (not (string-empty-p s)) s)))
                               (split-string code "\n")))
             "\n"))

(defun prelude-trainer--shuffle (list)
  (let ((v (vconcat list)))
    (cl-loop for i from (1- (length v)) downto 1
             do (cl-rotatef (aref v i) (aref v (random (1+ i)))))
    (append v nil)))

;; ---------------------------------------------------------------- progress

(defun prelude-trainer--load-progress ()
  (setq prelude-trainer--unlocked
        (or (ignore-errors
              (with-temp-buffer
                (insert-file-contents prelude-trainer-progress-file)
                (plist-get (read (current-buffer)) :unlocked)))
            1)))

(defun prelude-trainer--save-progress ()
  (with-temp-file prelude-trainer-progress-file
    (prin1 (list :unlocked prelude-trainer--unlocked) (current-buffer))))

;; ---------------------------------------------------------------- mode

(defvar prelude-trainer-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "C-c C-c") #'prelude-trainer-check)
    (define-key map (kbd "C-c C-r") #'prelude-trainer-give-up)
    (define-key map (kbd "C-c C-q") #'prelude-trainer-quit)
    map)
  "Keys while typing an answer.")

(defvar prelude-trainer-menu-map
  (let ((map (make-sparse-keymap)))
    (set-keymap-parent map special-mode-map)
    (define-key map (kbd "SPC") #'prelude-trainer-next)
    (define-key map (kbd "RET") #'prelude-trainer-next)
    (define-key map "n" #'prelude-trainer-new-game)
    (define-key map "r" #'prelude-trainer-replay)
    (define-key map "l" #'prelude-trainer-choose-level)
    (define-key map "q" #'prelude-trainer-quit)
    map)
  "Keys between cards and between levels.")

(define-derived-mode prelude-trainer-mode python-mode "Prelude"
  "Major mode for the prelude typing game.

While typing an answer:
\\{prelude-trainer-mode-map}
Between cards and levels:
\\{prelude-trainer-menu-map}"
  (setq-local header-line-format '(:eval (prelude-trainer--header-line)))
  (setq-local truncate-lines nil))

(defun prelude-trainer--header-line ()
  (if (eq prelude-trainer--state 'won)
      (format " Prelude Trainer   all %d levels cleared" (length prelude-trainer--levels))
    (format " Prelude Trainer   Level %d/%d  %s   card %d/%d   correct %d   missed %d"
            prelude-trainer--level (length prelude-trainer--levels)
            (prelude-trainer--level-name prelude-trainer--level)
            (- prelude-trainer--total (length prelude-trainer--queue))
            prelude-trainer--total
            prelude-trainer--hits (length prelude-trainer--misses))))

(defun prelude-trainer--level-name (n)
  (car (aref prelude-trainer--levels (1- n))))

(defun prelude-trainer--level-items (n)
  (cdr (aref prelude-trainer--levels (1- n))))

(defun prelude-trainer--insert (face &rest strings)
  "Insert STRINGS, shown in FACE (an overlay, so font-lock leaves it alone)."
  (let ((beg (point)))
    (apply #'insert strings)
    (when face
      (overlay-put (make-overlay beg (point)) 'face face))))

(defun prelude-trainer--clear ()
  (let ((inhibit-read-only t))
    (remove-overlays)
    (erase-buffer))
  (setq buffer-read-only nil))

(defun prelude-trainer--menu-phase ()
  (setq buffer-read-only t)
  (use-local-map prelude-trainer-menu-map)
  (goto-char (point-min)))

;; ---------------------------------------------------------------- play

;;;###autoload
(defun prelude-trainer ()
  "Play the prelude typing game: 15 levels, perfect score to advance."
  (interactive)
  (setq prelude-trainer--levels (prelude-trainer--parse))
  (when (zerop (length prelude-trainer--levels))
    (error "No sections found in %s" prelude-trainer-file))
  (prelude-trainer--load-progress)
  (switch-to-buffer prelude-trainer-buffer-name)
  (unless (derived-mode-p 'prelude-trainer-mode)
    ;; A game buffer, not a source file: keep linters, LSP and line
    ;; numbers from the user's Python hooks out of it.
    (let ((python-mode-hook nil)
          (prog-mode-hook nil)
          (python-indent-guess-indent-offset nil))
      (prelude-trainer-mode)))
  (prelude-trainer--start-level (min prelude-trainer--unlocked
                                     (length prelude-trainer--levels))))

(defun prelude-trainer-new-game ()
  "Start over at the highest unlocked level."
  (interactive)
  (prelude-trainer))

(defun prelude-trainer--start-level (n)
  (setq prelude-trainer--level n
        prelude-trainer--queue (prelude-trainer--shuffle (prelude-trainer--level-items n))
        prelude-trainer--total (length prelude-trainer--queue)
        prelude-trainer--hits 0
        prelude-trainer--misses nil)
  (prelude-trainer--deal))

(defun prelude-trainer--deal ()
  "Put the next card on the table."
  (let* ((item (pop prelude-trainer--queue))
         (prompt (nth 1 item)))
    (setq prelude-trainer--item item
          prelude-trainer--state 'typing)
    (prelude-trainer--clear)
    (use-local-map prelude-trainer-mode-map)
    (prelude-trainer--insert 'bold (format "Level %d: %s" prelude-trainer--level
                                          (prelude-trainer--level-name prelude-trainer--level)))
    (prelude-trainer--insert 'font-lock-comment-face
                             (format "   card %d of %d\n"
                                     (- prelude-trainer--total (length prelude-trainer--queue))
                                     prelude-trainer--total))
    (prelude-trainer--insert 'font-lock-comment-face
                             "Finish the definition.   C-c C-c check   C-c C-r give up   C-c C-q quit\n\n")
    (insert prompt)
    (let ((end (point))
          (inhibit-read-only t))
      (put-text-property (point-min) end 'read-only t)
      (put-text-property (point-min) (1+ (point-min)) 'front-sticky t)
      (put-text-property (1- end) end 'rear-nonsticky t)
      (setq prelude-trainer--answer-start (copy-marker end)))))

(defun prelude-trainer--attempt ()
  (buffer-substring-no-properties prelude-trainer--answer-start (point-max)))

(defun prelude-trainer--expected ()
  (substring (nth 2 prelude-trainer--item) (length (nth 1 prelude-trainer--item))))

(defun prelude-trainer-check ()
  "Check the answer typed under the prompt."
  (interactive)
  (unless (eq prelude-trainer--state 'typing)
    (user-error "No card on the table"))
  (let ((attempt (prelude-trainer--attempt)))
    (prelude-trainer--show-result
     (string= (prelude-trainer--normalize attempt)
              (prelude-trainer--normalize (prelude-trainer--expected))))))

(defun prelude-trainer-give-up ()
  "Give up on this card: it counts as a miss and the answer is shown."
  (interactive)
  (unless (eq prelude-trainer--state 'typing)
    (user-error "No card on the table"))
  (prelude-trainer--show-result nil))

(defun prelude-trainer--show-result (ok)
  (setq prelude-trainer--state 'shown)
  (if ok
      (cl-incf prelude-trainer--hits)
    (push (car prelude-trainer--item) prelude-trainer--misses))
  (let ((inhibit-read-only t))
    (goto-char (point-max))
    (unless (bolp) (insert "\n"))
    (insert "\n")
    (if ok
        (prelude-trainer--insert 'success "Correct!\n")
      (prelude-trainer--insert 'error "Miss.  The prelude has:\n\n")
      (insert (nth 2 prelude-trainer--item) "\n"))
    (prelude-trainer--insert 'font-lock-comment-face
                             (if prelude-trainer--queue
                                 "\nSPC  next card     q  quit\n"
                               "\nSPC  level result  q  quit\n")))
  (prelude-trainer--menu-phase)
  (goto-char (point-max)))

(defun prelude-trainer-next ()
  "Continue: next card, level result, or the next level."
  (interactive)
  (pcase prelude-trainer--state
    ('shown (if prelude-trainer--queue
                (prelude-trainer--deal)
              (prelude-trainer--level-end)))
    ('level-end (prelude-trainer--start-level
                 (min prelude-trainer--unlocked (length prelude-trainer--levels))))
    ('won (prelude-trainer-choose-level))
    (_ (user-error "Type your answer, then C-c C-c"))))

(defun prelude-trainer--level-end ()
  (let* ((n prelude-trainer--total)
         (nlevels (length prelude-trainer--levels))
         (perfect (= prelude-trainer--hits n))
         (last (= prelude-trainer--level nlevels))
         (next (1+ prelude-trainer--level)))
    (when (and perfect (> next prelude-trainer--unlocked) (not last))
      (setq prelude-trainer--unlocked next)
      (prelude-trainer--save-progress))
    (prelude-trainer--clear)
    (cond
     ((and perfect last)
      (setq prelude-trainer--state 'won)
      (prelude-trainer--insert 'success
                               (format "\n   *** LEVEL %d CLEARED -- %d/%d ***\n\n" prelude-trainer--level n n))
      (prelude-trainer--insert 'bold
                               (format "   You have typed the whole prelude from memory.  All %d levels cleared.\n\n" nlevels))
      (prelude-trainer--insert 'font-lock-comment-face
                               "   l  replay any level     n  new game     q  quit\n"))
     (perfect
      (setq prelude-trainer--state 'level-end)
      (prelude-trainer--insert 'success
                               (format "\n   *** LEVEL %d CLEARED -- %d/%d perfect! ***\n\n" prelude-trainer--level n n))
      (prelude-trainer--insert 'bold
                               (format "   Level %d unlocked: %s (%d cards)\n\n"
                                       next (prelude-trainer--level-name next)
                                       (length (prelude-trainer--level-items next))))
      (prelude-trainer--insert 'font-lock-comment-face
                               (format "   SPC  play level %d     r  replay level %d     l  choose level     q  quit\n"
                                       next prelude-trainer--level)))
     (t
      (setq prelude-trainer--state 'level-end)
      (prelude-trainer--insert 'error
                               (format "\n   Level %d: %d/%d.  " prelude-trainer--level prelude-trainer--hits n))
      (prelude-trainer--insert 'bold
                               "Missed: " (mapconcat #'identity (reverse prelude-trainer--misses) ", ") "\n\n")
      (insert "   A perfect score is needed to clear the level.\n\n")
      (prelude-trainer--insert 'font-lock-comment-face
                               (format "   SPC  try level %d again     l  choose level     q  quit\n"
                                       prelude-trainer--level))))
    (prelude-trainer--menu-phase)))

(defun prelude-trainer-replay ()
  "Play the current level again from the start."
  (interactive)
  (prelude-trainer--start-level prelude-trainer--level))

(defun prelude-trainer-choose-level ()
  "Play any level up to the highest unlocked one."
  (interactive)
  (let* ((top (min prelude-trainer--unlocked (length prelude-trainer--levels)))
         (n (read-number (format "Level (1-%d): " top) top)))
    (unless (<= 1 n top)
      (user-error "Level %d is not unlocked yet" n))
    (prelude-trainer--start-level n)))

(defun prelude-trainer-quit ()
  "Leave the game.  Cleared levels are already saved."
  (interactive)
  (quit-window))

(defun prelude-trainer-reset ()
  "Forget all progress: lock every level but the first."
  (interactive)
  (when (yes-or-no-p "Forget all prelude-trainer progress? ")
    (setq prelude-trainer--unlocked 1)
    (prelude-trainer--save-progress)
    (message "Progress reset")))

(provide 'prelude-trainer)
;;; prelude-trainer.el ends here
