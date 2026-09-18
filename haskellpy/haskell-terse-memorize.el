;;; haskell-terse-memorize.el --- Type the whole haskell-terse.py file at once -*- lexical-binding: t; -*-

;; A single-session bulk-typing exercise over haskell-terse.py, distinct
;; from haskellpy-memorize's per-card, per-level fading game: here the
;; WHOLE file is the target, typed in one sitting, with the reference
;; visible in a companion window you can hide once you're ready to go
;; from memory. Comments, blank lines and all per-line leading/trailing
;; whitespace are ignored when checking -- only the code has to match.
;;
;;   M-x haskell-terse-memorize            open the practice buffers
;;   C-c C-c (in the typing buffer)        check your work against the target
;;   C-c C-r (in the typing buffer)        reveal/hide the target window
;;   M-x haskell-terse-memorize-reset      clear the typing buffer, restart timer

;;; Code:

(require 'cl-lib)

(defgroup haskell-terse-memorize nil
  "Type the whole haskell-terse.py file at once."
  :group 'games
  :prefix "haskell-terse-memorize-")

(defcustom haskell-terse-memorize-file
  (expand-file-name "haskell-terse.py"
                    (file-name-directory
                     (file-truename (or load-file-name buffer-file-name
                                        default-directory))))
  "Path to haskell-terse.py, the file typed in one sitting.
\(symlinks resolved, so this file may live in a load-path directory)."
  :type 'file)

(defconst haskell-terse-memorize-buffer-name "*HaskellTerseMemorize*")
(defconst haskell-terse-memorize-target-buffer-name "*HaskellTerseTarget*")

(defvar haskell-terse-memorize--start-time nil
  "When the current typing session started, for the elapsed-time report.")

(defun haskell-terse-memorize--target-text ()
  "The file's current contents, read fresh every time it's needed."
  (with-temp-buffer
    (insert-file-contents haskell-terse-memorize-file)
    (buffer-string)))

(defun haskell-terse-memorize--normalize (text)
  "Strip blank lines and per-line leading/trailing whitespace, so the
comparison cares only about the code, not incidental formatting."
  (mapconcat #'identity
             (cl-remove-if (lambda (l) (string-empty-p (string-trim l)))
                           (mapcar #'string-trim (split-string text "\n")))
             "\n"))

(defvar haskell-terse-memorize-mode-map
  (let ((m (make-sparse-keymap)))
    (define-key m (kbd "C-c C-c") #'haskell-terse-memorize-check)
    (define-key m (kbd "C-c C-r") #'haskell-terse-memorize-toggle-target)
    m)
  "Keymap for `haskell-terse-memorize-mode'.")

(define-minor-mode haskell-terse-memorize-mode
  "Minor mode for the haskell-terse-memorize typing buffer."
  :lighter " HTMemo"
  :keymap haskell-terse-memorize-mode-map)

;;;###autoload
(defun haskell-terse-memorize ()
  "Open a two-window practice session: the target file read-only on top,
an empty buffer to type it into below.  `haskell-terse-memorize-check'
compares what you typed against the target, ignoring whitespace."
  (interactive)
  (unless (file-exists-p haskell-terse-memorize-file)
    (error "No such file: %s" haskell-terse-memorize-file))
  (delete-other-windows)
  (let ((target (get-buffer-create haskell-terse-memorize-target-buffer-name))
        (work (get-buffer-create haskell-terse-memorize-buffer-name)))
    (with-current-buffer target
      (let ((inhibit-read-only t))
        (erase-buffer)
        (insert (haskell-terse-memorize--target-text)))
      (goto-char (point-min))
      (when (fboundp 'python-mode) (python-mode))
      (read-only-mode 1))
    (with-current-buffer work
      (unless (eq major-mode 'python-mode)
        (when (fboundp 'python-mode) (python-mode)))
      (haskell-terse-memorize-mode 1))
    (switch-to-buffer target)
    (split-window-below)
    (other-window 1)
    (switch-to-buffer work)
    (setq haskell-terse-memorize--start-time (current-time))
    (message "Type the whole file below. C-c C-c checks; C-c C-r shows/hides the target.")))

(defun haskell-terse-memorize-toggle-target ()
  "Show or hide the reference target window."
  (interactive)
  (let ((tbuf (get-buffer haskell-terse-memorize-target-buffer-name)))
    (unless tbuf
      (error "No target buffer -- run M-x haskell-terse-memorize first"))
    (let ((w (get-buffer-window tbuf)))
      (if w
          (delete-window w)
        (save-selected-window
          (select-window (split-window-below))
          (switch-to-buffer tbuf))))))

(defun haskell-terse-memorize-check ()
  "Compare the typing buffer against the target, ignoring whitespace.
Reports success (with elapsed time and a line count) or the first line
where the two diverge, plus how many lines matched before that point."
  (interactive)
  (let* ((typed (haskell-terse-memorize--normalize (buffer-string)))
         (target (haskell-terse-memorize--normalize (haskell-terse-memorize--target-text)))
         (tlines (split-string typed "\n"))
         (glines (split-string target "\n")))
    (if (string= typed target)
        (message "Match! %d lines, %.1f minutes."
                 (length glines)
                 (/ (float-time (time-subtract (current-time)
                                               (or haskell-terse-memorize--start-time
                                                   (current-time))))
                    60.0))
      (let ((i 0) (n (min (length tlines) (length glines))))
        (while (and (< i n) (string= (nth i tlines) (nth i glines)))
          (setq i (1+ i)))
        (message "Mismatch at line %d of %d -- got %S, want %S"
                 (1+ i) (length glines)
                 (or (nth i tlines) "") (or (nth i glines) ""))))))

;;;###autoload
(defun haskell-terse-memorize-reset ()
  "Clear the typing buffer and restart the elapsed-time timer."
  (interactive)
  (when (get-buffer haskell-terse-memorize-buffer-name)
    (with-current-buffer haskell-terse-memorize-buffer-name
      (erase-buffer)))
  (setq haskell-terse-memorize--start-time (current-time))
  (message "Cleared. Timer restarted."))

(provide 'haskell-terse-memorize)
;;; haskell-terse-memorize.el ends here
