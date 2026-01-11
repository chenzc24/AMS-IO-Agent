
;; list_all_labels.il - List all labels in layout
(let ((cv (dbOpenCellViewByType "llm_test" "testv1" "layout" "" "r"))
      (labelList nil))
  (when cv
    (foreach label cv~>labels
      (setq labelList (cons (list label~>layer label~>bBox label~>text) labelList)))
    (dbClose cv)
    labelList))
