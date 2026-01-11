
;; list_labels2.il - List all labels in layout
(let ((cv (dbOpenCellViewByType "llm_test" "testv1" "layout" "" "a"))
      (labelTexts nil))
  (when cv
    (foreach label cv~>labels
      (setq labelTexts (cons label~>text labelTexts)))
    (dbClose cv)
    labelTexts))
