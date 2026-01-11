
;; list_label_shapes.il - List shapes with purpose "drawing" that have text
(let ((cv (dbOpenCellViewByType "llm_test" "testv1" "layout" "" "a"))
      (labelInfo nil))
  (when cv
    (foreach shape cv~>shapes
      (when (and (equal shape~>purpose "drawing") shape~>text)
        (setq labelInfo (cons (list shape~>layer shape~>bBox shape~>text) labelInfo))))
    (dbClose cv)
    labelInfo))
