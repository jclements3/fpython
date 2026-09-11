;;; ps-print-sources.el --- print source files to PostScript, in color  -*- lexical-binding: t; -*-

;; Driven by make_prints.py; not meant to be loaded interactively.
;; Prints each file named in the PSPRINT_FILES environment variable
;; (space-separated paths) to <file>.ps beside it, the way
;; `ps-print-buffer-with-faces' does from a running Emacs: A4, line
;; numbers, two-line header, faces from the adwaita theme.
;;
;; Needs a display for color -- ps-print turns color off on a tty, and
;; batch Emacs maps hex colors onto an 8-color palette -- so make_prints.py
;; runs this under xvfb-run:
;;
;;     PSPRINT_FILES="prelude.py" xvfb-run -a emacs -Q -l ps-print-sources.el

(require 'ps-print)
(require 'python)

(load-theme 'adwaita t)

(setq ps-paper-type 'a4
      ps-line-number t
      ps-font-size 7.5                      ; 105-column source fits unwrapped
      ps-print-color-p t
      ps-header-lines 2
      ps-left-header (list 'ps-get-buffer-name 'ps-header-dirpart)
      ps-right-header (list "/pagenumberstring load"
                            (lambda () (format-time-string "%m/%d/%y"))))

(dolist (f (split-string (or (getenv "PSPRINT_FILES") "")))
  (find-file f)
  (delay-mode-hooks (python-mode))          ; highlight without the user's hooks
  (font-lock-ensure)
  (ps-print-buffer-with-faces (concat (file-name-sans-extension f) ".ps")))

(kill-emacs 0)
;;; ps-print-sources.el ends here
