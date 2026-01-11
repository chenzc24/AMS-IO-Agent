
;; count_pins.il - Count pins in current cellview
(let ((cv (geGetEditCellView))
      (pinCount 0))
  (when cv
    (foreach term (cv~>terminals)
      (when (equal (term~>direction) "inputOutput")
        (setq pinCount (plus pinCount 1))))
    (printf "Pin count: %d\n" pinCount)
    pinCount))
