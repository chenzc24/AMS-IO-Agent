
;; Open cellview llm_test/test_v2/layout
(let ((lib "llm_test")
      (cell "test_v2")
      (view "layout")
      (cv nil))
  (setq cv (dbOpenCellViewByType lib cell view "maskLayout" "w"))
  (if cv
      (progn
        (println "Opened cellview: " lib "/" cell "/" view)
        (string-append "Success: " (get_cellview_info))
      )
      (progn
        (println "Failed to open cellview")
        "Failed"
      )
  )
)
