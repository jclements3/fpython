;;; haskellpy-memorize.el --- fading-source memorization of haskell.py, terse form  -*- lexical-binding: t; -*-
;; Drills haskell-terse.py: haskell.py with docstrings, comments, alignment
;; padding and the __main__ block stripped -- exactly the keystrokes worth
;; memorizing (section headers are kept: they are the level structure).
;; Reuses the haskellpy-trainer engine unchanged -- same fading, grading and
;; level gating -- with its own target, buffer and progress file.
;;
;;   M-x haskellpy-memorize          play (also: resume inside its buffer)
;;   M-x haskellpy-memorize-reset    forget memorization progress only

(require 'haskellpy-trainer)

(defcustom haskellpy-memorize-file
  (expand-file-name "haskell-terse.py"
                    (file-name-directory
                     (file-truename (or load-file-name buffer-file-name
                                        default-directory))))
  "Path to haskell-terse.py, the memorization target.
\(symlinks resolved, so the file may live in a load-path directory)."
  :type 'file :group 'haskellpy-trainer)

(defcustom haskellpy-memorize-progress-file
  (locate-user-emacs-file "haskellpy-memorize-progress")
  "Where memorization progress is saved (separate from the trainer's)."
  :type 'file :group 'haskellpy-trainer)

(defconst haskellpy-memorize-buffer-name "*HaskellPyMemorize*")

(defvar haskellpy-memorize--orig
  (list haskellpy-trainer-file haskellpy-trainer-progress-file haskellpy-trainer-buffer-name)
  "Trainer settings as they were before memorize took over.")

;;;###autoload
(defun haskellpy-memorize ()
  "Type haskell.py from memory, terse form, with fading cues."
  (interactive)
  (setq haskellpy-trainer-file haskellpy-memorize-file
        haskellpy-trainer-progress-file haskellpy-memorize-progress-file
        haskellpy-trainer-buffer-name haskellpy-memorize-buffer-name)
  (haskellpy-trainer))

(defun haskellpy-memorize--restore (&rest _)
  "Hand the engine back to the plain trainer, unless memorize is driving."
  (unless (or (eq this-command 'haskellpy-memorize)
              (string= (buffer-name) haskellpy-memorize-buffer-name))
    (setq haskellpy-trainer-file (nth 0 haskellpy-memorize--orig)
          haskellpy-trainer-progress-file (nth 1 haskellpy-memorize--orig)
          haskellpy-trainer-buffer-name (nth 2 haskellpy-memorize--orig))))
(advice-add 'haskellpy-trainer :before #'haskellpy-memorize--restore)

;;;###autoload
(defun haskellpy-memorize-reset ()
  "Forget memorization progress (the trainer's own progress is untouched)."
  (interactive)
  (let ((haskellpy-trainer-progress-file haskellpy-memorize-progress-file))
    (haskellpy-trainer-reset)))

(provide 'haskellpy-memorize)
;;; haskellpy-memorize.el ends here
