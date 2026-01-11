
;; create_terminals2.il - Create terminals using dbSetField
(let ((cv (dbOpenCellViewByType "llm_test" "testv1" "layout" "" "a"))
      (termCount 0))
  (when cv
    (foreach shape (cv~>shapes)
      (when (and (shape~>objType == "label") (equal (shape~>purpose) "pin"))
        (let ((layer (shape~>lpp))
              (labelText (shape~>theLabel))
              (bBox (shape~>bBox)))
          ;; Create terminal
          (let ((term (dbCreateTerm cv labelText "inputOutput")))
            (when term
              (dbSetField term "layer" layer)
              (dbSetField term "bBox" bBox)
              (setq termCount (1+ termCount)))))))
    (printf "Created %d terminals\n" termCount)
    (dbSave cv)
    (dbClose cv)
    termCount))
