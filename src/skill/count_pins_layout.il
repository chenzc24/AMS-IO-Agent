
;; count_pins_layout.il - Open layout and count pins
(let ((cv (dbOpenCellViewByType "llm_test" "testv1" "layout" "" "r"))
      (pinCount 0))
  (when cv
    (foreach term (cv~>terminals)
      (when (equal (term~>direction) "inputOutput")
        (setq pinCount (plus pinCount 1))))
    (printf "Layout pin count: %d\n" pinCount)
    (dbClose cv)
    pinCount))
