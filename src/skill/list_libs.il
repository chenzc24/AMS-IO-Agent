
;; List all libraries in the current session
(let ((libs (getOpenLibs)))
  (println "Open libraries: " libs)
  (println "All libraries: " (getLibList))
  (buildString libs)
)
