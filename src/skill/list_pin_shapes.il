
;; list_pin_shapes.il - List shapes with purpose "pin"
(let ((cv (dbOpenCellViewByType "llm_test" "testv1" "layout" "" "a"))
      (pinShapes nil))
  (when cv
    (foreach shape cv~>shapes
      (when (equal shape~>purpose "pin")
        (setq pinShapes (cons shape pinShapes))))
    (dbClose cv)
    (length pinShapes)))
