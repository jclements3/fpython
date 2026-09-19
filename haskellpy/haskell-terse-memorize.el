;;; haskell-terse-memorize.el --- Quiz haskell-terse.py one SECTION at a time, with fading cues -*- lexical-binding: t; -*-

;; Reuses the haskellpy-trainer engine unchanged -- same fading, grading,
;; and level gating -- but with a different card shape: where
;; haskellpy-memorize deals one card per DEFINITION (so a section/level
;; can have many small cards), this deals exactly ONE card per SECTION,
;; whose target is the section's entire code block. You must reproduce
;; the whole section from memory (blind) to clear its level and unlock
;; the next one -- the same 17 sections, same order, same fade-steps
;; cycle, just one big card per level instead of many small ones.
;;
;;   M-x haskell-terse-memorize          play (also: resume inside its buffer)
;;   M-x haskell-terse-memorize-reset    forget this mode's progress only

(require 'haskellpy-trainer)

(defcustom haskell-terse-memorize-file
  (expand-file-name "haskell-terse.py"
                    (file-name-directory
                     (file-truename (or load-file-name buffer-file-name
                                        default-directory))))
  "Path to haskell-terse.py, the file quizzed one section at a time.
\(symlinks resolved, so this file may live in a load-path directory)."
  :type 'file :group 'haskellpy-trainer)

(defcustom haskell-terse-memorize-progress-file
  (locate-user-emacs-file "haskell-terse-memorize-progress")
  "Where this mode's progress is saved (separate from the trainer's and
from haskellpy-memorize's -- clearing one does not affect the others)."
  :type 'file :group 'haskellpy-trainer)

(defconst haskell-terse-memorize-buffer-name "*HaskellTerseSectionQuiz*")

(defvar haskell-terse-memorize--orig
  (list haskellpy-trainer-file haskellpy-trainer-progress-file haskellpy-trainer-buffer-name)
  "Trainer settings as they were before this flavor took over.")

(defun haskell-terse-memorize--section-marker (line)
  "The (NUM . NAME) a `# NUM. NAME' section-header LINE names, or nil."
  (when (string-match "\\`# \\([0-9]+\\)\\. \\(.+\\)\\'" line)
    (cons (match-string 1 line) (match-string 2 line))))

(defun haskell-terse-memorize--parse ()
  "Read `haskell-terse-memorize-file' into a vector of levels, ONE CARD
PER SECTION: the card's prompt is the section's own `# NUM. NAME' header
line, and its target is the header plus the section's entire code,
verbatim. Text before the first header (the import lines) belongs to no
section and is not quizzed, matching how haskellpy-trainer's own
per-definition parser already treats that preamble."
  (let (levels name header lines)
    (cl-flet ((close ()
                (when name
                  (let ((code (mapconcat #'identity
                                         (cons header (nreverse lines)) "\n")))
                    (push (cons name (list (list name header code))) levels)))
                (setq lines nil)))
      (with-temp-buffer
        (insert-file-contents haskell-terse-memorize-file)
        (goto-char (point-min))
        (while (not (eobp))
          (let* ((line (buffer-substring-no-properties
                        (line-beginning-position) (line-end-position)))
                 (marker (haskell-terse-memorize--section-marker line)))
            (if marker
                (progn (close) (setq name (cdr marker) header line))
              (when name (push line lines))))
          (forward-line 1))
        (close)))
    (vconcat (nreverse levels))))

(defun haskell-terse-memorize--restore (&rest _)
  "Hand the engine back to the plain trainer's own defaults, but only when
the user invoked bare `haskellpy-trainer' directly."
  (when (eq this-command 'haskellpy-trainer)
    (setq haskellpy-trainer-file (nth 0 haskell-terse-memorize--orig)
          haskellpy-trainer-progress-file (nth 1 haskell-terse-memorize--orig)
          haskellpy-trainer-buffer-name (nth 2 haskell-terse-memorize--orig))))
(advice-add 'haskellpy-trainer :before #'haskell-terse-memorize--restore)

(advice-add 'haskellpy-trainer--parse :around
  (lambda (orig-fn &rest args)
    "Use the one-card-per-section parser only while THIS flavor is active
\(recognised by its own buffer name -- haskellpy-memorize points at the
same haskell-terse.py file, so the file path alone can't tell them apart)."
    (if (string= haskellpy-trainer-buffer-name haskell-terse-memorize-buffer-name)
        (haskell-terse-memorize--parse)
      (apply orig-fn args))))

;;;###autoload
(defun haskell-terse-memorize ()
  "Quiz haskell-terse.py one section at a time: each of the 17 sections is
one big fading-cue card. Get it right blind to unlock the next section."
  (interactive)
  (setq haskellpy-trainer-file haskell-terse-memorize-file
        haskellpy-trainer-progress-file haskell-terse-memorize-progress-file
        haskellpy-trainer-buffer-name haskell-terse-memorize-buffer-name)
  (haskellpy-trainer))

;;;###autoload
(defun haskell-terse-memorize-reset ()
  "Forget this mode's progress (the trainer's and haskellpy-memorize's own
progress are each untouched)."
  (interactive)
  (let ((haskellpy-trainer-progress-file haskell-terse-memorize-progress-file))
    (haskellpy-trainer-reset)))

(provide 'haskell-terse-memorize)
;;; haskell-terse-memorize.el ends here
