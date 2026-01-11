
;; get_pin_shape_info.il - Get pin shape info
(let ((cv (dbOpenCellViewByType "llm_test" "testv1" "layout" "" "a"))
      (pinInfo nil))
  (when cv
    (foreach shape cv~>shapes
      (when (equal shape~>purpose "pin")
        (setq pinInfo (cons (list shape~>layer shape~>bBox shape~>text) pinInfo))))
    (dbClose cv)
    pinInfo))
