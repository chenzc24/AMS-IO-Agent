
;; add_terminals2.il - Create terminals from pin labels
(let ((cv (dbOpenCellViewByType "llm_test" "testv1" "layout" "" "a"))
      (termCount 0))
  (when cv
    (foreach shape (cv~>shapes)
      (when (and (shape~>objType == "label") (equal (shape~>purpose) "pin"))
        (let ((layer (shape~>lpp))
              (labelText (shape~>theLabel))
              (bBox (shape~>bBox))
              (orientation (shape~>orientation)))
          ;; Create a pin shape (rectangle) around label
          (let ((pinShape (dbCreateRect cv layer (list (car bBox) (cadr bBox)) (list (caddr bBox) (cadddr bBox)))))
            (when pinShape
              (setq pinShape~>purpose "pin")
              ;; Create terminal
              (let ((term (dbCreateTerm cv labelText "inputOutput")))
                (when term
                  (setq term~>layer layer)
                  (setq term~>bBox bBox)
                  (setq termCount (1+ termCount)))))))))
    (printf "Created %d terminals\n" termCount)
    (dbSave cv)
    (dbClose cv)
    termCount))
