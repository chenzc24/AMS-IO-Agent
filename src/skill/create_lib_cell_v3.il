
;; Create library llm_test and cell test_v2 layout
(let ((lib "llm_test")
      (cell "test_v2")
      (view "layout")
      (tech "tpd018bcdnv5")
      (cv nil))
  (unless (ddGetObj lib)
    (println "Creating library: " lib)
    (dbCreateLib lib tech)
  )
  (setq cv (dbOpenCellViewByType lib cell view "maskLayout" "w"))
  (if cv
      (progn
        (println "Created cellview: " lib "/" cell "/" view)
        (string-append "Success: " lib "/" cell "/" view)
      )
      (progn
        (println "Failed to create cellview")
        "Failed"
      )
  )
)
