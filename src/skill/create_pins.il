
;; create_pins2.il - Create pins from pin labels using dbCreatePin (4 args)
(let ((cv (dbOpenCellViewByType "llm_test" "testv1" "layout" "" "a"))
      (pinCount 0))
  (when cv
    (foreach shape (cv~>shapes)
      (when (and (shape~>objType == "label") (equal (shape~>purpose) "pin"))
        (let ((layer (shape~>lpp))
              (labelText (shape~>theLabel))
              (bBox (shape~>bBox)))
          ;; Determine pin layer: use METAL6 for outer pins, METAL1 for inner pins
          (let ((pinLayer (if (equal layer "METAL6") "METAL6" "METAL1")))
            ;; Create pin using dbCreatePin
            (let ((pin (dbCreatePin cv pinLayer labelText bBox)))
              (when pin
                (setq pinCount (1+ pinCount))))))))
    (printf "Created %d pins\n" pinCount)
    (dbSave cv)
    (dbClose cv)
    pinCount))
