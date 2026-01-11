
;; list_pins_layout.il - List pins in layout cellview
(let ((cv (dbOpenCellViewByType "llm_test" "testv1" "layout" "" "r"))
      (pins '()))
  (when cv
    (foreach shape (cv~>shapes)
      (when (and (shape~>objType == "label") (equal (shape~>purpose) "pin"))
        (setq pins (cons (shape~>theLabel) pins))))
    (printf "Layout pin labels: %L\n" pins)
    (dbClose cv)
    pins))
