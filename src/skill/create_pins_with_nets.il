
;; create_pins_proper.il - Create pins with proper net handling
(let ((cv (dbOpenCellViewByType "llm_test" "testv1" "layout" "" "a"))
      (pinCount 0))
  (when cv
    (foreach shape (cv~>shapes)
      (when (and (shape~>objType == "label") (equal (shape~>purpose) "pin"))
        (let ((layer (shape~>lpp))
              (labelText (shape~>theLabel))
              (bBox (shape~>bBox)))
          ;; Find or create net
          (let ((net (dbFindNetByName cv labelText)))
            (unless net
              (setq net (dbCreateNet cv labelText)))
            (when net
              ;; Create pin on the net
              (let ((pin (dbCreatePin cv net layer bBox)))
                (when pin
                  (setq pinCount (1+ pinCount)))))))))
    (printf "Created %d pins\n" pinCount)
    (dbSave cv)
    (dbClose cv)
    pinCount))
