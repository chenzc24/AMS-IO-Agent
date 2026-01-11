
;; list_terminals_names.il - List terminal names
(let ((cv (geGetEditCellView))
      (names '()))
  (when cv
    (foreach term (cv~>terminals)
      (setq names (cons (term~>name) names)))
    (printf "Terminal names: %L\n" names)
    names))
