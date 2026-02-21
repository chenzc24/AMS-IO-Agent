
;; Description: Create library llm_test, cell test_v2, and generate IO ring layout
(let ((lib "llm_test")
      (cell "test_v2")
      (view "layout")
      (tech "tpd018bcdnv5")
      (cv nil))
  ;; Create library if not exists
  (unless (ddGetObj lib)
    (println "Creating library: " lib)
    (dbCreateLib lib tech)
  )
  ;; Open or create cellview
  (setq cv (dbOpenCellViewByType lib cell view "maskLayout" "w"))
  (unless cv
    (println "Failed to create cellview")
    (return nil)
  )
  (println "Cellview opened: " lib "/" cell "/" view)
  (hiSetCurrentWindow (hiGetCurrentWindow))
  ;; Now execute the layout generation script
  (println "Starting layout generation...")
  ; The layout script expects cv variable to be set (already set)
  ; We'll embed the layout script here
  ; Instead of embedding, we can load the file, but easier to embed the content
  ; We'll copy the content from the generated layout script
  ; For brevity, we'll include the whole script (but we need to be careful with quotes)
  ; Let's use load function to load the IL file
  (load "output/io_ring_layout.il")
  (println "Layout generation completed.")
  (return t)
)
