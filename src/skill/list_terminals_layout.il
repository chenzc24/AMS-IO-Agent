
;; list_terminals_layout.il - List terminals in layout cellview
(let ((cv (dbOpenCellViewByType "llm_test" "testv1" "layout" "" "r"))
      (names '()))
  (when cv
    (foreach term (cv~>terminals)
      (setq names (cons (term~>name) names)))
    (printf "Layout terminal names: %L\n" names)
    (dbClose cv)
    names))
