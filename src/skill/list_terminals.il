
;; list_terminals.il - List terminals in current cellview
(let ((cv (geGetEditCellView)))
  (when cv
    (foreach term (cv~>terminals)
      (printf "Terminal: %s direction: %s\n" (term~>name) (term~>direction)))))
