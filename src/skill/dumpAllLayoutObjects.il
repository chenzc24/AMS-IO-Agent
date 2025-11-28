(procedure (dumpAllLayoutObjects_enhanced libName cellName viewName outFile)
  (let (cv fp obj bbox xMin xMax yMin yMax ctr)
    (setq cv (dbOpenCellViewByType libName cellName viewName "maskLayout" "r"))
    (when cv
      (setq fp (outfile outFile "w"))

      (foreach obj cv~>shapes
        (setq bbox (obj~>bBox))
        (setq xMin (car (car bbox)))
        (setq yMin (cadr (car bbox)))
        (setq xMax (car (cadr bbox)))
        (setq yMax (cadr (cadr bbox)))
        (setq ctr (list (* 0.5 (+ xMin xMax)) (* 0.5 (+ yMin yMax))))
        (if (equal obj~>objType "label")
          (fprintf fp "SHAPE_LABEL LAYER=%s BBOX=%L CENTER=%L\n"
                   (obj~>layerName) bbox ctr)
          (fprintf fp "SHAPE %s LAYER=%s BBOX=%L\n"
                   (obj~>objType) (obj~>layerName) bbox))
      )

      (foreach obj cv~>labels
        (fprintf fp "TEXT_LABEL NAME=\"%s\" LAYER=%s AT=%L\n"
                 (obj~>theLabel) (obj~>layerName) (obj~>xy)))

      (foreach obj cv~>instances
        (fprintf fp "INST %s LIB=%s CELL=%s XY=%L ORIENT=%s\n"
                 (obj~>name)
                 (obj~>master~>libName)
                 (obj~>master~>cellName)
                 (obj~>xy)
                 (obj~>orient)))

      (close fp)
      (dbClose cv)
      (println (strcat "Dump completed to: " outFile))
    )
  )
)
